# -*- coding:utf-8 -*-
# created 2018/05/23 @Riheng
# 检测回归测试结果分析

import os
import argparse
import sys
import json

from collections import Counter, OrderedDict, defaultdict

'''
    检测回归测试结果分析
    --detResultFile 模型在测试数据集上的结果，暴恐检测回归测试 tsv文件的格式
        eg : 文件样例
        split by \t
        knives.jpg  [{"class": "knives", "index": 3, "pts": [[49, 69], [
            75, 69], [75, 108], [49, 108]], "score":0.9993000030517578}]
        ISIS.jpg    [{"class": "isis flag", "index": 1, "pts": [[157, 107], [
            515, 107], [515, 328], [157, 328]], "score":0.9998000264167786}]

'''


def load_tsv(file_path):
    '''
    read  file
    '''
    results = OrderedDict()
    with open(file_path, 'r') as f:
        for line in f:
            line = line.strip()
            (image, det_result) = line.split('\t')
            results[image] = det_result
    return results


def analyze(results):
    # 将相同类别的图片放在一个group中
    group = defaultdict(list)
    for (image, det_res) in results.iteritems():
        label = image.split('_0523_')[0]
        group[label].append(det_res)
    
    # 分析每一个类别的统计信息
    for label in group.iterkeys():
        length = len(group[label])
        num = group[label].count('[]')
        portion = (length-num) * 1.0 /length
        print label
        print "Image with detectation num: %d, %f" % (length-num, portion)

def parse_args():
    parser = argparse.ArgumentParser(description="md5 process check image")
    parser.add_argument('--detResultFile', type=str, required=True)
    return parser.parse_args()

args = parse_args()
def main():
    results = load_tsv(args.detResultFile)
    analyze(results)

if __name__ == '__main__':
    print "Start processing"
    main()
    print "...done"
