from numpy import asarray
import numpy as np
from limix_plot.consensus_curve import ConsensusCurve
import limix_plot.cycler_ as cycler
from limix_util.dict import OrderedDict
from .score import WindowScore

class ROCPlot(object):
    def __init__(self, axes, window_size=None):
        ws = WindowScore(wsize=window_size) if window_size else WindowScore()
        self._window_score = ws
        self._axes = axes
        self._pv = OrderedDict()
        self._color = dict()
        self._ccurve = ConsensusCurve(axes)

    def add(self, pv, label, color=None):
        if label not in self._pv:
            self._pv[label] = []

            if color:
                self._color[label] = color
            else:
                prop = cycler.next(self._axes)
                if 'color' in prop:
                    self._color[label] = prop['color']
                else:
                    self._color[label] = None

        self._pv[label].append(pv)

    def set_chromossome(self, label, positions, causals, X=None, r2=None):
        self._window_score.set_chrom(label, positions, causals, X=X, r2=r2)

    def _plot_for_label(self, label):
        for pv in self._pv[label]:
            cm = self._window_score.confusion(pv)
            y = cm.tpr[1:]
            x = cm.fpr[1:]

            idx = np.argsort(x)
            x = x[idx]
            y = y[idx]

            self._ccurve.add(x, y, label, self._color[label])

    def plot(self, legend=True):
        axes = self._axes

        for label in self._pv.keys():
            self._plot_for_label(label)

        axes.set_xlabel('False-positive rate')
        axes.set_ylabel('True-positive rate')

        self._ccurve.plot(same_steps=True)

        eps = 1e-4
        axes.set_xlim([0, 1 + eps])
        axes.set_ylim([0, 1 + eps])

        if legend:
            self._plot_legend(self._pv.keys())

        return axes

    def _plot_legend(self, labels):
        axes = self._axes
        fakes = []
        for l in labels:
            fake, = axes.plot([1,1], color=self._color[l], lw=3)
            fakes.append(fake)

        axes.legend(fakes, labels, bbox_to_anchor=(0., 1.02, 1., .102), loc=3,
                ncol=len(labels), mode="expand", borderaxespad=0.,
                frameon=False)
        for fake in fakes:
            fake.set_visible(False)

if __name__ == '__main__':
    import numpy as np
    import limix_plot.pylab as plt
    random = np.random.RandomState(5)
    roc = ROCPlot(plt.gca())

    N = 100

    roc.set_chromossome('chrom1',
                         np.sort(random.choice(1000000, N, replace=False)),
                         [5, 70])
    roc.add(random.rand(N), 'label1')
    roc.add(random.rand(N), 'label1')
    roc.add(random.rand(N), 'label1')
    roc.add(random.rand(N), 'label1')
    roc.add(random.rand(N), 'label1')
    roc.add(random.rand(N), 'label1')

    for i in range(30):
        roc.add(random.rand(N), 'label2')

    roc.plot()
    plt.show()
