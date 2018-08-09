# -*- coding: utf-8 -*-
'''
In this example, we will load a RefineDet model and use it to detect objects.

Todo:
    - support multiple batch inference
    - improve get_labelname() function
    - modify the process of saving inference results
'''
import numpy as np
import sys
import os
import cv2
sys.path.insert(0, "/opt/caffe/python")
import caffe
import time
import argparse
import random 
import json
import datetime

from google.protobuf import text_format
from caffe.proto import caffe_pb2


def parse_args():
    parser = argparse.ArgumentParser(description='refineDet Model inference')
    parser.add_argument('--modelBasePath',default=None, type=str)
    parser.add_argument('--weight', default=None, type=str)
    parser.add_argument('--deploy',default=None, type=str)
    parser.add_argument('--labelmap',default=None, type=str)
    parser.add_argument('--gpuId', default=0, type=int)
    parser.add_argument('--batch_size', help='batch size', type=int, default=1)
    parser.add_argument('--image_width', help='image width, 320 by default', type=int, default=320)
    parser.add_argument('--img_folder',default=None, type=str)
    parser.add_argument('--img_list',default=None, type=str)
    parser.add_argument('--img_root', default=None, type=str)
    parser.add_argument('--threshold', default=0.6, type=float)
    parser.add_argument('--saveImage', action='store_true')

    return parser.parse_args()


def init_models(weight, deploy, batch_size, gpu=0, image_width=320):
    """
    initialization caffe model 
        :param gpu: gpu id, 0 by default
        :param weight: weight of caffemodel
        :param deploy: deploy.prototxt
    """
    caffe.set_mode_gpu()
    caffe.set_device(gpu)

    net = caffe.Net(deploy, weight, caffe.TEST)
    net.blobs['data'].reshape(
        batch_size, 3, image_width, image_width)   # 3-channel (BGR) images
    return net

def get_labelname(labelmap, labels):
    num_labels = len(labelmap.item)
    labelnames = []
    if type(labels) is not list:
        labels = [labels]
    for label in labels:
        found = False
        for i in xrange(0, num_labels):
            if label == labelmap.item[i].label:
                found = True
                labelnames.append(
                    [labelmap.item[i].display_name, labelmap.item[i].label])
                break
        #assert found == True
    return labelnames


def ShowResults(img=None, image_file=None, save_img_dir=None, results=None, labelmap=None, threshold=0.6, save_fig=False):
    img = img  # image_file absolute path
    color_white = (255, 255, 255)
    num_classes = len(labelmap.item) - 1
    # colors = plt.cm.hsv(np.linspace(0, 1, num_classes)).tolist()
    rgWriteInfo = []
    all_bbox = results[0]
    conf = results[1]
    cls = results[2]
    for i in range(0, all_bbox.shape[0]):
        bbox_dict = dict()
        score = conf[i]
        if threshold and score < threshold:
            continue
        color = (random.randint(0, 256), random.randint(
            0, 256), random.randint(0, 256))
        bbox = all_bbox[i]
        label = int(cls[i])
        if label < 1:
            continue
        name_label = get_labelname(labelmap, label)[0]
        name = name_label[0]
        xmin = np.max(int(round(bbox[0])), 0)
        ymin = np.max(int(round(bbox[1])), 0)
        xmax = np.max(int(round(bbox[2])), 0)
        ymax = np.max(int(round(bbox[3])), 0)
        coords = (xmin, ymin), xmax - xmin, ymax - ymin
        cv2.rectangle(img, (xmin, ymin), (xmax, ymax),
                      color=color_white, thickness=3)
        cv2.putText(img, "%s-%.3f" % (name, score), (xmin, ymin + 25),
                    color=color_white, fontFace=cv2.FONT_HERSHEY_COMPLEX, fontScale=0.5)

        bbox_position_list = []
        bbox_position_list.append([xmin, ymin])
        bbox_position_list.append([xmax, ymin])
        bbox_position_list.append([xmax, ymax])
        bbox_position_list.append([xmin, ymax])
        bbox_dict['pts'] = bbox_position_list
        bbox_dict['score'] = float(score)
        bbox_dict['index'] = name_label[1]
        bbox_dict['class'] = name
        rgWriteInfo.append(bbox_dict)
    if save_fig:
        img_name = image_file.split('/')[-1]
        label_name = image_file.split('/')[-2]
        outputName = os.path.join(save_img_dir, label_name, img_name)
        cv2.imwrite(outputName, img)
    res = "%s\t%s" % (image_file.split('/')[-1], json.dumps(rgWriteInfo))
    return res

def preprocess(img=None, img_resize=None):
    img = cv2.resize(img, (img_resize, img_resize))
    img = img.astype(np.float32, copy=False)
    img = img - np.array([[[103.52, 116.28, 123.675]]])
    img = img * 0.017
    return img


def postprocess(img=None, out=None):
    h = img.shape[0]
    w = img.shape[1]
    box = out['detection_out'][0, 0, :, 3:7] * np.array([w, h, w, h])
    cls = out['detection_out'][0, 0, :, 1]
    conf = out['detection_out'][0, 0, :, 2]
    return (box.astype(np.int32), conf, cls)


def process_img_list(net, imgPath, image_width, threshold=0.6, saveImage=None, save_img_dir=None):
    result = []
    for im_name in imgPath:
        print("process : %s" % (im_name))
        origimg = cv2.imread(im_name)
        origin_h, origin_w, ch = origimg.shape
        img = preprocess(img=origimg, img_resize=image_width)
        img = img.astype(np.float32)
        img = img.transpose((2, 0, 1))
        net.blobs['data'].data[...] = img
        starttime = time.time()
        out = net.forward()
        box, conf, cls = postprocess(img=origimg, out=out)
        num = len(box)
        endtime = time.time()
        per_time = float(endtime - starttime)
        print('speed: {:.3f}s / iter'.format(endtime - starttime))

        res = ShowResults(img=origimg, image_file=im_name, save_img_dir=save_img_dir,
                    results=[box, conf, cls], labelmap=labelmap, threshold=threshold, save_fig=saveImage)
        result.append(res)
    return result
    

args = parse_args()
if __name__ == '__main__':
    # model inialization
    deploy = os.path.join(args.modelBasePath, args.deploy)
    weight = os.path.join(args.modelBasePath, args.weight)
    batch_size = args.batch_size
    net = init_models(weight, deploy, batch_size,
                      args.gpuId, args.image_width)

    # load labelmap
    labelmap_file = os.path.join(args.modelBasePath, args.labelmap)
    file = open(labelmap_file, 'r')
    labelmap = caffe_pb2.LabelMap()
    text_format.Merge(str(file.read()), labelmap)

    # image preprocessing
    imgPath = []

    if args.img_folder != None:
        for im_name in os.listdir(args.img_folder):
            image_file = os.path.join(args.img_folder, im_name)
            imgPath.append(image_file)
    elif args.img_list != None:
        with open(args.img_list, 'r') as f:
            for line in f:
                line = line.strip()
                line = line + '.jpg' if line.split('.')[-1] != 'jpg' else line
                image_file = os.path.join(args.img_root, line)
                imgPath.append(image_file)

    now = datetime.datetime.now()
    output_folder = "result/{}".format(now.strftime("%m%d"))
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    rg_output = os.path.join(
        output_folder, 'regression_%s.tsv' % (now.strftime("%H%M%S")))
        
    save_img_dir = os.path.join(output_folder, 'images')
    if not os.path.exists(save_img_dir):
        os.makedirs(save_img_dir)
    
    batches = [imgPath[i:i + batch_size]
               for i in xrange(0, len(imgPath), batch_size)]  # for py3: range()
    results = []
    saveImage = True if args.saveImage else False
    for batch in batches:
        result = process_img_list(net, batch, args.image_width, args.threshold, saveImage, save_img_dir)
        results.extend(result)
    
    with open(rg_output, 'w') as f:
        for result in results:
            f.write('%s\n' % result)
    print("save file with success: %s" % (rg_output))

'''
python refinedet_infer.py \
--modelBasePath models/ \
--weight caffe.weight \
--deploy deploy.prototxt \
--labelmap labelmap.prototxt \
--batch_size 1 \
--image_width 320 \
--img_list  \
--img_root \
--gpuId 0 \
--threshold 0.6 \
--saveImage False 
'''
