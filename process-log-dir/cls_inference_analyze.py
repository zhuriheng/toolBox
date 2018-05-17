# -*- coding: utf-8 -*-
#
# Created on 2018/04/11 @Riheng
# Filter inference results based on threshold
# 版本更新：
#   V0.1  初始版本

import json
import os
import numpy as np
import argparse


def load_json(file_path):
    with open(file_path, 'r') as f:
        json_lists = [json.loads(line) for line in f]
    return json_lists


def write_to_json(json_lists, output):
    # 输出到json格式的文本中
    with open(output, 'w') as fi:
        for json_list in json_lists:
            json.dump(json_list, fi)  # 不使用indent
            fi.write('\n')


def filter(result, threshold):
    index = int(result.values()[0]['Top-1 Index'])
    prob = result.values()[0]['Confidence'][index]
    if index <= 10:
        if threshold <= float(prob):
            return True
    else:
        return False


def parse_args():
    parser = argparse.ArgumentParser(
        description='Filter inference results based on threshold')
    parser.add_argument('-p','--path', type=str, help='file path' )
    parser.add_argument('-thrs', '--threshold', type=float,
                        help='json list, Ali BK output')
    parser.add_argument(
        '-o', '--output',
        help='output json file path, will be saved as <infile>_threshold_<threshold>.log path by default',
        type=str)
    return parser.parse_args()


args = parse_args()
def main():
    output = args.output if args.output else '%s_threshold_%f.json' % ( \
        os.path.splitext(args.path)[0], args.threshold)
    results = load_json(args.path)
    images_threshold = []
    for result in results:
        if filter(result, args.threshold):
            images_threshold.append(result)
    write_to_json(images_threshold, output)

if __name__  == '__main__':
    args = parse_args()
    print "Start processing"
    main()
    print "End processing"
