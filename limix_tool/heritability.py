from __future__ import division
from numpy import asarray
from numpy import sqrt
import scipy.stats as stats
from limix_math.special import normal_pdf as pdf
from limix_math.special import normal_cdf as cdf
from limix_math.special import normal_logsf as logsf
from limix_math.special import normal_logpdf as logpdf
from limix_math.special import normal_logcdf as logcdf
from numba import jit
import numpy as np


def _lambda_alpha(alpha):
    return pdf(alpha) / (1 - cdf(alpha))


def _exp_norm_trunc(t):
    return _lambda_alpha(t)


def _mean_truncnorm_rtail(a, mean=0., sd=1.):
    alpha = (a - mean) / sd
    return mean + sd * np.exp(logpdf(alpha) - logsf(alpha))


def _mean_truncnorm_ltail(b, mean=0., sd=1.):
    beta = (b - mean) / sd
    lphi_b = logpdf(beta)
    lPhi_b = logcdf(beta)
    return mean - sd * np.exp(lphi_b - lPhi_b)


def _var_truncnorm_rtail(a, mean=0., sd=1.):
    alpha = (a - mean) / sd
    lphi_a = logpdf(alpha)
    lambda_ = np.exp(lphi_a - logsf(alpha))
    return sd * sd * (1.0 - lambda_ * (lambda_ - alpha))


def _var_truncnorm_ltail(b, mean=0., sd=1.):
    return _var_truncnorm_rtail(-b, -mean, sd)


def _mom2_truncnorm_rtail(a):
    return _var_truncnorm_rtail(a) + _mean_truncnorm_rtail(a)**2


def _mom2_truncnorm_ltail(a):
    return _var_truncnorm_ltail(a) + _mean_truncnorm_ltail(a)**2


def h2_correct(h2, prevalence, ascertainment):
    h2 = asarray(h2)
    t = -stats.norm.ppf(prevalence)
    m = _exp_norm_trunc(t)
    c1 = ((ascertainment - prevalence) / (1 - prevalence))
    c2 = (m * ((ascertainment - prevalence) / (1 - prevalence)) - t)
    theta = m * c1 * c2
    # h2 = (1 - np.sqrt(1 - 4*theta*h2))/(2*theta)
    if theta != 0.0:
        h2 = (1 - sqrt(1 - 4 * theta * h2)) / (2 * theta)
    return h2


def _h2_correct2_eq_eq(h2, prevalence, ascertainment, real_h2):
    h2 = asarray(h2)
    real_h2 = asarray(real_h2)
    real_h = np.sqrt(real_h2)
    pre = prevalence
    asc = ascertainment

    t = stats.norm.ppf(1 - pre)

    hj = _mom2_truncnorm_rtail(t / real_h)
    hj2 = _mom2_truncnorm_ltail(t / real_h)

    hr = _mom2_truncnorm_rtail(t / np.sqrt(1 - real_h2))
    hr2 = _mom2_truncnorm_ltail(t / np.sqrt(1 - real_h2))

    A = asc * hr + (1 - asc) * hr2
    B = asc * hj + (1 - asc) * hj2

    return h2 * A / (h2 * A + (1 - h2) * B)


def h2_correct2(h2, prevalence, ascertainment):
    pv = h2
    v = _h2_correct2_eq_eq(h2, prevalence, ascertainment, pv)
    eps = 1e-5
    max_iter = 500
    i = 0
    while abs(pv - v) > eps and i < max_iter:
        pv = v
        v = _h2_correct2_eq_eq(h2, prevalence, ascertainment, pv)
        i += 1
    if i == max_iter:
        print("Warning: maximum number of iterations reached in h2_correct2")
    return v


def h2_observed_space_correct(h2, prevalence, ascertainment):
    t = stats.norm.ppf(1 - prevalence)
    z = stats.norm.pdf(t)
    k = prevalence * (1 - prevalence)
    p = ascertainment * (1 - ascertainment)
    return asarray(h2) * k**2 / (z**2 * p)


def dichotomous_h2_to_liability_h2(h2, prevalence):
    h2 = asarray(h2, float)
    t = stats.norm.ppf(1 - prevalence)
    z = stats.norm.pdf(t)
    return asarray(h2) * (prevalence * (1 - prevalence)) / z**2


def correct_liability_h2(h2, prevalence, ascertainment):
    part1 = (prevalence * (1 - prevalence))
    part2 = (ascertainment * (1 - ascertainment))
    return h2 * (part1 / part2)


@jit
def _haseman_elston_regression(y, K):
    r1 = 0.
    r2 = 0.
    i = 0
    while i < y.shape[0] - 1:
        j = i + 1
        while j < y.shape[0]:
            r1 += y[i] * y[j] * K[i, j]
            r2 += K[i, j] * K[i, j]
            j += 1
        i += 1
    return r1 / r2


def haseman_elston_regression(y, K):
    y = asarray(y, float)
    K = asarray(K, float)
    # u = np.unique(y)
    # assert np.all([ui in [0., 1.] for ui in u])
    return _haseman_elston_regression(y, K)


def sample_phenotype(h2, n, prev):
    h = np.sqrt(h2)
    g = np.random.randn(n) * h
    e = np.random.randn(n) * np.sqrt(1 - h2)
    t = prevalence_threshold(prev)
    y = np.zeros(n)
    y[g + e > t] = 1.
    return (y, g, e)


def prevalence_threshold(prev):
    return -stats.norm.ppf(prev)


def _subselect(y, ncases, ncontrols):
    selected = np.empty(ncases + ncontrols, int)
    idx = np.random.permutation(n)
    i = 0
    while ncases + ncontrols > 0:
        j = idx[i]
        if y[j] == 1 and ncases > 0:
            selected[ncases + ncontrols - 1] = j
            ncases -= 1
        elif y[j] == 0 and ncontrols > 0:
            selected[ncases + ncontrols - 1] = j
            ncontrols -= 1
        i += 1
    return selected


def subselect(ascertainment, y):
    tcases = np.sum(y)
    tcontrols = len(y) - tcases
    asc = ascertainment

    cases = len(y) * asc
    controls = len(y) * (1 - asc)

    cases = min(tcases, cases)
    controls = min(tcontrols, controls)

    N1 = cases / asc
    N2 = controls / (1 - asc)

    N = np.floor(min(N1, N2))

    ncases = int(np.floor(N * asc))
    ncontrols = int(np.floor(N * (1 - asc)))
    return _subselect(y, ncases, ncontrols)

if __name__ == '__main__':
    h2 = 0.6
    ascertainment = 0.5
    prevalence = 0.01
    # print(h2_correct2(h2, prevalence, ascertainment))
    # print(h2_correct(h2, prevalence, ascertainment))
    # print(_second_moment_truncnorm_rtail(1.))
    np.testing.assert_almost_equal(0.6296862857766054588637,
                                   _var_truncnorm_rtail(-1.))

    np.testing.assert_almost_equal(0.1628812078322379730544,
                                   _mean_truncnorm_rtail(-1.4))

    tvals = [-6., -3.2, 0., 0.9, 1.9, 3.]
    expected = [[0.9999999635447027745982, 37.95089781126748107454],
                [0.9923656719188573838153, 12.10269397703079974349],
                [1, 1],
                [2.301078788562801680229, 0.7065019956149924951205],
                [5.34139913940579624807, 0.8716440094476765043652],
                [10.84929596479124391806, 0.9866864828736230386141]]

    from numpy.testing import assert_almost_equal
    for (i, tval) in enumerate(tvals):
        assert_almost_equal(expected[i][0], _mom2_truncnorm_rtail(tval),
                            decimal=5)
        assert_almost_equal(expected[i][1], _mom2_truncnorm_ltail(tval),
                            decimal=5)

    # print(h2_correct(h2, prevalence, ascertainment))
    ascertainment = 0.5
    prevalence = 0.01
    n = 500000
    h2 = 0.2
    (y, g, e) = sample_phenotype(h2, n, prevalence)
    idx = subselect(ascertainment, y)
    print("g %.5f -> %.5f" % (np.var(g) + np.mean(g)**2, np.var(g[idx]) + np.mean(g[idx])**2))
    print("e %.5f -> %.5f" % (np.var(e) + np.mean(e)**2, np.var(e[idx]) + np.mean(e[idx])**2))

    # print(np.var(g[:]), np.var(e[:]))
    # print(np.mean(g[:]), np.mean(e[:]))
    # print("covar: %.5f" % np.cov(g[:], e[:])[0,1])
    # print(np.var(g[:]) / (np.var(g[:])+np.var(e[:])))
    #
    # print("")
    #
    # print(np.var(g[idx]) + np.mean(g[idx])**2, np.var(e[idx]) + np.mean(e[idx])**2)
    # print(np.mean(g[idx]), np.mean(e[idx]))
    # print("covar: %.5f" % np.cov(g[idx], e[idx])[0,1])
    # print(np.var(g[idx]) + np.mean(g[idx])**2) / (np.var(g[idx]) + np.mean(g[idx])**2 + np.var(e[idx]) + np.mean(e[idx])**2)
    #
    # print("corrected: %.5f" % h2_correct(0.105, prevalence, ascertainment))
    # print(h2_correct2(0.105, prevalence, ascertainment))

    # print(_mom2_truncnorm_rtail(0.3))
    # print(h2_correct2(h2, prevalence, ascertainment))
    # print(h2_correct(h2, prevalence, ascertainment))
    # # print(v)
    # # v = h2_correct2(h2, prevalence, ascertainment, v)
    # # print(v)
    # # v = h2_correct2(h2, prevalence, ascertainment, v)
    # # print(v)
    # # v = h2_correct2(h2, prevalence, ascertainment, v)
    # # print(v)
    # # v = h2_correct2(h2, prevalence, ascertainment, v)
    # # print(v)
    # # v = h2_correct2(h2, prevalence, ascertainment, v)
    # # print(v)
    # # v = h2_correct2(h2, prevalence, ascertainment, v)
    # # print(v)
    # # v = h2_correct2(h2, prevalence, ascertainment, v)
    # # print(v)
    # # v = h2_correct2(h2, prevalence, ascertainment, v)
    # # print(v)
