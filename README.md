# Clash_testbench

A python utility to facilitate the creation and execution of Clash testbenches

## Installation

``pip install clash-testbench``

command ``clashi`` needs to be available inside the working environment

## Usage

- From a chronogram
  1) Create a wavedrom file containing all of the inputs, expected outputs (and optionaly actual output placeholders).
  2) Create a ```test_xxx.py``` file containing the test (see test template)
  3) Run ``pytest`` at the root of your directory to run all of the tests (or refer to the pytest documentation to run a single test)
- From a Python description
  1) Create a ``test_xxx.py`` file for each test you which to run (see test template)
  2) Use the Signal class to create an input / expected output and add them to the testbench
  3) (Optional) Create an output chronogram
  3) Run ``pytest`` at the root of your project

## Test template

```python
from clash_testbench import Testbench, Chronogram
from clash_testbench.signals import *
from os.path import join, dirname

def test_conditional_register_0(doprint=False):
    # Create a testbench class, this must always be done
    testbench = Testbench(join(dirname(__file__), 'your_file.hs'), 'your_entity')
    
    # (Optional) load a chronogram
    cg = Chronogram(join(dirname(__file__), 'your_chronogram.json'))

    # Generate the inputs and expected outputs

    ################# Option A : load them from the chronogram ################
    # NOTE : the order matters ! the signals will be given to
    # the clash entity in that order
    testbench.setInputs([
        cg["input_0"],
        cg["input_1"],
        cg["input_2"]
    ])
    # A "None" indicates that the output exists but there's no signal to check
    # it against
    testbench.setExpectedOutputs([
        cg["output_0"],
        cg["output_1"],
        None
    ])
    ################# Option B : Create the signals manually ##################
    input_0 = Signal("input_0", [0,0,0,0,1,1,1,1])
    input_1 = Signal("input_1", [0,0,1,1,0,0,1,1])
    input_2 = Signal("input_2", [0,1,0,1,0,1,0,1])
    # And add them to the testbench
    testbench.setInputs([
        input_0,
        input_1,
        input_2
    ])
    output_0 = Signal("output_0")
    output_0 += [0,1] * 4
    output_1 = Signal("output_1")
    output_1 += [0] * 8
    testbench.setExpectedOutputs([
        output_0,
        output_1,
        None
    ])


    # Declare the actual outputs, this list must match EXACTLY the number of
    # outputs of the clash entity
    # Note that the name CANNOT be the same as the expected output, otherwise
    # it would get ovewritten
    testbench.setActualOutputsNames([
        "output_0 (actual)",
        "output_1 (actual)",
        "output_2 (actual)"
    ])

    # Run the testbench
    tb.run()

    # (Optional) Load the testbench to generate a chronogram
    ch.loadTestbench(tb)
    # Generate a .svg file
    cg.saveSVG(join(dirname(__file__), 'chronogram_output.svg'))
    
    # (Optional) Assert a print a report for each signal
    for s in report:
        if s.isChecked():
            s.print(True)
        else:
            s.print(True)
            assert s.isValid(), s.message()
```
