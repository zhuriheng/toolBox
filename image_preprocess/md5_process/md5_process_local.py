# -*- coding:utf-8 -*-
# created 2018/03/29 @Riheng
# 从本地读取图片，计算图片的md5值


'''
    从本地读取图片，计算图片的md5值,并将重复的图片去除:
        -input, --inputImagesPath  [required]
        -dup, --duplicationDir  [optional]
        -mv whether to move the duplication image, store_true [optional]

'''

import os, sys
import argparse
import hashlib
import json

# 使用argparse
def parse_args():
    parser = argparse.ArgumentParser(description="md5 process check image")
    parser.add_argument('-input', '--inputImagesPath', dest='inputImagesPath')
    parser.add_argument('-dup', '--duplicationDir', dest='duplicationDir')
    parser.add_argument(
        '-mv', '--move', help='whether to move the duplication image', action='store_true')
    # save md5 file 
    parser.add_argument('--md5_file', dest='md5_file', action='store_true')
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


# hashlib.md5()
def md5_process(image=None):
    hash_md5 = hashlib.md5()
    with open(image, 'rb') as f: 
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def mv_same_md5_file(one, two, duplicationDir):
    if(os.path.exists(duplicationDir)) == False:
        os.makedirs(duplicationDir)
    cmdStr = "mv %s %s" % (two, duplicationDir)
    result_flag = os.system(cmdStr)
    print cmdStr


def write_json(md5_imagaPath_dict, output):
    # 输出到文件中
    with open(output, 'w') as fi:
        for md5_key, url in md5_imagaPath_dict.items():
            temp = {'url': url, 'md5': md5_key}
            json.dump(temp, fi)
            fi.write('\n')

        #json.dump(hash_dic, f)  # 不使用indent

args = parse_args()
def main():
    allImagesPathList = getAllImages(basePath=args.inputImagesPath)
    md5_imagaPath_dict = {}
    for imagePath in allImagesPathList:
        md5_key = md5_process(imagePath)
        if md5_key in md5_imagaPath_dict:
            print("%s --- %s same md5_key" %
                  (imagePath, md5_imagaPath_dict.get(md5_key)))
            if args.move:
                mv_same_md5_file(one=md5_imagaPath_dict.get(
                    md5_key), two=imagePath, duplicationDir=args.duplicationDir)
        else:
            md5_imagaPath_dict[md5_key] = imagePath
    
    # 将md5值存储下来
    if args.md5_file:
        output = os.path.join(args.inputImagesPath, 'md5.json')
        write_json(md5_imagaPath_dict, output)
        print("Generate %s with success" % (output))

    print("Images number: %d" % (len(allImagesPathList)))
    print("Duplication images number: %d " %
          (len(allImagesPathList) - len(md5_imagaPath_dict)))
    print("Images number after deduplication: %d " % (len(md5_imagaPath_dict)))



if __name__ == '__main__':
    print 'Start processing'
    main()
    print 'End ...'
