# Testbench generator
# Sébastien Deriaz 23.11.2022

import numpy as np
from rich.console import Console
from rich.text import Text

#from .signals import Signal, LogicLevel
from .logic import Signal, Level
from .clashi import Clashi

from itertools import groupby

class ExpectedActualPair:
    def __init__(self, expectedValues : Signal, actualValues : Signal):
        """
        
        Parameters
        ----------
        expectedValues, actualValues : list[tuple]
        
        """
        self._expected : Signal = expectedValues
        self._actual : Signal = actualValues
        self.valid = self.evalValid()

    def evalValid(self):
        HIGHS = ['1', 1, Level.HIGH]
        LOWS = ['0', 0, Level.LOW]

        self.valid_list = np.zeros(len(self._actual), dtype=bool)
        if len(self._expected) != len(self._actual):
            raise ValueError(f"Actual values aren't the same length ({len(self._actual)}) as expected ({len(self._expected)})")
        else:
            for i, (e, a) in enumerate(zip(self._expected, self._actual)):
                if e._value == Level.UNKNOWN:
                    # If there's no expected value, return true
                    self.valid_list[i] = True
                elif (e._value in HIGHS and a._value in HIGHS) or (e._value in LOWS and a._value in LOWS):
                    # If there are both the same logic level (in any way)
                    self.valid_list[i] = True
                elif e._value == a._value:
                    # If there are the same
                    self.valid_list[i] = True

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
            c.print(f"✅ {self._actual.name}", style='bold green')
        else:
            c.print(f"❌ {self._actual.name}", style='bold red')
        
        if (not self.valid) or print_values:
            arrays_str = np.array2string(np.stack([self._expected.values(), self._actual.values()]), suppress_small=True, max_line_width=1e6)
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
        self.inputSignals = {}
        self.expectedOutputSignals = {}

    def _add_lengths(self, signals : "list[Signal]"):
        self._lengths |= {s.name : len(s) for s in signals if s is not None}

    def _check_lengths(self):
        g = groupby(list(self._lengths.values()))
        length = next(g)[0]
        if length == 0:
            raise ValueError("Signals cannot be of 0 length")
        if next(g, False):
            # There one more group (multiple sizes)
            raise ValueError(f"All signals must be of the same length ({self._lengths})")

        return length

    def setInputs(self, signals : "list[Signal]"):
        """
        Add the testbench stimulis
        """
        TAB = 4*' '
        self.inputSignals = signals

        if signals == {}:
            raise ValueError("Inputs cannot be empty")

        # Check if all the signals are the same length, if they aren't print them
        self._add_lengths(signals)
        self.N = self._check_lengths()

    def setExpectedOutputs(self, signals : "list[Signal]"):
        """
        Add the testbench outputs
        """
        # CHeck if all the signals are the same length
        self._add_lengths(signals)
        self.N = self._check_lengths()

        if signals == {}:
            raise ValueError("Inputs cannot be empty")

        self.expectedOutputSignals = signals

    def setActualOutputsNames(self, signalsNames : "list[str]"):
        """
        Declare the actual outputs used
        """

        self.actualOutputNames = signalsNames

    def _fit_constant_signals(self):
        """
        Fit all constant signals to size N (create their values vector)
        """

        for l in [self.inputSignals, self.expectedOutputSignals]:
            for s in l:
                if s is not None:
                    if len(s) == 1:
                        s.fit(self.N)


    def run(self):

        self._clashi = Clashi()
        # Load the two files
        #self._clashi.load(self._file)
        # Sample the testbench
        self._fit_constant_signals()
        input_list = ' '.join([f"(fromList [{','.join([str(v) for v in s.values()])}])" for s in self.inputSignals])
        print(f"Running testbench with {len(input_list)} input(s) and {len(self.expectedOutputSignals)} output(s)")

        testbenchOutput = self._clashi.sampleN(self._file, self.N, self.entity, input_list)
        
        self._pairs = []

        if len(testbenchOutput) != len(self.actualOutputNames):
            raise ValueError(f"Number of actual outputs ({len(testbenchOutput)}) doesn't match what was declared ({len(self.actualOutputNames)})")

        self._actualOutputs = {}
        for tbOut, exp, name in zip(testbenchOutput, self.expectedOutputSignals, self.actualOutputNames):
            if name is not None:
                act = Signal(name)
                act.fromList(tbOut)
                self._actualOutputs[name] = act
                if exp is not None:
                    # Do a comparison
                    self._pairs.append(ExpectedActualPair(exp, act))

    def actualOutputs(self):
        """
        Return actual outputs
        """
        return self._actualOutputs



    def __iter__(self):
        self._signals_iter = iter(self._pairs)
        return self

    def __next__(self):
        return next(self._signals_iter)

    
        


