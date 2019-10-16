# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import pandas as pd
#import matplotlib.pyplot as plt
import numpy as np
#import os
from scipy import ndimage

#file='C:\\Users\\firo\\Desktop\\10_050_025H3_dry.CorrelationLines.xlsx'
#
#xls=pd.ExcelFile(file)
#
##Points=pd.read_excel(xls, 'Points')
##Segments=pd.read_excel(xls, 'Segments')
#
#deg=6
#
#numfibers=10
#fit_coeff=np.zeros([deg+1,numfibers*2])


def get_coord(Points,pointids):
    length=len(pointids)
    x=np.zeros(length)
    y=np.zeros(length)
    z=np.zeros(length)
    for i in range(length):
       x[i]=int(Points['X Coord'][i])
       y[i]=int(Points['Y Coord'][i])
       z[i]=int(Points['Z Coord'][i])
    return x,y,z
       



def get_coeff(xls,numfibers=False,deg=6):
    Points=pd.read_excel(xls, 'Points')
    Segments=pd.read_excel(xls, 'Segments')
    if not numfibers: numfibers=len(Segments)
    fit_coeff_x=np.zeros([deg+1,numfibers])
    fit_coeff_y=np.zeros([deg+1,numfibers])
    for i in range(numfibers):
        pointids=Segments['Point IDs'][i]
        pointids=pointids.split(",")
        pointids=list(map(int,pointids))
        x,y,z = get_coord(Points,pointids)
        x_fit=np.polyfit(z,x,deg)
        y_fit=np.polyfit(z,y,deg)
        fit_coeff_x[:,i]=x_fit  # highest power first, eg. ax^6+bx^5+...+fx+g
        fit_coeff_y[:,i]=y_fit
    return fit_coeff_x, fit_coeff_y
        
        
        
        
def trace_mask(coeff_x, coeff_y, shape, sampling=1,R=20):
    s0=int(shape[0]*sampling)
    s1=int(shape[1]*sampling)
    s2=int(shape[2]*sampling)
    new_shape=[s0,s1,s2]
    print('get traces')
    traces=np.zeros(new_shape,dtype=np.bool)
    for z in range(new_shape[2]):
        zz=z/sampling
        Z=[zz**6,zz**5,zz**4,zz**3,zz**2,zz,1]
        for i in range(coeff_x.shape[1]):
            x0=sampling*np.sum(coeff_x[:,i]*Z)
            y0=sampling*np.sum(coeff_y[:,i]*Z)
            traces[int(x0),int(y0),int(z)]=True
    print('distance transform')
    raw_mask=ndimage.morphology.distance_transform_edt(1-traces)<R*sampling
    mask=np.zeros(shape,dtype=np.bool)
#    back to normal resolution
    print('resampling')
    for z in range(shape[2]):
        for y in range(shape[1]):
            for x in range(shape[0]):
                mask[x,y,z]=raw_mask[int(x*sampling),int(y*sampling),int(z*sampling)]
    return mask
            
    
    










#for i in range(1,numfibers+1):
#    X=np.array(list(data[''.join(['Fiber ',str(i)])][1:]))
#    Y=np.array(list(data[''.join(['Unnamed: ',str(i*3-2)])][1:]))
#    Z=np.array(list(data[''.join(['Unnamed: ',str(i*3-1)])][1:]))
#    
#    x=X[np.where(~np.isnan(X))]
#    y=Y[np.where(~np.isnan(Y))]
#    z=Z[np.where(~np.isnan(Z))]
#    
#    x_fit=np.polyfit(z,x,deg)
#    y_fit=np.polyfit(z,y,deg)
#    
#    fit_coeff[:,i*2-2]=x_fit
#    fit_coeff[:,i*2-1]=y_fit