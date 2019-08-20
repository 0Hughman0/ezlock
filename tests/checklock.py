from pathlib import Path
import sys
sys.path.append(Path('.').absolute().as_posix())

from ezlock import Lock
from test_ezlock import LDIR

_, name = sys.argv

l = Lock(LDIR / check)

sys.exit(l.locked)


