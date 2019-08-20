# ezlock

Super simple file-based locking:

    # first.py
    from ezlock import Lock
    import time

    with Lock():
        print("I got the lock and I'm keeping it for 20s")
        time.sleep(20)
        
    
and

    # second.py
    ...
    with Lock():
        print("Trying to get a lock too")
        

running

    >>> python3 first.py &
    I got the lock and I'm keeping it for 20s
    >>> echo "before 20s"
    before 20s
    >>> python3 second.py
    locking.LockError: Attempted to acquire on already locked lock!
    
Lock files have an owner. A lock can check if it owns a file with `lock.mine`. `Lock`s will only release a lock that's not theirs if it's forced i.e. `lock.release(force=True)`.

You can wait for a lock to be released with `Lock.wait()`
