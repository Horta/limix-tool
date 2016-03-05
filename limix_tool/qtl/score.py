from __future__ import division
import numpy as np
from numpy import asarray
from bisect import bisect_left
from numba import jit
from hcache import Cached, cached
from numpy import log10
from stats import gcontrol

@jit(cache=True)
def first_occurrence(arr, v):
    for i in range(arr.shape[0]):
        if arr[i] == v:
            return i
    return None

@jit(cache=True)
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

@jit(cache=True)
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

# class MultiScore(object):
#     def __init__(self):
#         self._scores = dict()
#
#     def add(self, name, score):
#         self._scores[name] = score
#
#     def get_tprs(self, method, fpr=0.05, approach='rank'):
#         assert approach == 'rank'
#         scores = self._scores.values()
#         tprs = np.empty(len(scores))
#         for (i, s) in enumerate(scores):
#             tprs[i] = s.rank_score(name=method, fpr=fpr)
#         return tprs

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



class WindowScore(Cached):
    def __init__(self, causals, pos, wsize=50000, verbose=True):
        Cached.__init__(self)
        wsize = int(wsize)
        # print 'Info: using window size %d.' % wsize
        self._pv = dict()
        self._sidx = dict()

        total_size = pos[-1] - pos[0]
        if wsize > 0.1 * total_size:
            perc = wsize/total_size * 100
            print('Warning: the window' +
                  ' size is {perc}%'.format(perc=int(perc)) +
                  ' of the total candidate region.')

        causals = asarray(causals, int)

        assert len(causals) == len(np.unique(causals))
        causality = dict()
        for c in causals:
            if wsize == 1:
                right = left = pos[c]
            else:
                left = _walk_left(pos, c, int(wsize/2))
                right = _walk_right(pos, c, int(wsize/2))
            for i in range(left, right+1):
                if i not in causality:
                    causality[i] = []
                causality[i].append(c)

        self._causality = causality

        self._P = len(causals)
        self._N = len(pos) - len(causality)

        snp_within_window = asarray(self._causality.keys())
        causal_snps = self._causality.values()
        idx = np.argsort(snp_within_window)
        snp_within_window = snp_within_window[idx]
        causal_snps = [causal_snps[i] for i in idx]
        self._responsible_causal_snps = asarray(causal_snps, int)
        self._snp_within_window = snp_within_window

        if verbose:
            print("Found %d positive and %d negative SNPs."
                  % (self._P, self._N))

    @property
    def ncandidates(self):
        k = self._pv.keys()[0]
        return self._pv[k].shape[0]

    def add(self, name, pv):
        if not np.all(np.isfinite(pv)):
            print 'Warning: not all p-values from %s are finite.' % name
            print 'Setting those p-values to 1.'
            pv[np.logical_not(np.isfinite(pv))] = 1.0

        self._pv[name] = np.asarray(pv, float)
        self._sidx[name] = np.argsort(pv)
        self.clear_cache('_compute_rank_scores')


    @property
    def names(self):
        return self._pv.keys()

    def rank_score(self, name, fpr=0.05):
        (fprs, tprs) = self._compute_rank_scores(name, fpr)
        diff = fprs - fpr
        if len(diff) == 1:
            return diff[0]

        i = bisect_left(diff, 0)
        i = max(0, i-1)

        assert i < len(diff)
        if abs(diff[i]) <= abs(diff[i+1]):
            return tprs[i]
        return tprs[i+1]

    def accuracy_score(self, name, fpr=0.05):
        (total, tp) = self.hits_score(name, fpr=fpr)
        if total == 0:
            return 0.
        return tp / total

    def hits_score(self, name, fpr=0.05):
        pv = self._pv[name]
        sidx = self._sidx[name]
        i = bisect_left(pv[sidx], fpr)
        i = max(0, i-1)
        significants = sidx[:i]

        sww = self._snp_within_window
        fpos = np.searchsorted(sww, significants)

        rcs = self._responsible_causal_snps
        hit_causal_snp = set()
        hcs = hit_causal_snp
        hcs_size = len(hcs)

        i = 0
        n = len(fpos)
        FP = 0
        TP = 0
        while i < n:
            j = fpos[i]
            if j == len(sww) or sww[j] != significants[i]:
                FP += 1
            else:
                TP += 1
                # for c in rcs[j]:
                #     hcs.add(c)
                #     if len(hcs) > hcs_size:
                #         hcs_size = len(hcs)
                #         TP += 1
            i += 1
        return (TP + FP, TP)

    @cached
    def _compute_rank_scores(self, name, upper_fpr=1.0):
        P = self._P
        N = self._N
        sww = self._snp_within_window
        rcs = self._responsible_causal_snps

        # (fpr, tpr) = _tf_pos_rate(P, N, sww, rcs, self._sidx[name])
        (fpr, tpr) = _tf_pos_rate_limited(P, N, sww, rcs, self._sidx[name], upper_fpr)


        # initially I was doing:
        # idx = np.argsort(fpr)
        # (asarray(fpr)[idx], asarray(tpr)[idx])
        # the problem is that fpr might have repeat
        # values which means that tpr might not end up
        # in ascending order afterall...

        fpr = np.sort(fpr)
        tpr = np.sort(tpr)

        return (fpr, tpr)

@jit(cache=True)
def _tf_pos_rate(P, N, snp_within_window, responsible_causal_snps,
                 idx_pvsorted):

    rcc = responsible_causal_snps
    hit_causal_snp = set()
    hcs = hit_causal_snp
    hcs_size = len(hcs)

    n = len(idx_pvsorted)
    sww = snp_within_window
    idx = idx_pvsorted
    TP = np.empty(n+1)
    FP = np.empty(n+1)

    fpos = np.searchsorted(sww, idx)

    TP[0] = 0
    FP[0] = 0
    for i in range(n):
        FP[i+1] = FP[i]
        TP[i+1] = TP[i]

        j = fpos[i]
        if j == len(sww) or sww[j] != idx[i]:
            FP[i+1] += 1
        else:
            for c in rcc[j]:
                hcs.add(c)
                if len(hcs) > hcs_size:
                    hcs_size = len(hcs)
                    TP[i+1] += 1

    tpr = TP/P
    fpr = FP/N
    return (fpr[1:], tpr[1:])


@jit(cache=True)
def _tf_pos_rate_limited(P, N, snp_within_window, responsible_causal_snps,
                 idx_pvsorted, upper_fpr):

    upper_fpr = min(2*upper_fpr, 1.0)
    rcc = responsible_causal_snps
    hit_causal_snp = set()
    hcs = hit_causal_snp
    hcs_size = len(hcs)

    n = len(idx_pvsorted)
    sww = snp_within_window
    idx = idx_pvsorted
    TP = np.empty(n+1)
    FP = np.empty(n+1)

    fpos = np.searchsorted(sww, idx)

    TP[0] = 0
    FP[0] = 0
    i = 0
    while i < n:
    # for i in range(n):
        FP[i+1] = FP[i]
        TP[i+1] = TP[i]

        j = fpos[i]
        if j == len(sww) or sww[j] != idx[i]:
            FP[i+1] += 1
            if FP[i+1]/N > upper_fpr:
                i += 1
                break
        else:
            for c in rcc[j]:
                hcs.add(c)
                if len(hcs) > hcs_size:
                    hcs_size = len(hcs)
                    TP[i+1] += 1
        i += 1

    tpr = TP[1:i]/P
    fpr = FP[1:i]/N
    return (fpr, tpr)
