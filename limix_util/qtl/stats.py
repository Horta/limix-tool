from scipy.stats import chi2
from numpy import partition
from numpy import mean

def _get_median_terms(n):
    if n % 2 == 0:
        nh = n // 2
        kth = [nh - 1, nh]
    else:
        kth = [(n - 1) // 2]
    return kth

def gcontrol(pv):
    n = len(pv)
    kth = _get_median_terms(n)
    c = chi2(df=1)
    pv = partition(pv, kth)
    x2obs = mean(c.ppf(1-pv[kth]))
    x2exp = c.ppf(0.5)
    return x2obs/x2exp

def qvalues(pv):
    import rpy2.robjects as robjects
    from rpy2.robjects.packages import importr
    import rpy2.robjects.numpy2ri
    rpy2.robjects.numpy2ri.activate()
    qvalue = importr('qvalue')
    print qvalue.qvalue(pv)

if __name__ == '__main__':
    import numpy as np
    pv = np.random.rand(5)
    qvalues(pv)
