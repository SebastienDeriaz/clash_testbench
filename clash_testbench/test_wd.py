from .wd import compress, uncompress

def test_compress():
    INPUT_OUTPUT = [
        (['0','1','0','0','x','x','0'], '010.x.0'),
        ((['3','3','3','x','3', '3'], ['A', 'A', 'A', None, 'B', 'B']), ('3..x3.', ['A', 'B'])),        
    ]

    for inp, exp in INPUT_OUTPUT:
        if isinstance(inp, tuple):
            act = compress(*inp)
        else:
            act = compress(inp)
        assert act == exp, f"Fail : {inp} -> {act} instead of {exp}"


def test_uncompress():
    INPUT_OUTPUT = [
        ('010.x.0', ['0','1','0','0','x','x','0']),
        (('3..x3.', ['A', 'B']), (['3','3','3','x','3', '3'], ['A', 'A', 'A', None, 'B', 'B'])),        
    ]

    for inp, exp in INPUT_OUTPUT:
        if isinstance(inp, tuple):
            act = uncompress(*inp)
        else:
            act = uncompress(inp)
        assert act == exp, f"Fail : {inp} -> {act} instead of {exp}"