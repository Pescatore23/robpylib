# -*- coding: utf-8 -*-
"""
Created on Thu Sep  2 09:25:07 2021

module to store networkx object to netcdf4 and reconstruct it from file

@author: firo
"""

import networkx as nx
import xarray as xr


def store_graph_to_netcdf4(graph, path, attrs={}):
    adj_matrix = nx.to_numpy_array(graph)
    nodes = graph.nodes()
    data = xr.Dataset({'adj_matrix': (['nodes', 'nodes'], adj_matrix)},
                      coords= {'nodes': nodes*2})
    data.attrs = attrs
    data.to_netcdf(path)
    
    
def reconstruct_grah_from_netcdf4(path):
    data = xr.load_dataset(path)
    nodes = data['nodes'].data
    mapping = {}
    for i in range(len(nodes)):
        mapping[i] = nodes[i]
    adj_matrix = data['adj_matrix'].data
    graph = nx.from_numpy_array(adj_matrix)
    H = nx.relabel_nodes(graph, mapping)
    return H
    
    