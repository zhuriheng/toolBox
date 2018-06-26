#coding=utf-8

import argparse
import json
import os
import sys
import time
import datetime
from collections import OrderedDict

import cv2
import numpy as np


def label_correspond(label_corres_list, dict_results):
    """
    docstring here
        :param label_corres_list: 
        :param dict_results: 
    """
    label_map = {}   # label的映射map
    for line in label_corres_list:
        ori_label = line.split(' ')[0]
        corres_label = line.split(' ')[1]
        label_map[ori_label] = corres_label

    for (img_name, results) in dict_results.iteritems():
        corres_label = label_map[results['Top-1 Class']]
        dict_results[img_name].update({'Top-1 Class': corres_label})
        dict_results[img_name].update(
            {'Top-1 Index': int(corres_label.split('_')[0])})

        output_prob = results['Confidence']
        corres_prob = []
        corres_prob.append(output_prob[0])
        corres_prob.append(max(float(output_prob[i]) for i in range(1, 5)))
        corres_prob.append(max(float(output_prob[i]) for i in range(5, 7)))
        corres_prob.append(max(float(output_prob[i]) for i in range(7, 9)))
        corres_prob.append(max(float(output_prob[i]) for i in range(9, 11)))
        corres_prob.append(output_prob[11])
        corres_prob.append(output_prob[12])
        corres_prob.append(output_prob[13])
        corres_prob.append(output_prob[14])
        corres_prob.append(output_prob[15])
        corres_prob.append(output_prob[16])
        corres_prob.append(output_prob[17])
        corres_prob.append(max(float(output_prob[i]) for i in range(18, 48)))

        dict_results[img_name].update(
            {'Confidence': [str(i) for i in list(corres_prob)]})
    return dict_results


def convert_infer_result(infer_result, labels_corres):
    """
    docstring here
        :param infer_result: 
        :param labels_corres: 
    """
    dict_results = dict()
    with open(infer_result, 'r') as f:
        for line in f:
            result = json.loads(line)
            img_name = result.keys()[0]
            result = result.values()[0]
            dict_results[img_name] = result

    label_corres_list = np.loadtxt(labels_corres, str, delimiter='\n')
    dict_results = label_correspond(label_corres_list, dict_results)

    now = datetime.datetime.now()
    output = '{}_cls13_{}.json'.format(os.path.splitext(infer_result)[0], now.strftime("%Y%m%d%H%M"))
    with open(output, 'w') as f:
        json.dump(dict_results, f, indent=4)
    

def convert_ground_truth(gt_file, map):
    now = datetime.datetime.now()
    output = '{}_cls13_{}.json'.format(os.path.splitext(gt_file)[
                                       0], now.strftime("%Y%m%d%H%M"))
    with open(gt_file, 'r') as fi, open(output, 'w') as fo:
        for line in fi:
            img_name, idx = line.strip().split(' ')
            idx = int(idx)
            for key in map.keys():
                if idx in map[key]:
                    idx = key
                    break
            fo.write('%s %s\n' % (img_name, idx))
    

def parse_arg():
    parser = argparse.ArgumentParser(description='convert cls48 to cls13')
    parser.add_argument('--infer', help='inference result json file under cls48', type=str, required=False)
    parser.add_argument('--gt', help='ground truth under cls48', type=str, required=False)
    parser.add_argument('--weight', help='caffemodel', type=str, required=True)
    parser.add_argument('--labels_corres', help='labels correspond list', type=str, required=False)
    return parser.parse_args()


def main():
    args = parse_arg()
    if args.infer:
        label_corres_list = np.loadtxt(args.labels_corres, str, delimiter='\n')
        convert_infer_result(args.infer, label_corres_list)

    if args.gt:
        map = {'0': [0], '1': [1, 2, 3, 4], '2': [
            5, 6], '3': [7, 8], '4': [9, 10]}  # 暴恐5类
        for idx in range(11, 18):
            map[str(idx)] = idx-6  # 敏感类别7类
        map['12'] = list(range(18, 48))  # 正常18到47类
        print map
        convert_ground_truth(args.gt, map)
        
    


if __name__ == '__main__':
    print('Start caffe image classify:')
    main()
    print('End process.')
