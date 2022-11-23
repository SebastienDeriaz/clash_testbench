# Clash stimulis
# Sébastien Deriaz - 22.11.2022

class Stimuli:
    def __init__(self) -> None:
        pass

    def values(self) -> list:
        return ["0", "0", "0", "0"]
            
    def type(self) -> str:
        pass



class Bit(Stimuli):
    def __init__(self, values=None) -> None:
        """
        Bit Class
        """
        pass

    def type(self) -> str:
        return "Bit"

class BitVector(Stimuli):
    def __init__(self, values) -> None:
        """
        BitVector class
        """
    
    def type(self) -> str:
        return "BitVector"

class Unsigned(Stimuli):
    def __init__(self, N) -> None:
        self.N = N

    def type(self) -> str:
        return f"Unsigned {self.N}"
