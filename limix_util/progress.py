import progressbar as pbm

class ProgressBar(object):
    def __init__(self, n):
        self._pb = pbm.ProgressBar(widgets=[pbm.Percentage(), pbm.Bar()],
                                   maxval=n).start()

    def update(self, i):
        self._pb.update(i)

    def finish(self):
        self._pb.finish()
