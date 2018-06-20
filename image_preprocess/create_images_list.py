# -*- coding: utf-8 -*-
#
# Created on 2018/04/04 @Riheng
# Traverse the folder and generate the index
# 版本更新：
#   V1.1 在图片地址后面增加label信息 2018/04/05

from __future__ import with_statement
import os
import argparse
import datetime

from collections import defaultdict
'''
actionFlag : 功能flag
    1  : 从本地读取图片生成image list + index
        --root  图片地址根目录 [required] [optional][default=False]
        --with_label_idx 是否在图片后加上label index 
        --output  输出文件, <root>/images.lst by default [optional][default=<root>/images.lst]
        --nb_prefix -np 图片地址目录的级数 [optional][default=2]
        --suffix 是否添加suffix [optional][default=False]
        --readme 是否生成readme.txt文件 add --readme for True [optional][default=False]
    
'''

def parse_args():
    parser = argparse.ArgumentParser(
        description='Traverse the folder and generate the index')
    #parser.add_argument('--actionFlag', required=True,
    #                    help = '1: create image list with label index; 2: without label index', 
    #                    type=int, choices=[1, 2])
    parser.add_argument('--root', 
                        help='root path', default=None, type=str)
    parser.add_argument('--with_label_idx', help='add label index', action='store_true')
    parser.add_argument('--output',
                        help='output file name', type=str)
    parser.add_argument(
        '-np', '--nb_prefix', help='number of prefix, default=2', default=2, type=int)
    parser.add_argument(
        '--suffix', help='whether to add suffix, add --suffix for True  ', action='store_true')
    parser.add_argument(
        '--readme', help='whether to generate readme.txt, add --readme for True', action='store_true')
    #parser.add_argument('--mode', choices=[1, 2], default=1, type=int,
    #                    help='mode 1: generate total index; 2: generate index for each category, default = 1')
    #parser.add_argument('-s','--sort', help='whether sort index', action='store_true')
    #parser.add_argument(
    #    '--portion',  help='float variable, the portion of images choosen, like 0.3, default = 1.0,', default=1.0, type=float)
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
    for parent, _, filenames in os.walk(path):
        for file in filenames:
            imagePathName = os.path.join(parent, file)
            #临时更改
            if imagePathName[-2:] == '==':
                newImagePathName = imagePathName + '.jpg'
                cmdStr = "mv %s %s" % (imagePathName, newImagePathName)
                print cmdStr
                #result_flag = os.system(cmdStr)

            if checkFileIsImags(imagePathName):
                allImageList.append(imagePathName)
            else:
                print("%s isn't image"%(imagePathName))
    return allImageList

def generate_with_labels(allImageList, sort=None):
    '''
    将每个类别的图片分别存储在一个dict中
    category:
        key: label
        value: image name
    '''
    # 构建每一个类别的字典，用于存储图片地址
    categorys= defaultdict(list)

    for imageList in allImageList:
        prefix, _ = os.path.split(imageList)
        label = prefix.split('/')[-1]
        tmp = imageList.split('/')[-args.nb_prefix:]
        tmp = '/'.join(tmp)
        categorys[label].append(tmp)
    '''
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
    '''
    return categorys

def write_each_category(categorys, portion=1.0):
    '''
    分别生成每个类别的index list
    '''
    for label in categorys.keys():
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

def write_total_category(categorys, output, portion=1.0, with_label=True):
    '''
    生成所有图片的index_list
    由于index list是有序的，训练时注意要shuffle
    '''
    with open(output, 'w') as f:
        for label in categorys.keys():
            length = len(categorys[label])
            for i in range(int(length * portion)):
                tmp = categorys[label][i]
                if not args.suffix:
                    tmp = os.path.splitext(tmp)[0]
                if with_label:
                    label_index = label.split('_')[0]
                    f.write(tmp + ' ' + label_index + '\n')
                else:
                    f.write(tmp + '\n')


def generate_readme(categorys, fname):
    # 按照类别的index对类别排序
    keys = categorys.keys()
    keys_sort = sorted(keys, key=lambda k: int(k.split('_')[0]))

    now = datetime.datetime.now()
    time = now.strftime("%D")

    with open(fname, 'w') as f:
        f.write("Label information:\n\n")
        for label in keys_sort:
            count = len(categorys[label])
            info = "%s \t count: %d" % (label,count)
            f.write(info + '\n')
        f.write('\n')
        f.write("Author: %s\n" % ('zhuriheng'))
        f.write("Time: %s\n" % (time))

args = parse_args()
def main():
    # actionFlag = args.actionFlag
    print '--------' * 8

    allImageList = tarverse(args.root) 
    categorys = generate_with_labels(allImageList)
    output = args.output if args.output else os.path.join(args.root, 'images.lst')

    if args.with_label_idx:
        print "create image list with label index"
        write_total_category(categorys, output)
    else:
        print "create image list without label index "
        write_total_category(categorys, output, with_label=False)
    if args.readme:
        fname = os.path.join(args.root, 'readme.txt')
        generate_readme(categorys, fname)

if __name__ == '__main__':
    print "Start processing"
    main()
    print "...done"
