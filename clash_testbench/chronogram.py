# Chronogram class
# Sébastien Deriaz - 26.11.2022

from .testbench import Testbench
import wavedrom
from .signals import *
from functools import reduce

from json import dumps

WD_WAVE = 'wave'
WD_DATA = 'data'

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
    def compress(raw_wave : str, ext = None):
        """
        Compress a WD wave 000111 -> 0..1..
        """
        
        current = ''
        new_wave = type(raw_wave)()

        for x, key in zip(raw_wave, ext if ext is not None else raw_wave):
            if key != current:
                if isinstance(raw_wave, str):
                    new_wave += x
                else:
                    new_wave.append(x)
            elif isinstance(raw_wave, str):
                new_wave += '.' 
            current = key
        
        return new_wave

    output = {}
    output["name"] = name
    if st.type() == 'Bit':
        output[WD_WAVE] = compress(''.join(['1' if x else '0' for x in st.valuesInt()]))
    elif st.type() == 'BitVector':
        output[WD_WAVE] = compress('3'*len(st.valuesInt()), st.valuesInt())
        output[WD_DATA] = compress(st.valuesInt())
    elif st.type() == 'Unsigned':
        output[WD_WAVE] = compress('4'*len(st.valuesInt()), st.valuesInt())
        output[WD_DATA] = compress(st.valuesInt())

    return output




class Chronogram:
    def __init__(self, tb : Testbench):
        """
        Chronogram class
        
        Parameters
        ----------
        tb : Testbench
            testbench Class
        """
        self._tb = tb

    def saveSVG(self, svgFile : str):
        """
        Save the chronogram as an svg file
        
        """
        json_content = {}
        chronogram_length = len(list(self._tb.inputSignals.values())[0])
        json_content["signal"] = []
        json_content["signal"].append(_clock(chronogram_length))
        json_content["signal"].append(['inputs', *[_stimuliToWD(*t) for t in self._tb.inputSignals.items()]])
        json_content["signal"].append({})
        json_content["signal"].append(['out (th)', *[_stimuliToWD(*t) for t in self._tb.expectedOutputSignals.items()]])
        json_content["signal"].append({})
        if self._tb.actualOutputSignals is not None:
            json_content["signal"].append(['out', *[_stimuliToWD(*t) for t in self._tb.actualOutputSignals.items()]])
            json_content["signal"].append({})



        svg = wavedrom.render(str(json_content))
        svg.saveas(svgFile)
    
