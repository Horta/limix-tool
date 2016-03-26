from __future__ import division
import logging
import numpy as np
from numpy import asarray
from numba import jit
from numpy import log10
from .stats import gcontrol
from limix_util.array_ import iscrescent

@jit
def first_occurrence(arr, v):
    for i in range(arr.shape[0]):
        if arr[i] == v:
            return i
    return None

@jit
def _walk_left(pos, c, dist):
    assert dist > 0
    step = 0
    middle = pos[c]
    i = c
    while i > 0 and step < dist:
        i -= 1
        assert pos[i] <= middle
        step = (middle - pos[i])
    if step > dist:
        i += 1
    assert i <= c
    return i

@jit
def _walk_right(pos, c, dist):
    assert dist > 0
    step = 0
    middle = pos[c]
    i = c
    n = len(pos)
    while i < n-1 and step < dist:
        i += 1
        assert pos[i] >= middle
        step = (pos[i] - middle)
    if step > dist:
        i -= 1
    assert i >= c
    return i

def roc_curve(multi_score, method, max_fpr=0.05):
    max_fpr = float(max_fpr)
    fprs = np.arange(0., max_fpr, step=0.001)
    tprs = np.empty_like(fprs)
    tprs_stde = np.empty_like(fprs)
    for (i, fpr) in enumerate(fprs):
        tprs_ = multi_score.get_tprs(method, fpr=fpr, approach='rank')
        tprs[i] = np.mean(tprs_)
        assert tprs[i] >= tprs[max(i-1, 0)]
        tprs_stde[i] = np.std(tprs_)/np.sqrt(len(tprs_))
    return (fprs, tprs, tprs_stde)

def _rank_confidence_band(nranks, alpha, max_n2ret=100):
    """calculate theoretical expectations for qqplot"""
    import scipy.stats as st

    left, right = 0., 1.
    width = right - left

    n2ret = min(max_n2ret, nranks)
    eps = np.finfo(float).eps
    i2ret = np.logspace(log10(eps), log10(nranks-1-eps), n2ret,
                         endpoint=True)

    mean = np.empty(n2ret)
    top = np.empty(n2ret)
    bottom = np.empty(n2ret)
    for (i, i2r) in enumerate(i2ret):
        b = st.beta(i2r + 1, nranks - i2r)
        mean[i] = left + width * b.stats('m').item()
        top[i] = left + width * b.ppf(1-alpha/2.)
        bottom[i] = left + width * b.ppf(alpha/2.)

    return (bottom, mean, top)

def combine_pvalues(pvals, strategy='concat'):
    assert strategy == 'concat'
    return np.concatenate(pvals)

class NullScore(object):
    def __init__(self):
        self._pv = dict()

    def pv(self, method):
        return self._pv[method]

    @property
    def methods(self):
        return self._pv.keys()

    def add(self, method, pv):
        pv = asarray(pv, float)
        pv = pv.ravel()

        if not np.all(np.isfinite(pv)):
            print("Not all p-values are finite.")
            print('Setting those to 1.')
            ok = np.isfinite(pv)
            pv[np.logical_not(ok)] = 1.

        if np.any(np.logical_or(pv < 0, pv > 1)):
            print('There are p-values outside the range [0, 1].')
            print('Clipping those to lie between 0 and 1.')
            pv = np.clip(pv, 0., 1.)

        self._pv[method] = pv

    def gcontrol(self, m):
        return gcontrol(self._pv[m])

    def confidence_band(self, m, alpha=0.05):
        n = len(self._pv[m])
        (bottom, mean, top) = _rank_confidence_band(n, alpha)
        return (bottom, mean, top)


class _WindowScore(object):
    def __init__(self, causal, pos, wsize=50000):
        """Provide a couple of scores based on the idea of windows around
           genetic markers.

           :param causal: Indices defining the causal markers.
           :param pos: Base-pair position of each candidate marker, in crescent
                       order.
        """
        self._logger = logging.getLogger()
        wsize = int(wsize)
        self._pv = dict()
        self._sidx = dict()
        pos = asarray(pos)
        assert iscrescent(pos)
        self._ncandidates = len(pos)

        total_size = pos[-1] - pos[0]
        if wsize > 0.1 * total_size:
            perc = wsize/total_size * 100
            self._logger.warn('The window size is %d%% of the total candidate' +
                              ' region.', int(perc))

        causal = asarray(causal, int)

        assert len(causal) == len(np.unique(causal))
        marker_within_window = set()
        for c in causal:
            if wsize == 1:
                right = left = pos[c]
            else:
                left = _walk_left(pos, c, int(wsize/2))
                right = _walk_right(pos, c, int(wsize/2))
            for i in range(left, right+1):
                marker_within_window.add(i)

        self._P = len(marker_within_window)
        self._N = len(pos) - self._P

        self._marker_within_window = list(marker_within_window)

        self._logger.info("Found %d positive and %d negative markers.",
                          self._P, self._N)

    def confusion(self, pv):
        pv = np.asarray(pv, float)
        assert self._ncandidates == len(pv)
        cm = ConfusionMatrix(self._P, self._N, self._marker_within_window,
                             np.argsort(pv))
        return cm

class WindowScore(object):
    def __init__(self, wsize=50000):
        """Provide a couple of scores based on the idea of windows around
           genetic markers.
        """
        self._logger = logging.getLogger()
        self._wsize = int(wsize)
        self._chrom = dict()

    def set_chrom(self, chromid, pos, causal):
        """
            :param causals: Indices defining the causal markers.
            :param pos: Within-chromossome base-pair position of each candidate
                        marker, in crescent order.
        """
        # self._chrom[chromid] = _WindowScore(causal, pos, self._wsize)
        pos = np.asarray(pos, int)
        assert iscrescent(pos)
        self._chrom[chromid] = (np.asarray(causal, int), pos)

    def _get_window_score(self, chromids):
        pos = []
        causal = []

        offset = 0
        idx_offset = 0
        for cid in sorted(chromids):
            pos.append(offset + self._chrom[cid][1])
            offset += pos[-1][-1] + int(self._wsize / 2 + 1)

            if len(self._chrom[cid][0]) > 0:
                causal.append(idx_offset + self._chrom[cid][0])
                idx_offset += len(self._chrom[cid][1])

        pos = np.concatenate(pos)
        causal = np.concatenate(causal)
        return _WindowScore(causal, pos, self._wsize)

    def confusion(self, pv):
        if isinstance(pv, dict):
            ws = self._get_window_score(pv.keys())
            pv = np.concatenate([pv[k] for k in sorted(pv.keys())])
        else:
            ws = self._get_window_score(self._chrom.keys())
        return ws.confusion(pv)

def getter(func):
    class ItemGetter(object):
        def __getitem__(self, i):
            return func(i)

        def __lt__(self, other):
            return func(np.s_[:]) < other

        def __le__(self, other):
            return func(np.s_[:]) <= other

        def __gt__(self, other):
            return func(np.s_[:]) > other

        def __ge__(self, other):
            return func(np.s_[:]) >= other

        def __eq__(self, other):
            return func(np.s_[:]) == other

    return ItemGetter()

class ConfusionMatrix(object):
    def __init__(self, P, N, true_set, idx_rank):
        self._TP = np.empty(P+N+1, dtype=int)
        self._FP = np.empty(P+N+1, dtype=int)
        assert len(idx_rank) == P + N

        true_set = np.asarray(true_set, int)
        true_set.sort()

        idx_rank = np.asarray(idx_rank, int)

        ins_pos = np.searchsorted(true_set, idx_rank)
        _confusion_matrix_tp_fp(P + N, ins_pos, true_set, idx_rank,
                          self._TP, self._FP)
        self._N = N
        self._P = P

    @property
    def TP(self):
        return getter(lambda i: self._TP[i])

    @property
    def FP(self):
        return getter(lambda i: self._FP[i])

    @property
    def TN(self):
        return getter(lambda i: self._N - self.FP[i])

    @property
    def FN(self):
        return getter(lambda i: self._P - self.TP[i])

    @property
    def sensitivity(self):
        """ Sensitivity (also known as true positive rate.)
        """
        return getter(lambda i: self.TP[i] / self._P)

    @property
    def tpr(self):
        return self.sensitivity

    @property
    def recall(self):
        return self.sensitivity

    @property
    def specifity(self):
        """ Specifity (also known as true negative rate.)
        """
        return getter(lambda i: self.TN[i] / self._N)

    @property
    def precision(self):
        return getter(lambda i: self.TP[i] / (self.TP[i] + self.FP[i]))

    @property
    def npv(self):
        """ Negative predictive value.
        """
        return getter(lambda i: self.TN[i] / (self.TN[i] + self.FN[i]))

    @property
    def fallout(self):
        """ Fall-out (also known as false positive rate.)
        """
        return getter(lambda i: 1 - self.specifity[i])

    @property
    def fpr(self):
        return self.fallout

    @property
    def fnr(self):
        """ False negative rate.
        """
        return getter(lambda i: 1 - self.sensitivity[i])

    @property
    def fdr(self):
        """ False discovery rate.
        """
        return getter(lambda i: 1 - self.precision[i])

    @property
    def accuracy(self):
        """ Accuracy.
        """
        return getter(lambda i: (self.TP[i] + self.TN[i]) / (self._N + self._P))

    @property
    def f1score(self):
        """ F1 score (harmonic mean of precision and sensitivity).
        """
        return getter(lambda i: 2 * self.TP[i] / (2*self.TP[i] + self.FP[i] + self.FN[i]))


def _confusion_matrix_tp_fp(n, ins_pos, true_set, idx_rank, TP, FP):
    TP[0] = 0
    FP[0] = 0
    i = 0
    while i < n:
        FP[i+1] = FP[i]
        TP[i+1] = TP[i]

        j = ins_pos[i]
        if j == len(true_set) or true_set[j] != idx_rank[i]:
            FP[i+1] += 1
        else:
            TP[i+1] += 1
        i += 1
