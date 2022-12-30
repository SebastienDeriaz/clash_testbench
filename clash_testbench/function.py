# Function tester
# Sébastien Deriaz
# 29.12.2022
#
# Test a function

from os.path import exists

from .clashi import Clashi

class Function:
    def __init__(self, file, name) -> None:
        """
        Testbench generator

        Parameters
        ----------
        file : str
            .hs file path
        name : str
            Name of the function
        """
        # File
        if not exists(file):
            raise FileNotFoundError(f"File {file} doesn't exist")

        self._clashi = Clashi(file)
        self._file = file
        self.name = name

    def test(self, inputs):
        """
        Test the function with the given inputs
        
        Parameters
        ----------
        inputs : list or single value

        Returns
        -------
        output : str
        """
        if not isinstance(inputs, list):
            # Make a list
            inputs = [inputs]
        
        # Convert to string if it wasn't the case yet
        inputs = [x if isinstance(x, str) else str(x) for x in inputs]



        output = self._clashi.testFunction(self.name, inputs)

        return output

        



