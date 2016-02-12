import numpy as np
from numpy import dot, sqrt
from scipy import special
import scipy as sp
# import scipy.integrate
from gwarped.util.norm import logpdf
from gwarped.util.norm import pdf

def logsf(x):
    return special.log_ndtr(-x)

def logcdf(x):
    return special.log_ndtr(x)

def cdf(x):
    return special.ndtr(x)

# def pdf(x):
    # return special.ndtr(x)

def generate_mafs(p):
    mafs = np.random.rand(p) * 0.45 + 0.05
    return mafs

def generate_snps(mafs, n, p):
    G = np.empty((n, p))
    for i in xrange(p):
        binom = sp.stats.binom(2, mafs[i])
        G[:,i] = binom.rvs(n)
    return G

def cc_selection(y, siz):
    ncontrols = siz / 2
    ncases = siz - ncontrols
    controls = np.where(y == 0.)[0]
    assert len(controls) >= ncontrols
    cases = np.where(y == 1.)[0]
    assert len(cases) >= ncases
    controls = controls[:ncontrols]
    cases = cases[:ncases]
    return np.concatenate((controls, cases))

def create_stuff(varg, G, n, nsnps, offset):
    vare = 1. - varg
    u = np.random.randn(nsnps) * sqrt(varg / nsnps)
    g = dot(G, u)
    e = np.random.randn(n) * sqrt(vare)
    z = offset + g + e
    y = np.zeros(n)
    y[z > 0.] = 1.
    return z, g, e, y

def sample_tge(varg, vare, offset, ascertainment):
    case = np.random.rand() < ascertainment
    while True:
        g = np.random.randn(1) * np.sqrt(varg)
        e = np.random.randn(1) * np.sqrt(vare)
        if case:
            if (g+e) > offset:
                return (g[0], e[0])
        elif (g+e) <= offset:
            return (g[0], e[0])

def compute_offset(varg, vare, prevalence):
    vg = np.sqrt(varg)
    ve = np.sqrt(vare)
    ic = sp.stats.norm.isf(prevalence)
    offset = ic*ve*np.sqrt(1+varg/vare)
    return offset

def E_tl_cdf(varg, vare, o):
    vg = np.sqrt(varg)
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


def recovery_true_heritability_test(hh2, a, p):
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
    print '%0.3f --> %0.3f' % (hh2, r['x'])
    from limix_util.h2 import h2_correct
    print '%0.3f --> %0.3f' % (hh2, h2_correct(hh2, p, a))

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

def recovery_true_heritability_standard(hh2, a, p):
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

        c = var_tg + var_te + 2*var_tge
        # c = var_tg + var_te
        custo = (hh2 - (var_tg + 2*var_tge)/c)**2
        # custo = (hh2 - (var_tg + 2*var_tge)/c)**2
        # print h2, 'custo', custo
        return custo

    r = sp.optimize.minimize_scalar(cost, bounds=[1e-4, 1-1e-4], method='Bounded')
    h2 = r['x']
    return h2

def recovery_true_heritability_nh3(hh2, a, p):
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

        c = var_tg + var_te + 2*var_tge
        # c = var_tg + var_te
        custo = (hh2 - (var_tg + 2*var_tge)/c)**2
        # custo = (hh2 - (var_tg + 2*var_tge)/c)**2
        # print h2, 'custo', custo
        return custo

    r = sp.optimize.minimize_scalar(cost, bounds=[1e-4, 1-1e-4], method='Bounded')
    h2 = r['x']
    return h2


if __name__ == '__main__':
    # import sys
    # varg = 0.2
    # vare = 0.8
    hh2 = 0.67
    a = 0.5
    p = 0.1

    recovery_true_heritability_test(hh2, a, p)
    #
    # o = compute_offset(varg, vare, p)
    # g_mu = tl_g_mu(varg, vare, o, a, p)
    # e_mu = tl_g_mu(vare, varg, o, a, p)
    #
    # g_mom2 = tl_g_mom2(varg, vare, o, a, p)
    # e_mom2 = tl_g_mom2(vare, varg, o, a, p)
    #
    # ge_mom = tl_ge_mom(varg, vare, o, a, p)
    #
    # samples = [sample_tge(varg, vare, o, a) for i in xrange(500000)]
    # tg = [s[0] for s in samples]
    # te = [s[1] for s in samples]
    #
    # mu_tg = np.mean(tg)
    # var_tg = np.var(tg)
    #
    # mu_te = np.mean(te)
    # var_te = np.var(te)
    #
    # cov_tge = np.cov(tg, te)[0,1]
    #
    # print g_mu, e_mu, (g_mom2 - g_mu**2), (e_mom2 - e_mu**2), (ge_mom - g_mu*e_mu)
    # print mu_tg, mu_te, var_tg, var_te, cov_tge
    #
    # # mom2_tg = var_tg + mu_tg*mu_tg
    #
    # # print cov_tge + mu_tg*mu_te
    # # print mom2_tg
    # # print np.mean(tg), np.mean(te)
