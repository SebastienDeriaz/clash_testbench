# Clash stimulis
# Sébastien Deriaz - 22.11.2022

import numpy as np
class Stimuli:
    def __init__(self) -> None:
        self._values = None

    def values(self) -> list:
        pass
            
    def type(self) -> str:
        pass

    def __str__(self) -> str:
        return f"{self.type()} : {self._values}"
    
    def __repr__(self) -> str:
        return self.__str__()



class Bit(Stimuli):
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
        
    def values(self):
        return [str(x) for x in self._values]

    def type(self) -> str:
        return "Bit"

class BitVector(Stimuli):
    def __init__(self, values=None) -> None:
        """
        BitVector class
        """

        if not (isinstance(values, list) or isinstance(values, np.ndarray) or isinstance(values, tuple)):
            raise TypeError(f"Invalid input type ({type(values)})")
        
        # Convert to int (for example if the data comes from the testbench)
        self._values = np.array(values).astype(int)

    def values(self):
        return [str(x) for x in self._values]
    
    def type(self) -> str:
        return "BitVector"

class Unsigned(Stimuli):
    def __init__(self, N, values=None) -> None:
        self.N = N

        if not (isinstance(values, list) or isinstance(values, np.ndarray) or isinstance(values, tuple)):
            raise TypeError(f"Invalid input type ({type(values)})")
        
        # Convert to int (for example if the data comes from the testbench)
        self._values = np.array(values).astype(int)

        if np.min(self._values) < 0 or np.max(self._values) > (2**N - 1):
            raise ValueError(f"Invalid values range ({np.min(self._values)} -> {np.max(self._values)})")
        
    def values(self):
        return [str(x) for x in self._values]

    def type(self) -> str:
        return f"Unsigned {self.N}"
    
