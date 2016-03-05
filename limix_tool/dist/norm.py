import scipy
from numba import vectorize, float64

def logcdf(x):
    return scipy.special.log_ndtr(x)

@vectorize([float64(float64)], nopython=True,
           locals=dict(_norm_pdf_logC=float64))
def logpdf(x):
    _norm_pdf_logC = 0.9189385332046726695409688545623794198036193847656250
    return -(x*x)/ 2.0 - _norm_pdf_logC
