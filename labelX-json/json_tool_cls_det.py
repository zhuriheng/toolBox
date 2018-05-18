# -*- coding:utf-8 -*-
# created 2018/04/13 @Riheng
# 生成图片分类和检测的jsonlist

import os
import json
import argparse

'''
dataTypeFlag : 数据类型  cls 分类  det 检测 

actionFlag : 功能flag
    1  : 从本地读取图片生成jsonlist
        --inputImagesPath  图片保存地址 [required]
        --dataset_label   分类：'terror'/'pulp'/'general' 检测：'detect' [required]
        --prefix  jsonlist中图片url的前缀 [optinal]
        --nb_prefix -np 图片地址目录的级数 [optinal][default=1]
        --output  输出文件, labels.json by default [optinal][default=labels.json]
    2  : 将其他的json格式修改为labelX标准的json格式
        根据个性化要求完成create_from_jsons()函数
        --inputJsonList  输入的jsonlist文件 [required]
        --dataset_label   分类：'terror'/'pulp'/'general' 检测：'detect' [required]
        --prefix  jsonlist中图片url的前缀 [optinal]
        --output  optional 输出文件, <infile>_labelX.json [optinal][default=labels.json]
        --label_is_None  optional 设置后所有的图片类别为空（用于labelx发包）[optinal][default=False]
'''


def make_labelX_json_det(url=None, dataset_label='detect'):
    '''
    url, type, <source_url>, <ops>, 
    label:
        [{
        "data": [{"class": "normal"}], 
        "version": "1", 
        "type": "detection", 
        "name": "detect"
        }]
    '''
    label_json = {"data": [], "version": "1",
                  "type": "detection", "name": dataset_label}
    ava_json = {"url": url, "ops": "download()", "type": "image",
                "label": [label_json]}
    return ava_json


def make_labelX_json_cls(url=None, cls=None, dataset_label=None):
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
    if cls:
        data = [{"class": cls}]
    else:
        data = []
    label_json = {"data": data, "version": "1",
                  "type": "classification", "name": dataset_label}
    ava_json = {"url": url, "ops": "download()", "type": "image",
                "label": [label_json]}
    return ava_json


def load_json(file_path):
    '''
    read json file
    '''
    with open(file_path, 'r') as f:
        json_lists = [json.loads(line) for line in f]
    return json_lists


def write_to_json(json_lists, output):
    # 输出到文件中
    with open(output, 'w') as fi:
        for json_list in json_lists:
            json.dump(json_list, fi)  # 不使用indent
            fi.write('\n')


# string.upper()的用法
def checkFileIsImags(filePath):
    if ('JPEG' in filePath.upper()) or ('JPG' in filePath.upper()) \
            or ('PNG' in filePath.upper()) or ('BMP' in filePath.upper()):
        return True
    return False

# os.walk()获得多层路径下文件的用法
def getAllImages(basePath=None):
    allImageList = []
    for parent, dirnames, filenames in os.walk(basePath):
        for file in filenames:
            imagePathName = os.path.join(parent, file)
            if checkFileIsImags(imagePathName):
                allImageList.append(imagePathName)
            else:
                # print("%s isn't image"%(imagePathName))
                pass
    return allImageList

def create_from_images():
    allImagesPathList = getAllImages(basePath=args.inputImagesPath)
    json_lists = []
    for imagePath in allImagesPathList:
        url = imagePath.split('/')[-args.nb_prefix:]
        url = '/'.join(url)
        # url添加前缀
        if args.prefix:
            url = os.path.join(args.prefix, url)
        # 判定数据类型
        if args.dataTypeFlag == 'det':
            json_list = make_labelX_json_det(
                url, dataset_label=args.dataset_label)
        elif args.dataTypeFlag == 'cls':
            # 需要修改cls部分
            json_list = make_labelX_json_cls(
                url, cls=None, dataset_label=args.dataset_label)
        json_lists.append(json_list)
    # 生成labelX jsonlist文件
    output = args.output if args.output else os.path.join(
        args.inputImagesPath, 'labels.json')
    write_to_json(json_lists, output)
    pass

def create_from_jsons():
    # 读取输入的jsonlist文件
    input_jsons = load_json(args.inputJsonList)
    json_lists = []

    # cifar10 class name
    # ['airplane', 'automobile', 'bird', 'cat', 'deer', 'dog', 'frog', 'horse', 'ship', 'truck']
    for input_json in input_jsons:
        url = input_json['url']
        # url添加前缀
        if args.prefix:
            url = os.path.join(args.prefix, url)
        # 判定数据类型
        if args.dataTypeFlag == 'det':
            json_list = make_labelX_json_det(
                url, dataset_label=args.dataset_label)
        elif args.dataTypeFlag == 'cls':
            # 需要修改cls部分
            if not args.label_is_None:
                cls = input_json['class']
            else:
                cls = None
            json_list = make_labelX_json_cls(
                url, cls=cls, dataset_label=args.dataset_label)
        json_lists.append(json_list)
    # 生成labelX jsonlist文件
    output = args.output if args.output else "{}_labelX.json".format(
        os.path.splitext(args.inputJsonList)[0])
    write_to_json(json_lists, output)
    

# 使用argparse
def parse_args():
    parser = argparse.ArgumentParser(description="生成图片分类和检测的jsonlist")
    parser.add_argument('--actionFlag', required=True,
                        type=int, choices=[1, 2])
    parser.add_argument('--dataTypeFlag', default=0, type=str, choices=['cls', 'det'], 
                        required=True, help="data type")
    parser.add_argument('--inputImagesPath', dest='inputImagesPath', type=str)
    parser.add_argument('--inputJsonList', type=str, help='input jsonlist file path')
    parser.add_argument('--output', dest='output',
                        help='output file name', type=str)
    parser.add_argument('--dataset_label', dest='dataset_label', choices=['terror', 'pulp', 'general', 'detect'],
                        help='default is general', default='terror', type=str)
    parser.add_argument('--prefix', dest='prefix',
                        help='prefix of url', default=None, type=str)
    parser.add_argument(
        '-np', '--nb_prefix', help='number of prefix, default = 1', default=1, type=int)
    parser.add_argument(
        '--label_is_None', help='optional 设置后所有的图片类别为空（用于labelx发包）', 
        default=False, type=bool, choices=[True, False])
    
    return parser.parse_args()

args = parse_args()
def main():
    actionFlag = args.actionFlag
    print '--------' * 8
    if actionFlag == 1:
        print "create labelX jsonlist from local images"
        create_from_images()
    elif actionFlag == 2:
        print "create labelX jsonlist from jsonlist"
        create_from_jsons()


if __name__ == '__main__':
    print 'Start processing'
    main()
    print 'End ...'


"""
# cifar10 test label
python json_tool_cls_det.py \
--actionFlag  2 \
--dataTypeFlag cls \
--inputJsonList /Users/zhuriheng/resources/json-list/cifar10/cifar10_test_with_labels.json \
--prefix  http://p3nocaipw.bkt.clouddn.com/test/ \
--dataset_label general
"""
