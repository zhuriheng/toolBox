# -*- coding:utf-8 -*-
# created 2018/04/04 @Riheng

from __future__ import with_statement
import os, sys
import argparse
import hashlib

'''
    从本地depot读取图片，计算图片的md5值,作为底库; 
    从本地2读取图片，计算md5值，并与底库比对。将重复的图片从本地2中移除.
        -dep depot image root path [required]
        -targ target image root path [required]
        -dup the path for saving duplication images [required]
        -mv whether to move the duplication image, store_true [optional]

'''



def parse_arg():
    parser = argparse.ArgumentParser(description='md5 process check image between db1 and db2')
    parser.add_argument('-dep', '--depot', help='depot image root path', type=str)
    parser.add_argument('-targ', '--target', help='target image root path', type=str)
    parser.add_argument('-dup', '--duplication', help='the path for saving duplication images', type=str)
    parser.add_argument('-mv', '--move', help='whether to move the duplication image', action='store_true')
    return parser.parse_args()

def checkIsImage(filePath):
    suffix = os.path.splitext(filePath)[1]
    if ('.JPG' == suffix.upper()) or ('.PNG' == suffix.upper()) \
        or ('.JPEG' == suffix.upper()) or ('.BMP' == suffix.upper()):
        return True
    return False

def getAllImageList(path):
    '''
    返回所有的图片地址
    '''
    path = os.path.abspath(path)
    allImageList = []
    for parent, dirnames, filenames in os.walk(path):
        for file in filenames:
            imagePathName = os.path.join(parent, file)
            if checkIsImage(imagePathName):
                allImageList.append(imagePathName)
            else:
                print '%s is not image.' % (imagePathName)
    return allImageList

# hashlib.md5()
def md5_process(image=None):
    hash_md5 = hashlib.md5()
    with open(image, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()
                        

def move_same_md5_image(duplication_path, filePath):
    if not os.path.exists(duplication_path):
        os.mkdir(duplication_path)
    cmdStr = 'mv %s %s' % (filePath, duplication_path)
    result_flag = os.system(cmdStr)
    print cmdStr
    

def compare(depot_path, target_path, duplication_path):
    '''
    比较目标数据库中是否有图片与底库中的图片有相同的md5值
    '''
    # 生成底库的md5字典
    print 'depot md5 process'
    depotImageList = getAllImageList(depot_path)
    md5_depot = dict()
    for imageList in depotImageList:
        md5_key = md5_process(imageList)
        md5_depot[md5_key] = imageList
    # 生成目标地址的md5字典
    print 'target md5 process'
    targetImageList = getAllImageList(target_path)
    nb_dup = 0
    for imageList in targetImageList:
        md5_key = md5_process(imageList)
        if md5_depot.has_key(md5_key):
            nb_dup += 1
            print '%s -- %s same md5 value' % (imageList,
                                               md5_depot.get(md5_key))
            if args.move:
                move_same_md5_image(duplication_path, imageList)
        else:
            md5_depot[md5_key] = imageList
    print 'Initial target images number: ' + str(len(targetImageList))
    print 'Duplication image number: ' + str(nb_dup)
    print 'Final target images number: ' + str(len(targetImageList) - nb_dup)


args = parse_arg()
def main():
    depot_path = args.depot
    target_path = args.target
    duplication_path = args.duplication
    compare(depot_path, target_path, duplication_path)

if __name__ == '__main__':
    print 'Start processing'
    main()
    print 'End ...'

