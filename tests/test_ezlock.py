import subprocess
from pathlib import Path
import shutil
import os

import pytest

from ezlock import Lock, LockError

LDIR = Path('tests') / 'locks'


@pytest.fixture
def clear_locks():
    if LDIR.exists():
        shutil.rmtree(LDIR.as_posix())
    LDIR.mkdir()


def run_dolock(path, do):
    if isinstance(path, Path):
        path = path.as_posix()
    return subprocess.run(['python', 
                        'tests/dolock.py', 
                        path, 
                        do])
                        

def popen_dolock(path, do):
    if isinstance(path, Path):
            path = path.as_posix()
    return subprocess.Popen(['python', 
                           'tests/dolock.py', 
                           path, 
                           do])


def test_attributes(clear_locks):
    lock = Lock(LDIR / 'attributes')

    with pytest.raises(LockError):
        assert not lock.mine

    assert lock.name == 'pid:{}, obj:{}'.format(os.getpid(), id(lock))

    assert bool(lock) == False

    lock.acquire()

    assert bool(lock) == True


def test_with(clear_locks):
    lock = Lock(LDIR / 'with')
    with lock:
        assert lock.locked
        assert lock.mine
    assert not lock.locked


def test_same_process(clear_locks):
    lock1 = Lock(LDIR / 'same_process')
    lock2 = Lock(LDIR / 'same_process')

    lock1.acquire()
    assert lock1.locked
    assert lock2.locked

    assert lock1.mine
    assert not lock2.mine

    lock1.release()

    assert not lock1.locked
    assert not lock2.locked

    lock1.acquire()
    lock2.release(force=True)

    assert not lock1.locked
    assert not lock2.locked

    lock1.acquire()

    with pytest.raises(LockError):
        lock2.acquire()

    lock1.release()

    with pytest.raises(LockError):
        lock2.release(rerelease=False)

    lock1.acquire()

    with pytest.raises(LockError):
        lock2.release()


def test_other_process(clear_locks):
    lock = Lock(LDIR / "other_process")
    process = run_dolock(lock.path, 'lock')

    assert lock.locked

    process = run_dolock(lock.path, 'unlock')

    assert not lock.locked

    lock.acquire()

    assert lock.locked

    process = run_dolock(lock.path, 'unlock')

    assert not lock.locked


def test_release_on_exit(clear_locks):
    lock = Lock(LDIR / 'release_on_exit')

    lock.release_on_exit = True
    assert lock.release_on_exit
    lock.release_on_exit = False
    assert not lock.release_on_exit

    lock.acquire()

    assert lock.locked

    process = run_dolock(lock.path, 'onexit')

    assert not lock.locked

    lock.acquire()

    assert lock.locked

    process = run_dolock(lock.path, 'unonexit')

    assert lock.locked


def test_wait(clear_locks):
    lock = Lock(LDIR / 'wait')
    lock.acquire()
    
    assert lock.locked
    
    process = popen_dolock(lock.path, 'wait')
    
    assert lock.locked
    
    lock.wait()
    
    assert not lock.locked

