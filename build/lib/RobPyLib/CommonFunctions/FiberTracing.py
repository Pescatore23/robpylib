"""
Some Functions used on images with labeled fibers

Input: Label image of fiber centers (for example produced by cylinder correlation + thresholding in Avizo)
        (label image: imagej disconnect particle disc 0 and reasonable volume threshold)
Output: Segmented 3D image of yarn assuming all fibers have the same diameter

Optional input: Extracted fiber edges (Canny edge in ImageJ) to consider real fiber perimeter
"""
import numpy as np
from scipy import ndimage



"""
get centroid of label image; label = greyscale value from label image
"""
def getcentroid2D(Slice,label):
    phase = np.where(Slice == label)
    X=np.uint16(np.round(np.mean(phase[0])))
    Y=np.uint16(np.round(np.mean(phase[1])))
    return X,Y
	
	
"""
create 3D image of fiber traces
"""
def tracefield(Stack):
    print('Tracing fibers...')
    shp=Stack.shape
    indexmax=shp[2]
    tracefield=np.zeros((shp[0],shp[1],shp[2]),dtype=np.uint8)
    tracefieldbin=np.zeros((shp[0],shp[1],shp[2]),dtype=np.uint8)
    searchlabels = np.unique(Stack)
    for z in range(indexmax):
        if z % 500 == 0:
            print(z,' slices traced')
        for i in range(1,searchlabels.size):
            [X,Y]=getcentroid2D(Stack[:,:,z],searchlabels[i])
            tracefield[X,Y,z]=searchlabels[i]
            tracefieldbin[X,Y,z]=1
    print('Tracing complete')
    return tracefield, tracefieldbin		

	
"""
expand traces to approximated fibers
"""
def expandtraces(tracefield,Radius):
    print('Calculating distance transform...')
    dt=ndimage.morphology.distance_transform_edt(1-tracefield)
    shp=tracefield.shape
    fibers=np.zeros((shp[0],shp[1],shp[2]),dtype=np.uint8)
    fibers=dt
    print('Expanding fiber traces to fibers...')
    fibers[np.where(dt>Radius-1)]=0
    print('Traces expanded to fibers with radius ',Radius)
    return fibers, dt