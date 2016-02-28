import progressbar as pbm
from time import time
import sys

class ProgressBar(object):
    def __init__(self, n):
        self._pb = pbm.ProgressBar(widgets=[pbm.Percentage(), pbm.Bar()],
                                   maxval=n).start()

    def update(self, i):
        self._pb.update(i)

    def finish(self):
        self._pb.finish()

class BeginEnd(object):
    def __init__(self, task, silent=False):
        self._task = str(task)
        self._start = None
        self._silent = silent

    def __enter__(self):
        self._start = time()
        if not self._silent:
            print('-- %s start --' % self._task)
            sys.stdout.flush()

    def __exit__(self, *args):
        elapsed = time() - self._start
        if not self._silent:
            print('-- %s end (%.2f s) --' % (self._task, elapsed))
            sys.stdout.flush()
