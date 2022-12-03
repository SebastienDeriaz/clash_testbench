from .logic import *
import json
import wavedrom

WD_KEY_NAME = 'name'
WD_KEY_WAVE = 'wave'
WD_KEY_DATA = 'data'
WD_KEY_MAIN = 'signal'


WD_LOGIC_HIGH = '1'
WD_LOGIC_LOW = '0'
WD_LOGIC_UNKNOWN = 'x'
WD_DATA_SYMBOLS = ['2', '3', '4', '5', '6', '7', '8', '9']

WD_SYMBOL_LOGIC = {
    '0': Level.LOW,
    '1': Level.HIGH,
    'x': Level.UNKNOWN
}

WD_LOGIC_SYMBOL = {
    Level.LOW: '0',
    Level.HIGH: '1',
    Level.UNKNOWN: 'x',
    0: '0',
    1: '1'
}


def isClock(entry: dict):
    """
    Check if an entry has a clock wave

    Parameters
    ----------
    entry : dict

    Returns
    -------
    output : bool
    """
    if WD_KEY_WAVE in entry:
        if 'p' in entry[WD_KEY_WAVE] or 'P' in entry[WD_KEY_WAVE]:
            return True
    return False


def symbolDataToSample(symbol: str, data=None) -> Sample:
    """
    Convert a symbol (+data) to a sample

    Parameters
    ----------
    symbol : str
        a wavedrom symbol
    data : int or str
        An optional data value for this symbol
    """
    if symbol in WD_SYMBOL_LOGIC:
        # Data doesn't matter
        return Sample(WD_SYMBOL_LOGIC[symbol])
    elif symbol in WD_DATA_SYMBOLS:
        if data is None:
            raise ValueError(
                f"Sample's symbol '{symbol}' cannot be linked with None data")
        return Sample(data, colorIndex=WD_DATA_SYMBOLS.index(symbol))


def sampleToSymbolData(sample: Sample):
    """
    Convert a sample to symbol (+ data)

    Parameters
    ----------
    sample : Sample

    Returns
    -------
    wave : str
    data : str or int
    """
    wave, data = None, None

    if sample._value in WD_LOGIC_SYMBOL:
        # It is a logic level
        wave = WD_LOGIC_SYMBOL[sample._value]
    elif isinstance(sample._value, str) or isinstance(sample._value, int):
        # int 0 and 1 are taken care of above
        wave = WD_DATA_SYMBOLS[sample.colorIndex]
        data = sample._value
    else:
        raise ValueError(
            f"Cannot convert sample value of type {type(sample._value)}")

    return wave, data


def compress(wave: list, data: list = None):
    """
    Compress a WD wave ['0', '0', '0', '1', '1', '1'] -> 0..1..
    Data (if supplied) is also compressed
    """

    current_w = ''
    current_d = ''
    new_wave = ''
    new_data = []

    data_list = [None] * len(wave) if data is None else data

    for w, d in zip(wave, data_list):
        if w != current_w or (d != None and d != current_d):
            new_wave += w
            if w in WD_DATA_SYMBOLS:
                new_data.append(d)
        else:
            new_wave += '.'
        current_w = w
        current_d = d

    #print(f"{wave}, {data} -> {new_wave}, {new_data}")
    if data is None:
        return new_wave
    else:
        return new_wave, new_data


def uncompress(wave: str, data: list = None):
    """
    Uncompress a WD wave
    '0..1..' -> ['0', '0', '0', '1', '1', '1']

    '3.x3' + ['A', 'B'] -> '33x3' + ['A', 'A', None, 'B']
    Data (if supplied) is also uncompressed
    """
    new_wave = []
    new_data = []

    if data is not None:
        data_iter = iter(data)

    #data_list = [None] * len(wave) if data is None else data
    for i, w in enumerate(wave):
        if w == '.':
            if i == 0:
                raise ValueError("Signal cannot start with '.'")
            new_wave.append(new_wave[-1])
            new_data.append(new_data[-1])
        else:
            new_wave.append(w)
            if (w == 'x') or (data is None) or (w in [WD_LOGIC_HIGH, WD_LOGIC_LOW]):
                new_data.append(None)
            elif w in WD_DATA_SYMBOLS:
                # This is a data frame
                try:
                    new_data.append(next(data_iter))
                except StopIteration:
                    raise ValueError(f"Mismatch in wave and data length : {wave}, {data}")
            else:
                raise ValueError(f"Couldn't parse symbol : '{w}'")

    #print(f"{wave}, {data} -> {new_wave}, {new_data}")

    if data is None:
        return new_wave
    else:
        return new_wave, new_data


def entryToSignal(entry: dict):
    """
    Convert an entry (wave, data and name)

    Parameters
    ----------
    entry : dict
        The entry must contain the following keys : wave, name
        The following keys are optional : data

    Returns
    -------
    signal : Signal
    """
    # 1) Check if the entry has the necessary keys
    if WD_KEY_NAME not in entry:
        raise ValueError(f"Entry {entry} missing key '{WD_KEY_NAME}")
    if WD_KEY_WAVE not in entry:
        raise ValueError(f"Entry {entry} missing key '{WD_KEY_WAVE}")

    data, wave, name = entry.get(WD_KEY_DATA), entry.get(
        WD_KEY_WAVE), entry.get(WD_KEY_NAME)
    # 2) Uncompress the signal (remove the '.')
    if data is None:
        uwave = uncompress(wave)
        udata = [None] * len(uwave)
    else:
        uwave, udata = uncompress(wave, data)

    # 3) Create the signal
    signal = Signal(name)

    for w, d in zip(uwave, udata):
        signal += symbolDataToSample(w, d)

    return signal


def signalToEntry(signal: Signal) -> dict:
    """
    Convert a signal to an entry (data, wave, name)

    Parameters
    ----------
    signal : Signal

    Returns
    -------
    entry : dict
    """
    entry = {}
    # 1) Set the name
    entry[WD_KEY_NAME] = signal.name
    uwave, udata = [], []

    # 2) Add the samples

    for sample in signal:
        w, d = sampleToSymbolData(sample)
        uwave.append(w)
        udata.append(d)

    entry[WD_KEY_WAVE], entry[WD_KEY_DATA] = compress(uwave, udata)

    return entry


def _listWDEntries(entry, remove_first=False, branch=[]):
    if isinstance(entry, list):
        # It's a group
        output = []
        # Remove the first value (the header)
        offset = 1 if remove_first else 0
        for i, e in enumerate(entry[offset:]):
            n = _listWDEntries(e, True, branch + [i + offset])
            output += n if isinstance(n, list) else [n]
    else:
        output = (branch, entry)
    return output


class Chronogram:
    def __init__(self, file: str = None):
        """
        Create a new chronogram

        Parameters
        ----------
        file : str
            The file from which the chronogram is loaded
            if None (default), a new chronogram will be made
        """

        # 1) Read the json file
        with open(file, 'r', encoding='utf-8') as f:
            self._json_content = json.load(f)

            # 1) List all of the entries and create a tree of their position based on their names
            #    note : no two entries can have the same name
            self.updateEntriesTree()

        self._templates = None

        self._signals = self.getSignals()

    def updateEntriesTree(self):
        entries = _listWDEntries(self._json_content[WD_KEY_MAIN])
        self._entriesTree = {}
        for branch, entry in entries:
            # Check if the entry is empty and if it has a name
            if entry:
                if WD_KEY_NAME in entry:
                    _name = entry[WD_KEY_NAME]
                    # Check if another entry has the same name (not allowed)
                    if _name in self._entriesTree:
                        raise ValueError(f"Duplicate of name {_name}")

                    # If not, it's all good we can add it
                    self._entriesTree[_name] = branch
                else:
                    # This entry is ignored
                    raise ValueError(f"Entry {entry} does not have a name")

    def _WDGetEntry(self, branch: list) -> dict:
        """
        Return an entry from the WD description and a branch

        Parameters
        ----------
        branch : list
            List of indices to get to the entry

        Returns
        -------
        entry : dict
        """
        entry = self._json_content[WD_KEY_MAIN]
        for b in branch:
            entry = entry[b]

        return entry

    def _WDSetEntry(self, entry: dict, branch: list):
        """
        Set an entry inside the WD description

        Parameters
        ----------
        entry : dict
            The entry to replace
        branch : list
            List of indices to get to the entry
        """
        top = self._json_content[WD_KEY_MAIN]
        for b in branch[:-1]:
            # Go into the branch but to keep the last one for mutability
            top = top[b]

        top[branch[-1]] = entry

    def _WDAddEntry(self, entry: dict):
        """
        Add an entry to the list of entries

        Parameters
        ----------
        entry : dict
        """
        self._json_content[WD_KEY_MAIN].append(entry)

    def getSignals(self, names: "list[str]" = None) -> dict:
        """
        Get a list of signals

        Parameters
        ----------
        name : list
            List of signals names. If None, all of the signals are returned

        Returns
        -------
        signals : dict
            List of signals
        """

        output = {}
        if names is None:
            for name, branch in self._entriesTree.items():
                entry = self._WDGetEntry(branch)
                if WD_KEY_WAVE in entry and not isClock(entry):
                    output[name] = entryToSignal(entry)
        else:
            for n in names:
                if n not in self._entriesTree:
                    raise ValueError(
                        f"name {n} doesn't exist inside this chronogram")
                entry = self._WDGetEntry(self._entriesTree[n])
                output[n] = entryToSignal(entry)

        return output

    def setSignals(self, signals: dict):
        """
        Set a list of signals

        Parameters
        ----------
        signals : dict
            List of signals
        """

        for _name, signal in signals.items():
            # Update the name of the signal, just to be sure
            signal.name = _name

            if _name in self._entriesTree:
                # Edit the entry
                self._WDSetEntry(signalToEntry(signal),
                                 self._entriesTree[_name])
            else:
                # Create a new one
                self._WDAddEntry(signalToEntry(signal))

    def applyTemplate(self, entry: dict, entry_template: dict) -> dict:
        """
        Apply a template to an entry

        Parameters
        ----------
        entry : dict
        entry_template : dict

        Returns
        -------
        new_entry : dict

        """
        new_entry = entry
        if WD_KEY_DATA not in entry:
            raise RuntimeError(
                "Cannot apply template to an entry that doesn't contain a data field")

        uwave, udata = uncompress(
            entry.get(WD_KEY_WAVE), entry.get(WD_KEY_DATA))
        uwavet, udatat = uncompress(entry_template.get(
            WD_KEY_WAVE), entry_template.get(WD_KEY_DATA))
        if len(uwave) != len(uwavet):
            raise RuntimeError(
                f"Length of entry and template entry do not match ! ({len(uwave)})/({len(uwavet)})")

        uwaven = uwave.copy()
        udatan = udata.copy()
        
        for i, (w, d, wt, dt) in enumerate(zip(uwave, udata, uwavet, udatat)):
            if w != wt:
                # There's something to change
                if wt in WD_DATA_SYMBOLS:
                    # Convert to data
                    uwaven[i] = wt
                    if w in [WD_LOGIC_LOW, WD_LOGIC_HIGH]:
                        # The original is '1' and we want a 3 + ['1'] for example
                        # Insert the value inside data
                        udatan[i] = w
                        pass

                    else:
                        # Only the colors needs to be changed
                        pass
        
        waven, datan = compress(uwaven, udatan)

        new_entry[WD_KEY_DATA] = datan
        new_entry[WD_KEY_WAVE] = waven

        return new_entry

    def setTemplates(self, templates: dict):
        """
        Set templates

        Parameters
        ----------
        templates : dict
            in the form {signal_name : template_name, ...}
        """
        self._templates = templates

    def applyTemplates(self):
        """
        Apply templates to all the signals
        """
        if self._templates is not None:
            for _name, branch in self._entriesTree.items():
                if _name in self._templates:
                    # This entry needs to be updated
                    template = self._WDGetEntry(
                        self._entriesTree[self._templates[_name]])
                    entry = self._WDGetEntry(self._entriesTree[_name])
                    self._WDSetEntry(self.applyTemplate(
                        entry, template), branch)

    def saveJson(self, output_file: str):
        """
        Outputs the chronogram to a .json file

        Parameters
        ----------
        output_file : str
            Output file path
        """
        self.updateEntriesTree()
        self.applyTemplates()

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self._json_content, f, indent=2)

    def saveSVG(self, output_file: str):
        """
        Output the chronogram to an SVG file

        Parameters
        ----------
        output_file : str
            Output file path
        """
        self.updateEntriesTree()
        self.applyTemplates()

        svg = wavedrom.render(str(self._json_content))
        svg.saveas(output_file)
    
    def __getitem__(self, key):
        return self._signals[key]