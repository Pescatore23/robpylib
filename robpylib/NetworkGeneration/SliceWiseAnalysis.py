# -*- coding: utf-8 -*-
"""
Created on Thu Mar 15 09:40:51 2018

Second part of statistical pore space analysis. Try to merge into one file

@author: firo
"""

import numpy as np
import robpylib


def poreAnalysis(Stack, Hull ,whiteonblack=True):
    filetype=np.uint8
    Stack=Stack/255
    sigma = 0.35
    r_max = 5
    
    if whiteonblack == True:
        Stack=1-Stack
    
    Pores2D = np.zeros(Stack.shape,dtype=filetype)
    dt = np.zeros(Stack.shape,dtype=filetype)
    print('pore labeling')
    for z in range(Stack.shape[2]):
        try:
            TEST=Stack[:,:,z]*Hull[:,:,z]
            Pores2D[:,:,z],dt[:,:,z] = RobPyLib.NetworkGeneration.JeffGostick.SNOW.porelabel(TEST, sigma, r_max)
            Pores2D[:,:,z]=Pores2D[:,:,z]*Stack[:,:,z]*Hull[:,:,z]
        except Exception as e:
            print(e,'z=',z)
            pass
    
        
    net = {}
    print('network extraction')    
    for z in range(Stack.shape[2]):
        try:
            net[z]=RobPyLib.NetworkGeneration.JeffGostick.GETNET.extract_pore_network(im=Pores2D[:,:,z], dt=dt[:,:,z])
        except Exception as e:
            print(e,'z=',z)
            net[z]=[]
            pass        
    
    return net#, Pores2D



def shapefactor(net):
    indexmax=len(net)
    for z in range(indexmax):
        net[z]['pore.shape_factor']=net[z]['pore.volume']/(net[z]['pore.surface_area'])**2
        falsepores=np.where(net[z]['pore.volume']<2)
        falsepores2=np.where(net[z]['pore.shape_factor']>0.1)
        net[z]['pore.shape_factor'][falsepores]=0
        net[z]['pore.shape_factor'][falsepores2]=0
    return net


def netstatistics(net):
    netstat={}
    indexmax=len(net)
    
    netstat['pore.mean_inscribed_radius2D']=np.zeros(indexmax)
    netstat['pore.median_inscribed_radius2D']=np.zeros(indexmax)
    for z in range(indexmax):
        
        netstat['pore.mean_inscribed_radius2D'][z]=np.mean(net[z]['pore.diameter'][net[z]['pore.diameter']>2])
        netstat['pore.median_inscribed_radius2D']=np.median(net[z]['pore.diameter'][net[z]['pore.diameter']>2])
    
    netstat['pore.mean_inscribed_radius3D']=np.mean(netstat['pore.mean_inscribed_radius2D'])
    
#    netstat['pore.median_inscribed_radius3D']
    
    netstat['pore.mean_area2D']=np.zeros(indexmax)
    netstat['pore.median_area2D']=np.zeros(indexmax)
    for z in range(indexmax):
        netstat['pore.mean_area2D'][z]=np.mean(net[z]['pore.volume'][net[z]['pore.volume']>1])
        netstat['pore.median_area2D'][z]=np.median(net[z]['pore.volume'][net[z]['pore.volume']>1])
    netstat['pore.mean_area3D']=np.mean(netstat['pore.mean_area2D'])
         
    
#    netstat['pore.median_area3D'] 
    netstat['pore.mean_perimeter2D']=np.zeros(indexmax)
    netstat['pore.median_perimeter2D']=np.zeros(indexmax)
    for z in range(indexmax):
        netstat['pore.mean_perimeter2D'][z]=np.mean(net[z]['pore.surface_area'][net[z]['pore.surface_area']>1])
        netstat['pore.median_perimeter2D']=np.median(net[z]['pore.surface_area'][net[z]['pore.surface_area']>1])
    netstat['pore.mean_perimeter3D']=np.mean(netstat['pore.mean_perimeter2D'])
    

#    netstat['pore.median_perimeter3D']     
    
    netstat['pore.mean_shape_factor2D']=np.zeros(indexmax)
    netstat['pore.median_shape_factor2D']=np.zeros(indexmax)
    for z in range(indexmax):
        netstat['pore.mean_shape_factor2D'][z]=np.mean(net[z]['pore.shape_factor'][net[z]['pore.shape_factor']>0])
        netstat['pore.median_shape_factor2D']=np.median(net[z]['pore.shape_factor'][net[z]['pore.shape_factor']>0])
    
    netstat['pore.mean_shape_factor3D']=np.mean(netstat['pore.mean_shape_factor2D'])
    
#    netstat['pore.median_shape_factor3D']
    netstat['connections_per_slice']=np.zeros(indexmax)
    for z in range(indexmax):
        netstat['connections_per_slice'][z]=len(net[z]['throat.all'])
    
    netstat['connections_mean']=np.mean(netstat['connections_per_slice'])
    
    
    netstat['pore.area_hist']={}
    for z in range(indexmax):
        maxpore=np.max(net[z]['pore.volume'][net[z]['pore.volume']>1])+200
        bins=np.arange(0,maxpore,200)
        netstat['pore.area_hist'][z]=np.histogram(net[z]['pore.volume'][net[z]['pore.volume']>1],bins=bins)
        
    netstat['pore.radius_hist']={}
    for z in range(indexmax):
        maxpore=np.max(net[z]['pore.diameter'][net[z]['pore.diameter']>2])+5
        bins=np.arange(0,maxpore,5)
        netstat['pore.radius_hist'][z]=np.histogram(net[z]['pore.diameter'][net[z]['pore.diameter']>2],bins=bins)
        
    
    netstat['pore.perimeter_hist']={}
    for z in range(indexmax):
        maxpore=np.max(net[z]['pore.surface_area'][net[z]['pore.surface_area']>1])+20
        bins=np.arange(0,maxpore,20)
        netstat['pore.perimeter_hist'][z]=np.histogram(net[z]['pore.surface_area'][net[z]['pore.surface_area']>1],bins=bins)
        
    netstat['pore.shape_hist']={}
    for z in range(indexmax):
        bins=np.linspace(0,0.1,11)
        netstat['pore.shape_hist'][z]=np.histogram(net[z]['pore.shape_factor'][net[z]['pore.shape_factor']>0],bins=bins)

#    netstat['pore.shape_hist3D']
    poreshapes=net[0]['pore.shape_factor'][net[0]['pore.shape_factor']>0]
    for z in range(1,indexmax):   
        poreshapes=np.append(poreshapes, net[z]['pore.shape_factor'][net[z]['pore.shape_factor']>0])
    bins=np.linspace(0,0.1,21)
    netstat['pore.shape_hist3D']=np.histogram(poreshapes,bins)
    
    poreareas=net[0]['pore.volume'][net[0]['pore.volume']>1]
    for z in range(1,indexmax):   
        poreareas=np.append(poreareas,net[z]['pore.volume'][net[z]['pore.volume']>1])
    maxpore=np.max(poreareas)+200
    bins=np.arange(0,maxpore,200)
    netstat['pore.area_hist3D']=np.histogram(poreareas,bins)
    
    

        
    return netstat
	
def poreAnalysis2(net):
	net=shapefactor(net)
	netstat=netstatistics(net)
	return netstat
    
