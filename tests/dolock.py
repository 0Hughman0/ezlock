from pathlib import Path
import time

import sys
sys.path.append(Path('.').absolute().as_posix())

from ezlock import Lock
from test_ezlock import LDIR

_, name, do = sys.argv

l = Lock(name)

if do == 'lock':
    l.acquire()
elif do == 'unlock':
    l.release(force=True)
elif do == 'onexit':
    l.acquire(force=True)
    l.release_on_exit = True
elif do == 'unonexit':
    l.acquire(force=True)
    l.release_on_exit = True
    l.release_on_exit = False
elif do == 'wait':
    l.release(force=True)
 