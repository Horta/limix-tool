import time

class Timer(object):
    def __init__(self):
        self._tstart = None
        self.elapsed = None

    def __enter__(self):
        self._tstart = time.time()
        return self

    def __exit__(self, type_, value_, traceback_):
        self.elapsed = time.time() - self._tstart
