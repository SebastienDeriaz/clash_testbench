# Clashi management class
#
#

#from subprocess import Popen, PIPE, call
#import pexpect
from subprocess import PIPE, Popen, TimeoutExpired
import re
import numpy as np

_PROMPT = b"clashi>"
class Clashi:
    def __init__(self):
        """
        Clashi instance
        """
        try:
            self._process = Popen(['clashi'], stdin=PIPE, stdout=PIPE, stderr=PIPE)

        except FileNotFoundError as e:
            raise RuntimeError("Couldn't find clashi in the current environment")

    def _runCommand(self, command, timeout):
        """
        Run a clashi command

        Parameters
        ----------
        command : bytes / bytearray
        timeout : int or float

        Returns
        -------
        stdout : bytes
        stderr : bytes
        """
        # Everything is done at once because the communication method can only be called once
        try:
            try:
                stdout, stderr = self._process.communicate(command, timeout=20.0)
            except TimeoutExpired:
                self._process.kill()
                raise TimeoutError("Clashi command timeout")
        except KeyboardInterrupt as e:
            self._process.kill()
            raise e


    def sampleN(self, file, N, entity, inputs):
        """
        run SampleN on a specified module
        """
        # Load the file
        load_file_command = f':l {file}\n'
        # Run the testbench command
        command = f'sampleN @System {N} ({entity} {inputs})\n'

        #print(load_file_command)
        #print(command)

        stdout, stderr = self._runCommand((load_file_command + command).encode('utf-8'))

        if stderr:
            # An error occured
            raise RuntimeError(stderr.decode('utf-8'))
        # The testbench output is located one line before the "leaving ghci" message
        testbench_output = (stdout.split(_PROMPT)[-2]).decode('utf-8')
        # Capture the groups
        if '(' in testbench_output:
            # It's a list of tuples
            groups = re.findall(r'(\([\w,]+\))', testbench_output)
            # Remove the ( ) and split by comma
            list_of_tuples = [x[1:-1].split(',') for x in groups]

            # Transpose [(a[0], b[0], ...), (a[1], b[1], ...)] -> [(a[0], a[1],...), ([b[0], b[1], ...)]
            # Convert the output tuples into each output signal
            output = np.transpose(list_of_tuples).tolist()
            
        else:
            # It's only comma-separated values
            raw = ''.join([c for c in testbench_output if str.isdigit(c) or c == ','])
            # Making a list of list, because there's only one signal
            output = [raw.split(',')]

        # output is a list of tuples (with each value corresponding to an output)
        return output
    
    def testFunction(self, file : str, entity : str, inputs : list[str]):
        """
        Test a function with the given arguments

        Parameters
        ----------
        file : str
            Path to the .hs file
        entity : str
            Name of the entity / function
        inputs : list[str]
            List of inputs (str)

        Returns
        -------
        output : str
        """
        # Load the file
        load_file_command = f':l {file}\n'
        # Run the testbench command
        command = f'{entity} {" ".join(inputs)}\n'

        # Everything is done at once because the communication method can only be called once
        stdout, stderr = self._runCommand(load_file_command + command)

        if stderr:
            # An error occured
            raise RuntimeError(stderr.decode('utf-8'))

        print(f"testFunction output : {stdout}")

        return stdout

        

