# Clash_testbench

A python utility to facilitate the creation and execution of Clash testbenches

## Installation

``pip install clash-testbench``

command ``clashi`` needs to be available and while be run by the package

## Usage

1) Create a ``test_xxx.py`` file for each test you which to run (see test template)
2) Run ``pytest`` at the root of your project

## Test template

```python
from clash_testbench import Entity, Chronogram
from clash_testbench.signals import *
from os.path import join, dirname

def test_conditional_register_0(doprint=False):
    entity = Entity(join(dirname(__file__), 'your_file.hs'), 'your_entity')

    inputs = {
        "input" : Unsigned(8, ([0,0,1,2,3,4])),
        "enable" : Bit([0,0,0,1,1,1])
    }

    outputs = {
        "output" : Unsigned(8, [0,0,0,0,2,3])
    }

    report = entity.test(inputs, outputs)

    cg = Chronogram(report)
    cg.saveSVG(join(dirname(__file__), 'chronogram_output.svg'))

    for s in report:
        s.print(True)
        assert s.valid, s.message()
```
