# -*- coding: utf-8 -*-
'''
Loading results of ocr and visualization the bounding box and txt.

Todo:
    - fix bug of cv2.putText chinese character 
'''
import json
import os
import sys
import cv2
import numpy as np
import random
import argparse

if sys.version_info[0] >= 3:
    import urllib.request as urllib
else:
    import urllib

def parse_arg():
    parser = argparse.ArgumentParser(
        description='Loading results of ocr and visualization the bounding box and txt.')
    parser.add_argument('src', help='input ocr result list', type=str)
    parser.add_argument('-s', '--save', help='save image wiht bbox', action='store_true')
    parser.add_argument('-p', '--save_path', help='save image path', type=str, default=None)
    return parser.parse_args()

def load_json(file_path):
    '''
    read json file
    '''
    with open(file_path, 'r') as f:
        json_lists = [json.loads(line) for line in f]
    return json_lists


def sensitive_results(result):
    if result['label'][0]['data']:
        all_box = result['label'][0]['data']
        for bbox in all_box:
            if bbox['sensitive']:
                return True
    return False


def readImage_fun(imagePath=None):
    """
    read image from url
    """
    im = None
    try:
        data = urllib.urlopen(imagePath.strip()).read()
        nparr = np.fromstring(data, np.uint8)
        if nparr.shape[0] < 1:
            im = None
    except:
        im = None
    else:
        try:
            im = cv2.imdecode(nparr, 1)
        except:
            im = None
    finally:
        return im
    if np.shape(im) == ():
        return None
    return im

def visualization(image_url=None,  results=None, save_fig=False, outputDir=None):
    # load image from url
    img = readImage_fun(image_url)
    if img is  None:
        print('Load image failure: %s' % image_url)
    else:
        color_white = (255, 255, 255)
        all_bbox = results
        for i in range(0, len(all_bbox)):
            color = (random.randint(0, 256), random.randint(
                0, 256), random.randint(0, 256))
            bbox = all_bbox[i]
            text = bbox['text']
            pts = np.array(bbox['bbox'])
            xmin = np.min(pts[:, 0])
            ymin = np.min(pts[:, 1])
            # 顶点个数：4，矩阵变成4*1*2维
            pts = pts.reshape((-1, 1, 2))
            cv2.polylines(img, [pts], True, (0, 255, 255))
            #cv2.rectangle(img, (xmin, ymin), (xmax, ymax),
            #            color=color_white, thickness=3)
            cv2.putText(img, "%s" % (text), (xmin, ymin + 25),
                        color=color_white, fontFace=cv2.FONT_HERSHEY_COMPLEX, fontScale=0.5)

        if save_fig:
            img_name = image_url.split('/')[-1]
            outputName = os.path.join(outputDir, img_name+'.jpg')
            cv2.imwrite(outputName, img)

def main():
    args = parse_arg()
    results = load_json(args.src)
    for result in results:
        if sensitive_results(result):
            url = result['url']
            all_bbox = result['label'][0]['data']
            sensitive_bbox = []
            for bbox in all_bbox:
                if bbox['sensitive']:
                    sensitive_bbox.append(bbox)
            print(sensitive_bbox)
            save_or_not = True if args.save else False
            visualization(url, sensitive_bbox, save_or_not, args.save_path)
    

if __name__ == "__main__":
    print("Loading results of ocr and visualization the bounding box and txt.")
    main()
    print("End")
    
