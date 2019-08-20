from pathlib import Path
import os
import time
import atexit

class LockError(Exception):
    pass


class Lock:

    def __init__(self, path='.lock', release_on_exit=False):
        """
        Lock object that keeps track of a file found at `self.path`. If there is a file found at `self.path`, the lock is considered... locked!
        
        Parameters
        ==========
        path : str, Path
            path to write the lock file to (will be converted to `pathlib.Path`). Defaults to '.lock'.
        """
        self.path = Path(path)
        self._do_release_on_exit = None
        self.release_on_exit = release_on_exit

    @property
    def name(self):
        """
        name written to lock to prove ownership
        """
        return 'pid:{}, obj:{}'.format(os.getpid(), id(self))

    @property
    def locked(self):
        """
        Does the lock-file at `self.path` exist?
        """
        return self.path.exists()

    @property
    def mine(self):
        """
        Was the lock created by this object?
        """
        try:
            return self.path.read_text() == self.name
        except FileNotFoundError:
            raise LockError("Attempted to check ownership on lock that doesn't exist")

    def acquire(self, force=False):
        """
        Create the lock-file, and stamp on it that it was made by me!
        
        Parameters
        ==========
        force : bool
            If the lock already exists, force switching ownership to me so `self.mine==True`. Defaults to False
        """
        if self.locked and not force:
            raise LockError("Attempted to acquire on already locked lock!")
        self.path.write_text(self.name)

    def release(self, force=False, rerelease=True):
        """
        Release the lock.
        
        Will get upset if the lock isn't `self.mine` but can override by setting `force=True`.
        
        Parameters
        ==========
        force : bool
            force releasing the lock, even if not `self.mine`. (default `False`)
        rerelease : 
            when `True` will not complain if attempting to release and already released lock. (default `True`)

        Returns
        =======
        name : str
            the name of the lock that was just released (None if no lock was released)
        """
        if not self.locked:
            if not rerelease:
                raise LockError("Attempted to release an already released lock")
            return None
        if not self.mine and not force:
            raise LockError("Attempted to release a lock that wasn't mine, can set `force=True`")
        name = self.path.read_text()
        os.remove(self.path.as_posix())
        return name
        
    @property
    def release_on_exit(self):
        return self._do_release_on_exit

    @release_on_exit.setter
    def release_on_exit(self, do):
        if do:
            atexit.register(self.release)
        else:
            atexit.unregister(self.release)
        self._do_release_on_exit = do

    def wait(self, dt=0.01):
        """
        Wait until lock is released.
        
        Parameters
        ==========
        dt : float
            how long to wait between checking for `self.locked`
        """
        while self.locked:
              time.sleep(dt)

    def __enter__(self):
        self.acquire()

    def __exit__(self, exception_type, exception_value, traceback):
        self.release()

    def __bool__(self):
        return self.locked
