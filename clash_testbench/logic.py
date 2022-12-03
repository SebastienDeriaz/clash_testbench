from enum import Enum
from random import randint

class Level(Enum):
    LOW = 0
    HIGH = 1
    UNKNOWN = 2

class Sample:
    def __init__(self, value, colorIndex : int = 0) -> None:
        """
        New signal sample

        Parameters
        ----------
        value : str, int or Level
        colorIndex : int
            Index of the signal color
        """
        self._value = value
        self.colorIndex = colorIndex

    def __str__(self) -> str:
        return self._value.__str__()
    
    def value(self):
        if self._value == Level.LOW:
            return 0
        elif self._value == Level.HIGH:
            return 1
        elif self._value == Level.UNKNOWN:
            return randint(0,1)
        else:
            return self._value
    
    def __repr__(self) -> str:
        return self._value.__repr__()

class Signal:
    def __init__(self, name) -> None:
        self.name = name

        self.samples : "list[Sample]" = []

    def __iadd__(self, x):
        if isinstance(x, Sample):
            self.samples.append(x)
        else:
            raise TypeError(f"Cannot add type {type(x)} to Signal")
        return self

    def __iter__(self):
        self._samples_iter = iter(self.samples)
        return self

    def __next__(self):
        return next(self._samples_iter)

    def __getitem__(self, key):
        return self.samples[key]
    
    def __setitem__(self, key, value):
        if isinstance(key, int):
            self.samples[key] = Sample(value)
        else:
            # TODO add this
            pass

    def __len__(self):
        return len(self.samples)

    def copy(self):
        newSignal = Signal(self.name)
        newSignal.samples = self.samples.copy()
        return newSignal

    def fromList(self, lst : list):
        """
        Create a signal from a list of values
        """
        self.samples = []
        for l in lst:
            self.samples.append(Sample(l))
    
    def fit(self, N : int):
        """
        Fit the signal to an integer
        """
        self.samples = N * [self.samples[0]]

    def values(self):
        """
        Return a list of all samples
        """
        print(f"samples = {self.samples} ({type(self.samples[0])})")
        return [s.value() for s in self.samples]


    