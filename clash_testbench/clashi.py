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
    def __init__(self, file : str, verbose : bool = False):
        """
        Clashi instance

        Parameters
        ----------
        file : str
            File path
        verbose : bool
            Print debug information
        """
        self._verbose = verbose
        try:
            self._process = pexpect.spawn('clashi', encoding='utf-8')
            self._process.expect(_PROMPT)

            #self._process = Popen(['clashi'], stdin=PIPE, stdout=PIPE, stderr=PIPE)

        except FileNotFoundError as e:
            raise RuntimeError("Couldn't find clashi in the current environment")

        # Remove delays (allows for quicker function test)
        self._process.delayafterread = None
        self._process.delaybeforesend = None

        load_file_command = f':l {file}'

        self._runCommand(load_file_command)        

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
        
        self._print_verbose(f"[Clashi] Sending command '{command}'")

        self._process.send(command + '\n')
        self._process.expect(_PROMPT, timeout=timeout)

        raw_output = self._process.before

        self._print_verbose(f"[Clashi] Raw output : ")
        self._print_verbose(raw_output)
        self._print_verbose(f"[Clashi] (end of raw output) ")

        if 'error:' in raw_output or 'Exception:' in raw_output:
            raise RuntimeError(raw_output)

        # Return the 
        # Convert \x1b> to \n (because that's what clashi uses ??)
        filtered_output = raw_output.replace('\x1b>', '\n')
        # Remove all other ANSI escape codes
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        filtered_output = ansi_escape.sub('', filtered_output)
        # Split lines
        split_output = filtered_output.splitlines()
        # Only keep the middle ones (remove the function call and the last line break)
        output = ''.join(split_output[1:-1])

        return output

    def _sampleNParser(self, data, singleValue):
        """
        Parse the data by level
        [  level0  ( level 1   (level 2)  level 1 ) level0  ]
        Everything that is in level0 is removed
        Everthing that is in level 1 is kept (including parantheses)

        The output is a list of each sample, for each value
        [
            ['0','0','1','1',...], # Value 0
            ['0','0','0','0',...], # Value 1
            ['A','B','C','D',...], # Value 2
            ...
        ]

        If singleValue is True, then everything is assume to be a single tuple (if necessary)

        Parameters
        ----------
        data : str
        singleValue : bool
            Tells the parser there's only one output value (that may be a tuple)

        Returns
        -------
        values : str
        """

        level = 0
        values = [['']]
        vcounter = 0
        for d in data[1:-1]:
            if d == '(':
                level += 1
                if level == 1:
                    if not singleValue:
                        continue
            elif d == ')':
                level -= 1
                if level == 0:
                    vcounter = 0
                    if not singleValue:
                        continue
            elif d == ',' and level == 0:
                for v in values:
                    v.append('')
                continue
            
            #print(f"{level} : {d}")
            if d == ',' and level == 1 and not singleValue:
                vcounter += 1
                if len(values) < vcounter + 1:
                    values.append([''])
            else:
                values[vcounter][-1] += d

        for i, s in enumerate(values):
                print(f"  {i} : {s}")

        return values



    def sampleN(self, N, entity, inputs, singleOutput):
        """
        run SampleN on a specified module

        Parameters
        ----------
        N : int
            Number of sample to simulate
        entity : str
            Name of the entity
        inputs : str
            input signals
        singleOutput : bool
            Tells the parser there's only one input, and treat any tuple at a single value
        """
        # Run the testbench command
        command = f'sampleN @System {N} ({entity} {inputs})\n'

        raw_output = self._runCommand((command))

        output = self._sampleNParser(raw_output, singleOutput)

        # output is a list of tuples (with each value corresponding to an output)
        return output
    
    def testFunction(self, entity : str, inputs : list[str]):
        """
        Test a function with the given arguments

        Parameters
        ----------
        entity : str
            Name of the entity / function
        inputs : list[str]
            List of inputs (str)

        Returns
        -------
        output : str
        """
        # Load the file
        
        # Run the testbench command
        command = f'{entity} {" ".join(inputs)}'
        
        output = self._runCommand(command)

        return output

    def __del__(self):
        self._process.kill(1)
        self._process.terminate()

    def _print_verbose(self, x):
        if self._verbose:
            print(x)

        

