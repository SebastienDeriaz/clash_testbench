# Clash stimulis
# Sébastien Deriaz - 22.11.2022

import numpy as np

class Signal:
    def __init__(self) -> None:
        self._values = None

    def valuesStr(self) -> list:
        pass
    
    def valuesInt(self) -> list:
        pass
            
    def type(self) -> str:
        pass

    def fromActual(self, actualValues):
        pass

    def __str__(self) -> str:
        return f"{self.type()} : {self._values}"
    
    def __repr__(self) -> str:
        return self.__str__()
    
    def __len__(self):
        return len(self.valuesInt())
    
    



class Bit(Signal):
    def __init__(self, values : list) -> None:
        """
        Bit Class
        """
        if not (isinstance(values, list) or isinstance(values, np.ndarray) or isinstance(values, tuple)):
            raise TypeError(f"Invalid input type ({type(values)})")
        
        # Convert to int (for example if the data comes from the testbench)
        self._values = np.array(values).astype(int)

        if np.min(self._values) < 0 or np.max(self._values) > 1:
            raise ValueError(f"Invalid values range ({np.min(self._values)} -> {np.max(self._values)})")
        
    def valuesStr(self):
        return [str(x) for x in self._values]
    
    def valuesInt(self):
        return [int(x) for x in self._values]

    def type(self) -> str:
        return "Bit"
    
    def test_method(self):
        return "test"
    
    def fromActual(self, actualValues):
        return Bit(actualValues)

class BitVector(Signal):
    def __init__(self, N, values=None) -> None:
        """
        BitVector class
        """
        self.N = N

        if not (isinstance(values, list) or isinstance(values, np.ndarray) or isinstance(values, tuple)):
            raise TypeError(f"Invalid input type ({type(values)})")
        
        # Convert to int (for example if the data comes from the testbench)
        self._values = np.array(values).astype(int)

    def valuesStr(self):
        return [str(x) for x in self._values]

    def valuesInt(self):
        return [int(x) for x in self._values]
    
    def type(self) -> str:
        return "BitVector"
    
    def fromActual(self, actualValues):
        return BitVector(self.N, actualValues)

class Unsigned(Signal):
    def __init__(self, N, values=None) -> None:
        self.N = N

        if not (isinstance(values, list) or isinstance(values, np.ndarray) or isinstance(values, tuple)):
            raise TypeError(f"Invalid input type ({type(values)})")
        
        # Convert to int (for example if the data comes from the testbench)
        self._values = np.array(values).astype(int)

        if np.min(self._values) < 0 or np.max(self._values) > (2**N - 1):
            raise ValueError(f"Invalid values range ({np.min(self._values)} -> {np.max(self._values)})")
        
    def valuesStr(self):
        return [str(x) for x in self._values]

    def valuesInt(self):
        return [int(x) for x in self._values]
    
    def fromActual(self, actualValues):
        return Unsigned(self.N, actualValues)

    def type(self) -> str:
        return f"Unsigned"
    
