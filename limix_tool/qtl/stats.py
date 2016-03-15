from __future__ import division
import scipy.stats as st
from scipy.misc import logsumexp
import numpy as np
from numpy import log
from numpy import partition
from numpy import mean
from limix_util.scalar import isint

def _get_median_terms(n):
    if n % 2 == 0:
        nh = n // 2
        kth = [nh - 1, nh]
    else:
        kth = [(n - 1) // 2]
    return kth

def gcontrol(chi2):
    """ Genomic control
    """
    n = len(chi2)
    kth = _get_median_terms(n)
    c = st.chi2(df=1)
    chi2 = partition(chi2, kth)
    # x2obs = mean(c.ppf(1-chi2[kth]))
    x2obs = mean(chi2[kth])
    x2exp = c.ppf(0.5)
    return x2obs/x2exp

def qvalues(pv):
    import rpy2.robjects as robjects
    from rpy2.robjects.packages import importr
    import rpy2.robjects.numpy2ri
    rpy2.robjects.numpy2ri.activate()
    qvalue = importr('qvalue')
    print qvalue.qvalue(pv)

def hwe_test(n_ab, n_a, n_b):
    """ Exact test for Hardy-Weinberg Equilibrium for biallelic genotype.

    This statistics is described in "A Note on Exact Tests of
    Hardy-Weinberg Equilibrium."

    :param int n_a: Number of the rarer alleles.
    :param int n_b: Number of the common alleles.
    :param int n_ab: Number of heterozygous AB genotypes.

    Note that n_aa = (n_a - n_ab)/2 and n_bb = (n_b - n_ab)/2.
    """
    assert isint(n_a)
    n_a = int(n_a)
    assert isint(n_b)
    n_b = int(n_b)
    assert isint(n_ab)
    n_ab = int(n_ab)
    assert n_a <= n_b
    assert n_a >= n_ab
    assert (n_a + n_b) % 2 == 0
    # N = n_ab + int((n_a - n_ab)/2) + int((n_b - n_ab)/2)

    def ln_upper_weight(n_ab):
        n_aa = int((n_a - n_ab)/2)
        n_bb = int((n_b - n_ab)/2)
        return log(4) + log(n_aa) + log(n_bb) - log(n_ab + 2) - log(n_ab + 1)

    def ln_lower_weight(n_ab):
        n_aa = int((n_a - n_ab)/2)
        n_bb = int((n_b - n_ab)/2)
        return log(n_ab) + log(n_ab - 1) - log(4) - log(n_aa + 1) - log(n_bb + 1)

    lnP = np.empty(int(n_a / 2) + 1)
    # this can be an arbitrary as long as I normalize the probabilities
    # at the end
    lnP[int(n_ab / 2)] = 0.
    n_ab_i = n_ab
    while n_ab_i >= 2:
        i = int(n_ab_i / 2)
        lnP[i-1] = lnP[i] + ln_lower_weight(n_ab_i)
        n_ab_i -= 2

    n_ab_i = n_ab
    while n_ab_i <= n_a - 2:
        i = int(n_ab_i / 2)
        lnP[i+1] = lnP[i] + ln_upper_weight(n_ab_i)
        n_ab_i += 2

    lnPab = lnP[int(n_ab / 2)]
    ok = lnPab >= lnP
    lnC = logsumexp(lnP)
    return np.exp(logsumexp(lnP[ok]) - lnC)
