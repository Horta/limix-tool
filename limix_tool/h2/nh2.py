import numpy as np
import scipy as sp
import scipy.stats as st
from limix_math.dist.norm import logpdf
from limix_math.dist.norm import pdf
from limix_math.dist.norm import logcdf
from limix_math.dist.norm import cdf
from limix_math.dist.norm import logsf

def compute_offset(varg, vare, prevalence):
    # vg = np.sqrt(varg)
    ve = np.sqrt(vare)
    ic = st.norm.isf(prevalence)
    offset = ic*ve*np.sqrt(1+varg/vare)
    return offset

def E_tl_cdf(varg, vare, o):
    # vg = np.sqrt(varg)
    ve = np.sqrt(vare)
    b = ve * np.sqrt(1 + varg/vare)
    return -varg * pdf(o/b)/b

def E_tl2_cdf(varg, vare, o):
    g_mu = 0
    # vg = np.sqrt(varg)
    ve = np.sqrt(vare)
    b = ve * np.sqrt(1 + varg/vare)
    c = o/b
    #_tl2_g_mu = 2*g_mu*E_tl_cdf(varg, vare, o)
    _tl2_g_mu = cdf(c)*(varg - g_mu*g_mu)
    _tl2_g_mu -= varg*varg*c*pdf(c)/(vare + varg)
    return  _tl2_g_mu

def tl_g_mu(varg, vare, o, a, p):
    g_mu = 0.
    _tl_g_mu = (a/p) * g_mu
    E = E_tl_cdf(varg, vare, o)
    _tl_g_mu -= (a/p) * E
    _tl_g_mu += ((1 - a)/(1 - p)) * E
    return _tl_g_mu

def tl_g_mom2(varg, vare, o, a, p):
    # we assume g_mu = 0.
    _tl_g_mu = (a/p) * varg
    E2 = E_tl2_cdf(varg, vare, o)
    _tl_g_mu -= (a/p) * E2
    _tl_g_mu += ((1 - a)/(1 - p)) * E2
    return _tl_g_mu

def E_tl_e_trunc_upper(tg, vare, o):
    e_mu = 0.
    ve = np.sqrt(vare)
    alpha = (o - tg - e_mu)/ve
    lambda_ = np.exp(logpdf(alpha) - logsf(alpha))
    return (e_mu + ve * lambda_) * np.exp(logsf((o-tg-e_mu)/ve))

def E_tl_e_trunc_lower(tg, vare, o):
    e_mu = 0.
    ve = np.sqrt(vare)
    b = o - tg
    beta  = (b - e_mu) / ve
    return (e_mu - ve * np.exp(logpdf(beta) - logcdf(beta))) * cdf((o-tg-e_mu)/ve)

def tl_ge_mom(varg, vare, o, a, p):
    g_mu = 0.
    def fun1(tg):
        return tg * E_tl_e_trunc_upper(tg, vare, o) * pdf(tg, g_mu, varg)

    part1 = sp.integrate.quad(fun1, -30., +30.)
    # print part1

    def fun2(tg):
        return tg * E_tl_e_trunc_lower(tg, vare, o) * pdf(tg, g_mu, varg)

    part2 = sp.integrate.quad(fun2, -30., +30.)
    # print part2

    return (a/p) * part1[0] + ((1-a)/(1-p)) * part2[0]
    # (a/p) * integrate_over_g(E_tl_e_trunc(tg) * pdf(tg, 0, varg))
    # ((1-a)/(1-p)) * integrate_over_g((tl_e_+mu - E_tl_e_trunc(tg)) * pdf(tg, 0, varg))

def recovery_true_heritability(hh2, a, p):
    o = compute_offset(0.5, 0.5, p)

    def cost(h2):
        h2 = max(h2, 1e-4)
        h2 = min(h2, 1-1e-4)
        varg = h2
        vare = 1. - h2

        g_mu = tl_g_mu(varg, vare, o, a, p)
        e_mu = tl_g_mu(vare, varg, o, a, p)

        g_mom2 = tl_g_mom2(varg, vare, o, a, p)
        e_mom2 = tl_g_mom2(vare, varg, o, a, p)

        ge_mom = tl_ge_mom(varg, vare, o, a, p)

        var_tg = (g_mom2 - g_mu**2)
        var_te = (e_mom2 - e_mu**2)
        var_tge = (ge_mom - g_mu*e_mu)

        # c = var_tg + var_te + 2*var_tge
        c = var_tg + var_te
        # custo = (hh2 - (var_tg + 2*var_tge)/c)**2
        custo = (hh2 - (var_tg + 2*var_tge)/c)**2
        # print h2, 'custo', custo
        return custo

    r = sp.optimize.minimize_scalar(cost, bounds=[1e-4, 1-1e-4], method='Bounded')
    h2 = r['x']
    return h2
