# Clash entity class
# Sébastien Deriaz - 22.11.2022
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
        tb = Testbench(self._file, self._entity)
        tb.setInputs(stimulis)
        tb.setOutputs(outputs)

        report = tb.run()

        return report


