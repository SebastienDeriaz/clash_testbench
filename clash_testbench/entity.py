# Clash entity class
# Sébastien Deriaz - 22.11.2022
from .testbench import Testbench



class Entity:
    def __init__(self, hs_file, entity):
        """
        New instance of an entity under test

        hs_file : str
            Path to the .hs file
        entity : str
            Name of the entity (must start with a lowercase letter)
        """
        self._file = hs_file
        self._entity = entity

    def test(self, stimulis : dict = None, outputs : dict = None) -> Testbench:
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
        if stimulis is not None:
            tb.setInputs(stimulis)
        if outputs is not None:
            tb.setOutputs(outputs)

        tb.run()

        return tb


