# -*- coding:utf-8 -*-
# created 2018/05/15 @Riheng
# 将分成1000分的推理结果整合在一起


import os
import json
import argparse

from collections import Counter

'''
将多线程多进程推理的1000份结果整合在一起，输出各个类别的统计信息
    
        --root  数据根目录 [required]
        --output   输出的json list，set <root name>_result.json by default [optional]
        --num  分割任务的数量，1000 by default [required][default=1000]
        --gpuNumber  推理是gpu的数量， 4 by default [required][default=4]
        --threshold  模型阈值，0.9 by default [required][default=0.9]
        --index 模型类别，目前只支持根据index的范围选择类别 [required][default=17]
'''


def make_labelX_json_cls(url=None, cls=None, dataset_label='terror'):
    '''
    url, type, <source_url>, <ops>, 
    label:
        [{
        "data": [{"class": "normal"}], 
        "version": "1", 
        "type": "classification", 
        "name": "terror" / "pulp" / "general"
        }]
    '''
    label_json = {"data": [{"class": cls}], "version": "1",
                  "type": "classification", "name": dataset_label}
    ava_json = {"url": url, "ops": "download()", "type": "image",
                "label": [label_json]}
    return ava_json


def merge_file(filenames, output):
    '''
    concatenate text files
    '''
    with open(output, 'w') as outfile:
        for fname in filenames:
            print "merge %s" % (fname)
            with open(fname) as infile:
                for line in infile:
                    outfile.write(line)
    

def merge_filter_file(filenames, output, threshold):
    '''
    concatenate text files
    '''
    with open(output, 'w') as outfile:
        for fname in filenames:
            print "merge %s" % (fname)
            json_fname = load_json(fname)
            filter_results = filter(json_fname, threshold)
            for json_list in filter_results:
                json.dump(json_list, outfile)  # 不使用indent
                outfile.write('\n')


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


def filter(results, threshold):
    json_lists = []
    for result in results:
        ind = int(result.values()[0]['Top-1 Index'])
        prob = result.values()[0]['Confidence'][ind]
        if ind <= args.index:
            if threshold <= float(prob):
                url = result.values()[0]['File Name']
                cls = result.values()[0]['Top-1 Class']
                result_labelX = make_labelX_json_cls(url, cls)
                json_lists.append(result_labelX)
    return json_lists

def get_file_list(path, num, gpuNumber):
    filenames = []
    for i in range(num):
        folder = os.path.join(path,'job-0' + str(i))
        for j in range(gpuNumber):
            filename = os.path.join(folder, 'split_file-0'+str(j)+'_0-result.json')
            if os.path.isfile(filename):
                filenames.append(filename)
    return filenames


def labels_cls_analyse(json_lists):
    '''
    统计分析分类labels信息，并返回各个类别的json list / url
    '''
    labels = [json_list['label'][0]['data'][0]['class']
              for json_list in json_lists
              if json_list['label']]
    # 统计labels的类别信息
    print Counter(labels).most_common()

# 使用argparse
def parse_args():
    parser = argparse.ArgumentParser(description="将多线程多进程推理的1000份结果整合在一起")
    parser.add_argument('--root', required=True,type=str)
    parser.add_argument('--output', type=str, help = 'set <root name>_result.json by default')
    parser.add_argument('--num', type=int, default=1000)
    parser.add_argument('--gpuNumber', type=int, default=4)
    parser.add_argument('--threshold', type=float, default=0.9, help='model threshold')
    parser.add_argument('--index', type=int, default=17)
    return parser.parse_args()

args = parse_args()
def main():
    filenames = get_file_list(args.root, args.num, args.gpuNumber)
    output_thresh = args.output if args.output else '{}_results_threshold_{}.json'.format(
        os.path.join(args.root, os.path.dirname(args.root).split('/')[-1]), str(args.threshold))
    # 在阈值筛选下，合并文件
    merge_filter_file(filenames, output_thresh, args.threshold)
    # 统计类别信息
    json_lists = load_json(output_thresh)
    labels_cls_analyse(json_lists)

if __name__ == '__main__':
    print 'Start processing'
    main()
    print 'End ...'

