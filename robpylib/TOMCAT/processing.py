# -*- coding: utf-8 -*-
"""
Created on Fri Jan  3 07:52:00 2020

collection of slice by slice processing steps for TOMCAT data

input: each function takes a int32 2D-time-dependent stack

output: processed 2D-time-dependent stack


@author: firo
"""

import numpy as np
from pystackreg import StackReg
from skimage import transform as tf
import os
from scipy.ndimage import morphology
import robpylib
from skimage import io


#  00_intensity correction
def intensity_correction(Tstack):
    """
    Parameters
    ----------
    Tstack : uint16 3D-array [x,y,t]
    
    DESCRIPTION:
    adjusts the distorted median image brightness caused by phase artefacts
    from non-constant material absorption outsiode the FOV
    
    Returns
    -------
    uint16 3D-array
    
    """
    
    refmed = np.median(Tstack[:,:,0])
    
    for t in range(Tstack.shape[2]):
        Tstack[:,:,t] = Tstack[:,:,t] - (np.median(Tstack[:,:,t]) - refmed )
    
    Tstack[Tstack<0] = 0
    
    return Tstack


# 01 rigid registration
def get_transformation(Tstack, reference):
    """

    Parameters
        reference: register frame according to 'previous' or 'first' frame
    ----------
    Tstack : uint16 3D array [x,y,t]

    Returns
    -------
    outStack : uint16 3D array [x,y,t]
        in time registered slice
    trans_matrix :
        calculated transformation matrix

    """
    Tstack=np.transpose(Tstack,(2,0,1))
    sr = StackReg(StackReg.RIGID_BODY)
    # trans_matrix= sr.register_stack(Tstack, reference='first')
    trans_matrix= sr.register_stack(Tstack, reference = reference)
    outStack = sr.transform_stack(Tstack)
    outStack = np.uint16(outStack)
    outStack = np.transpose(outStack,(1,2,0))
    
    return outStack, trans_matrix

def apply_transformation(Tstack, trans_matrix):
    """
    only applies transformation matrix calcluated from other slices

    Parameters
    ----------
    Tstack : uint16 3D array [x,y,t]
        slice to be registered in time
    trans_matrix : 
        transformation matrix

    Returns
    -------
    outStack : uint16 3D array [x,y,t]
        in time registered slice

    """
    Tstack = np.transpose(Tstack,(2,0,1))
    outStack = np.zeros(Tstack.shape).astype(np.float)
    for t in range(Tstack.shape[0]):
        tform = tf.AffineTransform(matrix=trans_matrix[t,:,:])
        outStack[t,:,:] = tf.warp(Tstack[t,:,:],tform)
    outStack = np.uint16(outStack*2**16)
    outStack = np.transpose(outStack,(1,2,0))
    
    return outStack

def merge_transformation_matrices(matFolder):
    """
    Parameters
    ----------
    matFolder : str
        folder, where transformation matrices are stored

    Returns
    -------
    res_trans_mat : numpy array
        mean transformation matrix

    """
    names = os.listdir(matFolder)
    if 'Thumbs.db' in names: names.remove('Thumbs.db')
    test=np.load(os.path.join(matFolder,names[0]))
    mats=np.zeros([len(names),test.shape[0],test.shape[1],test.shape[2]])
    for z in range(len(names)):
        mats[z,:,:,:]=np.load(os.path.join(matFolder,names[z]))
    res_trans_mat=np.mean(mats, axis=0)
    return res_trans_mat

def register(Tstack, z, matFolder, reference = 'previous', trans_mat_flag = False, trans_mat = None, return_mat = False):
    """
    

    Parameters
    ----------
    Tstack : uint16 array [x,y,t]
        slice to be registered
    z : int
        slice number
    matFolder : str
        folder, where transformation matrices should be stored
        
    reference : str
        use 'previous' or 'first' frame as reference
    trans_mat_flag : boolean, optional
        triggers use of mean transformation matrix. The default is False.
    trans_mat : array, optional
        output of merge_transformation_matrices. The default is None.

    Returns
    -------
    Tstack : uint16 array [x,y,t]
        registered slice.

    """
    if trans_mat_flag:
        Tstack = apply_transformation(Tstack, trans_mat)
    else:
        Tstack, trans_mat = get_transformation(Tstack, reference)
        np.save(os.path.join(matFolder,''.join(['trans_mat_z_',str(z),'.npy'])),trans_mat)
    
    if return_mat:
        return Tstack, trans_mat
    else:
        return Tstack

#02_sgementation time series

def masking(last_frame, maskingthreshold = 11000):
    last_frame[last_frame < maskingthreshold] = 0
    last_frame[last_frame>0] = 1
    mask = morphology.binary_fill_holes(last_frame)
    return mask

def pore_masking(mask, fiber_folder, z):
    fibernames = os.listdir(fiber_folder)
    if 'Thumbs.db' in fibernames: fibernames.remove('Thumbs.db')
    fibernames.sort()
    fibername = fibernames[z]
    fibermask = np.uint8(io.imread(os.path.join(fiber_folder, fibername)))
    fibermask = (fibermask/fibermask.max()).astype(np.uint8)
    poremask = mask*(1-fibermask)
    return poremask
    

def get_jump_height(currpx,pos,pos2=0,receding=False):
    if not receding:
        low = np.median(currpx[max(0,pos-20):pos-2])              #"pos-20" changed to 10 because my time resolution is much coarser than Marcelo's
        hig = np.median(currpx[pos+2:min(len(currpx),pos+20)])
        jump = hig-low
    if receding:
        hig = np.median(currpx[max(pos,pos2-20):pos-2])
        low = np.median(currpx[pos2+2:min(len(currpx),pos2+20)])
        jump = low-hig
    return jump

def fft_grad_segmentation(imgs, poremask,z, waterpos=1600):
    check=6000
    if z<waterpos: check=9500
    # timg = np.zeros(np.shape(imgs), dtype='uint8')
    transitions = np.zeros([np.shape(imgs)[0],np.shape(imgs)[1]], dtype=np.uint16)
    transitions2 = transitions.copy()

#    tinitial = 10000 # initial threshold    -> deprecated (fibers are masked out before)
    jumpmin = 1500 # minimum jumpheight
    X=imgs.shape[0]
    Y=imgs.shape[1]
    for pX in range(X):
        for pY in range(Y):
#            a=1
#            check if pixel is actually in the relevant pore space
            if poremask[pX,pY] >0:
                # current pixel time series
                currpx = imgs[pX,pY,:].astype(dtype='float')                
                s_filtered = robpylib.CommonFunctions.Tools.fourier_filter(currpx,band=0.1,dt=1.2)
                
#                # find where maximum gradient occurs
                g_filtered=np.gradient(s_filtered)

                pos = np.argmax(g_filtered)-1                
                jump = get_jump_height(currpx,pos)
    #            
                pos2 = np.argmin(g_filtered)-1
                jump2 = get_jump_height(currpx,pos,pos2=pos2,receding=True)
                
                if jump > jumpmin: # there is a transition; careful, water can also receed!! (can clearly be seen in rare cases)
                    # timg[pX,pY,:pos] = 0
#                    double check for noise
                    if np.median(currpx[min(pos+10,len(currpx)):min(pos+25,len(currpx))])>check:#7500:#9500:
#                    if np.median(currpx[min(pos+5,len(currpx)):min(pos+10,len(currpx))])>9500:
                        # timg[pX,pY,pos:] = 255
                        transitions[pX,pY] = pos
                    # else: timg[pX,pY,pos:] = 0
                    
                if jump2 < -2000 and pos2>pos and z<waterpos:
                    # timg[pX,pY,pos2:] = 0
                    transitions2[pX,pY] = pos2
    return transitions, transitions2


def segmentation(Tstack, fiber_folder, z):
    mask = masking(Tstack[:,:,-1])
    poremask = pore_masking(mask, fiber_folder, z)
    transitions, transitions2 = fft_grad_segmentation(Tstack, poremask, z)
    return transitions, transitions2
