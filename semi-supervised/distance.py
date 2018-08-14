#-*- coding: utf-8 -*-
'''
Version:
    - V1.0 using scipy.spatial.distance.pdist(n, 'euclidean') to save calculation time
           using bcolz to save memory 
    - V1.1 support multiple process with concurrent.futures package

Todo:
    - support ...
'''

import numpy as np
import bcolz
import os
import scipy.spatial.distance as dis
import time
from glob2 import glob
from functools import partial
from concurrent.futures import ProcessPoolExecutor

import argparse

class Distance(object):
    '''
    transfer points vector to distance vector
    '''

    def __init__(self, filename):
        self.vectors = bcolz.open(filename)[:]

    def euclidean_distance(self, vec1, vec2):
        '''
        Return the Euclidean Distance of two vectors
        '''
        return np.linalg.norm(vec1 - vec2)
    
    def euclidean_distance_set(self, X):
        '''
        Compute distance between each pair of the two collections of inputs.
        XA : An m_A by n array of m_A original observations in an n-dimensional space
        XA : An m_B by n array of m_B original observations in an n-dimensional space
        '''
        Y = dis.pdist(X, 'euclidean')
        return dis.squareform(Y)

    def build_distance_file(self, filename):
        '''
        Calculate distance, save the result for cluster
        '''
        distance = self.euclidean_distance_set(self.vectors)
        c = bcolz.carray(distance, rootdir=filename, mode='w')
        c.flush()


def parse_arg():
    parser = argparse.ArgumentParser(description='calculate distance')
    parser.add_argument('input', help='input points file', type=str, default=None)
    return parser.parse_args()


def calculate(input, save_folder):
    builder = Distance(input)
    
    file_name = os.path.split(input)[-1].split('.')[0]
    output = os.path.join(save_folder, "%s_distance.bc" % (file_name))
    
    start = time.time()
    builder.build_distance_file(output)
    cost = time.time() - start
    print("Create file successufully: %s" % (output))
    print("images number: %d, cost time: %f" % (builder.vectors.shape[0], cost))


if __name__ == '__main__':
    args = parse_arg()
    if os.path.isfile(args.input):
        dir = os.path.split(args.input)[0]
        save_folder = os.path.join(dir, 'distance')
        if not os.path.exists(save_folder):
            os.makedirs(save_folder)
        calculate(args.input, save_folder)
    elif os.path.isdir(args.input):
        files = glob(args.input + '/*.bc')
        save_folder = os.path.join(args.input, 'distance')
        if not os.path.exists(save_folder):
            os.makedirs(save_folder)
        
        start = time.time()
        # Nonparallel code
        # for file in files:
        #     calculate(file, save_folder)
        # Parallel implementation
        with ProcessPoolExecutor() as pool:
            pool.map(partial(calculate, save_folder=save_folder), files)
        print("Total cost time: %f" % (time.time() - start))
    else:
        print("Please input valid input points file")
