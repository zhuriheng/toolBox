# -*- coding:utf-8 -*-
# created 2018/05/12 @Riheng
# 解析json文件，并实现个性化的需求

import os
import argparse
import sys
import json

from collections import Counter, defaultdict

'''
dataTypeFlag : 数据类型  cls 分类  det 检测 

actionFlag : 功能flag
    1: 统计jsonlist的类别（分类），bbox（检测）信息
        --input-json 输入的json文件 [required]
        --output-json 输出的json文件 <infile>_new.json by default

    2: 
'''

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


def write_to_file(json_lists, output):
    # 输出到非json格式的文本中
    with open(output, 'w') as fi:
        for json_list in json_lists:
            fi.write(json_list + '\n')

def parse_args():
    parser = argparse.ArgumentParser(description='解析json文件，并实现个性化的需求')
    parser.add_argument('--actionFlag', required=True,
                        type=int, choices=[1, 2])
    parser.add_argument('--dataTypeFlag', default=0, type=str, choices=['cls', 'det'],
                        required=True, help="data type")
    parser.add_argument('--input-json', help='input json file', type=str)
    parser.add_argument('--output-json', help='output json file, <infile>_new.json by default', type=str)
    return parser.parse_args()


def generate_each_label_json(label_lists):
    '''
    生成每个label的jsonlist
    output json file, <infile>_<labels>.json by default
    '''
    for keys in label_lists.keys():
        output_name = "{}_{}.json".format(
            os.path.splitext(args.input_json)[0], keys)
        write_to_json(label_lists[keys], output_name)


def bbox_det_analyse(json_lists):
    '''
    统计分析检测bbox信息
    '''
    labels = [bbox['class']
              for bbox in json_list['label'][0]['data']
              for json_list in json_lists
              if json_list['label']]
    # 统计labels的类别信息
    print Counter(labels).most_common()
    

def labels_cls_analyse(json_lists):
    '''
    统计分析分类labels信息，并返回各个类别的json list / url
    '''
    labels = [json_list['label'][0]['data'][0]['class'] \
            for json_list in json_lists
              if json_list['label']]
    # 统计labels的类别信息
    print Counter(labels).most_common()

    # 返回各个类别的json list
    label_lists = defaultdict(list)
    for json_list in json_lists:
        if json_list['label']:
            # get label information
            label = str(json_list['label'][0]['data'][0]['class'])
            url = json_list['url']
            label_lists[label].append(json_list)
            # label_lists[label].append(url)
    return label_lists

args = parse_args()
def main():
    input_json = args.input_json
    output_json = args.output_json if args.output_json \
                    else "{}_new.json".format(os.path.splitext(args.input_json)[0])
    json_lists = load_json(input_json)

    if args.dataTypeFlag == 'cls':
        label_lists = labels_analyse(json_lists)
        generate_each_label_json(label_lists)
    elif args.dataTypeFlag == 'det':
        bbox_det_analyse(json_lists)
    pass

if __name__ == '__main__':
    print 'Start process'
    main()
    print 'End ...'
