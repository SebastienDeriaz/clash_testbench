# Clashi management class
#
#

#from subprocess import Popen, PIPE, call
#import pexpect
from subprocess import PIPE, Popen, TimeoutExpired
import re
import numpy as np

import pexpect

_PROMPT = "clashi>"
class Clashi:
    def __init__(self):
        """
        Clashi instance
        """
        try:
            self._process = pexpect.spawn('clashi', encoding='ASCII')
            self._process.expect(_PROMPT)
            #self._process = Popen(['clashi'], stdin=PIPE, stdout=PIPE, stderr=PIPE)

        except FileNotFoundError as e:
            raise RuntimeError("Couldn't find clashi in the current environment")
        

    def _runCommand(self, command, timeout = -1):
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
        self._process.send(command + '\n')
        self._process.expect(_PROMPT, timeout=timeout)
        # Return the 
        raw_output = self._process.before
        # Convert \x1b> to \n (because that's what clashi uses ??)
        filtered_output = raw_output.replace('\x1b>', '\n')
        # Remove all other ANSI escape codes
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        filtered_output = ansi_escape.sub('', filtered_output)
        # Split lines
        split_output = filtered_output.splitlines()
        # Only keep the middle ones (remove the function call and the last line break)
        output = '\n'.join(split_output[1:-1])

        return output

        # try:
        #     try:
        #         stdout, stderr = self._process.communicate(command, timeout=20.0)
        #     except TimeoutExpired:
        #         self._process.kill()
        #         raise TimeoutError("Clashi command timeout")
        # except KeyboardInterrupt as e:
        #     self._process.kill()
        #     raise e


    def sampleN(self, file, N, entity, inputs):
        """
        run SampleN on a specified module
        """
        # Load the file
        load_file_command = f':l {file}\n'
        # Run the testbench command
        command = f'sampleN @System {N} ({entity} {inputs})\n'
        
        # Load the file
        self._runCommand(load_file_command)
        
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
        load_file_command = f':l {file}'
        # Run the testbench command
        command = f'{entity} {" ".join(inputs)}'
        
        print(self._runCommand(load_file_command))
        
        output = self._runCommand(command)

        return output

    def __del__(self):
        self._process.kill(1)
        self._process.terminate()

        

