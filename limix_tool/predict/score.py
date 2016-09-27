from __future__ import division
import logging
import numpy as np
from numpy import asarray
from numba import jit
from numpy import log10
from limix_math import iscrescent
from limix_math.special import r_squared


def roc_curve(multi_score, method, max_fpr=0.05):
    max_fpr = float(max_fpr)
    fprs = np.arange(0., max_fpr, step=0.001)
    tprs = np.empty_like(fprs)
    tprs_stde = np.empty_like(fprs)
    for (i, fpr) in enumerate(fprs):
        tprs_ = multi_score.get_tprs(method, fpr=fpr, approach='rank')
        tprs[i] = np.mean(tprs_)
        assert tprs[i] >= tprs[max(i - 1, 0)]
        tprs_stde[i] = np.std(tprs_) / np.sqrt(len(tprs_))
    return (fprs, tprs, tprs_stde)


class _WindowScore(object):

    def __init__(self, causal, pos, wsize=50000, r2=None):
        """Provide a couple of scores based on the idea of windows around
           genetic markers.

           :param causal: Indices defining the causal markers.
           :param pos: Base-pair position of each candidate marker, in crescent
                       order.
        """
        self._logger = logging.getLogger(__name__)
        wsize = int(wsize)
        self._pv = dict()
        self._sidx = dict()
        pos = asarray(pos)
        assert iscrescent(pos)
        self._ncandidates = len(pos)

        total_size = pos[-1] - pos[0]
        if wsize > 0.1 * total_size:
            perc = wsize / total_size * 100
            self._logger.warn('The window size is %d%% of the total candidate' +
                              ' region.', int(perc))

        causal = asarray(causal, int)

        if r2 is None:
            r2 = np.ones((len(causal), len(pos)))
        else:
            r2 = np.asarray(r2, float)
            assert r2.shape[0] == len(causal)
            assert r2.shape[1] == len(pos)
            assert np.all(r2[:] >= 0.)

        assert len(causal) == len(np.unique(causal))
        ld_causal_markers = set()
        for (j, c) in enumerate(causal):
            if wsize == 1:
                right = left = pos[c]
            else:
                left = _walk_left(pos, c, int(wsize / 2))
                right = _walk_right(pos, c, int(wsize / 2))
            for i in range(left, right + 1):
                if r2[j, i] >= 0.8:
                    ld_causal_markers.add(i)

        self._P = len(ld_causal_markers)
        self._N = len(pos) - self._P

        self._ld_causal_markers = list(ld_causal_markers)

        self._logger.info("Found %d positive and %d negative markers.",
                          self._P, self._N)


class ClassificationScore(object):

    def __init__(self, y):
        self._logger = logging.getLogger(__name__)
        self._y = y

    def confusion(self, probabilities):
        assert len(self._y) == len(probabilities)
        p = np.empty((len(self._y),))
        for i in range(len(self._y)):
            p[i] = probabilities[i][1]
        cm = ConfusionMatrix(self._y, p)
        return cm


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

    def __init__(self, y, p):
        P = int(sum(y))
        N = len(y) - P
        self._TP = np.empty(P + N + 1, dtype=int)
        self._FP = np.empty(P + N + 1, dtype=int)

        self._TP[0] = 0
        self._FP[0] = 0

        idx = np.argsort(-p)
        for i in range(1, P + N + 1):
            if y[idx[i - 1]] == 1:
                self._TP[i] = self._TP[i - 1] + 1
                self._FP[i] = self._FP[i - 1]
            else:
                self._TP[i] = self._TP[i - 1]
                self._FP[i] = self._FP[i - 1] + 1

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
        return getter(lambda i: 2 * self.TP[i] / (2 * self.TP[i] + self.FP[i] + self.FN[i]))

    def roc(self):
        tpr = self.tpr[1:]
        fpr = self.fpr[1:]

        idx = np.argsort(fpr)
        fpr = fpr[idx]
        tpr = tpr[idx]

        return (fpr, tpr)


def auc(fpr, tpr):
    left = fpr[0]
    area = 0.
    for i in range(1, len(fpr)):
        width = fpr[i] - left
        area += width * tpr[i - 1]
        left = fpr[i]
    area += (1 - left) * tpr[-1]
    return area


def _confusion_matrix_tp_fp(n, ins_pos, true_set, idx_rank, TP, FP):
    TP[0] = 0
    FP[0] = 0
    i = 0
    while i < n:
        FP[i + 1] = FP[i]
        TP[i + 1] = TP[i]

        j = ins_pos[i]
        if j == len(true_set) or true_set[j] != idx_rank[i]:
            FP[i + 1] += 1
        else:
            TP[i + 1] += 1
        i += 1
