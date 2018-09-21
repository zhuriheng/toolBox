# -*- coding:utf-8 -*-
# created 2018/05/12 @Riheng
# 下载图片

'''
Version:
    - V1.1 09/02/18 support download with multiple process

Todo:
    - fix bug of create <name_map_list> file
    - a better realization of re-wget
    - support download with multiple thread
'''

import os
import argparse
import sys
import json
import datetime
import cv2
import numpy as np
import time

from multiprocessing import Pool
from collections import Counter, defaultdict
from cfg import CATEGORYS
from functools import partial

download_err_urls = []  # 存储下载失败的url
not_valid_img_urls = []  # 存储无效图片，cv2读图势必啊
name_map_list = []  # 存储图片的原始名字，以及下载后的名字


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
    print("save file: {}".format(output))


def write_to_list(lists, output):
    with open(output, 'w') as f:
        for line in lists:
            f.write('{}\n'.format(line))
    print("save file: {}".format(output))


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
    labels_images = defaultdict(list)
    for json_list in json_lists:
        if json_list['label'] and json_list['label'][0]['data']:
            url = json_list['url']
            label = json_list['label'][0]['data'][0]['class']
            labels_images[label].append(url)
    return labels_images


def download(url, output_path):
    flag = True
    try:
        if not os.path.exists(output_path):
            cmd = 'wget  --retry-connrefused --waitretry=1 --read-timeout=10 --timeout=10 -t 10 -O {} {}'.format(
                output_path, url)
            if os.system(cmd) != 0:
                print('download error:', url)
                flag = False
    except all as e:
        print('download error:', url)
        flag = False
    return flag


def download_images_with_same_label(label, labels_images, day, download_path):
    global download_err_urls
    global not_valid_img_urls
    global name_map_list

    num = 0  # 对每个类别的图片计数
    for url in labels_images[label]:
        name_map = {}
        ori_filename = url.split('/')[-1]
        new_filename = '{}_{}_{}.jpg'.format(label, day, num)
        name_map['ori_image_name'] = url
        name_map['new_image_name'] = new_filename
        output_path = os.path.join(
            download_path, 'train', label, new_filename)

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


def parse_args():
    parser = argparse.ArgumentParser(description='通过json制作数据集')
    parser.add_argument('input', help='input json file', type=str)
    parser.add_argument('download_path', help='download images path', type=str)
    return parser.parse_args()

args = parse_args()

def main():
    global download_err_urls
    global not_valid_img_urls
    global name_map_list

    input_json = args.input
    start_time = time.time()
    # 获取当日日期
    now = datetime.datetime.now()
    day = now.strftime("%m%d")
    date = now.strftime("%m%d%H%M")

    create_folder_tree(args.download_path, CATEGORYS, 'train')

    images_jsons_lists = load_json(input_json)
    labels_images = get_url_label(images_jsons_lists)

    label_list = labels_images.keys()

    pool = Pool(processes=8)
    pool.map(partial(download_images_with_same_label,
                     labels_images=labels_images, day=day,
                     download_path=args.download_path), label_list)
    pool.close()
    pool.join()

    print 'processes done'

    output_name_map = os.path.join(
        args.download_path, 'name_map_{}.json'.format(date))
    write_to_json(name_map_list, output_name_map)

    download_err_urls_output = os.path.join(
        args.download_path, 'download_error_url_{}.lst'.format(date))
    write_to_list(download_err_urls, download_err_urls_output)

    not_valid_img_urls_output = os.path.join(
        args.download_path, 'not_valid_images_{}.lst'.format(date))
    write_to_list(not_valid_img_urls, not_valid_img_urls_output)

    #************ print information *******************
    err_ulrs = len(download_err_urls)
    print 'Total error number: ' + str(err_ulrs)
    print download_err_urls
    print '*' * 60
    not_vaild = len(not_valid_img_urls)
    print 'Total unvalid images number: ' + str(not_vaild)
    print not_valid_img_urls
    print '*' * 60
    total = len(images_jsons_lists)
    success = total - err_ulrs - not_vaild
    print 'Successful images number: ' + str(success)

    print 'Done! Time taken: {}'.format(time.time() - start_time)
    #*******************************************


if __name__ == '__main__':
    print 'Start process'
    main()
    print 'End ...'
