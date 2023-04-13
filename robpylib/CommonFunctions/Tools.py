# -*- coding: utf-8 -*-
"""
Created on Mon Feb 18 14:32:41 2019

@author: firo
"""
import numpy as np
import skimage.morphology
from scipy import ndimage as ndi
import os
from skimage import measure
import matplotlib.pyplot as plt
plt.ioff()
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from scipy.interpolate import interp1d

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

def Buterworth_like_filter(im, wc, n):
    gain = 1/(1+(im**2/wc**2)**n)
    im_filt = im*gain
    return im_filt

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



def rendering(threshold, transitions, name, outfolder, label = False, pore_object = False):
#    for now, only works with matplotlib 3.0.3
    t = threshold
    if np.any(transitions==t):
        if not os.path.exists(os.path.join(outfolder, ''.join([str(name),'.png']))):
            
            Shape = transitions.shape
            
            fig = plt.figure(frameon=False)
            ax = fig.add_subplot(111, projection='3d')
        
            dx=dy=dz=1
            ax.set_xlim(0, Shape[1]*dy)
            ax.set_ylim(0, Shape[0]*dx)
            ax.set_zlim(0, Shape[2]*dz)
            
            ax.set_xticks([])
            ax.set_yticks([])
            ax.set_zticks([])
            ax.set_aspect(np.int16(Shape[2]/Shape[0]))
        
            Stack = (transitions < t + 1 ).astype(np.uint8)*255
            Stack[transitions==0] = 0
            
            if label:
                Stack2 = Stack*pore_object
                Stack[pore_object] = 0
        
            if Stack.max() > 0:
                verts, faces, _, _ = measure.marching_cubes_lewiner(Stack,100,(1,1,1),step_size=1)
                mesh1 = Poly3DCollection(verts[faces],alpha=1, edgecolor='#27408B',linewidth = 0.001)
                mesh1.set_facecolor('#3A5FCD')
                ax.add_collection3d(mesh1)
           
            if label:
                if Stack2.max() > 0:
                    verts, faces, _, _ = measure.marching_cubes_lewiner(Stack2,100,(1,1,1),step_size=1)
                    mesh2 = Poly3DCollection(verts[faces],alpha=1, edgecolor='#8B0000',linewidth = 0.001)
                    mesh2.set_facecolor('#CD0000')
                    ax.add_collection3d(mesh2)
                
                
            ax.view_init(-10, 45)
            fig.savefig(''.join([outfolder,"/",str(name),'.png']), format='png', dpi=600, transparent=True, facecolor='w', edgecolor='w', bbox_inches='tight')
            fig.clf()
            ax.cla()
            plt.close(fig)
            
            
            
            
def weighted_ecdf(data, weight = False):
    """
    input: 1D arrays of data and corresponding weights
    sets weight to if no weights given
    """
    if not np.any(weight):
        weight = np.ones(len(data))
    
    sorting = np.argsort(data)
    x = data[sorting]
    weight = weight[sorting]
    y = np.cumsum(weight)/weight.sum()
     
    # clean duplicates
    
    x_clean = np.unique(x)
    y_clean = np.zeros(x_clean.shape)
    
    for i in range(len(x_clean)):
        y_clean[i] = y[x==x_clean[i]].max()
    return x_clean, y_clean

def cdf(ecdf_x, ecdf_y):
    f = interp1d(ecdf_x, ecdf_y, fill_value = 'extrapolate')
    return f

