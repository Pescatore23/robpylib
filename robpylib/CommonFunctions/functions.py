# -*- coding: utf-8 -*-
"""
Created on Wed May 27 19:16:53 2020

@author: firo
"""

import numpy as np
import scipy as sp

def R_squared(x,y, func, *p):
    R = 0
    y_mean = np.mean(y)
    if y_mean > 0:
        SStot = np.sum((y-y_mean)**2)
        SSres = np.sum((y-func(x,*p))**2)
        R = 1 - SSres/SStot
    return R

def weibull_cdf(x, lamb, k):
    y = 1 - np.exp(-(x/lamb)**k)
    return y

def weibull(x, lamb, k):
    y = k/lamb*(x/lamb)**(k-1)*np.exp(-(x/lamb)**k)
    return y

def weibull_cdf_3(x, a, b, c):
    y = 1 - np.exp(-((x-c)/a)**b)
    return y

def weibull_3(x, a, b, c):
    y = b/a*((x-c)/a)**(b-1)*np.exp(-((x-c)/a)**b)
    return y

def log_norm_cdf(x, mu, sig):
    y = 1/2+1/2*sp.special.erf((np.log(x)-mu)/sig/np.sqrt(2))
    return y

def log_norm(x, mu, sig):
    y=1/x/sig/np.sqrt(2*np.pi)*np.exp(-(np.log(x)-mu)**2/2/sig**2)
    return y

def power_law(x, a,b,c):
    y = a*x**b+c
    return y


def exp_decay(x, a, b, c):
    y = b*np.exp(-b*x)
    return y

def exp_decay_cdf(x, a, b, c):
    y = 1-a*np.exp(-b*x)
    return y

def power_law2(x, a,b):
    y = a*x**b
    return y

def log_fit(x, a,b,c):
    y = c + a*np.log(a*x)
    return y

def gaussian_cdf(x, sig, mu):
    y = 1/2*(1+sp.special.erf((x-mu)/sig*np.sqrt(2)))
    return y

def gaussian(x, sig, mu):
    y = 1/np.sqrt(2*np.pi*sig**2)*np.exp(-(x-mu)**2/np.sqrt(2*sig**2))
    return y

def guttenberg_richter_cdf(x, a, b):
    y = 1- 10**(a-b*x)
    return y

def frechet(x, alpha, s, m):
    y = alpha/s*((x-m)/s)**(-1-alpha)*np.exp(-((x-m)/s)**-alpha)
    return y

def frechet_cdf(x, alpha, s, m):
    y = np.exp(-((x-m)/s)**-alpha)
    return y

def log_cauchy(x, sig, mu):
    y = 1/x/np.pi*sig/((np.log(x)-mu)**2+sig**2)
    return y

def log_cauchy_cdf(x, sig, mu):
    y = 1/np.pi*np.arctan2((np.log(x)-mu)/sig)+0.5
    return y

def gumbel(x, mu, beta):
    # also  sometimes called log-weibull
    # z = (x-mu)/beta
    y = 1/beta*np.exp(-((x-mu)/beta+np.exp(-(x-mu)/beta)))
    return y

def gumbel_cdf(x, mu, beta):
    y = np.exp(-np.exp(-(x-mu)/beta))
    return y

def laplace_dist(x, mu, b):
    y = 1/2/b*np.exp(-np.abs(x-mu)/b)
    return y

def gamma_scale(x, k, theta):
    # wikipedia form with theta the scale
    y = 1/sp.special.gamma(k)/theta**k*x**(k-1)*np.exp(-x/theta)
    return y

def gamma_scale_cdf(x,k, theta):
    y = 1/sp.special.gamma(k)*sp.special.gammainc(k, x/theta)
    return y

def generalized_gamma(x, a, d, p):
    y= p/a**d/sp.special.gamma(d/p)*x**(d-1)*np.exp(-(x/a)**p)
    return y

def generalized_gamma_cdf(x, a, d, p):
    y = sp.special.gammainc(d/p, (x/a)**p)/sp.special.gamma(d/p)
    return y

def universal_earthquake_times_cdf(x, xm, b, c):
    y = 1-(x/xm)**b*np.exp(-(x/xm*c))
    return y

def pareto_typ_1(x, xm, alpha):
    y = alpha*xm**alpha/x**(alpha+1)
    return y

def pareto_typ_1_cdf(x, xm, alpha):
    y = 1 - (xm/x)**alpha
    return y

def pareto_general(x, xi, mu, sig):
    # z = (x-mu)/sig
    y = 1/sig*(1+xi*(x-mu)/sig)**(-1/(xi+1))
    return y

def pareto_general_cdf(x, xi, mu, sig):
    y = 1-(1+xi*(x-mu)/sig)**(-1/xi)
    return y

def maxwell_boltzmann(x, a):
    y = np.sqrt(2/np.pi)*x**2*np.exp(-x**2/4/a**2)/a**3
    return y

def maxwell_boltzmann_cdf(x, a):
    y = sp.special.erf(x/np.sqrt(2)/a)-np.sqrt(2/np.pi)*x*np.exp(-x**2/2/a**2)/a
    return y

def chi(x, k):
    y = 1/2**(k/2-1)/sp.special.gamma(k/2)*x**(k-1)*np.exp(-x**2/2)
    return y

def chi_cdf(x, k):
    y = sp.special.gammainc(k/2,x**2/2)
    return y

def cauchy(x, gamma, x0):
    y = 1/np.pi/gamma/(1+((x-x0)/gamma)**2)
    return y

def lorentz(x, gamma, x0, A, y0):
    y= y0 + (2*A/np.pi)*(gamma/(4*(x-x0)**2+gamma**2))
    return y

def lorentz_FWHM(gamma, x0):
    FWHM = np.sqrt(x0**2+gamma*x0)-np.sqrt(x0**2-gamma*x0)
    return FWHM

