# -*- coding:utf-8 -*-

'''
Create labelmap.prototxt from label list for LMDB

created by Riheng ZHU, 08/02/2018
'''
from __future__ import print_function
import os
import argparse
import json

from collections import OrderedDict

def parse_arg():
    parser = argparse.ArgumentParser(
        description='Create labelmap.prototxt from label list for LMDB')
    parser.add_argument(
        'label_list', help='label_list, e.g: 1 Sweatpants, label index should start from 1')
    return parser.parse_args()

def create_item(name, label, display_name):
    """
    labelmap.prototxt format:
    e.g:    item {
                name: "none_of_the_above"
                label: 0
                display_name: "background"
            }
    
        :param name: str, label name
        :param label: int, label index
        :param display_name: str, label display_name
    """
    item = OrderedDict()
    item['name'] = name
    item['label'] = label
    item['display_name'] = display_name
    info = json.dumps(item, indent=2)
    info = info.replace(',', '').replace('"name"', 'name')
    info = info.replace('"label"', 'label').replace('"display_name"', 'display_name')
    return info

def main():
    args = parse_arg()
    labels = []
    # label index should start from 1
    with open (args.label_list, 'r') as fi:
        for line in fi:
            index, label = line.strip().split()
            labels.append(label)
    
    abspath = os.path.abspath(args.label_list)
    output = os.path.join(os.path.split(abspath)[0], 'labelmap.prototxt')
    with open(output, 'w') as fo:
        # add background item
        item = create_item(
            "none_of_the_above", 0, 'background')
        fo.write('%s %s\n' % ('item', item))
    
        for i in range(len(labels)):
            item = create_item(labels[i], i+1, labels[i])
            fo.write('%s %s\n' % ('item', item))
    
    print("save file successfully: %s" % (output))

if __name__ == '__main__':
    print("Create labelmap.prototxt from label list for LMDB")
    main()
    print('End')
