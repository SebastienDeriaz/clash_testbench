from .convertvalues import convertValues
from .logic import LogicLevel as LL

INPUT_OUTPUT = [
        ('01x', [(0, LL.LOGIC), (1, LL.LOGIC) , (None, LL.UNKNOWN)]),
        (1, [(1, LL.LOGIC)]),
        ([1, 1, 0, 0], [(1, LL.LOGIC), (1, LL.LOGIC) , (0, LL.LOGIC), (0, LL.LOGIC)]),
        ([1,2,3], [(1, LL.LOGIC), (2, LL.LOGIC) , (3, LL.LOGIC)]),
        (['Idle', 'StateX'], [('Idle', LL.LOGIC), ('StateX', LL.LOGIC)]),
        (['1', '1', '0', '0'], [(1, LL.LOGIC), (1, LL.LOGIC) , (0, LL.LOGIC), (0, LL.LOGIC)]),
        (('3x', ['Idle']), [('Idle', LL.LOGIC), (None, LL.UNKNOWN)]),
        (('33x', ['Idle', 'StateX']), [('Idle', LL.LOGIC), ('StateX', LL.LOGIC), (None, LL.UNKNOWN)])
]


def test_convertvalues():
    for inp, exp in INPUT_OUTPUT:
        if isinstance(inp, tuple):
            act = convertValues(*inp)
        else:
            act = convertValues(inp)
        assert act == exp, f"Fail : {inp} -> {act} instead of {exp}"