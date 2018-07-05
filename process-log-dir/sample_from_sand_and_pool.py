# -*- coding:utf-8 -*-
# 同时从48类池子以及48类沙子库中采样

import os
import sys
import json
import argparse
import pprint
import random
import datetime
import numpy as np
from collections import Counter

from cfg import Config


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

def labels_cls_analyse(inputFile=None):
    '''
    统计分析分类labels信息，并返回各个类别的数量
    '''
    json_lists = load_json(inputFile)
    labels = [json_list['label'][0]['data'][0]['class']
              for json_list in json_lists
              if json_list['label']]
    # 统计labels的类别信息
    cls_analyse = Counter(labels).most_common()
    output = "{}_cls_analyse.txt".format(os.path.splitext(inputFile)[0])
    with open(output, 'w') as f:
        for line in cls_analyse:
            f.write(str(line)+'\n')
    print("generate outputfile is %s" % (output))


def _representsNum(s):
    try:
        float(s)
        return True
    except ValueError:
        return False


def _calculate_count(ClsRatio, categorys, Num=None):
    """
        ClsRatio: dict eg : ['pulp','2' 'sexy', '2',normal', '1']
        categorys: list eg : ['pulp', 'sexy', 'normal']
    """
    # 确认是否是有效的输入
    for category, weight in ClsRatio.items():
        if category not in categorys:
            print("Error, print input correct label name!!!")
            exit()
        elif not _representsNum(weight):
            print("Error, print input correct label weight number!!!")
            exit()

    # 计算各个类别的权重比例，以及相应的个数
    total = sum(ClsRatio.values())
    ClsCount_dict = {k: int(float(v) / total * Num)
                     for k, v in ClsRatio.items()}
    # 若按照类别比例分配后总数与Num不等
    reminder = Num - sum(ClsCount_dict.itervalues())
    if reminder != 0 :
        keys = [key for key, val in ClsCount_dict.items() if val != 0]
        for i in range(abs(reminder)):
            tmp = len(keys)
            key = keys[i % tmp]
            value = ClsCount_dict[key]
            ClsCount_dict.update(
                {key: value + reminder/abs(reminder)})
    return ClsCount_dict
        

def getListFromLibrary(inputFileRoot=None, categorys=None, ClsCount_dict=None, move=False):
    """
    randomly select samples 
        inputFile : input file name absolute path
        Num : get num ,type int
        outputFile : store output file absolute path
        ClsCount_dict : dict eg : ['pulp','2' 'sexy', '2',normal', '1']
    """
    sample = []
    for category, count in ClsCount_dict.items():
        if count > 0:
            print('class name: {label: >40s}, sample number: {count: >4d}'.format(
                label=category, count=count))
            file_path = os.path.join(inputFileRoot, category + '.json')
            pool_json_lists = load_json(file_path)
            if len(pool_json_lists) >= count:
                random.shuffle(pool_json_lists)
                for _ in range(count):
                    sample.append(pool_json_lists.pop())
                if move:
                    write_to_json(pool_json_lists, file_path)
            else:
                print("\t: library count %d < required num %d " %
                      (len(pool_json_lists), count))
                #exit()
    return sample
    
def parse_args():
    parser = argparse.ArgumentParser(description="create jsonlist according to cls-ratio",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--actionFlag', required=True, type=int, choices=[0,1],
                        help="0 or 1， #0：分析jsonlist的类别信息，1：按cls_ratio对jsonlist分包")
    parser.add_argument('--sand', help='sand directory saving sand json list files', default=None, type=str)
    parser.add_argument('--pool', help='pool directory saving pool json list files', default=None, type=str)
    parser.add_argument('-sn','--sand_num', help='the number of jsonlist', type=int, default=500)
    parser.add_argument('-pn', '--pool_num', help='the number of jsonlist', type=int, default=4500)
    parser.add_argument(
        '--inputJsonList', help='input json list file absolute path', default=None, type=str)
    parser.add_argument(
        '--root', help='root directory saving json list file', default=None, type=str)
    return parser.parse_args()

args = parse_args()
def main():
    actionFlag = args.actionFlag
    if actionFlag == 0:
        if args.root:
            pass
        elif args.inputJsonList:
            labels_cls_analyse(inputFile=args.inputJsonList)
        else:
            print("Please input root or inputJsonList!!!")
    elif actionFlag == 1:
        # 计算沙子中每个类别的采样图片数，并进行采样
        sample_sand = list()
        if args.sand:
            ClsCount_dict_sand = _calculate_count(
                Config.SAND_RATIO, Config.CATEGORYS, args.sand_num)
            sample_sand = getListFromLibrary(
                inputFileRoot=args.sand, categorys=Config.CATEGORYS, ClsCount_dict=ClsCount_dict_sand)
            print("*"*40 + " Sample from sand library " + "*"*40)
        # 计算池子中每个类别的采样图片数，并进行采样
        sample_pool = list()
        if args.pool:
            ClsCount_dict_pool = _calculate_count(
                Config.POOL_RATIO, Config.CATEGORYS, args.pool_num)
            sample_pool = getListFromLibrary(
                inputFileRoot=args.pool, categorys=Config.CATEGORYS, ClsCount_dict=ClsCount_dict_pool, move=False)
            print("*"*40 + " Sample from pool library " + "*"*40)
        # 保存采样后的数据
        result = sample_sand + sample_pool
        # random.shuffle(result)
        now = datetime.datetime.now()
        output_json = os.path.join(args.sand, 'sample_%d_%s.json' %
                                   (len(result), now.strftime("%Y%m%d%H%M%S")))
        write_to_json(result, output_json)
        print("generate outputfile is %s" % (output_json))

if __name__ == '__main__':
    print ('Start process')
    main()
    print ('End ...')
