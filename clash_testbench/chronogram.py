# Chronogram class
# Sébastien Deriaz - 26.11.2022

from .testbench import Testbench
import wavedrom
from .signals import *
from functools import reduce
from os.path import basename
import json


from json import dumps

# Wavedrom keys
WD_WAVE = 'wave'
WD_DATA = 'data'
WD_MAIN = 'signal'
WD_NAME = 'name'

# Clash-testbench keys
CT_DIR = 'dir'
CT_ORDER = 'order'
CT_BITS = 'bits'
CT_TYPE = 'type'
CT_FROM = 'from'

CT_DIR_IN = 'in'
CT_DIR_OUT = 'out'


def _clock(N):
    """
    Return a clock wave

    Parameters
    ----------
    N : int
        The number of clock cycles
    """

    output = {}

    output[WD_WAVE] = 'P' + '.' * (N-1)

    return output


def compress(wave : str, data : list = None):
        """
        Compress a WD wave ['0', '0', '0', '1', '1', '1'] -> 0..1..
        Data (if supplied) is also compressed
        """
        
        current = ''
        new_wave = ''
        new_data = []

        data_list = [None] * len(wave) if data is None else data

        for w, d in zip(wave, data_list):
            key = w if d is None else d
            if key != current:
                new_wave += w
                new_data.append(d)
            else:
                new_wave += '.'
            current = key
        
        if data is None:
            return new_wave
        else:
            return new_wave, new_data

def uncompress(wave : str, data : list = None):
    """
    Uncompress a WD wave '0..1..' -> ['0', '0', '0', '1', '1', '1']
    Data (if supplied) is also uncompressed
    """
    new_wave = ''
    new_data = []

    data_list = [None] * len(wave) if data is None else data

    for w, d in zip(wave, data_list):
        if w == '.':
            new_wave += new_wave[-1]
            new_data.append(new_data[-1])
        else:
            new_wave += w
            new_data.append(d)
    
    if data is None:
        return new_wave
    else:
        return new_wave, new_data


def _stimuliToWD(name : str, st : Signal):
    """
    Convert a stimuli to a wavedrom entry
    
    Parameters
    ----------
    st : Stimuli

    Returns
    -------
    output : dict
        Dictionary containing all the keys and values for the wavedrom entry
    """

    output = {}
    if name is not None:
        output["name"] = name
    if st.type() == 'Bit':
        output[WD_WAVE] = compress(''.join(['1' if x else '0' for x in st.valuesList()]))
    elif st.type() == 'BitVector':
        output[WD_WAVE], output[WD_DATA] = compress('3'*len(st.valuesList()), st.valuesList())
    elif st.type() == 'Unsigned':
        output[WD_WAVE], output[WD_DATA] = compress('4'*len(st.valuesList()), st.valuesList())

    return output



def _listWDNodes(entry, remove_first=False, branch=[]):    
    if isinstance(entry, list):
        # It's a group
        output = []
        # Remove the first value (the header)
        offset = 1 if remove_first else 0
        for i, e in enumerate(entry[offset:]):
            n = _listWDNodes(e, True, branch + [i + offset])
            output += n if isinstance(n, list) else [n]
    else:
        output = (branch, entry)
    return output





class Chronogram:
    def __init__(self, initializer):
        """
        Chronogram class
        
        Parameters
        ----------
        initializer : str or Testbench
            - str : Path to chrogogram file (generate from chronogram)
            - Testbench : Generate from testbench
        """
        self.inputs = {}
        self.expectedOutputs = {}


        if isinstance(initializer, Testbench):
            self._file = None
            self._tb = initializer
        elif isinstance(initializer, str):
            self._tb = None
            self._file = initializer

            unordered_inputs = []
            unordered_expectedOutputs = []

            with open(self._file, 'r', encoding='utf-8') as f:
                self._input_json_content = json.load(f)

                # 1) remove groups
                self.entries_list = _listWDNodes(self._input_json_content[WD_MAIN])

                # 2) List inputs and expected outputs

                # List of orders (for inputs [0] and outputs [1])
                order_lists = [[],[]]

                for _, entry in self.entries_list:
                    if (CT_DIR in entry) and (WD_NAME in entry) and (CT_TYPE in entry) and (CT_FROM not in entry):
                        # The entry will be used (otherwise it will be ignored)
                        _dir = entry[CT_DIR]
                        isInput = _dir == CT_DIR_IN
                        _name = entry[WD_NAME]
                        _type = entry[CT_TYPE]
                        order_list = order_lists[0 if isInput else 1]
                        
                        # Check if the order is set
                        if CT_ORDER not in entry:
                            raise ValueError(f"Entry {_name} is missing 'order' property")

                        order = entry[CT_ORDER]
                        if order in order_list:
                            raise ValueError(f"Duplicate of order property {order} for {'inputs' if isInput else 'outputs'}")
                        # Add it to the list
                        order_list.append(order)

                        # Create each signal accordingly
                        wave_data = uncompress(entry.get(WD_WAVE), entry.get(WD_DATA))
                        if _type == 'Bit':
                            signal = Bit(wave_data)
                        elif _type == 'BitVector':
                            signal = BitVector(entry[CT_BITS], wave_data[1])
                        elif _type == 'Unsigned':
                            signal = Unsigned(entry[CT_BITS], wave_data[1])
                        elif _type == 'State':
                            signal = State(wave_data[1])
                        else:
                            raise RuntimeError(f"Unsupported type \"{_type}\"")

                        if isInput:
                            unordered_inputs.append((order, _name, signal))
                            
                        else:
                            unordered_expectedOutputs.append((order, _name, signal))

                # Sort inputs and save them
                unordered_inputs.sort(key = lambda x : x[0])
                self.inputs = {name : signal for (_, name, signal) in unordered_inputs}
                # Sort expected outputs and save them
                unordered_expectedOutputs.sort(key = lambda x : x[0])
                self.expectedOutputs = {name : signal for (_, name, signal) in unordered_expectedOutputs}
        else:
            raise ValueError("Invalid initializer type")

    def loadReport(self, report):
        """
        Load the report
        """

        self._tb = report

    def _fromChronogram(self):
        """
        Edit the given chronogram and output its new json definition
        """
        # Check if the report was loaded
        if self._tb is None:
            raise ValueError("Testbench (report) wasn't loaded, please use chronogram.loadReport(report)")

        # Replace all entries with CT_FROM key with their actual values
        json_content = self._input_json_content.copy()


        for branch, entry in self.entries_list:
            if CT_FROM in entry:
                # This entry needs to be edited
                _from = entry[CT_FROM]
                # get the name of the expected output
                for _, _entry in self.entries_list:
                    if (WD_NAME in _entry) and (CT_FROM not in _entry) and (_entry[WD_NAME] == _from):
                        # Found it ! get its name
                        expectedOutputName = _entry[WD_NAME]
                        #order = int(_entry[CT_ORDER])
                        break
                else:
                    raise ValueError(f"Couldn't find associated expected output for \"{_from}\"")

                # Now we can match edit the json entry (by locating with the branch) and putting the corresponding signal (found with "from")
                dest = json_content[WD_MAIN]
                # Traverse the branch backward and keep the last index (to keep reference to the main list), which is branch[-1]
                for b in branch[:-1]:
                    dest = dest[b]

                for key, val in _stimuliToWD(None, self._tb.actualOutputSignals[expectedOutputName]).items():
                    dest[branch[-1]][key] = val



        return json_content



    def _fromTestbench(self, title):
        json_content = {}
        chronogram_length = len(list(self._tb.inputSignals.values())[0])
        json_content["head"] = {
            'text' : title,
            'tick' : 0,
            'every' : 1
        }
        json_content["signal"] = []
        json_content["signal"].append(_clock(chronogram_length))
        json_content["signal"].append(['inputs', *[_stimuliToWD(*t) for t in self._tb.inputSignals.items()]])
        json_content["signal"].append({})
        json_content["signal"].append(['out (th)', *[_stimuliToWD(*t) for t in self._tb.expectedOutputSignals.items()]])
        json_content["signal"].append({})
        if self._tb.actualOutputSignals is not None:
            json_content["signal"].append(['out', *[_stimuliToWD(*t) for t in self._tb.actualOutputSignals.items()]])
            json_content["signal"].append({})

        return json_content

    def saveSVG(self, svgFile : str):
        """
        Save the chronogram as an svg file
        
        """

        if self._file is None:
            # From testbench
            json_content = self._fromTestbench(basename(svgFile))
        else:
            json_content = self._fromChronogram()



        svg = wavedrom.render(str(json_content))
        svg.saveas(svgFile)
    
