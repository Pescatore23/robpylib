# -*- coding: utf-8 -*-
"""
Created on Wed Nov 13 15:48:21 2019

@author: firo
"""

#import scipy as sp
import scipy.ndimage as ndimage
from skimage.morphology import disk, cube
import numpy as np
from skimage import measure
#from dask.distributed import Client
#import joblib
from joblib import Parallel, delayed
import multiprocessing as mp

#clientlocation = '152.88.86.193:8786'    #<scheduler-ip>:<port>

#chunksize = 35 * 128 # needs to be multiple of 128Mb (default chunk size), but this is just an upper limit. Probably not that strict to use multiples
#chunkstring = ''.join([str(chunksize), 'MiB'])

#client = Client(processes=False)

#dask.config.set({'array.chunk_size': chunkstring}) 
#client = Client(clientlocation, processes = False)

# num_cores = mp.cpu_count()

def extend_bounding_box(s, shape, pad=3):
    a = []
    for i, dim in zip(s, shape):
        start = 0
        stop = dim
        if i.start - pad >= 0:
            start = i.start - pad
        if i.stop + pad < dim:
            stop = i.stop + pad
        a.append(slice(start, stop, None))
    return a

def label_function(struct, pore_object, sub_dt, bounding_box, label):
    pore_im = pore_object == label
    im_w_throats = ndimage.binary_dilation(input = pore_im, structure = struct(3))
    im_w_throats = im_w_throats*pore_object
    n_labels = np.unique(im_w_throats)[1:]
    t_params = []
    for n_label in n_labels: #check neighbor labels for connections, later take the mean of the
#                               property of throat A->B and B->A as throat property A-B
           if n_label == label: continue
#           FIXME: what about multiple connections between two pores --> do a find objects and then make them as extra throats
#           what about inverse throats? can you match them again? maybe via position (com) --> seems to be fixed
           throat_im = (im_w_throats == n_label).astype(np.uint8)
           
           throat_im = measure.label(throat_im, connectivity=3)
           
           ids = np.unique(throat_im)[1:]
           
           for idx in ids:
               sub_throat_im = throat_im == idx
               throat_bb = ndimage.find_objects(sub_throat_im)[0]
               
               extent = [throat_bb[0].stop-throat_bb[0].start, throat_bb[1].stop-throat_bb[1].start, throat_bb[2].stop-throat_bb[2].start]
               conn = [label, n_label]
               throat = np.where(sub_throat_im)
               rad_inscribed = sub_dt[throat].max()
               perimeter = np.count_nonzero(sub_dt[throat]<2)
               area = len(throat[0])     #fairly accurate by counting the number of pixels inside the throat
               if perimeter >0:
                   shape_factor = area/perimeter**2
               else:
                   shape_factor = 0
               com = ndimage.measurements.center_of_mass(sub_throat_im)
               com = com + np.array([bounding_box[0].start, bounding_box[1].start, bounding_box[2].start]) 
               
               inertia_tensor = measure._moments.inertia_tensor(sub_throat_im)
               in_tens_eig = np.linalg.eigvalsh(inertia_tensor)
                
               major_axis = 4*np.sqrt(np.abs(in_tens_eig[-1]))
               minor_axis = 4*np.sqrt(np.abs(in_tens_eig[0]))
                
               aspect_ratio = major_axis/minor_axis
               
               t_param = [conn[0], conn[1], idx, extent[0], extent[1], extent[2], rad_inscribed, perimeter, area, shape_factor, com[0], com[1], com[2], major_axis, minor_axis, aspect_ratio]
#               t_param = np.array(t_param)
               t_params.append(t_param)
    t_params = np.array(t_params)
    return t_params

def extract_throat_list(label_matrix, labels, dt = None): 
    """
    inspired by Jeff Gostick's GETNET
    
    extracts a list of directed throats connecting pores i->j including a few throat parameters
    undirected network i-j needs to be calculated in a second step
    """
    im = label_matrix
    
    struct = cube  #FIXME: ball does not work as you would think (anisotropic expansion)
    if im.ndim == 2:
        struct = disk
    
    if dt == None:
        dt = ndimage.distance_transform_edt(im>0)
    
    crude_pores = ndimage.find_objects(im)
#    throw out None-entries (counterintuitive behavior of find_objects)
    pores = []
    for pore in crude_pores:
        if not pore == None:
            pores.append(pore)
    crude_pores = None
    
    shape = im.shape
    bounding_boxes = []
    for pore in pores:
        bounding_boxes.append(extend_bounding_box(pore, shape))
    
#    num_cores = 6
#    with joblib.parallel_backend('dask'):
    t_params_raw = Parallel(n_jobs=num_cores)(delayed(label_function)(struct, im[bounding_box], dt[bounding_box], bounding_box, label) for (bounding_box, label) in zip(bounding_boxes, labels))
    
    parameters = ['pore_1', 'pore_2', 'index', 'x_extent', 'y_extent', 'z_extent', 'inscribed_radius', 'perimeter', 'area',
                     'shape_factor', 'X', 'Y', 'Z', 'major_axis', 'minor_axis', 'aspect_ratio']
#    clear out empty objects
    t_params = []
    for i in range(len(t_params_raw)):
        if len(t_params_raw[i]) > 0:
            t_params.append(t_params_raw[i])
    
    t_params = np.concatenate(t_params, axis = 0)
    return t_params, parameters

#           get activation time by taking the median step value around throat COM
           
def make_network_undirected(directed_network):
    t_params = directed_network
    undirected_network = np.zeros([int(t_params.shape[0]/2),  t_params.shape[1]])
    t_conns = np.uint16(t_params[:,:2])

    c=0
    for i in range(t_conns.shape[0]):
        p1 = t_conns[i,0]
        p2 = t_conns[i,1]
        if not p2>p1: continue
        line1 = np.where(t_conns[:,0] == p2)[0]
        line2 = np.where(t_conns[:,1] == p1)[0]
        line = np.intersect1d(line1, line2)
#        FIXME len(line) == 0, can't be right, error happens already earlier, this part should be fine
        com1 = t_params[i,10:13]
#       loop over connections and match throats via COM or FIXME find best match without loop
        comdiffref = 100000000
        for j in range(len(line)):
            com2 = t_params[line[j],10:13]
#            comdiff = np.abs((com1**2-com2**2)).sum()  #<-- I think this is wrong, use next line
            comdiff = ((com1-com2)**2).sum()
            if comdiff < comdiffref:
                jc = line[j]
                comdiffref = comdiff.copy()
        vals1 = t_params[i, 2:]
        vals2 = t_params[jc, 2:]
        vals = (vals1 + vals2)/2
        undirected_network[c, 2:] = vals
        undirected_network[c, :2] = [p1, p2]
        c=c+1
    undirected_network[np.isnan(undirected_network)] = 0
    undirected_network[np.isinf(undirected_network)] = 0
    return undirected_network   


def label_image_by_horizontal_slices(image, thickness=50):
    """
    takes a pore space image (0 for solid, >0 for pores) and creates a label
    image by cutting slices (thickness) and finding separated objects in slices
    """
    
    num_slices = int(image.shape[2]/thickness)+1
    
    label_image = np.zeros(image.shape, dtype = np.uint32)
    
    max_label = 0
    
#    if needed, make it parallel
    for slc in range(num_slices):
        start = slc*thickness
        if start > image.shape[2]: continue
        end = (slc+1)*thickness
        if  end > image.shape[2]: end = image.shape[2]
        sub_image = image[:,:,start:end]
        sub_label = ndimage.measurements.label(sub_image)[0]   
        
#        compose label image, needs eventually adaption to parallelisation
        sub_label[sub_label>0] = sub_label[sub_label>0] + max_label
        max_label = sub_label.max()
        label_image[:,:,start:end] = sub_label
        
    return label_image
 

def neighbour_search(label, im, struct=cube):
    mask = im==label
    mask = ndimage.binary_dilation(input = mask, structure = struct(3))
    neighbours = np.unique(im[mask])[1:]
    return neighbours      

def adjacency_matrix(label_im, num_cores=4):
    size = label_im.max()+1
    labels = np.unique(label_im)[1:]
    adj_mat = np.zeros([size,size], dtype=np.bool)
 
    results = Parallel(n_jobs=num_cores)(delayed(neighbour_search)(label, label_im) for label in labels)
    
    for (label, result) in zip(labels, results):
        adj_mat[label, result] = True
    
    # make sure that matrix is symmetric (as it should be)
    adj_mat = np.maximum(adj_mat, adj_mat.transpose())
    
    return adj_mat

#test           
           
           
#import xarray as xr
#
#path = r"W:\Robert_TOMCAT_3_netcdf4_archives\processed_1200_dry_seg_aniso_sep_good_samples\dyn_data_T3_025_3_III.nc"
#
#data = xr.load_dataset(path)
#
#label_matrix = data['label_matrix'].data
#labels = data['label'].data
## clean label_matrix from irrelevant labels (noise)
#for i in range(1, label_matrix.max()+1):
#    if not i in labels:
#        label_matrix[label_matrix == i] = 0
#
#directed_network, parameters = extract_throat_list(label_matrix, labels)
#
#undirected_network = make_network_undirected(directed_network)
       