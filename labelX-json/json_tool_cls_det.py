# -*- coding:utf-8 -*-
# created 2018/04/13 @Riheng
# 生成图片分类和检测的jsonlist

import os
import json
import argparse

'''
dataTypeFlag : 数据类型  cls 分类  det 检测 

actionFlag : 功能flag
    1  : 从本地读取图片生成类别信息为空的jsonlist，主要用于标注发包
        --inputImagesPath  图片保存地址 [required]
        --nb_prefix -np 图片地址目录的级数 [optional][default=1]
        --dataset_label   分类：'terror'/'pulp'/'general' 检测：'detect' [required]
        --prefix  jsonlist中图片url的前缀 [optional]
        --output  optional 输出文件, <infile>_labelX.json [optional][default=labels.json]
        --with_label  optional 
            a. 设置后，需要提供图片的类别信息，图片名/类别名或者包含图片类别信息的list
            b. 若不设置，图片类别为空（用于labelx发包）
        --label_from_imgname optional [default=False]
            a. 设置后从图片名获取label信息，根据实际情况修改get_label_from_imgname(imgname)函数
            b. 若不设置，需提供labels.csv 以及images.lst文件
        --labels  类别信息，包含类别名以及对应的index 的labels.lst文件 [optional]
        --index_list  图片的index list，包含图片名以及对应的类别index  [optional]

    2  : 将其他的json格式修改为labelX标准的json格式
        根据个性化要求完成create_from_jsons()函数
        --inputJsonList  输入的jsonlist文件 [required]
        --with_label  optional 
            a. 设置后增加图片原有的类别信息
            b. 不设置类别信息为空（用于labelX发包）
        --dataset_label   分类：'terror'/'pulp'/'general' 检测：'detect' [required]
        --prefix  jsonlist中图片url的前缀 [optional]
        --output  optional 输出文件, <infile>_new.json [optional][default=labels.json]
        
'''


def make_labelX_json_det(url=None, data=[], dataset_label='detect'):
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
    label_json = {"data": data, "version": "1",
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

def get_label_from_labelfile(imgname):
    '''
    通过label列表获得图片的label信息
    '''
    label = None
    return label


def get_label_from_imgname(imgname):
    '''
    通过文件名获得图片的label信息
    '''
    label = imgname.split('_0227_')[0]
    return label


def get_label_from_directory(imagePath):
    '''
    通过文件路径获得图片的label信息
    '''
    print imagePath
    label = None
    return label


def request_label(cls=None, index=None):
    if not cls:  # cls为空，没有类别信息，返回True
        return True
    else:
        id = index if index else int(cls.split('_')[0])
        if id <= 100:
            return True
        else:
            return False


def process_classification(imagesPathList, nb_prefix, prefix, with_label, label_from_imgname, dataset_label):
    json_lists = []
    for imagePath in imagesPathList:
        url = imagePath.split('/')[-nb_prefix:]
        url = '/'.join(url)
        url = url if not prefix else os.path.join(prefix, url)
        img_name = imagePath.split('/')[-1]

        cls = None
        if with_label:
            if label_from_imgname:
            cls = get_label_from_imgname(img_name)
            #elif label_from_directory:
            #    cls = get_label_from_directory(imagePath)
            #    print("暂不支持")
            #    exit()
            else:
                cls = get_label_from_labelfile(img_name)
                print("暂不支持")
                exit()
        if request_label(cls):  # 判定是否是需要的类别
            json_list = make_labelX_json_cls(
                url, cls, dataset_label=dataset_label)
        json_lists.append(json_list)
    return json_lists


def process_detection(imagesPathList, nb_prefix, prefix, with_label, dataset_label):
    json_lists = []
    for imagePath in imagesPathList:
        url = imagePath.split('/')[-nb_prefix:]
        url = '/'.join(url)
        url = url if not prefix else os.path.join(prefix, url)
        img_name = imagePath.split('/')[-1]

        if with_label:
            print("暂不支持")
            exit()
        else:
            json_list = make_labelX_json_det(
                url, dataset_label=dataset_label)
        json_lists.append(json_list)
    return json_lists


def create_from_images():
    allImagesPathList = getAllImages(basePath=args.inputImagesPath)
    
    if args.dataTypeFlag == 'cls':
        json_lists = process_classification(
            allImagesPathList, args.nb_prefix, args.prefix, args.with_label, args.label_from_imgname, args.dataset_label)
    elif args.dataTypeFlag == 'det':
        json_lists = process_detection(
            allImagesPathList, args.nb_prefix, args.prefix, args.with_label, args.dataset_label)
    
    # 生成labelX jsonlist文件
    output = args.output if args.output else os.path.join(
        args.inputImagesPath, 'labels.json')
    write_to_json(json_lists, output)
    print("generate file: %s" % (output))


def create_from_jsons():
    # 读取输入的jsonlist文件
    input_jsons = load_json(args.inputJsonList)
    json_lists = []

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
            if args.with_label:
                cls = input_json['class']
            else:
                cls = None
            json_list = make_labelX_json_cls(
                url, cls=cls, dataset_label=args.dataset_label)
        json_lists.append(json_list)
    # 生成labelX jsonlist文件
    output = args.output if args.output else "{}_new.json".format(
        os.path.splitext(args.inputJsonList)[0])
    write_to_json(json_lists, output)
    print("generate file: %s" % (output))
    

# 使用argparse
def parse_args():
    parser = argparse.ArgumentParser(description="生成图片分类和检测的jsonlist")
    parser.add_argument('--actionFlag', required=True,
                        type=int, choices=[1, 2])
    parser.add_argument('--dataTypeFlag', default='cls', type=str, choices=['cls', 'det'], 
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
        '-np', '--nb_prefix', help='number of prefix, default = 1, eg. if np=3, ouput: train/0_cat/cat1.jpg', default=1, type=int)
    parser.add_argument(
        '--with_label', help='optional 设置后所有的图片类别为空（用于labelx发包）', 
        action='store_true')
    parser.add_argument(
        '--label_from_imgname', help='optional 设置后从图片名获取label信息',
        default=False, type=bool, choices=[True, False])
    parser.add_argument('--labels', type=str,
                        help='类别信息，包含类别名以及对应的index 的labels.lst文件')
    parser.add_argument('--index_list', type=str,
                        help='图片的index list，包含图片名以及对应的类别index')
    
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


