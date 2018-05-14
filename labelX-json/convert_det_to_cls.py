# -*- coding:utf-8 -*-
# created 2018/05/11 @Riheng
# 将pascal voc格式的检测数据转换为分类数据

import os
import argparse
import xml.dom.minidom
import sys
import json

from collections import Counter

'''
    将pascal voc格式的检测数据转换为分类数据
        --det-root pascal voc格式数据的根目录 [required]
        --cls-root 分类格式数据的根目录 [required]
'''

def xml_parser(xml_file):
    '''
    读取xml中的annotation数据
    '''
    try:
        DOMTree = xml.dom.minidom.parse(xml_file)
        collection = DOMTree.documentElement
        imgname = str(collection.getElementsByTagName("filename")[0].childNodes[0].data)
        assert imgname.split('.')[0] == os.path.split(xml_file)[1].split('.')[0]
        # detection info
        objects = collection.getElementsByTagName('object')
        detections = []
        for object in objects:
            bbox = {}
            class_name = str(object.getElementsByTagName('name')[0].childNodes[0].data)
            xmin = str(object.getElementsByTagName('xmin')[0].childNodes[0].data)
            ymin = str(object.getElementsByTagName('ymin')[0].childNodes[0].data)
            xmax = str(object.getElementsByTagName('xmax')[0].childNodes[0].data)
            ymax = str(object.getElementsByTagName('ymax')[0].childNodes[0].data)
            bbox['class'] = class_name
            bbox['bbox'] = [
    			     [float(xmin), float(ymin)],
    			     [float(xmax), float(ymin)],
        			 [float(xmax), float(ymax)],
        			 [float(xmin), float(ymax)]
            ]
            detections.append(bbox)
        return 'success', detections
    except Exception as e:
        print "XML analyze ERROR"
        return 'fail', detections

def calculate_square(bbox):
    xmin = float(bbox[0][0])
    xmax = float(bbox[1][0])
    ymin = float(bbox[0][1])
    ymax = float(bbox[2][1])
    return (xmax - xmin) * (ymax - ymin)

def convert_det_to_cls(xml_file):
    '''
    将检测数据转换为分类数据，对于多object多label的图片：
        1. object数量多的类别的为当前图片的label
        2. 在ojbets数量相同的情况下，比较bbox的总面积
    '''
    res, detections = xml_parser(xml_file)
    
    # 去除‘not terror’类别
    labels = [bbox['class'] for bbox in detections if bbox['class'] != 'not terror']

    stat_labels = Counter(labels).most_common()
    print stat_labels
    print '-----' * 8

    if len(stat_labels) == 0:
        cls_label = 'null'
    elif len(stat_labels) == 1:
        cls_label = stat_labels[0][0]
    else:
        max_count = stat_labels[0][1]
        counts = [item[1] for item in stat_labels]
        labels = [item[0] for item in stat_labels]
        indices = [id for id, count in enumerate(counts) if count == max_count]
        max_square = 0
        for indice in indices: 
            squares_total = 0
            for bbox in detections:
                label = labels[indice]
                if bbox['class'] == label:
                    squares = calculate_square(bbox['bbox'])
                    #print label
                    #print bbox['bbox']
                    #print squares
                    squares_total += squares
            #print 'Total squrate:' + str(squares_total)
            #print '-----' * 8
            if squares_total >= max_square:
                max_square = squares_total
                cls_label = label
                
    return cls_label


def get_labels(xml_list):
    img_labels = {}
    for xml in xml_list:
        img_name = os.path.split(xml)[1].split('.')[0] + '.jpg'
        print "image: %s " % img_name
        cls_label = convert_det_to_cls(xml)
        img_labels[img_name] = cls_label
        print "label:%s" % cls_label
    return img_labels

def make_xmllist(file_path):
    '''
    遍历文件获得xml的文件list
    '''
    xml_list = []
    if os.path.isdir(file_path):
        annotation_path = os.path.join(file_path, 'Annotations')
        # os.listdir()结合endswith()获得当前目录下的所有文件
        for fo in os.listdir(annotation_path):
            if fo.endswith('.xml'):
                xml_list.append(os.path.join(annotation_path, fo))
        return 'success', xml_list
    else:
        print 'file_path error'
        return 'fail', None
    

def move_detImg_to_clsImg(det_root, cls_root, img_name, prefix):
    '''
    
    '''
    # 图片的原始路径
    img_path = os.path.join(det_root, 'JPEGImages', img_name)
    # 图片的目标路径
    dest_path = os.path.join(cls_root, prefix, img_name)
    # 复制图片
    cmdStr = 'cp %s %s' % (img_path, dest_path)
    result_flag = os.system(cmdStr)
    print cmdStr
    

def create_folder_tree(root, categorys):
    '''
    创建层级目录结构
    -- cls_root
        -- train
            -- 48_guns
            -- 50_isis_flag
            ...
        -- val
            -- 48_guns
            -- 50_isis_flag
            ...
        -- test
            -- 48_guns
            -- 50_isis_flag
            ...
    '''
    if not os.path.exists(root):
        os.makedirs(root)

    train_dir = os.path.join(root, 'train')
    val_dir = os.path.join(root, 'val')
    test_dir = os.path.join(root, 'test')
    if not os.path.exists(train_dir):
        os.makedirs(train_dir)
    if not os.path.exists(val_dir):
        os.makedirs(val_dir)
    if not os.path.exists(test_dir):
        os.makedirs(test_dir)
    
    for (categ, index) in categorys.items():
        for temp in [train_dir, val_dir, test_dir]:
            categ = '_'.join(categ.split(' '))
            categ_folder = str(index) + '_' + categ
            label_dir = os.path.join(temp, categ_folder)
            if not os.path.exists(label_dir):
                os.makedirs(label_dir)

def parse_args():
    parser = argparse.ArgumentParser(description="将pascal voc格式的检测数据转换为分类数据")
    parser.add_argument("--det-root",  help='dataset root for pascal voc', type=str)
    parser.add_argument(
        "--cls-root",  help='dataset root for pascal voc', type=str)
    #parser.add_argument("--label", help='label file', type=str)
    return parser.parse_args()


args = parse_args()
def main():
    # labels的信息
    categorys = {'knives': 48, 'guns': 49, 'isis flag': 50, 'islamic flag': 51, 'tibetan flag': 52, 'not terror': 53}
    # 获得图片对应的label信息
    det_root = args.det_root
    res, xml_list = make_xmllist(det_root)
    if res == 'fail':
        print 'make xml list error'
    else:
        img_labels = get_labels(xml_list)
    
    # 创建分类数据集
    cls_root = args.cls_root
    create_folder_tree(cls_root, categorys)

    ## 分别处理训练集和验证集中的数据
    for name in ['train', 'val', 'test']:
        det_list = os.path.join(det_root, 'ImageSets/Main/' + name + '.txt')
        cls_list = os.path.join(cls_root,  name + '.txt')
        with open(det_list, 'r') as fo, open(cls_list, 'w') as fi:
            for line in fo:
                line = line.strip()
                img_name = line + '.jpg'
                cls_label = img_labels[img_name]
                if cls_label != 'null' and cls_label != 'not terror':
                    index = categorys[cls_label]
                    cls_label = '_'.join(cls_label.split(' '))
                    # create label_folder, like 48_guns, 51_islamic_flag
                    label_folder = str(index) + '_' + cls_label  
                    prefix = name + '/' + label_folder
                    move_detImg_to_clsImg(det_root, cls_root, img_name, prefix)
                    # create image list with label index
                    string = prefix + '/' + img_name + '  ' + str(index)
                    fi.write(string + '\n')

if __name__ == "__main__":
    print "Start process"
    main()
    print "End ..."
