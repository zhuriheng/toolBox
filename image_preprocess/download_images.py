# -*- coding:utf-8 -*-
# created 2018/05/12 @Riheng
# 下载图片

import os
import argparse
import sys
import json

from collections import Counter, defaultdict


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


def create_folder_tree(root, categorys):
    '''
    创建层级目录结构
    -- cls_root
        -- test
            -- 48_guns
            -- 50_isis_flag
            ...
    '''
    if not os.path.exists(root):
        os.makedirs(root)

    test_dir = os.path.join(root, 'test')
    if not os.path.exists(test_dir):
        os.makedirs(test_dir)

    for (categ, index) in categorys.items():
        for temp in [test_dir]:
            #categ = '_'.join(categ.split(' '))
            #categ_folder = str(index) + '_' + categ
            label_dir = os.path.join(temp, categ)
            if not os.path.exists(label_dir):
                os.makedirs(label_dir)

def get_url_label(json_lists):
    result = {}
    for json_list in json_lists:
        if json_list['label'] and json_list['label'][0]['data']:
            url = json_list['url']
            label = json_list['label'][0]['data'][0]['class'][0] # 临时性修改
            result[url] = label
    return result

def download(url, output_path, err_num):
    try:
        # commands.getoutput('wget -O {} {}'.format(output_path, url))
        if os.system('wget -O {} {}'.format(output_path, url)) != 0:
            print('download error:', url)
            err_num += 1
    except all as e:
        print('download error:', url)
        err_num += 1
    return err_num

def parse_args():
    parser = argparse.ArgumentParser(description='解析json文件，下载图片')
    parser.add_argument('--input-json', help='input json file', type=str)
    parser.add_argument('--download-path', help='download images path', type=str)
    return parser.parse_args()

args = parse_args()

def main():
    input_json = args.input_json
    # labels的信息
    categorys = {'0_bk_bloodiness_human': 0, '1_bk_bomb_fire': 1, '2_bk_bomb_smoke': 2,
                 '3_bk_bomb_vehicle': 3, '4_bk_bomb_self-burning': 4, '5_bk_beheaded_isis': 5,
                 '6_bk_beheaded_decollation': 6, '7_bk_march_banner': 7, '8_bk_march_crowed': 8,
                 '9_bk_fight_police': 9, '10_bk_fight_person': 10}
                 # '11_sen_character': 11,
                 #'12_sen_masked': 12, '13_sen_army': 13, '14_sen_scene_person': 14,
                 #'15_sen_anime_likely_bloodiness': 15, '16_sen_anime_likely_bomb': 16, '17_sen_Islamic_dress': 17}

    create_folder_tree(args.download_path, categorys)

    json_lists = load_json(input_json)
    result = get_url_label(json_lists)
    
    err_num = 0
    for (url, label) in result.items():
        filename = url.split('/')[-1]
        if filename.split('.')[-1] != 'jpg':
            filename = filename + '.jpg'
        output_path = os.path.join(args.download_path, 'test', label, filename)
        download(url, output_path, err_num)
    print 'Total error num:' + str(err_num)

if __name__ == '__main__':
    print 'Start process'
    main()
    print 'End ...'
