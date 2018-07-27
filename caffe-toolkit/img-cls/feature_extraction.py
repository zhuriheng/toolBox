# coding=utf-8

from __future__ import print_function
import argparse
import json
import os
import sys
import time
import datetime
from collections import OrderedDict, defaultdict
import bcolz

import cv2
import numpy as np
import urllib

sys.path.insert(0, 'caffe/python')
import caffe


def save_array(fname, arr):
    print("Size of numpy: ", sys.getsizeof(arr))
    c = bcolz.carray(arr, rootdir=fname, mode='w')
    print("Size of carray: ", sys.getsizeof(c))
    c.flush()

def load_array(fname):
    return bcolz.open(fname)[:]

def init_models(weight, deploy, batch_size, gpu=0, image_width=225):
    """
    initialization caffe model 
        :param gpu: gpu id, 0 by default
        :param weight: weight of caffemodel
        :param deploy: deploy.prototxt
    """
    caffe.set_mode_gpu()
    caffe.set_device(gpu)

    net_cls = caffe.Net(deploy, weight, caffe.TEST)
    net_cls.blobs['data'].reshape(
        batch_size, 3, image_width, image_width)   # 3-channel (BGR) images
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


def multiple_batch_process(net_cls, img_list, label_list):
    global ERROR_IMG

    _t1 = time.time()
    for index, img in enumerate(img_list):
        try:
            img = img.astype(np.float32, copy=True)
            img = cv2.resize(img, (256, 256))
            #img = img.astype(np.float32, copy=True)
            img -= np.array([[[103.94, 116.78, 123.68]]])
            img = img * 0.017
            img = center_crop(img, 225)
            img = img.transpose((2, 0, 1))
        except Exception, e:
            print(Exception, ":", e)
            continue
        net_cls.blobs['data'].data[index] = img
    _t2 = time.time()
    print("Preprocess and load image to net: %f", _t2 - _t1)

    _t1 = time.time()
    output = net_cls.forward()
    _t2 = time.time()
    print("forward: %f", _t2 - _t1)

    lst_result = list()
    for index, output_prob in enumerate(output['prob']):
        # current batch can not satisfit batch-size argument
        if index > (len(img_list) - 1):
            continue
        output_prob = np.squeeze(output['prob'][index])
        feature = np.squeeze(net_cls.blobs['pool5'].data[index].copy()).reshape((2048))

        # sort index list & create sorted rate list
        index_list = output_prob.argsort()
        rate_list = output_prob[index_list]

        result_dict = OrderedDict()
        result_dict['Top-1 Index'] = index_list[-1]
        result_dict['Top-1 Class'] = label_list[index_list[-1]].split(' ')[1]
        # avoid JSON serializable error
        result_dict['Confidence'] = [str(i) for i in list(output_prob)]
        result_dict['feature'] = feature  # [str(i) for i in list(feature)]
        lst_result.append(result_dict)

    return lst_result


def process_img_list(root, img_list_path, net_cls, label_list, batch_size):
    img_list = np.loadtxt(img_list_path, str, delimiter='\n')
    dict_results = OrderedDict()

    batches = [img_list[i:i + batch_size]
               for i in xrange(0, len(img_list), batch_size)]  # for py3: range()
    
    for batch in batches:
        img_list = []
        for i in range(len(batch)):
            img_path = os.path.join(root, batch[i].split(' ')[0])
            img = cv2.imread(img_path)
            img_list.append(img)
        lst_result = multiple_batch_process(
            net_cls, img_list, label_list)
        for i in range(len(lst_result)):
            dict_result = lst_result[i]
            img_path = os.path.join(root, batch[i].split(' ')[0])
            dict_result.update({'File Name': img_path})
            dict_results[os.path.basename(img_path)] = dict_result
    return dict_results


def post_process(dict_results):
    '''
    return features dict and label dict
    '''
    features = defaultdict()
    img_dict = defaultdict()

    for key, value in dict_results.items():
        label = dict_results[key]['Top-1 Class']
        img_dict[label].append(key)
        features[label].append(dict_results[key]['feature'])
    return features, img_dict
        

def save_features_imglist(features, img_dict, save_root):
    '''
    a. save image list: 
        image_path  label_idx  
    b. save features in bcolz
    '''
    def RepresentsInt(s):
        '''判断字符串是否表示int'''
        try:
            int(s)
            return True
        except ValueError:
            return False

    if not os.path.exists(save_root):
        os.makedirs(save_root)

    keys = features.keys()
    # 假如label的形式是 “index_labelname”(0_bk_bloodiness_human),则对index排序
    if RepresentsInt(keys[0].split('_')[0]):
        keys = sorted(keys, key=lambda k: int(k.split('_')[0]))

    for key in keys:
        print("*"*20, key, "*"*20)
        file_name = os.path.join(save_root, key + '.bc')
        save_array(file_name, features[key])
        np.savetxt(os.path.join(save_root, key + '.txt'), features[key])  #  fmt='%10.4f'
        print("save features file successfully in %s" % (file_name))

        img_list = os.path.join(save_root, key + '.lst')
        with open(img_list, 'w') as f:
            label_index = key.split("_")[0]
            for img_name in img_dict[key]:
                f.write(img_name + ' ' + label_index + '\n')
    

def parse_arg():
    parser = argparse.ArgumentParser(description='caffe image classify')
    parser.add_argument('--weight', help='caffemodel', type=str, required=True)
    parser.add_argument('--deploy', help='deploy.prototxt',
                        type=str, required=True)
    parser.add_argument('--gpu', help='gpu id', type=int, required=True)
    parser.add_argument('--labels', help='labels list',
                        type=str, required=True)
    parser.add_argument('--batch_size', help='batch size', type=int, default=1)
    parser.add_argument('--img_list', help='input image list',
                        default=None, type=str, required=False)
    parser.add_argument('--root', help='data root for image',
                        default=None, type=str, required=False)
    parser.add_argument('--save_root', type=str, default=None)
    return parser.parse_args()


def main():
    args = parse_arg()
    now = datetime.datetime.now()
    day = now.strftime("%m%d")
    output_folder = "result/{}".format(day)
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    net_cls = init_models(args.weight, args.deploy, args.batch_size, args.gpu)
    label_list = np.loadtxt(args.labels, str, delimiter='\n')
    
    # 字典，key: label, value: feature list
    features = defaultdict(list)
    save_root = args.save_root if args.save_root else 'features/%s/' % (
        now.strftime("%Y%m%d%H%M%S"))

    dict_results = OrderedDict()
    dict_results = process_img_list(
        args.root, args.img_list, net_cls, label_list, args.batch_size)

    features, img_dict = post_process(dict_results)
    save_features_imglist(features, img_dict, save_root)

    output = os.path.join(output_folder, 'results_%s.json' %
                          (now.strftime("%H%M%S")))
    
    for key in dict_results.keys():
        feature = dict_results[key]['feature']
        dict_results[key].update({'feature': [str(i) for i in list(feature)]})
    with open(output, 'w') as f:
        json.dump(dict_results, f, indent=4)
    print("Generate %s with success" % (output))



if __name__ == '__main__':
    print('Start caffe image classify:')
    main()
    print('End process.')
