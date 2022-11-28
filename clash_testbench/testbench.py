# Testbench generator
# Sébastien Deriaz 23.11.2022

import numpy as np
from rich.console import Console
from rich.text import Text

from .signals import Signal
from .clashi import Clashi

from itertools import groupby

class ExpectedActualPair:
    def __init__(self, name, expectedValues : np.array, actualValues : np.array):
        self._name = name
        self._expected : np.array = expectedValues
        self._actual  : np.array = actualValues
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
            arrays_str = np.array2string(np.stack([self._expected, self._actual]), suppress_small=True) #prefix='  expected = \n  actual   = '
            arrays_str = arrays_str.replace('[', ' ').replace(']', ' ')
            for line, label in zip(arrays_str.split('\n'), ['expected', 'actual']):
                c.print(f"{label:<8s} = ", style='bold ', end='')
                c.print(line)

class Testbench:
    def __init__(self, file, entity) -> None:
        """
        Testbench generator
        """
        # File
        self._file = file
        self.entity = entity
        self.actualOutputSignals = None
        self._lengths = {}

    def _add_lengths(self, signals : "dict[str, Signal]"):
        for signal_name, signal in signals.items():
            self._lengths[signal_name] = len(signal)

    def _check_lengths(self):
        g = groupby(list(self._lengths.values()))
        if not (next(g, True) and not next(g, False)):
            # The list isn't equal
            raise ValueError(f"All signals must be of the same length ({self._lengths})")

    def setInputs(self, signals : "dict[str, Signal]"):
        """
        Add the testbench stimulis
        """
        TAB = 4*' '
        self.inputSignals = signals

        # Check if all the signals are the same length, if they aren't print them
        self._add_lengths(signals)
        self._check_lengths()
        
    
        self.Inputs = ' '.join([f"(fromList [{','.join(s.valuesStr())}])" for s in signals.values()])

        self.N = len(list(signals.values())[0].valuesStr())

    def setOutputs(self, signals : "dict[str, Signal]"):
        """
        Add the testbench outputs
        """
        # CHeck if all the signals are the same length
        self._add_lengths(signals)
        self._check_lengths()

        self.expectedOutputSignals = signals

    def run(self):

        self._clashi = Clashi()
        # Load the two files
        #self._clashi.load(self._file)
        # Sample the testbench
        testbenchOutput = self._clashi.sampleN(self._file, self.N, self.entity, self.Inputs)
        
        self._signals = []
        self.actualOutputSignals = {}
        for (output_signal_name, output_signal_class), testbenchSignal in zip(self.expectedOutputSignals.items(), testbenchOutput): 
            # Recreate the same class as expected (to parse the data)
            actual = output_signal_class.fromActual(testbenchSignal)
            self.actualOutputSignals[output_signal_name] = actual
            # Create an expected-actual pair to analyse and compare the signals
            self._signals.append(ExpectedActualPair(output_signal_name, output_signal_class._values, actual._values))


    def __iter__(self):
        self._signals_iter = iter(self._signals)
        return self

    def __next__(self):
        return next(self._signals_iter)

    
        


