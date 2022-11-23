# Clashi management class
#
#

from subprocess import Popen, PIPE

class Clashi:
    def __init__(self):
        """
        Clashi instance
        """
        try:
            self._process = Popen(['clashi'], stdin=PIPE, stdout=PIPE)
        except FileNotFoundError as e:
            print("Couldn't find clashi in the current environment")

    def load(self, file):
        """
        Load a file inside clashi
        """
        print(f"Loading file {file}...")
        self._process.stdin.write(f':l {file}\n')
        self._process.stdin.flush()
        print(self._process.stdout.readline())