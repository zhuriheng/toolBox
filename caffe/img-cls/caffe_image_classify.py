#coding=utf-8

import argparse
import json
import os
import sys
import time
import datatime
from collections import OrderedDict

import cv2
import numpy as np

sys.path.insert(0, 'caffe/python')
import caffe

def init_models(weight, deploy, gpu=0):
    """
    initialization caffe model 
        :param gpu: gpu id, 0 by default
        :param weight: weight of caffemodel
        :param deploy: deploy.prototxt
    """
    caffe.set_mode_gpu()
    caffe.set_device(gpu)

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


def label_correspond(label_corres_list, dict_results):
    """
    docstring here
        :param label_corres_list: 
        :param dict_results: 
    """
    label_map = {}   # label的映射map
    for line in label_corres_list:
        ori_label = line.split(' ')[0]
        corres_label = line.split(' ')[1]
        label_map[ori_label] = corres_label

    for (img_name,results) in dict_results.iteritems():
        corres_label = label_map[results['Top-1 Class']]
        dict_results[img_name].update({'Top-1 Class': corres_label})
        dict_results[img_name].update({'Top-1 Index': int(corres_label.split('_')[0])})

        output_prob = results['Confidence']
        corres_prob = []
        corres_prob.append(output_prob[0])
        corres_prob.append(max(float(output_prob[i]) for i in range(1, 5)))
        corres_prob.append(max(float(output_prob[i]) for i in range(5, 7)))
        corres_prob.append(max(float(output_prob[i]) for i in range(7, 9)))
        corres_prob.append(max(float(output_prob[i]) for i in range(9, 11)))
        corres_prob.append(output_prob[11])
        corres_prob.append(output_prob[12])
        corres_prob.append(output_prob[13])
        corres_prob.append(output_prob[14])
        corres_prob.append(output_prob[15])
        corres_prob.append(output_prob[16])
        corres_prob.append(output_prob[17])
        corres_prob.append(max(float(output_prob[i]) for i in range(18, 48)))

        dict_results[img_name].update({'Confidence': [str(i) for i in list(corres_prob)]})
    return dict_results


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
        img = img.astype(np.float32, copy=True)
        img = cv2.resize(img, (256, 256))
        # img = img.astype(np.float32, copy=True)
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
    parser.add_argument('--weight', help='caffemodel', type=str, required=True)
    parser.add_argument('--deploy', help='deploy.prototxt',type=str, required=True)
    parser.add_argument('--gpu', help='gpu id', type=int, required=True)
    parser.add_argument('--labels', help='labels list',type=str, required=True)
    parser.add_argument('--labels_corres', help='labels correspond list', type=str, required=False)
    parser.add_argument('--img_list', help='input image list',type=str, required=False)
    parser.add_argument('--root', help='data root for image',type=str, required=False)
    parser.add_argument('--url_list', help='input image url list', type=str, required=False)
    parser.add_argument('--img', help='input image, inference for single local image', type=str, required=False)
    
    return parser.parse_args()

def main():
    args = parse_arg()
    
    net_cls = init_models(args.weight, args.deploy, args.gpu)

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
    
    if args.labels_corres:
        label_corres_list = np.loadtxt(args.labels_corres, str, delimiter='\n')
        dict_results = label_correspond(label_corres_list, dict_results)

    now = datatime.datatime.now()
    output = os.path.join(args.root, 'results_%s.json' % (now.strftime("%m%d%H%M")))
    
    with open(output, 'w') as f:
        json.dump(dict_results, f, indent=4)

if __name__ == '__main__':
    print('Start caffe image classify:')
    main()
    print('End process.')
