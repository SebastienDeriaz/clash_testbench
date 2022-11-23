# Testbench generator
# Sébastien Deriaz 23.11.2022

from pathlib import Path

from .stimulis import Stimuli
from .clashi import Clashi

_EQ_ALIGN = 20
_file_template = lambda entity, tbmodule, tbentity, module, signals, arguments, outputs_list : f"""
module {tbmodule} where

import Clash.Prelude
import Clash.Explicit.Testbench

import {module}


{tbentity} :: Signal System Bool
{tbentity} = done
  where
    {'clk':<{_EQ_ALIGN}} = tbSystemClockGen (not <$> done)
    {'rst':<{_EQ_ALIGN}} = systemResetGen
    {'en':<{_EQ_ALIGN}} = enableGen
{signals}
    {'expectOutput':<{_EQ_ALIGN}} = outputVerifier' clk rst $(listToVecTH [{outputs_list}])
    {'done':<{_EQ_ALIGN}} = expectOutput (withClockResetEnable clk rst en $ {entity}{arguments})


"""

class TestReport:
    def __init__(self) -> None:
        """
        Test report instance
        """
        pass
        

    def __bool__(self):
        return False


class Testbench:
    def __init__(self, entity, module) -> None:
        """
        Testbench generator
        """
        # File
        self.module = module
        self.entity = entity
        self._modulehierarchy = '.'.join(module.split('.')[:-1]) if '.' in module else module
        # Testbench
        self.tbentity = f'testbench_{entity}'
        self.tbmodule = f'Testbench_{entity}'
        # Code generation
        self.arguments = ''
        self.signals = ''
        self.outputs_list = ''

    def setInputs(self, signals : "dict[str, Stimuli]"):
        """
        Add the testbench stimulis
        """
        TAB = 4*' '
        for key, value in signals.items():
            self.arguments += f' {key}'
            values_list = f"{value.values()[0]} :: {value.type()}, {', '.join(value.values()[1:])}"
            print(f"values_list : {values_list}")

            self.signals += f'{TAB}{key:<{_EQ_ALIGN}} = stimuliGenerator clk rst $(listToVecTH [{values_list}])\n'

        self.N = len(list(signals.values())[0].values())

    def setOutputs(self, signals : "dict[str, Stimuli]"):
        """
        Add the testbench outputs
        """
        

        values_list = [st.values() for st in signals.values()]

        print(f"list : {values_list}")

        values = [f"({', '.join(v)})" for v in zip(*values_list)]

        initial_values = values[0]
        rest_values = ', '.join(values[1:])
        types = ', '.join([x.type() for x in signals.values()])
        

        self.outputs_list = f"{initial_values} :: ({types}), {rest_values}"

    def create(self, file : Path):
        """
        Create the testbench file
        """
        self._testbench_file = file
        with open(file.absolute(), 'w', encoding='utf8') as f:
            f.write(_file_template(self.entity, '.'.join([self._modulehierarchy, self.tbmodule]), self.tbentity, self.module, self.signals, self.arguments, self.outputs_list))

    def run(self):

        self._clashi = Clashi()
        # Load the two files
        self._clashi.load(self._testbench_file)
        # Sample the testbench
        testbenchOutput = self._clashi.sampleN(self.tbentity, self.N)

        self._parse(testbenchOutput)


    def _parse(self, consoleOutput):
        print(f"Console outpout : {consoleOutput}")

        return TestReport()


