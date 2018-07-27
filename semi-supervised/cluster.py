#-*- coding: utf-8 -*-
import sys
import math
import numpy as np
from glob2 import glob
import bcolz
import argparse


def load_data(distance_file):
    '''
    Load distance from data file:
    column1: index1, column2: index2, column3: distance

    Return: distance dict, max distance, min distance, num of points
    '''
    distance = bcolz.open(distance_file)[:]

    num = distance.shape[0]
    max_dis = np.max(distance)
    invalid_idx = np.where(distance > 0)
    min_dis = np.min(distance[invalid_idx])

    return distance, num, max_dis, min_dis


def auto_select_dc(distance, num, max_dis, min_dis):
    '''
    Auto select the dc so that the average number of neighbors is around 1 to 2 percent
    of the total number of points in the data set
    '''
    dc = (max_dis + min_dis) / 2
    # Converts a square-form distance matrix to a vector-form distance vector
    values = distance[np.tril_indices(distance.shape[0], -1)]
    while True:
        neighbor_percent = sum(
            [1 for value in values if value < dc]) / num ** 2
        if neighbor_percent >= 0.01 and neighbor_percent <= 0.02:
            break
        if neighbor_percent < 0.01:
            min_dis = dc
        elif neighbor_percent > 0.02:
            max_dis = dc
        dc = (max_dis + min_dis) / 2
        if max_dis - min_dis < 0.0001:
            break

    return dc


def local_density(distance, num, dc, gauss=True, cutoff=False):
    '''
    Compute all points' local density
    Return: local density vector of points that index from 1
    '''
    assert gauss and cutoff == False and gauss or cutoff == True

    def gauss_func(dij, dc): return math.exp(- (dij / dc) ** 2)

    def cutoff_func(dij, dc): return 1 if dij < dc else 0
    func = gauss_func if gauss else cutoff_func
    rho = [-1] + [0] * num
    for i in range(0, num - 1):
        for j in range(i + 1, num):
            rho[i] += func(distance[i, j], dc)
            rho[j] += func(distance[j, i], dc)

    return np.array(rho, np.float32)


def min_distance(distance, num, max_dis, rho):
    '''
    Compute all points' min distance to a higher local density point
    Return: min distance vector, nearest neighbor vector
    '''
    sorted_rho_idx = np.argsort(-rho)
    delta = [0.0] + [max_dis] * num
    nearest_neighbor = [0] * (num + 1)
    delta[sorted_rho_idx[0]] = -1.0
    for i in range(1, num):
        idx_i = sorted_rho_idx[i]
        for j in range(0, i):
            idx_j = sorted_rho_idx[j]
            if distance[(idx_i, idx_j)] < delta[idx_i]:
                delta[idx_i] = distance[(idx_i, idx_j)]
                nearest_neighbor[idx_i] = idx_j

    delta[sorted_rho_idx[0]] = max(delta)
    return np.array(delta, np.float32), np.array(nearest_neighbor, np.int)


class DensityPeakCluster(object):

    def __init__(self):
        self.distance = None
        self.rho = None
        self.delta = None
        self.nearest_neighbor = None
        self.num = None
        self.dc = None
        self.core = None

    def density_and_distance(self, distance_file, dc=None):
        distance, num, max_dis, min_dis = load_data(distance_file)
        if dc == None:
            dc = auto_select_dc(distance, num, max_dis, min_dis)
        rho = local_density(distance, num, dc)
        delta, nearest_neighbor = min_distance(distance, num, max_dis, rho)

        self.distance = distance
        self.rho = rho
        self.delta = delta
        self.nearest_neighbor = nearest_neighbor
        self.num = num
        self.dc = dc

        return rho, delta

    def cluster(self, density_threshold, distance_threshold, dc=None):
        if self.distance == None:
            print('Please run density_and_distance first.')
            exit(0)
        distance = self.distance
        rho = self.rho
        delta = self.delta
        nearest_neighbor = self.nearest_neighbor
        num = self.num
        dc = self.dc

        print('Find the center.')
        cluster = [-1] * (num + 1)
        center = []
        for i in range(1, num + 1):
            if rho[i] >= density_threshold and delta[i] >= distance_threshold:
                center.append(i)
                cluster[i] = i

        print('Assignation begings.')
        #assignation
        sorted_rho_idx = np.argsort(-rho)
        for i in range(num):
            idx = sorted_rho_idx[i]
            if idx in center:
                continue
            cluster[idx] = cluster[nearest_neighbor[idx]]

        print('Halo and core.')
        '''
        halo: points belong to halo of a cluster
        core: points belong to core of a cluster, -1 otherwise
        '''
        halo = cluster[:]
        core = [-1] * (num + 1)
        if len(center) > 1:
            rho_b = [0.0] * (num + 1)
            for i in range(1, num):
                for j in range(i + 1, num + 1):
                    if cluster[i] != cluster[j] and distance[i-1, j-1] < dc:
                        rho_avg = (rho[i] + rho[j]) / 2
                        rho_b[cluster[i]] = max(rho_b[cluster[i]], rho_avg)
                        rho_b[cluster[j]] = max(rho_b[cluster[j]], rho_avg)

            for i in range(1, num + 1):
                if rho[i] > rho_b[cluster[i]]:
                    halo[i] = -1
                    core[i] = cluster[i]

        for i in range(len(center)):
            n_ele, n_halo = 0, 0
            for j in range(1, num + 1):
                if cluster[j] == center[i]:
                    n_ele += 1
                if halo[j] == center[i]:
                    n_halo += 1
            n_core = n_ele - n_halo
            print("Cluster %d: Center: %d, Element: %d, Core: %d, Halo: %d\n" %
                  (i + 1, center[i], n_ele, n_core, n_halo))

        self.core = core
        self.distance = distance
        self.num = num

        return rho, delta, nearest_neighbor


if __name__ == '__main__':
    dpcluster = DensityPeakCluster()
    dpcluster.density_and_distance(r'./data/example_distances.data')
    dpcluster.cluster(20, 0.1)
