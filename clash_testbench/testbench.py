# Testbench generator
# Sébastien Deriaz 23.11.2022

import numpy as np
from rich.console import Console
from rich.text import Text

from .signals import Signal, LogicLevel
from .clashi import Clashi

from itertools import groupby

class ExpectedActualPair:
    def __init__(self, name, expectedValues : Signal, actualValues : Signal):
        """
        
        Parameters
        ----------
        expectedValues, actualValues : list[tuple]
        
        """
        self._name = name
        self._expected : Signal = expectedValues
        self._actual : Signal = actualValues
        self.valid = self.evalValid()

    def message(self):
        return f"{self._name} doesn't match expected signal"

    def evalValid(self):
        self.valid_list = np.zeros(len(self._actual), dtype=bool)
        if len(self._expected) != len(self._actual):
            raise ValueError(f"Actual values aren't the same length ({len(self._actual)}) as expected ({len(self._expected)})")
        else:
            
            for i, (e, a) in enumerate(zip(self._expected._values, self._actual._values)):
                # TODO : Expected value shouldn't be UNKNOWN
                if e[1] in [LogicLevel.DONTCARE, LogicLevel.UNKNOWN]: 
                    self.valid_list[i] = True
                elif e[1] == LogicLevel.LOGIC:
                    # Check the value of the signal
                    self.valid_list[i] = e[0] == a[0]

        return np.all(self.valid_list)

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
            c.print(f"✅ {self._name}", style='bold green')
        else:
            c.print(f"❌ {self._name}", style='bold red')
        
        if (not self.valid) or print_values:
            arrays_str = np.array2string(np.stack([self._expected.valuesList(), self._actual.valuesList()]), suppress_small=True, max_line_width=1e6)
            arrays_str = arrays_str.replace('[', ' ').replace(']', ' ')
            for line, label, style in zip(arrays_str.split('\n'), ['expected', 'actual'], ['cyan', 'dark_orange3']):
                c.print(f"{label:<8s} ={line}", style=style, highlight=False)

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
            if len(signal) == 0:
                raise RuntimeError("Length of signal cannot be 0")
            elif len(signal) > 1:
                self._lengths[signal_name] = len(signal)

    def _check_lengths(self):
        g = groupby(list(self._lengths.values()))
        length = next(g)[0]
        if next(g, False):
            # There one more group (multiple sizes)
            raise ValueError(f"All signals must be of the same length ({self._lengths})")

        return length

    def setInputs(self, signals : "dict[str, Signal]"):
        """
        Add the testbench stimulis
        """
        TAB = 4*' '
        self.inputSignals = signals

        # Check if all the signals are the same length, if they aren't print them
        self._add_lengths(signals)
        self.N = self._check_lengths()

    def setOutputs(self, signals : "dict[str, Signal]"):
        """
        Add the testbench outputs
        """
        # CHeck if all the signals are the same length
        self._add_lengths(signals)
        self.N = self._check_lengths()

        self.expectedOutputSignals = signals

    def _fit_constant_signals(self):
        """
        Fit all constant signals to size N (create their values vector)
        """

        for l in [self.inputSignals.values(), self.expectedOutputSignals.values()]:
            for s in l:
                if len(s) == 1:
                    s.fit(self.N)


    def run(self):

        self._clashi = Clashi()
        # Load the two files
        #self._clashi.load(self._file)
        # Sample the testbench
        self._fit_constant_signals()
        input_list = ' '.join([f"(fromList [{','.join(s.valuesList())}])" for s in self.inputSignals.values()])

        testbenchOutput = self._clashi.sampleN(self._file, self.N, self.entity, input_list)

        print(testbenchOutput)
        
        self._signals = []
        self.actualOutputSignals = {}
        for (output_signal_name, output_signal_class), testbenchSignal in zip(self.expectedOutputSignals.items(), testbenchOutput): 
            # Recreate the same class as expected (to parse the data)
            actual = output_signal_class.fromActual(testbenchSignal)
            self.actualOutputSignals[output_signal_name] = actual
            # Create an expected-actual pair to analyse and compare the signals
            self._signals.append(ExpectedActualPair(output_signal_name, output_signal_class, actual))


    def __iter__(self):
        self._signals_iter = iter(self._signals)
        return self

    def __next__(self):
        return next(self._signals_iter)

    
        


