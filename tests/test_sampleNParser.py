# Test the SampleN parser
#

from clash_testbench.clashi import Clashi
import pytest

SINGLE_VALUE = [False, False, True]

DATA = [
    "[(0,0,(0.0,0.0),0,0,Idle),(1,0,(0.0,0.0),0,0,WaitPilot),(0,1,(0.0,0.0),0,0,WaitData),(0,1,(0.0,0.0),0,0,WaitData)]",
    "[(0,0,0.0,0,0,Idle)]",
    "[(0,0,0.0,0,0,Idle)]",
    ]

EXPECTED_DATA = [
    [
        ['0', '1', '0', '0'],
        ['0', '0', '1', '1'],
        ['(0.0,0.0)', '(0.0,0.0)','(0.0,0.0)','(0.0,0.0)'],
        ['0', '0', '0', '0'],
        ['0', '0', '0', '0'],
        ['Idle', 'WaitPilot', 'WaitData', 'WaitData']
     ],
    [['0'],['0'],['0.0'],['0'],['0'],["Idle"]],
    [['(0,0,0.0,0,0,Idle)']]
]

@pytest.mark.parametrize("singleValue, data, expectedData", zip(SINGLE_VALUE, DATA, EXPECTED_DATA))
def test_sampleNParser(singleValue, data, expectedData):
    clashi = Clashi('')
    output = clashi._sampleNParser(data, singleValue)

    assert expectedData == output
