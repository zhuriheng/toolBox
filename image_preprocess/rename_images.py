# -*- coding:utf-8 -*-
# created 2018/04/13 @Riheng
# modified 2018/05/23 @Riheng
# 修改图片的名字

import os
import sys
import argparse
import hashlib
import json
import cv2
import numpy as np

from collections import defaultdict

'''
修改图片的名字,统一名字为 "prefix_date_index_suffix.jpg”,并且去除坏图
    --inputImagesPath 图片存储路径 [required]
    --date 时间  [default: 1234]
    --prefix 图片前缀，默认为label的名字
    --suffix 图片后缀
    --ext 图片的格式 [default=jpg]
'''

def parse_args():
    parser = argparse.ArgumentParser(description="md5 process check image")
    parser.add_argument('--inputImagesPath', type=str, required=True)
    parser.add_argument('--date', type=str, default='1234',help='time')
    parser.add_argument('--prefix', type=str, help='图片前缀，默认为label的名字')
    parser.add_argument('--suffix', type=str, help='图片后缀')
    parser.add_argument('--ext', type=str, default='jpg', help='图片的格式')
    return parser.parse_args()


def checkValidImages(filePath):
    try:
        img = cv2.imread(filePath)
    except:
        img = None
    if np.shape(img) == ():
        print("ERROR INFO : %s can't read" % (filePath))
        return False
    return True


def checkFileIsImages(filePath):
    if ('JPEG' in filePath.upper()) or ('JPG' in filePath.upper()) \
            or ('PNG' in filePath.upper()) or ('BMP' in filePath.upper()):
        return True
    return False

# os.walk()获得多层路径所有的图片
def getAllImages(basePath=None):
    allImageList = []
    for parent, dirnames, filenames in os.walk(basePath):
        for file in filenames:
            imagePathName = os.path.join(parent, file)
            if checkFileIsImages(imagePathName) and checkValidImages(imagePathName):
                allImageList.append(imagePathName)
            else:
                # print("%s isn't image"%(imagePathName))
                pass
    return allImageList

# os.walk()获得多层路径所有的图片


def getAllImagesWithGroup(basePath=None):
    '''
    获得所有类别目录下的所有图片，并且以字典的形式返回图片路径
    '''
    allImageListWithGroup = defaultdict(list)
    for parent, dirnames, filenames in os.walk(basePath):
        for file in filenames:
            imagePathName = os.path.join(parent, file)
            if checkFileIsImages(imagePathName) and checkValidImages(imagePathName):
                allImageListWithGroup[dirnames].append(imagePathName)
            else:
                # print("%s isn't image"%(imagePathName))
                pass
    return allImageListWithGroup


def rename_image(original_name, new_name):
    cmdStr = "mv %s %s" % (original_name, new_name)
    print cmdStr
    result_flag = os.system(cmdStr)


def rename_process_with_label(allImageListWithGroup, date, prefix, suffix, ext):
    for label in allImageListWithGroup.keys():
        num = 0
        for imagePath in allImageListWithGroup[label]:
            path_prefix = os.path.split(imagePath)[0]
            prefix = label
            new_name = prefix + '_{}_{:0>8}' + \
                suffix + '.' + ext
            new_name.format(date, num)
            num += 1
            rename_image(imagePath, os.path.join(path_prefix, new_name))

def rename_process(allImagesPathList):
    for imagePath in allImagesPathList:
        # 获得图片的label信息
        imagePath = os.path.abspath(imagePath)
        image_name, suffix = os.path.splitext(imagePath)
        path_prefix = os.path.split(imagePath)[0]
        label = path_prefix.split('/')[-1]
        # 定义图片的新名字
        new_name = image_name + '.jpg'
        original_name = imagePath
        if suffix != '.jpg':
            rename_image(original_name, new_name)
    

args = parse_args()
def main():
    prefix = "" if not args.prefix else args.prefix
    suffix = "" if not args.suffix else args.suffix

    #allImagesPathList = getAllImages(basePath=args.inputImagesPath)
    #rename_process(allImagesPathList)
    allImageListWithGroup = getAllImagesWithGroup(
        basePath=args.inputImagesPath)
    rename_process_with_label(allImageListWithGroup, args.date, prefix, suffix, args.ext)

if __name__ == '__main__':
    print 'Start processing'
    main()
    print 'End ...'
