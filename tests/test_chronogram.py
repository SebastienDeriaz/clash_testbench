from sys import path
path.append('.')

from clash_testbench import Chronogram
from clash_testbench.chronogram import _compress, _uncompress, _signalToEntry

from os.path import dirname, join

def test_compress():
    INPUT_OUTPUT = [
        (['0','1','0','0','x','x','0'], '010.x.0'),
        ((['3','3','3','x','3', '3'], ['A', 'A', 'A', None, 'B', 'B']), ('3..x3.', ['A', 'B'])),
        ((['0', '3', '3', '3', '3'], [None, 'A', 'A', 'B', 'C']), ('03.33', ['A', 'B', 'C']))
    ]

    for inp, exp in INPUT_OUTPUT:
        if isinstance(inp, tuple):
            act = _compress(*inp)
        else:
            act = _compress(inp)
        assert act == exp, f"Fail : {inp} -> {act} instead of {exp}"


def test_uncompress():
    INPUT_OUTPUT = [
        ('010.x.0', ['0','1','0','0','x','x','0']),
        (('3..x3.', ['A', 'B']), (['3','3','3','x','3', '3'], ['A', 'A', 'A', None, 'B', 'B'])),
        (('03.33', ['A', 'B', 'C']), (['0', '3', '3', '3', '3'], [None, 'A', 'A', 'B', 'C'])),
        (('1.33', ['A', 'B']), (['1','1','3','3'], [None, None, 'A', 'B']))

    ]

    for inp, exp in INPUT_OUTPUT:
        if isinstance(inp, tuple):
            act = _uncompress(*inp)
        else:
            act = _uncompress(inp)
        assert act == exp, f"Fail : {inp} -> {act} instead of {exp}"





def test_Chronogram():
    
    cg = Chronogram(join(dirname(__file__), "test_chronogram.json"))
    cg.saveSvg(join(dirname(__file__), "test_chronogram.svg"))

    my_signals = cg.getSignals()

    cg.setTemplates(
        {
            "state (actual)" : "state"
        }
    )
    my_signals["state (actual)"] = my_signals["state"].copy()
    

    my_signals["state (actual)"][0] = 1
    my_signals["state (actual)"][1] = 1

    cg.setSignals(my_signals)


    cg.saveJson(join(dirname(__file__), "test_chronogram2.json"))
    cg.saveSvg(join(dirname(__file__), "test_chronogram2.svg"))

if __name__ == '__main__':
    test_Chronogram()