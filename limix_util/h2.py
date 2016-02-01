from numpy import asarray
from numpy import sqrt
# import scipy
import scipy.stats as stats

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
