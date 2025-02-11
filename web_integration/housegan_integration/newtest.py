import argparse
import os
import numpy as np
import math
import sys
import random

import torchvision.transforms as transforms
from torchvision.utils import save_image

# sys.path.append(os.path.abspath())

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
# from models.models_improved import Generator

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

# Create output dir
os.makedirs(opt.out, exist_ok=True)

# Initialize generator and discriminator
model = Generator()
model.load_state_dict(torch.load(opt.checkpoint, map_location=torch.device('cpu')), strict=True)
model = model.eval()

# Initialize variables (skip CUDA if not available)
# No need for model.cuda() as we are on CPU

# initialize dataset iterator
# fp_dataset_test = FloorplanGraphDataset(rf"{opt.data_path}", transforms.Normalize(mean=[0.5], std=[0.5]), split='test')
# fp_loader = torch.utils.data.DataLoader(fp_dataset_test, 
#                                         batch_size=opt.batch_size, 
#                                         shuffle=False, collate_fn=floorplan_collate_fn)
# # optimizers
# Tensor = torch.FloatTensor  # Use CPU tensor

# run inference
def _infer(graph, model, prev_state=None):
    
    # configure input to the network
    z, given_masks_in, given_nds, given_eds = _init_input(graph, prev_state)
    # run inference model (ensure tensors are moved to CPU)
    with torch.no_grad():
        masks = model(z.to('cpu'), given_masks_in.to('cpu'), given_nds.to('cpu'), given_eds.to('cpu'))
        masks = masks.detach().cpu().numpy()
    return masks

def main():
    globalIndex = 0
    for i, sample in enumerate(fp_loader):
        # draw real graph and groundtruth
        mks, nds, eds, _, _ = sample
        real_nodes = np.where(nds.detach().cpu()==1)[-1]
        print(real_nodes)
        graph = [nds, eds]
        true_graph_obj, graph_im = draw_graph([real_nodes, eds.detach().cpu().numpy()])
        graph_im.save('./{}/graph_{}.png'.format(opt.out, i))  # save graph

        # add room types incrementally
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
        save_image(imk, './{}/fp_final_{}.png'.format(opt.out, i), nrow=1, normalize=False)


def summa():
    # balcony -5 , bathroom-4, living room-1,kitchen-2,,master room-3,comman room =study room=8


    real_nodes=np.array([ 4,  2,  2,  3,  1,  0 ,16 ,16 ,16, 16, 16, 14])

    ns=[[0., 0., 0., 0., 1., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0.],
        [0., 0., 1., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0.],
        [0., 0., 1., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0.],
        [0., 0., 0., 1., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0.],
        [0., 1., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0.],
        [1., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0.],
        [0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 1., 0.],
        [0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 1., 0.],
        [0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 1., 0.],
        [0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 1., 0.],
        [0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 1., 0.],
        [0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 1., 0., 0., 0.]]
    
    
    ed=[[ 0, -1,  1],
        [ 0, -1,  2],
        [ 0, -1,  3],
        [ 0, -1,  4],
        [ 0,  1,  5],
        [ 0, -1,  6],
        [ 0,  1,  7],
        [ 0, -1,  8],
        [ 0, -1,  9],
        [ 0, -1, 10],
        [ 0, -1, 11],
        [ 1, -1,  2],
        [ 1, -1,  3],
        [ 1, -1,  4],
        [ 1,  1,  5],
        [ 1,  1,  6],
        [ 1, -1,  7],
        [ 1, -1,  8],
        [ 1, -1,  9],
        [ 1, -1, 10],
        [ 1, -1, 11],
        [ 2, -1,  3],
        [ 2, -1,  4],
        [ 2,  1,  5],
        [ 2, -1,  6],
        [ 2, -1,  7],
        [ 2,  1,  8],
        [ 2, -1,  9],
        [ 2, -1, 10],
        [ 2, -1, 11],
        [ 3, -1,  4],
        [ 3,  1,  5],
        [ 3, -1,  6],
        [ 3, -1,  7],
        [ 3, -1,  8],
        [ 3,  1,  9],
        [ 3, -1, 10],
        [ 3, -1, 11],
        [ 4,  1,  5],
        [ 4, -1,  6],
        [ 4, -1,  7],
        [ 4, -1,  8],
        [ 4, -1,  9],
        [ 4,  1, 10],
        [ 4, -1, 11],
        [ 5,  1,  6],
        [ 5,  1,  7],
        [ 5,  1,  8],
        [ 5,  1,  9],
        [ 5,  1, 10],
        [ 5,  1, 11],
        [ 6, -1,  7],
        [ 6, -1,  8],
        [ 6, -1,  9],
        [ 6, -1, 10],
        [ 6, -1, 11],
        [ 7, -1,  8],
        [ 7, -1,  9],
        [ 7, -1, 10],
        [ 7, -1, 11],
        [ 8, -1,  9],
        [ 8, -1, 10],
        [ 8, -1, 11],
        [ 9, -1, 10],
        [ 9, -1, 11],
        [10, -1, 11]]
    
    nsd=torch.tensor(ns)
    egd=torch.tensor(ed)
    graph=[nsd,egd]
    # real_nodes=np.where(nsd.detach().cpu()==1)[-1]
    # print("realnodes:",real_nodes)

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

def finall():
# Given real_nodes
    real_nodes = np.array([0, 1, 2, 3, 4, 7, 16, 16, 16, 16, 16, 16, 14])

    # Create nds dynamically
    num_nodes = len(real_nodes)
    max_index = 18  # Ensuring we have enough columns
    nds = np.zeros((num_nodes, max_index), dtype=np.float32)
    for i, node in enumerate(real_nodes):
        nds[i][node] = 1.  # Ensure the format is 1. instead of 1.0

    # nsd = torch.tensor(nds)
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
    print(nsd)
    egd=torch.tensor(egs)
    graph=[nsd,egd]
    # real_nodes=np.where(nsd.detach().cpu()==1)[-1]
    # print("realnodes:",real_nodes)

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


def from_server(real_nds,edges):

    print(real_nds,edges)
    real_nodes=real_nds

    num_nodes = len(real_nodes)
    max_index = 18  
    nds = np.zeros((num_nodes, max_index), dtype=np.float32)
    for i, node in enumerate(real_nodes):
        nds[i][node] = 1.
    

    # egs=edges
    # nsd=torch.tensor(nds,dtype=torch.float32)
    # print(nsd)
    # egd=torch.tensor(egs)
    # graph=[nsd,egd]
    
    # # real_nodes=np.where(nsd.detach().cpu()==1)[-1]
    # # print("realnodes:",real_nodes)

    # true_graph_obj, graph_im = draw_graph([real_nodes, egd.detach().cpu().numpy()])
    # graph_im.save('./{}/graph_{}.png'.format(opt.out, 0))  # save graph
    # _types = sorted(list(set(real_nodes)))
    # selected_types = [_types[:k+1] for k in range(10)]
    # os.makedirs('./{}/'.format(opt.out), exist_ok=True)
    # _round = 0
    
    # # initialize layout
    # state = {'masks': None, 'fixed_nodes': []}
    # masks = _infer(graph, model, state)
    # im0 = draw_masks(masks.copy(), real_nodes)
    # im0 = torch.tensor(np.array(im0).transpose((2, 0, 1)))/255.0 
    # # save_image(im0, './{}/fp_init_{}.png'.format(opt.out, i), nrow=1, normalize=False) # visualize init image

    # # generate per room type
    # for _iter, _types in enumerate(selected_types):
    #     _fixed_nds = np.concatenate([np.where(real_nodes == _t)[0] for _t in _types]) \
    #         if len(_types) > 0 else np.array([]) 
    #     state = {'masks': masks, 'fixed_nodes': _fixed_nds}
    #     masks = _infer(graph, model, state)
        
    # # save final floorplans
    # imk = draw_masks(masks.copy(), real_nodes)
    # imk = torch.tensor(np.array(imk).transpose((2, 0, 1)))/255.0 
    # save_image(imk, './{}/fp_final_{}.png'.format(opt.out, 0), nrow=1, normalize=False)


if __name__ == '__main__':
    # change_real()
    # summa()
    finall()
