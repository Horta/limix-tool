from __future__ import division, absolute_import
import numpy as np
import colour
from scipy.special import betaincinv
from numba import jit, void, int64, float64
from limix_plot import cycler_ as cycler
from collections import OrderedDict
from ncephes.cprob import incbi

@jit(void(float64, int64, float64[:], float64[:], float64[:]),
     nogil=True, nopython=True)
def _do_rank_confidence_band(alpha, n, bottom, mean, top):
    for k in range(1, n+1):
        top[k-1] = incbi(k, n + 1. - k, 1-alpha)
        mean[k-1] = k/(n+1.)
        bottom[k-1] = incbi(k, n + 1. - k, alpha)

def _rank_confidence_band(nranks):
    alpha = 0.01
    n = nranks

    mean = np.empty(n)
    top = np.empty(n)
    bottom = np.empty(n)

    _do_rank_confidence_band(alpha, n, bottom, mean, top)

    return (bottom, mean, top)

def _expected(n):
    if n not in _expected.cache:
        lnpv = np.linspace(1/(n+1), n/(n+1), n, endpoint=True)
        lnpv = np.flipud(-np.log10(lnpv))
        _expected.cache[n] = lnpv
    return _expected.cache[n]
_expected.cache = dict()

class QQPlot(object):
    def __init__(self, axes):
        self._axes = axes
        self._pv = OrderedDict()
        self._color = dict()
        self._properties = dict()

    def add(self, pv, label, color=None, props=None):
        self._pv[label] = np.asarray(pv)

        if color:
            self._color[label] = color
        else:
            prop = cycler.next(self._axes)
            if 'color' in prop:
                self._color[label] = prop['color']
            else:
                self._color[label] = None
        self._properties[label] = props

    @property
    def _max_size(self):
        return max([len(v) for v in iter(self._pv.values())])

    def plot(self, confidence=True, plot_top=100, legend=True):
        print("PLOT 1")
        axes = self._axes
        labels = self._pv.keys()
        print("PLOT 2")
        for label in labels:
            self._plot_points(label, plot_top)
        print("PLOT 3")
        if confidence:
            self._plot_confidence_band()
        print("PLOT 4")
        axes.grid(False)
        axes.tick_params(axis='both', which='major', direction='out')
        axes.spines['right'].set_visible(False)
        axes.spines['top'].set_visible(False)
        axes.yaxis.set_ticks_position('left')
        axes.xaxis.set_ticks_position('bottom')


        N = self._max_size
        axes.set_xlim([0, -np.log10(1/(N+1))])

        if legend:
            self._plot_legend(labels)

        print("PLOT 5")
        return axes

    def _xymax(self):
        labels = self._pv.keys()
        x = -np.inf
        y = -np.inf
        for label in labels:
            (lpv, lnpv) = self._xy(label)
            x = max(x, max(lpv))
            y = max(y, max(lnpv))
        return (x, y)

    def _xy(self, label):
        lpv = -np.log10(self._pv[label])
        lpv.sort()

        return (_expected(len(lpv)), lpv)

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

    def _plot_points(self, label, plot_top):
        axes = self._axes
        print("POINTS 1")
        (lnpv, lpv) = self._xy(label)
        print("POINTS 2")
        n = int(len(lnpv) * plot_top/100)

        rest = dict()
        if self._color[label]:
            rest['color'] = self._color[label]

        if self._properties[label]:
            rest.update(self._properties[label])
        print("POINTS 3")
        try:
            ec = colour.Color(self._color[label])
        except ValueError:
            ec = colour.Color('#' + self._color[label])

        ec = int(ec.get_hex_l()[1:], base=16)
        ec = (ec & 0xfefefe) >> 1
        ec = colour.Color('#' + hex(ec)[2:]).get_web()

        print("POINTS 4")
        axes.plot(lnpv[-n:], lpv[-n:], 'o', markeredgecolor=ec,
                  clip_on=False, zorder=100, **rest)

        print("POINTS 5")
        axes.set_ylabel(r'Observed -log10(P-value)')
        axes.set_xlabel(r'Expected -log10(P-value)')

    def _plot_confidence_band(self):
        axes = self._axes

        print("CONFIDENCE 1")
        (bo, me, to) = _rank_confidence_band(self._max_size)
        print("CONFIDENCE 2")
        bo = np.flipud(-np.log10(bo))
        me = np.flipud(-np.log10(me))
        to = np.flipud(-np.log10(to))

        print("CONFIDENCE 3")
        x = y = me[0], me[-1]
        axes.plot(x, y, 'black')
        print("CONFIDENCE 4")
        axes.fill_between(me, bo, to, lw=0.0,
                          edgecolor='black', facecolor='0.90',
                          clip_on=False)

        print("CONFIDENCE 5")
