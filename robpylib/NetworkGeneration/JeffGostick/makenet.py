import robpylib
import numpy as np
import skimage.morphology
from scipy.ndimage import morphology

def makehull(Stack):
    exportHull=np.zeros(Stack.shape,dtype=np.uint8)
    for z in range(Stack.shape[2]):         #calculate slicewise the convex hull, 3d would be also possible, but takes longer and is more error prone
#        convexHull=convex_hull_image(Stack[:,:,z])
#        exportHull[:,:,z]=convexHull
    
#    Stack=Stack+1
        centers=morphology.distance_transform_edt(Stack[:,:,z])>9
        
#        filled=morphology.binary_fill_holes(Stack[:,:,z])
        tighthull=np.uint8(skimage.morphology.convex_hull_image(centers))
        exportHull[:,:,z]=tighthull
    return  exportHull  






def makenet(Stack,whiteonblack=True,sigma = 0.35,r_max = 5, useOpenPNM=True):
    Stack=Stack/255   
    
    if whiteonblack == True:
        Hull = makehull(Stack)
        Stack=1-Stack
    else:
        Hull = makehull(1-Stack)
    
    
    
    Hull = makehull(Stack)
    IM=np.uint16(Stack*Hull)
    Pores,dt = RobPyLib.NetworkGeneration.JeffGostick.SNOW.porelabel(IM, sigma, r_max)
    Pores=np.uint16(Pores*Stack*Hull)
    
           
    net=RobPyLib.NetworkGeneration.JeffGostick.GETNET.extract_pore_network(im=Pores, dt=dt, useOpenPNM=useOpenPNM)
    return net, Pores
