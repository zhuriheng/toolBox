# -*- coding: utf-8 -*-
#
# Created on 2018/04/04 @Riheng
# Traverse the folder and generate the index
# 版本更新：
#   V1.1 在图片地址后面增加label信息 2018/04/05

from __future__ import with_statement
import os
import argparse

def parse_args():
    parser = argparse.ArgumentParser(
        description='Traverse the folder and generate the index')
    parser.add_argument('--root', 
                        help='root path', default=None, type=str)
    parser.add_argument('--output', 
                        help='output file name', type=str)
    parser.add_argument('--mode', help='mode 1: generate total index; 2: generate index for each category, default = 1',
                        choices=[1, 2], default = 1, type=int)
    parser.add_argument(
        '-np', '--nb_prefix', help='number of prefix, default = 4', default=4, type=int)
    parser.add_argument('-s','--sort', help='whether sort index', action='store_true')
    parser.add_argument(
        '--portion',  help='float variable, the portion of images choosen, like 0.3, default = 1.0,', default=1.0, type=float)
    return parser.parse_args()


# string.upper()的用法
def checkFileIsImags(filePath):
    if ('JPEG' in filePath.upper()) or ('JPG' in filePath.upper()) \
            or ('PNG' in filePath.upper()) or ('BMP' in filePath.upper()):
        return True
    return False

def tarverse(path):
    '''
    遍历文件夹，获得所有的图片路径
    '''
    allImageList = []
    labels = []
    for parent, dirnames, filenames in os.walk(path):
        if dirnames:
            labels = dirnames
        for file in filenames:
            imagePathName = os.path.join(parent, file)
            if checkFileIsImags(imagePathName):
                allImageList.append(imagePathName)
            else:
                print("%s isn't image"%(imagePathName))
    return allImageList, labels


def generate_with_labels(allImageList, labels, sort=None):
    '''
    将每个类别的图片分别存储在一个dict中
    '''
    # 构建每一个类别的字典，用于存储图片地址
    categorys= dict()
    for label in labels:
        categorys[label] = []

    for imageList in allImageList:
        prefix, img = os.path.split(imageList)
        lab = prefix.split('/')[-1]
        tmp = imageList.split('/')[-args.nb_prefix:]
        tmp = '/'.join(tmp)
        if lab not in labels:
            print "Error, not right label info for %s" % (imageList)
        else:
            categorys[lab].append(tmp)
    
    if sort:
        # 提取出每张图片的index序号
        for label in labels:
            prefix = []
            for item in categorys[label]:
                img = os.path.split(item)[1]
                nb_prefix = int(img.split('_')[0])
                prefix.append(nb_prefix)
            categorys[label] = [x for _, x in sorted(
                                zip(prefix, categorys[label]), key=lambda pair: pair[0])]

    return categorys

def write_to_each_category(labels, categorys, portion=1.0):
    '''
    分别生成每个类别的index list
    '''
    for label in labels:
        filename = label + '.lst'
        filename = os.path.join(args.output, filename)
        print "Start: " + label
        with open(filename, 'w') as f:
            length = len(categorys[label])
            for i in range(int(length * portion)):
                tmp = categorys[label][i]
                label_index = label.split('_')[0]
                f.write(tmp + ' ' + label_index)
                f.write('\n')

def write_to_total_list(labels, categorys, output ,portion=1.0):
    '''
    生成所有图片的index_list
    由于index list是有序的，训练时注意要shuffle
    '''
    #filename = 'total.lst'
    #filename = os.path.join(args.output, filename)
    filename = output
    print "Start: Total index list"
    with open(filename, 'w') as f:
        for label in labels:
            length = len(categorys[label])
            for i in range(int(length * portion)):
                tmp = categorys[label][i]
                label_index = label.split('_')[0]
                f.write(tmp + ' ' + label_index)
                f.write('\n')

def main():
    allImageList, labels = tarverse(args.root)
    categorys = generate_with_labels(allImageList, labels, args.sort)

    write_to_each_category(labels, categorys, args.portion)
    write_to_total_list(labels, categorys, args.output, args.portion)

if __name__ == '__main__':
    args = parse_args()
    print "Start processing"
    allImageList, labels = tarverse(args.root)
    categorys = generate_with_labels(allImageList, labels, args.sort)
    if args.mode == 1:
        write_to_total_list(labels, categorys, args.output, args.portion)
    else:
        write_to_each_category(labels, categorys, args.portion)
    print "...done"
