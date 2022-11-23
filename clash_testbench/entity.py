# Clash entity class
# Sébastien Deriaz - 22.11.2022
from pathlib import Path

from .testbench import Testbench, TestReport



class Entity:
    def __init__(self, hs_file, entity, module):
        """
        New instance of an entity under test
        """
        self._file = hs_file
        self._entity = entity
        self._module = module

    def test(self, stimulis : dict, outputs : dict) -> TestReport:
        """
        Test the entity with a list of stimulis

        Parameters
        ----------
        stimulis : dict
            Dictionnary in the form : {
                "signal_name" : Stimuli()
            }
        outputs : dict
            Dictionnary in the form : {
                "signal_name" : Stimuli()
            }
        
        Returns
        -------
        TestReport
        """

        # Generate testbench
        tb = Testbench(self._entity, self._module)
        tb.setInputs(stimulis)
        tb.setOutputs(outputs)

        # Testbench for ./folder/file.hs is ./folder/file_tb.hs
        p = Path(self._file)

        filename = f'{p.stem}_tb{p.suffix}'
        tb.create(p.parents[0] / filename)

        return tb.run()


