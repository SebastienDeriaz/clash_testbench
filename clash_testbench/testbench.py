# Testbench generator
# Sébastien Deriaz 23.11.2022

import numpy as np
from rich.console import Console
from rich.text import Text

from .stimulis import Stimuli
from .clashi import Clashi

class TestReport:
    def __init__(self, outputsComparisons) -> None:
        """
        Test report instance
        """
        self._outputs = outputsComparisons
        

    def __bool__(self):
        valid = True

        for key, (A, B) in self._outputs.items():
            if not np.array_equal(A._values, B._values):
                valid = False

        return valid
    
    def report(self, colors=True) -> str:
        t = Text()

        for key, (A, B) in self._outputs.items():
            t.append(f"➩ {key}\n", style="bold cyan")
            if np.array_equal(A._values, B._values):
                t.append("    ok\n")
            else:
                t.append("    error\n")
                t.append(f"    A = {A}\n")
                t.append(f"    B = {B}\n")
        return t
    
    def print(self):
        Console().print(self.report(True))

    def __str__(self) -> str:
        return str(self.report(False))

    def __repr__(self) -> str:
        return str(self.report(False))
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

        outputs_dict = {}
        for (output_signal_name, output_signal_class), testbenchOutput in zip(self._outputSignals.items(), outputs):
            outputs_dict[output_signal_name] = (output_signal_class, type(output_signal_class)(testbenchOutput))

        return TestReport(outputs_dict)
        


