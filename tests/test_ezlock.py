from ezlock import __version__
from ezlock import Lock


def test_version():
    assert __version__ == '0.1.3'

def test_with():
    l = Lock()
    with l:
        assert l.locked == True
        assert l.mine == True
    assert l.locked == False
    