#-*- coding: utf-8 -*-

import numpy as np
import bcolz
import os
from scipy import spatial

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
    
    def euclidean_distance_set(self, XA, XB):
        '''
        Compute distance between each pair of the two collections of inputs.
        XA : An m_A by n array of m_A original observations in an n-dimensional space
        XA : An m_B by n array of m_B original observations in an n-dimensional space
        '''
        return spatial.distance.cdist(XA, XB, 'euclidean')

    def build_distance_file(self, filename):
        '''
        Calculate distance, save the result for cluster
        '''
        distance = self.euclidean_distance_set(self.vectors, self.vectors)
        c = bcolz.carray(distance, rootdir=filename, mode='w')
        c.flush()


def parse_arg():
    parser = argparse.ArgumentParser(description='clas')
    parser.add_argument('input', help='input points file', type=str, required=True)
    parser.add_argument(
        'output', help='output distance file, set <input>_distance.bc by default', type=str, default=None)
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_arg()
    builder = Distance(args.input)
    output = args.output if args.output else "%s_distance.bc" % (os.path.splitext(args.input)[0])
    builder.build_distance_file(output)
