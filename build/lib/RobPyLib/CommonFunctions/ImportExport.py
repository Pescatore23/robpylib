"""
Some basic functions to import and export tomographic data"
"""
import os
import numpy as np
from skimage import io
import scipy

"""
read testimage
"""
def readTEST(filemask,ext):
    TESTimage = io.imread(''.join([filemask,'0000',ext]))
    shape=TESTimage.shape
    return shape
	
	
	
"""
create image index (maximal 4 digits, adjust if necessary)
"""
def makeindex(indexmax):
    index=[None]*indexmax
    for z in range(indexmax):
        index[z]=z
    index=[str(item).zfill(4) for item in index]
    return index
	
	
"""
Load image stack
"""
def ReadStack(filemask,ext,filetype,indexmax):
    shape=readTEST(filemask,ext)
    index=makeindex(indexmax)
    Stack = np.zeros((shape[0],shape[1],indexmax),dtype=filetype)
    print('Loading stack...')
    for z in range(indexmax):
        if z % 500 == 0:
            print(z,' slices loaded')
        img = io.imread(''.join([filemask,index[z],ext]))
        Stack[:,:,z] = img
    print('Stack loaded')
    return Stack
	
"""
write image stack
"""
def WriteStack(foldername,name,path,Stack):
    print('Writing to file...')
    owd=os.getcwd()
    folderpath=''.join([path,'\\',foldername])
    if not os.path.exists(folderpath):
        os.makedirs(folderpath)
    os.chdir(folderpath)
    shp=Stack.shape
    indexmax=shp[2]
    index=makeindex(indexmax)
    for z in range(indexmax):
        if z % 500 == 0:
            print(z,' slices stored')
        scipy.misc.imsave(''.join([name,index[z],'.tif']), Stack[:,:,z])
    print('Images saved')
    os.chdir(owd)
    
"""
write single image"
"""

def WriteImage(foldername,name,path,image):
    owd=os.getcwd()
    folderpath=''.join([path,'\\',foldername])
    if not os.path.exists(folderpath):
        os.makedirs(folderpath)
    os.chdir(folderpath)
    scipy.misc.imsave(''.join([name,'.tif']),image)
    print('Image saved')
    os.chdir(owd)    