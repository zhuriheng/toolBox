# -*- coding:utf-8 -*-
# created 2018/06/05 @Riheng
# 解析json文件，并实现个性化的需求

import os
import argparse
import sys
import json

from collections import Counter, defaultdict

'''
dataTypeFlag : 数据类型  cls 分类  det 检测 

    将jsonlist根据label信息排序，统计jsonlist的类别（分类）
        --input-json 输入的json文件 [required]
        --output-json 输出的json文件 <infile>_sort.json by default

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
    parser = argparse.ArgumentParser(
        description='将jsonlist根据label信息排序，统计jsonlist的类别（分类）信息')
    parser.add_argument('input', help='input json file', type=str)
    parser.add_argument('--dataTypeFlag', default='cls', type=str, choices=['cls', 'det'],
                        help="data type")
    parser.add_argument(
        '--output', help='output json file, <infile>_sort.json by default', type=str)
    return parser.parse_args()


def generate_each_label_json(label_lists):
    '''
    生成每个label的jsonlist
    output json file, <infile>_<labels>.json by default
    '''
    for keys in label_lists.keys():
        output_name = "{}_{}.json".format(
            os.path.splitext(args.input)[0], keys)
        write_to_json(label_lists[keys], output_name)


def bbox_det_analyse(json_lists):
    '''
    统计分析检测bbox信息
    '''
    labels = [bbox['class']
              for json_list in json_lists
              if json_list['label']
              for bbox in json_list['label'][0]['data']]
    # 统计labels的类别信息
    print Counter(labels).most_common()


def labels_cls_analyse(json_lists):
    '''
    统计分析分类labels信息，并返回各个类别的json list / url
    '''
    labels = [json_list['label'][0]['data'][0]['class']
              for json_list in json_lists
              if json_list['label']
              if json_list['label'][0]['data']]
    # 统计labels的类别信息
    print Counter(labels).most_common()

    # 返回各个类别的json list
    label_lists = defaultdict(list)
    for json_list in json_lists:
        if json_list['label']:
            # get label information
            if json_list['label'][0]['data']:
                label = str(json_list['label'][0]['data'][0]['class'])
                url = json_list['url']
                label_lists[label].append(json_list)
        else:
            label = '0_null'
            label_lists[label].append(json_list)
    return label_lists


def RepresentsInt(s):
    try:
        int(s)
        return True
    except ValueError:
        return False


args = parse_args()
def main():
    input_json = args.input
    output_json = args.output if args.output \
        else "{}_sort.json".format(os.path.splitext(args.input)[0])
    json_lists = load_json(input_json)
    if args.dataTypeFlag == 'cls':
        label_lists = labels_cls_analyse(json_lists)
        keys = label_lists.keys()
        # 假如label的形式是 “index_labelname”(0_bk_bloodiness_human),则对index排序
        if RepresentsInt(keys[0].split('_')[0]):
            keys = sorted(keys, key=lambda k: int(k.split('_')[0]))
        sort_label_lists = [label_list for key in keys
                            for label_list in label_lists[key]]
        write_to_json(sort_label_lists, output_json)
    elif args.dataTypeFlag == 'det':
        print "暂未支持检测的json排序"
    pass


if __name__ == '__main__':
    print 'Start process'
    main()
    print 'End ...'
