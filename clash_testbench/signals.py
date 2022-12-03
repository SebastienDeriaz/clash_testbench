# Clash stimulis
# Sébastien Deriaz - 22.11.2022

import numpy as np

from enum import Enum
from random import randint
from .logic import LogicLevel

from .convertvalues import convertValues

class Signal:
    def __init__(self) -> None:
        self._values = None
        self.order = None

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
        SYMBOL = {
            LogicLevel.LOGIC : "L",
            LogicLevel.DONTCARE : "-",
            LogicLevel.UNKNOWN : "x"
        }
        values_list = ''
        for d, l in self._values:
            values_list += f"{d}_{SYMBOL[l]} "

        return f"{self.type()} : {values_list}"
    
    def __repr__(self) -> str:
        return self.__str__()

    def __iadd__(self, x):
        self._values += convertValues(x)
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
        for d, l in self._values:
            if l == LogicLevel.LOGIC:
                output.append(str(d))
            elif l == LogicLevel.UNKNOWN:
                output.append(str(randint(0,1)))
        return output

    def type(self) -> str:
        return "Bit"
    
    def fromActual(self, actualValues):
        newBit = Bit(actualValues)
        newBit.order = self.order
        return newBit

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
        newBitVector = BitVector(self.N, actualValues)
        newBitVector.order = self.order
        return newBitVector


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
        newUnsigned = Unsigned(self.N, actualValues)
        newUnsigned.order = self.order
        return newUnsigned

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
        newState = State(actualValues)
        newState.order = self.order
        return newState

    def type(self) -> str:
        return f"State"