# Clashi management class
#
#

#from subprocess import Popen, PIPE, call
import pexpect

_PROMPT = "clashi>"
class Clashi:
    def __init__(self):
        """
        Clashi instance
        """
        try:
            #self._process = Popen(['clashi'], stdin=PIPE, stdout=PIPE, stderr=PIPE)
            self._process = pexpect.spawn('clashi')
            self._process.expect('clashi>')
            self._process.flush()
            

        except FileNotFoundError as e:
            print("Couldn't find clashi in the current environment")

    def load(self, file):
        """
        Load a file inside clashi
        """
        print(f"Loading file {file}...")
        #(stdout, stderr) = self._process.communicate()
        self._process.write(f':l {file}\n')
        self._process.expect(_PROMPT, timeout=20)
        #output = self._process.read_nonblocking(size=10000,timeout=1)
        output = self._process.before
        print(f"output : {output}")
        #print(f"Read output : {stdout, stderr}")
        #output = self._process.stdout.readline()
        #print(f"output : {output}")
        #if output:
        #    raise RuntimeError(self._process.stderr.read())

    def sampleN(self, entity, N):
        """
        run SampleN on a specified module
        """
        self._process.flush()
        print(f"Running sampleN")
        #(stdout, stderr) = self._process.communicate()
        self._process.write(f'sampleN {N} {entity}\n')
        self._process.expect(_PROMPT)
        print("ok")
        output = self._process.before
        print(f"Read : {output}")
        return output