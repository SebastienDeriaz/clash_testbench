# Clash stimulis
# Sébastien Deriaz - 22.11.2022

import numpy as np

from enum import Enum

from random import randint

class LogicLevel(Enum):
    LOGIC = 0
    UNKNOWN = 1
    DONTCARE = 2


LOGIC_LEVEL_MATCH = {
    '0' : LogicLevel.LOGIC,
    '1' : LogicLevel.LOGIC,
    'x' : LogicLevel.UNKNOWN,
    '-' : LogicLevel.UNKNOWN
}
# If it is int, it will always be (x, LogicLevel.Unknown)

def _convertValues(wave, data = None):
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
    values : str or list[str] or int or list[int]
    """

    if data is None:
        data = wave

    if isinstance(wave, str):
        # '*' or '******'
        return [LOGIC_LEVEL_MATCH[x] for x in wave]
    elif isinstance(wave, int):
        # 123
        return [(wave, LogicLevel.LOGIC)]
    elif isinstance(wave, list):
        if isinstance(wave[0], int):
            # list[int]
            return [(v, LogicLevel.LOGIC) for v in wave]
        elif isinstance(wave[0], str):
            # list[str]
            return [LOGIC_LEVEL_MATCH[v] for v in wave]  
        else:
            raise ValueError(f"Invalid type : list[{type(wave[0])}]")
    else:
        raise ValueError(f"Invalid type : {type(wave)}")

class Signal:
    def __init__(self) -> None:
        self._values = None

    def valuesList(self) -> list:
        """
        List of values that, when printed, are readable by clash's sampleN function
        """
        pass
            
    def type(self) -> str:
        pass

    def fit(self, N):
        self._values = N * [self._values[0]]

    def fromActual(self, actualValues):
        pass

    def __str__(self) -> str:
        return f"{self.type()} : {self._values}"
    
    def __repr__(self) -> str:
        return self.__str__()

    def __iadd__(self, x):
        self._values += _convertValues(x)
        return self

    def __len__(self):
        return len(self._values)

class Bit(Signal):
    def __init__(self, values) -> None:
        """
        Bit Class 
        values : list[str] or str
        """

        self._values = []
        if values is not None:
            # Add them to the list
            self += values

    def valuesList(self):
        output = []
        for i in self._values:
            if i[1] == LogicLevel.LOGIC:
                output.append(str(i[0]))
            elif i[1] == LogicLevel.UNKNOWN:
                output.append(str(randint(0,1)))
        return output

    def type(self) -> str:
        return "Bit"
    
    def fromActual(self, actualValues):        
        return Bit(actualValues)

class BitVector(Signal):
    def __init__(self, N, values=None) -> None:
        """
        BitVector class
        """
        self.N = N

        self._values = []
        if values is not None:
            # Add them to the list
            self += values

        values_only = [x[0] for x in self._values]
        if np.min(values_only) < 0 or np.max(values_only) > (2**N - 1):
            raise ValueError(f"Invalid values range ({np.min(self._values)} -> {np.max(self._values)})")

    

    def valuesList(self):
        output = []
        for i in self._values:
            if i[1] == LogicLevel.LOGIC:
                output.append(str(i[0]))
            elif i[1] == LogicLevel.UNKNOWN:
                output.append(str(randint(0,2**self.N - 1)))
        return output
    
    def type(self) -> str:
        return "BitVector"
    
    def fromActual(self, actualValues):
        return BitVector(self.N, actualValues)


class Unsigned(Signal):
    def __init__(self, N, values=None) -> None:
        self.N = N

        self._values = []
        if values is not None:
            # Add them to the list
            self += values

        values_only = [x[0] for x in self._values]
        if np.min(values_only) < 0 or np.max(values_only) > (2**N - 1):
            raise ValueError(f"Invalid values range ({np.min(self._values)} -> {np.max(self._values)})")
        
    def valuesList(self):
        output = []
        for i in self._values:
            if i[1] == LogicLevel.LOGIC:
                output.append(str(i[0]))
            elif i[1] == LogicLevel.UNKNOWN:
                output.append(str(randint(0,2**self.N - 1)))
        return output
    
    def fromActual(self, actualValues):
        return Unsigned(self.N, actualValues)

    def type(self) -> str:
        return f"Unsigned"

class State(Signal):
    def __init__(self, values=None) -> None:

        self._values = []
        if values is not None:
            # Add them to the list
            self += values

        values_only = [x[0] for x in self._values]
        
    def valuesList(self):
        output = []
        for i in self._values:
            if i[1] == LogicLevel.LOGIC:
                output.append(str(i[0]))
            elif i[1] == LogicLevel.UNKNOWN:
                raise ValueError("Unknown is not supported for type \"State\"")
        return output
    
    def fromActual(self, actualValues):
        return Unsigned(self.N, actualValues)

    def type(self) -> str:
        return f"State"