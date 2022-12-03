# Convertvalues.py
# Sébastien Deriaz - 01.12.2022

from .logic import *
from .wd import WD_SYMBOL_MATCH


def convertValues(wave_data):
    """
    Convert input values into the corresponding (value, logicLevel) pair 

    Use cases :
    0 -> [(0, logic)]
    1 -> [(1, logic)]
    [0, 1] -> [(0, logic), (1, logic)]
    ['0', 'x', '1'] -> [(0, logic), (0, unknown), (1, logic)]
    '0x1' -> [(0, logic), (0, unknown), (1, logic)]
    '0' -> [(0, logic)]

    Parameters
    ----------
    wave_data : wave or (wave, data)
    """

    if isinstance(wave_data, tuple):
        wave, data = wave_data
    else:
        wave, data = wave_data, None

    if data is None:
        # Wave only
        if isinstance(wave, str):
            # '*' or '******'
            return [WD_SYMBOL_MATCH[w] for w in wave]
        elif isinstance(wave, int):
            # 123
            return [(wave, LogicLevel.LOGIC)]
        elif isinstance(wave, list):
            if isinstance(wave[0], int):
                # list[int]
                return [(w, LogicLevel.LOGIC) for w in wave]
            elif isinstance(wave[0], str):
                # list[str]
                if sum([len(w) for w in wave]) > len(wave):
                    # ['Idle', 'State1', ...]
                    return [(w, LogicLevel.LOGIC) for w in wave]
                else:
                    # ['0', '1', ... ]
                    return [WD_SYMBOL_MATCH[w] for w in wave]
    elif (isinstance(wave, str) or isinstance(wave, list)) and isinstance(data, list):
        return [(d, WD_SYMBOL_MATCH[w][1]) for w, d in zip(wave, data)]

    else:
        raise ValueError(f"Invalid wave/data type ({type(wave)} / {type(data)})")

    raise RuntimeError(f"Something was wrong with that wave/data pair : {wave} / {data}")