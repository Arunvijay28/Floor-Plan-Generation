import argparse
import os
import numpy as np
import math
import sys
import random
import torchvision.transforms as transforms
from torchvision.utils import save_image
from .floorplan_dataset_maps_functional_high_res import FloorplanGraphDataset, floorplan_collate_fn
from torch.utils.data import DataLoader
from torchvision import datasets
from torch.autograd import Variable
import torch.nn as nn
import torch.nn.functional as F
import torch.autograd as autograd
import torch
from PIL import Image, ImageDraw, ImageFont
import svgwrite
from .models import Generator
from .utils import _init_input, ID_COLOR, draw_masks, draw_graph, estimate_graph
from collections import defaultdict
import matplotlib.pyplot as plt
import networkx as nx
import glob
import cv2
import webcolors
import time

parser = argparse.ArgumentParser()
parser.add_argument("--n_cpu", type=int, default=16, help="number of cpu threads to use during batch generation")
parser.add_argument("--batch_size", type=int, default=1, help="size of the batches")
parser.add_argument("--checkpoint", type=str, default='./housegan_integration/checkpoints/pretrained.pth', help="checkpoint path")
parser.add_argument("--data_path", type=str, default='./data/sample_list.txt', help="path to dataset list file")
parser.add_argument("--out", type=str, default='./static/images', help="output folder")
opt = parser.parse_args()

# print(opt)

os.makedirs(opt.out, exist_ok=True)

model = Generator()
model.load_state_dict(torch.load(opt.checkpoint, map_location=torch.device('cpu')), strict=True)
model = model.eval()

# run inference
def _infer(graph, model, prev_state=None):
    # configure input to the network
    z, given_masks_in, given_nds, given_eds = _init_input(graph, prev_state)
    # run inference model (ensure tensors are moved to CPU)
    with torch.no_grad():
        masks = model(z.to('cpu'), given_masks_in.to('cpu'), given_nds.to('cpu'), given_eds.to('cpu'))
        masks = masks.detach().cpu().numpy()
    return masks

def finall():
    real_nodes = np.array([0, 1, 2, 3, 4, 7, 16, 16, 16, 16, 16, 16, 14])

    num_nodes = len(real_nodes)
    max_index = 18  
    nds = np.zeros((num_nodes, max_index), dtype=np.float32)
    for i, node in enumerate(real_nodes):
        nds[i][node] = 1. 

    egs=[[0,1,1],
         [0,-1,2],
         [0,1,3],
         [0,-1,4],
         [0,-1,5],
        [0,1,6],
        [0,-1,7],
        [0,-1,8],
        [0,-1,9],
        [0,-1,10],
        [0,-1,11],
        [0,1,12],
         [1,-1,2],
         [1,1,3],
         [1,-1,4],
         [1,-1,5],
         [1,1,6],
         [1,-1,7],
         [1,1,8],
         [1,-1,9],
         [1,-1,10],
         [1,-1,11],
         [1,-1,12],
         [2,1,3],
         [2,1,4],
         [2,1,5],
         [2,-1,6],
         [2,-1,7],
         [2,-1,8],
         [2,1,9],
         [2,1,10],
         [2,1,11],
         [2,-1,12],
         [3,-1,4],
         [3,-1,5],
         [3,-1,6],
         [3,1,7],
         [3,1,8],
         [3,1,9],
         [3,-1,10],
         [3,-1,11],
         [3,-1,12],
         [4,-1,5],
         [4,-1,6],
         [4,-1,7],
         [4,-1,8],
         [4,-1,9],
         [4,-1,10],
         [4,1,11],
         [4,-1,12],
         [5,-1,6],
         [5,-1,7],
         [5,-1,8],
         [5,-1,9],
         [5,1,10],
         [5,-1,11],
         [5,-1,12],
         [6,-1,7],
         [6,-1,8],
         [6,-1,9],
         [6,-1,10],
         [6,-1,11],
         [6,-1,12],
         [7,-1,8],
         [7,-1,9],
         [7,-1,10],
         [7,-1,11],
         [7,-1,12],
         [8,-1,9],
         [8,-1,10],
         [8,-1,11],
         [8,-1,12],
         [9,-1,10],
         [9,-1,11],
         [9,-1,12],
         [10,-1,11],
         [10,-1,12],
         [11,-1,12]
         ]
    
    nsd=torch.tensor(nds,dtype=torch.float32)
    egd=torch.tensor(egs)
    graph=[nsd,egd]

    true_graph_obj, graph_im = draw_graph([real_nodes, egd.detach().cpu().numpy()])
    graph_im.save('./{}/graph_{}.png'.format(opt.out, 0))  # save graph
    _types = sorted(list(set(real_nodes)))
    selected_types = [_types[:k+1] for k in range(10)]
    os.makedirs('./{}/'.format(opt.out), exist_ok=True)
    _round = 0
    
    # initialize layout
    state = {'masks': None, 'fixed_nodes': []}
    masks = _infer(graph, model, state)
    im0 = draw_masks(masks.copy(), real_nodes)
    im0 = torch.tensor(np.array(im0).transpose((2, 0, 1)))/255.0 
    # save_image(im0, './{}/fp_init_{}.png'.format(opt.out, i), nrow=1, normalize=False) # visualize init image

    # generate per room type
    for _iter, _types in enumerate(selected_types):
        _fixed_nds = np.concatenate([np.where(real_nodes == _t)[0] for _t in _types]) \
            if len(_types) > 0 else np.array([]) 
        state = {'masks': masks, 'fixed_nodes': _fixed_nds}
        masks = _infer(graph, model, state)
        
    # save final floorplans
    imk = draw_masks(masks.copy(), real_nodes)
    imk = torch.tensor(np.array(imk).transpose((2, 0, 1)))/255.0 
    save_image(imk, './{}/fp_final_{}.png'.format(opt.out, 0), nrow=1, normalize=False)


def node_edge_graph(real_nodes,edges):
    print(real_nodes)
    print("\nedges",edges)
    nodes=real_nodes
    edgeList = []
    for edge in range(len(nodes)):
        for j in range(edge + 1, len(nodes)):
            connection = -1
            for e in edges:
                if (e["from"] == edge and e["to"] == j) or (e["to"] == edge and e["from"] == j):
                    connection = 1
                    break
            edgeList.append([edge, connection, j])

    ind=nodes.index(16)
    doors=[ind+i for i in range(len(edges))]
    print("doors:",doors)
    for e in range(len(edges)):
        for j in range(len(edgeList)):
            if (edgeList[j][0]==edges[e]["from"] and edgeList[j][2]==doors[e]) or (edgeList[j][0]==edges[e]["to"] and edgeList[j][2]==doors[e]):
                edgeList[j][1]=1
    
    last_element = None
    for edge in edgeList:
        if edge[0] == 0:
            last_element = edge  # Keep updating to get the last occurrence

    # Modify the connection value if it is -1
    if last_element and last_element[1] == -1:
        last_element[1] = 1
        
    print("edgelist:",edgeList)
    return edgeList
        

def edgelist_creation(nodes,edges):
    edgeList=[]
# Create adjacency list with door info
    for edge in range(len(nodes)):
        for j in range(edge + 1, len(nodes)):
            connection = -1  # Default: Not connected
            for e in edges:
                if (e["from"] == edge and e["to"] == j) or (e["to"] == edge and e["from"] == j):
                    connection = 1
                    break
            edgeList.append([edge, connection, j])

    ind=nodes.index(16)
    doors=[ind+i for i in range(len(edges))]
    print(doors)

    # doors=[6,7,8,9,10]\
    d = 0
    doorLogic = []
    for i in range(len(edgeList)):
        if(edgeList[i][1]==1):
            print(edgeList[i])
            door = doors[d]
            print(door)
            ed = edgeList[i][:]
            ed.append(door)
            d+=1
            doorLogic.append(ed)
    print(doorLogic)

    for i in doorLogic:
        for j in range(len(edgeList)):
            if(edgeList[j][0]==i[0] and edgeList[j][2]==i[3]):
                edgeList[j][1] = 1
    print(edgeList)
    last_element = None
    for edge in edgeList:
        if edge[0] == 0:
            last_element = edge  # Keep updating to get the last occurrence

    # Modify the connection value if it is -1
    if last_element and last_element[1] == -1:
        last_element[1] = 1
    return edgeList
            
def from_server(real_nds,edges):

    real_nodes=real_nds
    num_nodes = len(real_nodes)
    max_index = 18  
    node_data = np.zeros((num_nodes, max_index), dtype=np.float32)
    for i, node in enumerate(real_nodes):
        node_data[i][node] = 1.

    # edge_data=node_edge_graph(real_nodes,edges)
    edge_data=edgelist_creation(real_nodes,edges)
    real_nodes=np.array(real_nds)
    nodes=torch.tensor(node_data,dtype=torch.float32)
    edge=torch.tensor(edge_data)
    graph=[nodes,edge]
    
    print(type(nodes),type(edge),type(real_nodes))

    true_graph_obj, graph_im = draw_graph([real_nodes, edge.detach().cpu().numpy()])
    graph_im.save('./{}/graph_{}.png'.format(opt.out, 0))  # save graph
    _types = sorted(list(set(real_nodes)))
    selected_types = [_types[:k+1] for k in range(10)]
    os.makedirs('./{}/'.format(opt.out), exist_ok=True)
    _round = 0
    
    # # initialize layout
    state = {'masks': None, 'fixed_nodes': []}
    masks = _infer(graph, model, state)
    im0 = draw_masks(masks.copy(), real_nodes)
    im0 = torch.tensor(np.array(im0).transpose((2, 0, 1)))/255.0 
    
    # # generate per room type
    for _iter, _types in enumerate(selected_types):
        _fixed_nds = np.concatenate([np.where(real_nodes == _t)[0] for _t in _types]) \
            if len(_types) > 0 else np.array([]) 
        state = {'masks': masks, 'fixed_nodes': _fixed_nds}
        masks = _infer(graph, model, state)
        
    # # save final floorplans
    imk = draw_masks(masks.copy(), real_nodes)
    imk = torch.tensor(np.array(imk).transpose((2, 0, 1)))/255.0 
    save_image(imk, './{}/fp_final_{}.png'.format(opt.out, 0), nrow=1, normalize=False)
