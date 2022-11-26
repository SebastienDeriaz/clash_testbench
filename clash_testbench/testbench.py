# Testbench generator
# Sébastien Deriaz 23.11.2022

import numpy as np
from rich.console import Console
from rich.text import Text

from .stimulis import Stimuli
from .clashi import Clashi

class ExpectedActualPair:
    def __init__(self, name, expectedValues, actualValues):
        self._name = name
        self._expected = expectedValues
        self._actual = actualValues
        self.valid = np.array_equal(self._expected, self._actual)

    def message(self):
        return f"{self._name} doesn't match expected signal"

    def print(self, print_values = False):
        """
        Print pass/fail of actual signal compared to expected signal.

        Parameters
        ----------
        force_print : bool
            Force print signal values even when the test passes
        """
        c = Console()
        # TODO : Change those icons
        if self.valid:
            c.print(f"✅ {self._name}")
        else:
            c.print(f"❌ {self._name}")
        
        if (not self.valid) or print_values:
            c.print(f"  expected = {self._expected}")
            c.print(f"  actual   = {self._actual}")

class Testbench:
    def __init__(self, file, entity) -> None:
        """
        Testbench generator
        """
        # File
        self._file = file
        self.entity = entity

    def setInputs(self, signals : "dict[str, Stimuli]"):
        """
        Add the testbench stimulis
        """
        TAB = 4*' '

        self.Inputs = ' '.join([f"(fromList [{','.join(s.values())}])" for s in signals.values()])

        self.N = len(list(signals.values())[0].values())

    def setOutputs(self, signals : "dict[str, Stimuli]"):
        """
        Add the testbench outputs
        """

        self._outputSignals = signals

    def run(self):

        self._clashi = Clashi()
        # Load the two files
        #self._clashi.load(self._file)
        # Sample the testbench
        testbenchOutput = self._clashi.sampleN(self._file, self.N, self.entity, self.Inputs)
        # Convert the output tuples into each output signal
        outputs = list(zip(*testbenchOutput))
        
        self._signals = []
        for (output_signal_name, output_signal_class), testbenchOutput in zip(self._outputSignals.items(), outputs): 
            # Recreate the same class as expected (to parse the data)
            actual = type(output_signal_class)(testbenchOutput)
            # Create an expected-actual pair to analyse and compare the signals
            self._signals.append(ExpectedActualPair(output_signal_name, output_signal_class._values, actual._values))


    def __iter__(self):
        self._signals_iter = iter(self._signals)
        return self

    def __next__(self):
        return next(self._signals_iter)

    
        


