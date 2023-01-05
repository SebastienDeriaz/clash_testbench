# Testbench generator
# Sébastien Deriaz 23.11.2022

import numpy as np
from rich.console import Console
from rich.text import Text

from typing import Iterator

#from .signals import Signal, LogicLevel
from .logic import Signal, Level
from .clashi import Clashi

from itertools import groupby

from os.path import exists

class SignalChecker:
    def __init__(self, expectedValues : Signal, actualValues : Signal):
        """
        
        Parameters
        ----------
        expectedValues, actualValues : list[tuple]
        
        """
        self._expected : Signal = expectedValues
        self._actual : Signal = actualValues
        self._isChecked = self._expected is not None
        if self._isChecked:
            self._isValid = self._evalValid()
        else:
            self._isValid = False

    def isValid(self):
        return self._isValid

    def isChecked(self):
        return self._isChecked

    def message(self):
        if self._expected:
            return f"Signal '{self._actual.name}' doesn't match '{self._expected.name}'"
        else:
            return f"Signal '{self._actual.name}' isn't checked"

    def _evalValid(self):
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
        Prints information about the signal
        - If it is checked (with an expected signal), a pass-fail report will be printed
        - otherwise, a simple signal list will be printed
        """

        if self._isChecked:
            self.printPassFail(print_values)
        else:
            self.printSignal(print_values)

    def printPassFail(self, print_values):
        """
        Print pass/fail of actual signal compared to expected signal.

        Parameters
        ----------
        force_print : bool
            Force print signal values even when the test passes
        """
        c = Console()
        if self._isValid:
            c.print(f"✅ {self._actual.name}", style='bold green')
        else:
            c.print(f"❌ {self._actual.name}", style='bold red')
        
        if (not self._isValid) or print_values:
            arrays_str = np.array2string(np.stack([self._expected.values(), self._actual.values()]), suppress_small=True, max_line_width=1e6)
            arrays_str = arrays_str.replace('[', ' ').replace(']', ' ')
            for line, label, style in zip(arrays_str.split('\n'), ['expected', 'actual'], ['cyan', 'dark_orange3']):
                c.print(f"{label:<8s} ={line}", style=style, highlight=False)

    def printSignal(self, print_values):
        """
        Print the actual signal wave
        """
        c = Console()
        c.print(f"❔  {self._actual.name}", style='bold violet')
        if print_values:
            arrays_str = np.array2string(np.array(self._actual.values()), suppress_small=True, max_line_width=1e6)
            arrays_str = arrays_str.replace('[', ' ').replace(']', ' ')
            c.print(f"{'actual':<8s} ={arrays_str}", style='violet', highlight=False)


class Testbench:
    __test__ = False # This is to prevent pytest from considering this class as  a test class
    def __init__(self, file : str, entity : str, verbose : bool = False) -> None:
        """
        Testbench generator

        Parameters
        ----------
        file : str
            File path
        entity : str
            Name of the entity
        verbose : bool
            Print debug information
        """
        # File
        if not exists(file):
            raise FileNotFoundError(f"File {file} doesn't exist")
        self._file = file
        self.entity = entity
        self.actualOutputSignals = None
        self._lengths = {}
        self.inputSignals = {}
        self._expectedOutputSignals = {}
        self.actualOutputNames = []
        self._verbose = verbose

    def _add_lengths(self, signals : "list[Signal]"):
        self._lengths |= {s.name : len(s) for s in signals if (s is not None) and (len(s) > 1)}

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

        if not isinstance(signals, list):
            raise ValueError("Input must be a list of Signal")
        if len(signals) == 0:
            raise ValueError("Input cannot be empty")
        if not isinstance(signals[0], Signal):
            raise ValueError("Input must be a list of Signal")

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

        self._expectedOutputSignals = signals

    def setActualOutputsNames(self, signalsNames : "list[str]"):
        """
        Declare the actual outputs used
        """

        self.actualOutputNames = signalsNames

    def _fit_constant_signals(self):
        """
        Fit all constant signals to size N (create their values vector)
        """

        for l in [self.inputSignals, self._expectedOutputSignals]:
            for s in l:
                if s is not None:
                    if len(s) == 1:
                        s.fit(self.N)


    def run(self):

        self._clashi = Clashi(self._file, self._verbose)
        # Sample the testbench
        self._fit_constant_signals()
        input_list = ' '.join([f"(fromList [{','.join([str(v) for v in s.values()])}])" for s in self.inputSignals])

        testbenchOutput = self._clashi.sampleN(self.N, self.entity, input_list, len(self.actualOutputNames) == 1)

        self._pairs = []

        if len(testbenchOutput) != len(self.actualOutputNames):
            raise ValueError(f"Number of actual outputs ({len(testbenchOutput)}) doesn't match what was declared ({len(self.actualOutputNames)})")

        self._actualOutputs = {}
        for i, (tbOut, name) in enumerate(zip(testbenchOutput, self.actualOutputNames)):
            if name is not None:
                act = Signal(name)
                act.fromList(tbOut)
                self._actualOutputs[name] = act
                if i < len(self._expectedOutputSignals):
                    # Do a comparison
                    exp = self._expectedOutputSignals[i]
                else:
                    # Simple add the signal, the SignalChecker will not make the comparison, only print it
                    exp = None
                self._pairs.append(SignalChecker(exp, act))

    def actualOutputs(self):
        """
        Return actual outputs
        """
        return self._actualOutputs

    def getAllSignals(self):
        """
        Return all Testbench signals
        """

        return {signal.name : signal for signal in self.inputSignals + self._expectedOutputSignals if signal is not None} | self._actualOutputs



    def __iter__(self) -> Iterator[Signal]:
        self._signals_iter = iter(self._pairs)
        return self

    def __next__(self) -> Signal:
        return next(self._signals_iter)

    
        


