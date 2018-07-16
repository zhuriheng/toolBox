# -*- coding:utf-8 -*-
# created 2018/05/12 @Riheng
# 下载图片

import os
import argparse
import sys
import json
import datetime
import cv2
import numpy as np

from collections import Counter, defaultdict
from cfg import CATEGORYS

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

def valid_image(img_path):
    image = cv2.imread(img_path)
    if np.shape(image) != () and np.shape(image)[2] != 4:
        return True
    else:
        return False

def create_folder_tree(root, categorys, tree_name):
    '''
    创建层级目录结构
    -- cls_root
        -- tree_name  # test, train or val
            -- 48_guns
            -- 50_isis_flag
            ...
    '''
    if not os.path.exists(root):
        os.makedirs(root)

    directory = os.path.join(root, tree_name)
    if not os.path.exists(directory):
        os.makedirs(directory)

    for (categ, index) in categorys.items():
        #categ = '_'.join(categ.split(' '))
        #categ_folder = str(index) + '_' + categ
        label_dir = os.path.join(directory, categ)
        if not os.path.exists(label_dir):
            os.makedirs(label_dir)

def get_url_label(json_lists):
    result = defaultdict(list)
    for json_list in json_lists:
        if json_list['label'] and json_list['label'][0]['data']:
            url = json_list['url']
            label = json_list['label'][0]['data'][0]['class']
            result[label].append(url)
    return result

def download(url, output_path):
    flag = True
    try:
        if not os.path.exists(output_path):
            if os.system('wget -O {} {}'.format(output_path, url)) != 0:
                print('download error:', url)
                flag = False
    except all as e:
        print('download error:', url)
        flag = False
    return flag

def parse_args():
    parser = argparse.ArgumentParser(description='解析json文件，下载图片')
    parser.add_argument('input', help='input json file', type=str)
    parser.add_argument('download_path', help='download images path', type=str)
    return parser.parse_args()

args = parse_args()

def main():
    input_json = args.input
    # 获取当日日期
    now = datetime.datetime.now()
    day = now.strftime("%m%d")
    time = now.strftime("%m%d%H%M")

    create_folder_tree(args.download_path, CATEGORYS, 'train')

    json_lists = load_json(input_json)
    result = get_url_label(json_lists)
    
    download_err_urls = [] # 存储下载失败的url
    not_valid_img_urls = [] # 存储无效图片，cv2读图势必啊
    name_map_list = [] # 存储图片的原始名字，以及下载后的名字
    for label in result.keys():
        num = 0 # 对每个类别的图片计数
        for url in result[label]:
            name_map = {}
            ori_filename = url.split('/')[-1]
            new_filename = '{}_{}_{}.jpg'.format(label, day, num)
            name_map['ori_image_name'] = url
            name_map['new_image_name'] = new_filename
            output_path = os.path.join(
                args.download_path, 'train', label, new_filename)
            
            # 下载图片
            flag = download(url, output_path)
            if flag:
                if valid_image(output_path):
                    num += 1
                    name_map_list.append(name_map)
                else:
                    not_valid_img_urls.append(url)
            else:
                download_err_urls.append(url)

    output_name_map = os.path.join(
        args.download_path, 'name_map_{}.json'.format(time))
    write_to_json(name_map_list, output_name_map)

    #************ print information *******************
    err_ulrs = len(download_err_urls)
    print 'Total error number: ' + str(err_ulrs)
    print download_err_urls
    print '*' * 60
    not_vaild = len(not_valid_img_urls)
    print 'Total unvalid images number: ' + str(not_vaild)
    print not_valid_img_urls
    print '*' * 60
    total = len(json_lists)
    success = total - err_ulrs - not_vaild
    print 'Successful images number: ' + str(success)
    #*******************************************

if __name__ == '__main__':
    print 'Start process'
    main()
    print 'End ...'
