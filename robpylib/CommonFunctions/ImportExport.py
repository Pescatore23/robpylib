"""
Some basic functions to import and export tomographic data"
"""
import os
import numpy as np
from skimage import io
import imageio
from astropy.io import fits
from datetime import datetime


"""
read testimage
"""
def readTEST(filemask,ext,index0='0005'):
    TESTimage = io.imread(''.join([filemask,index0,ext]))
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


def ReadStackNew(folder, filetype=np.uint16, track=True, time_request = False):
    imlist=os.listdir(folder)
    if 'Thumbs.db' in imlist: imlist.remove('Thumbs.db')
    stacksize=len(imlist)
    testim=io.imread(os.path.join(folder+'/'+imlist[0]))
    shp=np.shape(testim)
    Stack = np.zeros([shp[0],shp[1],stacksize],dtype=filetype)
    z=0
    timestamps = np.zeros(len(imlist))
    for im in imlist:
        if track==True and z % 500 == 0:
            print(z,' slices loaded')
        img = io.imread(''.join([folder,"/",im]))
        if time_request: timestamps[z] = os.path.getmtime(''.join([folder,"/",im]))
        Stack[:,:,z] = img
        z=z+1
    if track == True: print(z,' slices loaded')
#    imlist=imlist[imlist!='Thumbs.db']
    if time_request:
        return Stack, imlist, timestamps    
    else:
        return Stack, imlist



def ReadFitsStack(folder, filetype=np.uint16, track=True):
    imlist=os.listdir(folder)
    if 'Thumbs.db' in imlist: imlist.remove('Thumbs.db')
    stacksize=len(imlist)
    test_im= fits.open(os.path.join(folder,imlist[0]))
    testim=test_im[0].data
    timestamp=test_im[0].header['DATE']
    date_time_0=datetime.strptime(''.join([timestamp[:4],timestamp[5:7],
                                           timestamp[8:10],timestamp[11:13],timestamp[14:16],
                                           timestamp[17:19]]), '%Y' '%m' '%d' '%H' '%M' '%S')
    shp=np.shape(testim)
    Stack = np.zeros([shp[0],shp[1],stacksize],dtype=filetype)
    z=0
    time_list=np.zeros(stacksize)
    for im in imlist:
        if track==True and z % 500 == 0:
            print(z,' slices loaded')
        img = fits.open(''.join([folder,"/",im]))
        timestamp=img[0].header['DATE']
        date_time=datetime.strptime(''.join([timestamp[:4],timestamp[5:7],
                                           timestamp[8:10],timestamp[11:13],timestamp[14:16],
                                           timestamp[17:19]]), '%Y' '%m' '%d' '%H' '%M' '%S')
        time_list[z]=(date_time-date_time_0).total_seconds()
        Stack[:,:,z] = img[0].data
        z=z+1
    if track == True: print(z,' slices loaded')
#    imlist=imlist[imlist!='Thumbs.db']
    return Stack, imlist, time_list


def ReadFloatTif(folder, filetype=np.float32, track=True):
    imlist=os.listdir(folder)
    if 'Thumbs.db' in imlist: imlist.remove('Thumbs.db')
    stacksize=len(imlist)
    testim=io.imread(os.path.join(folder+'/'+imlist[0]))
    shp=np.shape(testim)
    Stack = np.zeros([shp[0],shp[1],stacksize],dtype=filetype)
    z=0
    for im in imlist:
        if track==True and z % 500 == 0:
            print(z,' slices loaded')
        img=imageio.imread(''.join([folder,"/",im]))
        Stack[:,:,z] = img
        z=z+1
    if track == True: print(z,' slices loaded')
    return Stack, imlist

"""
Load time series of one slice
"""


#def OpenTimeStack(folder, imgNumber, orient='t_z'):
#    """open all images in folder's subfolder corresponding to imgNumber, taken and modified from Marcelo"""
#    
#    names=[]
#    scans=[]
#    
#    subfolders = [d for d in os.listdir(folder) if os.path.isdir(os.path.join(folder, d))]
#    testfolder = folder + "/" + subfolders[0]
#    test=os.listdir(folder + "/" + subfolders[0])[0]
#    shape = readTEST(''.join([testfolder,'/',test]),ext='',index0='')
#    
#    t=0
#    if orient=='t_z':
#        Tstack=np.zeros((shape[0],shape[1],len(subfolders)),np.uint16)
#        for subfolder in subfolders:
#            imgs = os.listdir(folder + "/" + subfolder)
#            if 'Thumbs.db' in imgs: imgs.remove('Thumbs.db')
#            imgs.sort()
#            if len(imgs) >= imgNumber:
#                im=io.imread(folder+"/"+subfolder + "/"+imgs[imgNumber])
#                Tstack[:,:,t]=im
#                names.append(imgs[imgNumber])
#                scans.append(subfolder)
#            t=t+1
#    if orient=='t_x':
#        Tstack=np.zeros((len(subfolders),shape[0],shape[1]),np.uint16)
#        for subfolder in subfolders:
#            imgs = os.listdir(folder + "/" + subfolder)
#            if 'Thumbs.db' in imgs: imgs.remove('Thumbs.db')
#            imgs.sort()
#            if len(imgs) >= imgNumber:
#                im=io.imread(folder+"/"+subfolder + "/"+imgs[imgNumber])
#                Tstack[t,:,:]=im
#                names.append(imgs[imgNumber])
#                scans.append(subfolder)
#            t=t+1        
#    
#    return Tstack, names, scans
#            
#    return test


def OpenTimeStack(folder, imgNumber, orient='t_z'):
    
    names=[]
    scans=[]
    
    subfolders = [d for d in os.listdir(folder) if os.path.isdir(os.path.join(folder, d))]
    
    testfolder = folder + "/" + subfolders[0]
    folder_content=os.listdir(folder + "/" + subfolders[0])
    if 'Thumbs.db' in folder_content: folder_content.remove('Thumbs.db')
    folder_content.sort()
    name_shape=os.listdir(os.path.join(folder,subfolders[0]))[imgNumber]
    test=os.path.join(testfolder,name_shape)
    im_old=io.imread(test)
    shape = im_old.shape
    
    t=0   
    
    if orient=='t_z':
        Tstack=np.zeros((shape[0],shape[1],len(subfolders)),np.uint16)
    if orient=='t_x':
        Tstack=np.zeros((len(subfolders),shape[0],shape[1]),np.uint16)
        
    for subfolder in subfolders:
        time_id=subfolder[-5:]
        name_shape=list(name_shape)
        name_shape[-24:-19]=time_id
        name_shape=''.join(name_shape)
        try:
            im=io.imread(os.path.join(folder,subfolder,name_shape))
            im_old=im.copy()
        except:
            im=im_old.copy()
        
        names.append(name_shape)
        scans.append(subfolder)
        
        if orient=='t_z':
            Tstack[:,:,t]=im
        if orient=='t_x':
            Tstack[t,:,:]=im
        t=t+1
        
    return Tstack, names, scans
        
        

"""
Load single image
"""

def ReadImage(filemask,ext):
    image = io.imread(''.join([filemask,ext]))
    return image
	
    
"""
write single image
"""

def WriteImage(foldername,name,path,image):
    owd=os.getcwd()
    folderpath=''.join([path,'\\',foldername])
    if not os.path.exists(folderpath):
        os.makedirs(folderpath)
    os.chdir(folderpath)
    imageio.imsave(''.join([name,'.tif']),image)
    print('Image saved')
    os.chdir(owd)    
 
"""
write image stack
""" 
     
    
def WriteStack(foldername,name,path,Stack):
#    print('Writing to file...')
    owd=os.getcwd()
    folderpath=''.join([path,'\\',foldername])
    if not os.path.exists(folderpath):
        os.makedirs(folderpath)
    os.chdir(folderpath)
    shp=Stack.shape
    indexmax=shp[2]
    index=makeindex(indexmax)
    for z in range(indexmax):
#        if z % 500 == 0:
#            print(z,' slices stored')
        imageio.imsave(''.join([name,index[z],'.tif']), Stack[:,:,z])
    os.chdir(owd)
    


def WriteStackNew(outfolder,imlist,Stack, track=True):

    if not os.path.exists(outfolder):
        os.makedirs(outfolder)
    z=0
    for im in imlist:
        imageio.imsave(''.join([outfolder,"\\",im]), Stack[:,:,z])
        z=z+1


    
"""
write time series stack
"""

def WriteTimeSeries(folder,Tstack, names, scans, orient='t_z'):
    if orient=='t_z':
        for t in range(len(scans)):
            if not os.path.exists(os.path.join(folder+"/"+scans[t])):
                os.makedirs(os.path.join(folder+"/"+scans[t]))
            imageio.imsave(folder+"/"+scans[t]+"/"+names[t],Tstack[:,:,t])
    if orient=='t_x':
        for t in range(len(scans)):
            if not os.path.exists(os.path.join(folder+"/"+scans[t])):
                os.makedirs(os.path.join(folder+"/"+scans[t]))
            imageio.imsave(folder+"/"+scans[t]+"/"+names[t],Tstack[t,:,:])
        
        
        
        
        
        
"""
samplefolderlist for TOMCAT experiment I (Summer 2018)    
"""


def newRecoList(mountlocation):
    newRecoPath=''.join([mountlocation,"newReco"])   #mounlocation i.e. "T:\\" on windows or /mnt/t/  on linux or whatever
    disks=os.listdir(newRecoPath)
    newsamples=[]
    for disk in disks:
        newsamples.append(os.listdir(os.path.join(newRecoPath,disk)))
    
    newsamples2 = [item for sublist in newsamples for item in sublist]
    newsamples2.append('Robert')
    newsamples2.append('_hide')
    newsamples2.append('10_050_025H2_wet')
    newsamples2.append('10_200_300H2_01_b')
    newsamples2.append('32_200_025H2_cont')
    return newsamples2
    


def makesamplefolderlist(mount):
    samples=[]
    
    newsamples=newRecoList(mount)
    
    
#    disk1
    print('disk1')
    foldercontent=os.listdir(os.path.join(mount,'disk1'))
    
    for sample in foldercontent:
        if sample in newsamples: continue
        
        path=os.path.join(mount,'disk1',sample,'01a_weka_segmented_dry','classified')
        samples.append([path,sample])
        print(sample, path)
        
#    diks2
    print('disk2')
    foldercontent=os.listdir(os.path.join(mount,'disk2'))
    for sample in foldercontent:
        if sample in newsamples: continue
        
        path=os.path.join(mount,'disk2',sample,'01a_weka_segmented_dry','classified')
        samples.append([path,sample])
        print(sample, path)
        
#   newReco
    print('newReco')
    topfoldercontent=os.listdir(os.path.join(mount,'newReco'))
    for folder in topfoldercontent:
        foldercontent=os.listdir(os.path.join(mount,'newReco',folder))
        for sample in foldercontent:
            if sample == '03_500_100H1': continue
            if sample == '32_050_025_H1_cont': continue
            path=os.path.join(mount,'newReco',folder,sample,'01a_weka_segmented_dry','classified')
            if not os.path.exists(path): continue
            samples.append([path,sample])
            print(sample, path)
    
    return samples

"""
get parameters from sample name TOMCAT
"""

def get_yarn_properties(sample):  #sample = str of sample code
    num_fibers=int(sample[:2])
    twist=int(sample[3:6]) #tpm
    tension=int(sample[7:10])/10 #mN/tex
    return num_fibers, twist, tension


def get_interlace_properties(sample): 
    m1=2.1462 #g
    m2=1.0506
    m3=0.8893
    m4=0.4554
    m5=0.3313
    m6=0.2316
    m7=0.1287
    m8=0.0527
    m=[m1,m2,m3,m4,m5,m6,m7,m8]
    g=9.81 #N/kg=mN/g
    m_index=int(sample[3])
    m_app=m[m_index-1]
    
    linear_dens=int(sample[5:7])   #dtex
    if linear_dens == 33:
        num_fibers=16
    else:
        num_fibers=20
    
    twist=int(sample[8:11])   #tpm
    
    tension=m_app*g/linear_dens*10 #mN/tex
    
    return num_fibers, twist, tension
    