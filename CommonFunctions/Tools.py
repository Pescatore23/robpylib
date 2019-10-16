# -*- coding: utf-8 -*-
"""
Created on Mon Feb 18 14:32:41 2019

@author: firo
"""
import numpy as np
import skimage.morphology
from scipy import ndimage as ndi

def low_pass_rule(x,freq,band):
    if abs(freq) > band:
        return 0
    else:
        return x
    
def high_pass_rule(x,freq,band):
    if abs(freq) < band:
        return 0
    else:
        return x
    
def band_pass_rule(x,freq,band1,band2):
    band=[band1,band2]
    np.sort(band)
    if abs(freq) > band[0] or abs(freq) < band[1]:
        return 0
    else:
        return x
    
def fourier_filter(signal,band=0.1,dt=1,band2=0.2, filtertype='low'):
    F = np.fft.fft(signal)
    f = np.fft.fftfreq(len(F),dt)
    if filtertype=='low':
        F_filtered = np.array([low_pass_rule(x,freq,band) for x,freq in zip(F,f)])
    if filtertype=='high':
        F_filtered = np.array([high_pass_rule(x,freq,band) for x,freq in zip(F,f)])
    if filtertype=='band':
        F_filtered = np.array([band_pass_rule(x,freq,band,band2) for x,freq in zip(F,f)])
    s_filtered = np.fft.ifft(F_filtered)
    return s_filtered

def fourier_spectrum(signal, dt=1):
    ps=np.abs(np.fft.fft(signal))**2
    freqs=np.fft.fftfreq(signal.size,1)
    idx=np.argsort(freqs)
    ps=ps[idx]
    freqs=freqs[idx]
    return [freqs,ps]

def filter_outliers(data, radius=5, th=0.1):    #only 1D
    for i in range(len(data)):
        left=i-radius
        while left<0:
            left=left+1
        right=i+radius
        while right >=len(data):
            right=right-1
        med=np.median(data[left:right])
        if np.abs(data[i]-med)/med>th:
            data[i]=med
    return data

def capillary_number(v, mu=1, gamma=72.6): #water, mu[mPas] gamma[dyne/cm = mN/m]
    Ca=mu*v/gamma
    return Ca





def interface_tracker(binary, solid=True, dist=1):
#    returns interface pixels of binary image (pixels draping the true-phase)
#    ball = skimage.morphology.ball
#    if len(binary.shape)==2:
#        ball = skimage.morphology.disk
#    struct=ball(1)
#    if solid: struct=ball(1.5)
#    dilated=skimage.morphology.dilation(binary,selem=struct)
#    interface=np.bitwise_xor(dilated,binary)
    
    interface = ndi.distance_transform_cdt(binary)==dist

    return interface


def cylinder_coords(x, y, x0=0, y0=0):
    r = np.sqrt( (x-x0)**2 + (y-y0)**2)
    phi = np.arctan2(y-y0, x-x0)
    return r, phi
