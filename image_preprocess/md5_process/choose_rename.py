# -*- coding:utf-8 -*-
# created 2018/06/11 @Riheng
# 从本地读取图片，计算图片的md5值

'''
    从本地的图片库中，按照类别，每类挑一些图片，并且将图片重命名，并且记录下图片名对应的label信息
        -input, --inputImagesPath  [required]
        -dup, --duplicationDir  [optional]
        -mv whether to move the duplication image, store_true [optional]

'''

import os
import sys
import argparse
import hashlib
import json

# 使用argparse


def parse_args():
    parser = argparse.ArgumentParser(description="md5 process check image")
    parser.add_argument('--input', '--inputImagesPath', dest='inputImagesPath')

    parser.add_argument(
        '--cp', help='whether to move the duplication image', action='store_true')
    return parser.parse_args()

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


def cp_image(image, dir):
    if(os.path.exists(dir)) == False:
        os.makedirs(dir)
    cmdStr = "cp %s %s" % (image, dir)
    result_flag = os.system(cmdStr)
    print cmdStr

def add_suffix(image, suffix='.jpg'):
    cmdStr = "mv %s %s" % (image, image + suffix)
    result_flag = os.system(cmdStr)
    print cmdStr


def rename(image, suffix='.jpg'):
    cmdStr = "mv %s %s" % (image, image + suffix)
    result_flag = os.system(cmdStr)
    print cmdStr

args = parse_args()
def main():
    allImagesPathList = getAllImages(basePath=args.inputImagesPath)
    


if __name__ == '__main__':
    print 'Start processing'
    main()
    print 'End ...'
