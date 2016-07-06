from numpy import asarray
import numpy as np
from limix_plot.consensus_curve import ConsensusCurve
import limix_plot.cycler_ as cycler
from limix_util.dict import OrderedDict
from .score import ClassificationScore

class PRCurvePlot(object):
    def __init__(self, axes, window_size=None):
        self._axes = axes
        self._probabilities = OrderedDict()
        self._reference = dict()
        self._color = dict()
        self._ccurve = ConsensusCurve(axes)

    def add(self, probabilities, label, ref_name, color=None):
        if label not in self._probabilities:
            self._probabilities[label] = dict()

            if color:
                self._color[label] = color
            else:
                prop = cycler.next(self._axes)
                if 'color' in prop:
                    self._color[label] = prop['color']
                else:
                    self._color[label] = None

        if ref_name not in self._probabilities[label]:
            self._probabilities[label][ref_name] = []

        self._probabilities[label][ref_name].append(probabilities)

    def add_reference(self, name, y):
        self._reference[name] = ClassificationScore(y)

    def _plot_for_label(self, label):
        for ref_id in self._probabilities[label]:
            for p in self._probabilities[label][ref_id]:
                cm = self._reference[ref_id].confusion(p)
                x = cm.recall[1:]
                y = cm.precision[1:]

                idx = np.argsort(x)
                x = x[idx]
                y = y[idx]

                self._ccurve.add(x, y, label, self._color[label])

    def plot(self, legend=True):
        axes = self._axes

        for label in self._probabilities.keys():
            self._plot_for_label(label)

        axes.set_xlabel('Recall')
        axes.set_ylabel('Precision')

        self._ccurve.plot(same_steps=True)

        eps = 1e-4
        axes.set_xlim([0, 1 + eps])
        axes.set_ylim([0, 1 + eps])

        if legend:
            self._plot_legend(self._probabilities.keys())

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
