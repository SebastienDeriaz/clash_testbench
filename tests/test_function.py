
from clash_testbench import Function
from os.path import dirname, join


def test_function():

    A = Function(join(dirname(__file__), 'function.hs'), 'functionA')
    
    assert int(A.test(1)) == 2



