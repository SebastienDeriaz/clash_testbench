from sys import path

path.append('../clash')


from .._chronogram import Chronogram
from ..testbench import Testbench
from ..signals import *


def main():

    inputs = {
        "phrModeSwitch" : Bit([0,0,0,0,0,0]),
        "phrFCS" : Bit([0,0,0,0,0,0]),
        "phrDataWhitening" : Bit([0,0,0,0,0,0]),
        "phrFrameLength" : Unsigned(11, [1001,1000,1000,1000,1000,1000]),
        "start" : Bit([0,1,0,0,0,0]),
        "busy_i" : Bit([0,0,0,1,1,1])
    }

    outputs = {
        "a" : Bit([0,0,0,0,1,1]),
        "b" : Bit([1,0,0,0,0,0]),
        "c" : Bit([0,0,0,0,1,0])
    }

    tb = Testbench("", "")
    tb.setInputs(inputs)
    tb.setOutputs(outputs)



    cg = Chronogram(tb)

    cg.saveSVG('test.svg')

if __name__ == '__main__':
    main()