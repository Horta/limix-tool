import scipy.stats as st
from numpy import partition
from numpy import mean

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

if __name__ == '__main__':
    import numpy as np
    pv = np.random.rand(5)
    qvalues(pv)
