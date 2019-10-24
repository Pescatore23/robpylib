r'''
GETNET: Pore network extraction from SNOW segmented image
Copyright (C) 2017 Jeff Gostick

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

import scipy as sp
import scipy.ndimage as spim
#import OpenPNM
from skimage.morphology import disk, ball, square, cube
#from skimage.morphology import ball

def extend_slice(s, shape, pad=1):
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


def extract_pore_network(im, dt=None, voxel_size=1, useOpenPNM=False):
#    print('_'*60)
#    print('Extracting pore and throat information from image')
#    struct=ball
    struct=cube
    if im.ndim == 2:
#        cube = square
        struct = disk
    if ~sp.any(im == 0):
        raise Exception('The received image has no solid phase (0\'s)')
    if dt is None:
        dt = spim.distance_transform_edt(im > 0)
        dt = spim.gaussian_filter(input=dt, sigma=0.5)
    # Get 'slices' into im for each pore region
    slices = spim.find_objects(im)
    # Initialize arrays
    Ps = sp.arange(1, sp.amax(im)+1)
    Np = sp.size(Ps)
    p_coords = sp.zeros((Np, im.ndim), dtype=float)
    p_volume = sp.zeros((Np,), dtype=float)
    p_dia_local = sp.zeros((Np,), dtype=float)
    p_dia_global = sp.zeros((Np,), dtype=float)
    p_label = sp.zeros((Np,), dtype=int)
    p_area_surf = sp.zeros((Np,), dtype=int)
    p_area_solid = sp.zeros((Np,), dtype=int)
    t_conns = []
    t_dia_inscribed = []
    t_area = []
    t_perimeter = []
    t_coords = []
    # Start extracting size information for pores and throats
    for i in Ps:
        pore = i - 1
        if not im.any() == i: continue
        s = extend_slice(slices[pore], im.shape)
        if not len(s)>0: continue
        sub_im = im[s]
        sub_dt = dt[s]
        pore_im = sub_im == i
        pore_dt = spim.distance_transform_edt(sp.pad(pore_im, pad_width=1,
                                                     mode='constant'))
        s_offset = sp.array([i.start for i in s])
        p_label[pore] = i
        p_coords[pore, :] = spim.center_of_mass(pore_im) + s_offset
        p_volume[pore] = sp.sum(pore_im)
        p_dia_local[pore] = 2*sp.amax(pore_dt)
        p_dia_global[pore] = 2*sp.amax(sub_dt)
        p_area_surf[pore] = sp.sum(pore_dt == 1)
        p_area_solid[pore] = sp.sum(sub_dt == 1)
        im_w_throats = spim.binary_dilation(input=pore_im, structure=struct(3))
        im_w_throats = im_w_throats*sub_im
        Pn = sp.unique(im_w_throats)[1:] - 1
        for j in Pn:
            if j > pore:
                t_conns.append([pore, j])
                vx = sp.where(im_w_throats == (j + 1))
                t_dia_inscribed.append(2*sp.amax(sub_dt[vx]))
                t_perimeter.append(sp.sum(sub_dt[vx] < 2))
                t_area.append(sp.size(vx[0]))
                t_inds = tuple([i+j for i, j in zip(vx, s_offset)])
                temp = sp.where(dt[t_inds] == sp.amax(dt[t_inds]))[0][0]
                if im.ndim == 2:
                    t_coords.append(tuple((t_inds[0][temp],
                                           t_inds[1][temp])))
                else:
                    t_coords.append(tuple((t_inds[0][temp],
                                           t_inds[1][temp],
                                           t_inds[2][temp])))
    # Clean up values
    Nt = len(t_dia_inscribed)  # Get number of throats
    if im.ndim == 2:  # If 2D, add 0's in 3rd dimension
        p_coords = sp.vstack((p_coords.T, sp.zeros((Np,)))).T
        t_coords = sp.vstack((sp.array(t_coords).T, sp.zeros((Nt,)))).T
    # Start creating dictionary of pore network information
    #if useOpenPNM == True:
     #   net = OpenPNM.Network.Empty(Np=Np, Nt=Nt)
    #else:
    net = {}
    net['pore.all'] = sp.ones((Np,), dtype=bool)
    net['throat.all'] = sp.ones((Nt,), dtype=bool)
    net['pore.coords'] = sp.copy(p_coords)*voxel_size
    net['pore.centroid'] = sp.copy(p_coords)*voxel_size
    net['throat.centroid'] = sp.array(t_coords)*voxel_size
    net['throat.conns'] = sp.array(t_conns)
    net['pore.label'] = sp.array(p_label)
    net['pore.volume'] = sp.copy(p_volume)*(voxel_size**3)
    net['throat.volume'] = sp.zeros((Nt,), dtype=float)
    net['pore.diameter'] = sp.copy(p_dia_local)*voxel_size
    net['pore.inscribed_diameter'] = sp.copy(p_dia_local)*voxel_size
    net['pore.equivalent_diameter'] = 2*((3/4*net['pore.volume']/sp.pi)**(1/3))
    net['pore.extended_diameter'] = sp.copy(p_dia_global)*voxel_size
    net['pore.surface_area'] = sp.copy(p_area_surf)*(voxel_size)**2
    net['pore.solid_area'] = sp.copy(p_area_solid)*(voxel_size)**2
    net['pore.sphericity'] = sp.pi**(1/3)*(6*sp.array(p_volume))**(2/3)/sp.array(p_area_surf)
    net['pore.roundness'] = sp.array(p_dia_local)/sp.array(p_dia_global)
    net['pore.surface_ratio']=net['pore.volume']/net['pore.surface_area']
    net['throat.diameter'] = sp.array(t_dia_inscribed)*voxel_size
    net['throat.inscribed_diameter'] = sp.array(t_dia_inscribed)*voxel_size
    net['throat.area'] = sp.array(t_area)*(voxel_size**2)
    net['throat.perimeter'] = sp.array(t_perimeter)*voxel_size
    net['throat.shape_factor'] = sp.array(t_area)/sp.array(t_perimeter)**2
    net['throat.equivalent_diameter'] = (sp.array(t_area)*(voxel_size**2))**(0.5)
    P12 = net['throat.conns']
    if len(P12)>0:
        PT1 = sp.sqrt(sp.sum(((p_coords[P12[:, 0]]-t_coords)*voxel_size)**2, axis=1))
        PT2 = sp.sqrt(sp.sum(((p_coords[P12[:, 1]]-t_coords)*voxel_size)**2, axis=1))
        net['throat.total_length'] = PT1 + PT2
        PT1 = PT1 - p_dia_local[P12[:, 0]]/2*voxel_size
        PT2 = PT2 - p_dia_local[P12[:, 1]]/2*voxel_size
        net['throat.length'] = PT1 + PT2
        dist = (p_coords[P12[:, 0]]-p_coords[P12[:, 1]])*voxel_size
        net['throat.direct_length'] = sp.sqrt(sp.sum(dist**2, axis=1))
    return net

if __name__ == '__main__':
    net = extract_pore_network(im=regions*im, dt=dt)
