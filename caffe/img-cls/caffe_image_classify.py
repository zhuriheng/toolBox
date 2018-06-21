#coding=utf-8

import argparse
import time
import json
import os
import sys

import cv2
import numpy as np

sys.path.insert(0, 'caffe/python')
import caffe

from collections import OrderedDict


def init_models(weight, deploy, gpu_id=0):
    """
    initialization caffe model 
        :param gpu_id: gpu id, 0 by default
        :param weight: weight of caffemodel
        :param deploy: deploy.prototxt
    """
    caffe.set_mode_gpu()
    caffe.set_device(gpu_id)

    net_cls = caffe.Net(deploy, weight, caffe.TEST)

    return net_cls

# center_crop的具体效果
def center_crop(img, crop_size):
    """
    docstring here
        :param img: 
        :param crop_size: 
    """
    short_edge = min(img.shape[:2])
    if short_edge < crop_size:
        return 
    yy = int((img.shape[0] - crop_size) / 2)
    xx = int((img.shape[1] - crop_size) / 2)
    return img[yy:yy + crop_size, xx: xx + crop_size] 

def single_img_process(net_cls, img_path, ori_img, label_list):
    """
    docstring here
        :param net_cls: 
        :param img_path: 
        :param ori_img: 
        :param label_list: 
    """
    img = cv2.imread(os.path.join(img_path, ori_img))
    if np.shape(img) != () and np.shape(img)[2] != 4:
        start_time = time.time()
        img = cv2.resize(img, (256, 256))
        img = img.astype(np.float32, copy=True)
        img -= np.array([[[103.94, 116.78, 123.68]]])
        img = img * 0.017

        img = center_crop(img, 225)
        
        img = img.transpose((2, 0, 1))
        end_time = time.time()
        print('Image preprocess speed: {:.3f}s / iter'.format(end_time - start_time))

        net_cls.blobs['data'].data[...] = img
        output = net_cls.forward()
        output_prob = np.squeeze(output['prob'][0])

        index_list = output_prob.argsort()
        rate_list = output_prob[index_list]

        list_result = []
        result_dict = OrderedDict()
        result_dict['File Name'] = ori_img
        result_dict['Top-1 Index'] = index_list[-1]
        result_dict['Top-1 Class'] = label_list[int(index_list[-1])].split(' ')[1]

        result_dict['Confidence'] = [str(i) for i in list(output_prob)]
        list_result.append(result_dict)

    return list_result



def parse_arg():
    parser = argparse.ArgumentParser(description='caffe image classify')
    parser.add_argument('--weight', help='caffemodel', type=str)
    parser.add_argument('--deploy', help='deploy.prototxt', type=str)
    parser.add_argument('--gpu_id', help='gpu id', type=int)
    parser.add_argument('--labels', help='labels list', type=str)
    parser.add_argument('--img_list', help='input image list', type=str)
    parser.add_argument('--root', help='data root for image', type=str)
    parser.add_argument('--url_list', help='input image url list', type=str)
    parser.add_argument(
        '--img', help='input image, inference for single local image', type=str)
    return parser.parse_args()

def main():
    args = parse_arg()
    
    net_cls = init_models(args.weight, args.deploy, args.gpu_id)

    label_list = np.loadtxt(args.labels, str, delimiter='\n')
    img_list = np.loadtxt(args.img_list, str, delimiter='\n')

    dict_results = {}

    for i in range(len(img_list)):
        start_time = time.time()
        dict_result = single_img_process(
            net_cls, args.root, img_list[i], label_list)
        end_time = time.time()
        print('Inference speed: {:.3f}s / iter'.format(end_time - start_time))
        for item in dict_result:
            dict_results[os.path.basename(item['File Name'])] = item
    
    with open('log.json', 'w') as f:
        json.dump(dict_results, f, indent=4)

if __name__ == '__main__':
    print('Start caffe image classify:')
    main()
    print('End process.')
