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