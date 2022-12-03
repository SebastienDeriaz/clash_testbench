from .logic import LogicLevel



# Wavedrom keys
WD_WAVE = 'wave'
WD_DATA = 'data'
WD_MAIN = 'signal'
WD_NAME = 'name'

WD_DATA_SYMBOLS = ['2', '3', '4', '5', '6', '7', '8', '9']

WD_SYMBOL_MATCH = {
    '0' : (0, LogicLevel.LOGIC),
    '1' : (1, LogicLevel.LOGIC),
    '3' : (None, LogicLevel.LOGIC),
    '4' : (None, LogicLevel.LOGIC),
    '5' : (None, LogicLevel.LOGIC),
    '6' : (None, LogicLevel.LOGIC),
    '7' : (None, LogicLevel.LOGIC),
    '8' : (None, LogicLevel.LOGIC),
    '9' : (None, LogicLevel.LOGIC),
    'x' : (None, LogicLevel.UNKNOWN),
    '-' : (None, LogicLevel.UNKNOWN)
}

def compress(wave : list, data : list = None):
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
                if w != 'x':
                    new_data.append(d)
            else:
                new_wave += '.'
            current_w = w
            current_d = d

        if data is None:
            return new_wave
        else:
            return new_wave, new_data

def uncompress(wave : str, data : list = None):
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
            if w == 'x' or data is None:
                new_data.append(None)
            elif w in WD_DATA_SYMBOLS:
                # This is a data frame
                new_data.append(next(data_iter))
            else:
                # This is a logic 0 or 1 (or another)
                new_data.append(WD_SYMBOL_MATCH[w][0])
    
    if data is None:
        return new_wave
    else:
        return new_wave, new_data