#-*- coding: utf-8 -*-
import sys
import numpy as np
import matplotlib.pyplot as plt
from cluster import *
from sklearn import manifold
import os
import datetime

def plot_scatter_diagram(which_fig, x, y, x_label='x', y_label='y', title='title', cluster=None, output='figures.png'):
    '''
    Plot scatter diagram
    Args:
        which_fig  : which sub plot
        x          : x array
        y          : y array
        x_label    : label of x pixel
        y_label    : label of y pixel
        title      : title of the plot
    '''
    styles = ['k.', 'g.', 'r.', 'b.', 'y.', 'm.', 'c.']
    assert len(x) == len(y)
    if np.any(cluster != None):
        assert len(x) == len(cluster) and len(styles) >= len(set(cluster))
    plt.figure(which_fig)
    plt.clf()
    if np.any(cluster == None):
        plt.plot(x, y, styles[0])
    else:
        clses = set(cluster)
        print(clses)
        xs, ys = {}, {}
        for i in range(len(x)):
            try:
                xs[cluster[i]].append(x[i])
                ys[cluster[i]].append(y[i])
            except KeyError:
                xs[cluster[i]] = [x[i]]
                ys[cluster[i]] = [y[i]]
        color = 1
        for idx, cls in enumerate(clses):
            if cls == -1:
                style = styles[0]
            else:
                style = styles[color]
                color += 1
            plt.plot(xs[cls], ys[cls], style)
    plt.title(title)
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    #plt.show()
    plt.savefig(output)


def plot_rho_delta(rho, delta, output):
    '''
    Plot scatter diagram for rho-delta points
    Args:
        rho   : rho list
        delta : delta list
    '''
    plot_scatter_diagram(
        0, rho[1:], delta[1:], x_label='rho', y_label='delta', title='rho-delta', output=output)


def parse_arg():
    parser = argparse.ArgumentParser(description='clas')
    parser.add_argument('input', help='input points file',
                        type=str, default=None)
    return parser.parse_args()


if __name__ == '__main__':
    '''
    # test plot scatter diagram
    x =   np.array([1, 2, 3, 4, 5, 6, 7, 8, 7, 7])
    y =   np.array([2, 3, 4, 5, 6, 2, 4, 8, 5, 6])
    cls = np.array([1, 4, 2, 3, 5, -1, -1, 6, 6, 6])
    plot_scatter_diagram(0, x, y, cluster = cls)
    '''
    args = parse_arg()
    dpcluster = DensityPeakCluster()
    rho, delta = dpcluster.density_and_distance(args.input)

    now = datetime.datetime.now()
    dir, name = os.path.split(args.input)
    if not os.path.exists(os.path.join(dir, 'plot_rho_delta')):
        os.makedirs(os.path.join(dir, 'plot_rho_delta'))
    output = os.path.join(dir, 'plot_rho_delta', '%s_%s.png' %
                          (name, now.strftime('%Y%m%d%H%M')))
    plot_rho_delta(rho, delta, output)
