# Clashi management class
#
#

#from subprocess import Popen, PIPE, call
#import pexpect
from subprocess import PIPE, Popen
import re

_PROMPT = b"clashi>"
class Clashi:
    def __init__(self):
        """
        Clashi instance
        """
        try:
            self._process = Popen(['clashi'], stdin=PIPE, stdout=PIPE, stderr=PIPE)

        except FileNotFoundError as e:
            print("Couldn't find clashi in the current environment")

    def sampleN(self, file, N, entity, inputs):
        """
        run SampleN on a specified module
        """
        # Load the file
        load_file_command = f':l {file}\n'
        # Run the testbench command
        command = f'sampleN @System {N} ({entity} {inputs})\n'

        # Everything is done at once because the communication method can only be called once
        stdout, stderr = self._process.communicate((load_file_command + command).encode('utf-8'))

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
            output = list(zip(*list_of_tuples))
        else:
            # It's only comma-separated values
            raw = ''.join([c for c in testbench_output if str.isdigit(c) or c == ','])
            # Making a list of list, because there's only one signal
            output = [raw.split(',')]

        # output is a list of tuples (with each value corresponding to an output)
        return output