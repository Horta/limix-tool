from numpy import asarray
from numpy import sqrt
import numpy as np
import scipy.stats as stats
from numba import jit

def _lambda_alpha(alpha):
    return stats.norm.pdf(alpha) / (1 - stats.norm.cdf(alpha))

def _exp_norm_trunc(t):
    return _lambda_alpha(t)

def h2_correct(h2, prevalence, ascertainment):
    h2 = asarray(h2)
    t = -stats.norm.ppf(prevalence)
    m = _exp_norm_trunc(t)
    c1 = ((ascertainment-prevalence)/(1-prevalence))
    c2 = ( m*((ascertainment-prevalence)/(1-prevalence)) - t)
    theta = m * c1 * c2
    # h2 = (1 - np.sqrt(1 - 4*theta*h2))/(2*theta)
    ok = theta != 0.0
    if theta != 0.0:
        h2 = (1 - sqrt(1 - 4*theta*h2))/(2*theta)
    return h2

def h2_observed_space_correct(h2, prevalence, ascertainment):
    t = stats.norm.ppf(1-prevalence)
    z = stats.norm.pdf(t)
    k = prevalence * (1 - prevalence)
    p = ascertainment * (1 - ascertainment)
    return asarray(h2) * k**2 / (z**2 * p)

def dichotomous_h2_to_liability_h2(h2, prevalence):
    h2 = asarray(h2, float)
    t = stats.norm.ppf(1-prevalence)
    z = stats.norm.pdf(t)
    return asarray(h2) * (prevalence * (1 - prevalence)) / z**2

def correct_liability_h2(h2, prevalence, ascertainment):
    part1 = (prevalence * (1 - prevalence))
    part2 = (ascertainment * (1 - ascertainment))
    return h2 * (part1 / part2)

@jit(cache=True)
def _haseman_elston_regression(y, K):
    r1 = 0.
    r2 = 0.
    i = 0
    while i < y.shape[0]-1:
        j = i+1
        while j < y.shape[0]:
            r1 += y[i] * y[j] * K[i,j]
            r2 += K[i,j]*K[i,j]
            j += 1
        i += 1
    return r1 / r2

def haseman_elston_regression(y, K):
    y = asarray(y, float)
    K = asarray(K, float)
    u = np.unique(y)
    # assert np.all([ui in [0., 1.] for ui in u])
    return _haseman_elston_regression(y, K)

if __name__ == '__main__':
    y = np.random.randint(0, 2, 2000)
    X = np.random.randn(2000, 100)
    X = X - X.mean(0)
    X = X / X.std(0)
    K = X.dot(X.T) / float(100)
    K += np.eye(2000) * 0.0001
    # K = K / K.diagonal().mean()
    z = np.random.multivariate_normal(np.zeros(2000), K)
    y[z<0] = 0.
    y[z>=0] = 1
    hh2 = haseman_elston_regression(y, K)
    from gwarped_exp.method.leap import bernoulli_h2
    import ipdb; ipdb.set_trace()
    bernoulli_h2(np.asarray(y, float), np.ones(2000), K, 100, 0.5)
    print(hh2)
    # ascertainment = 0.5
    # prevalence = 0.1
    # h2 = h2_observed_space_correct(hh2, prevalence, ascertainment)
    # print hh2, h2
    # print hh2, correct_liability_h2(dichotomous_h2_to_liability_h2(hh2, prevalence), prevalence, ascertainment)
