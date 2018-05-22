# -*- coding:utf-8 -*-
# created 2018/05/15 @Riheng
# 将分成1000分的推理结果整合在一起


import os
import json
import argparse


def make_labelX_json_cls(url=None, cls=None, dataset_label='terror'):
    '''
    url, type, <source_url>, <ops>, 
    label:
        [{
        "data": [{"class": "normal"}], 
        "version": "1", 
        "type": "classification", 
        "name": "terror" / "pulp" / "general"
        }]
    '''
    label_json = {"data": [{"class": cls}], "version": "1",
                  "type": "classification", "name": dataset_label}
    ava_json = {"url": url, "ops": "download()", "type": "image",
                "label": [label_json]}
    return ava_json


def merge_file(filenames, output):
    '''
    concatenate text files
    '''
    with open(output, 'w') as outfile:
        for fname in filenames:
            print "merge %s" % (fname)
            with open(fname) as infile:
                for line in infile:
                    outfile.write(line)
    

def merge_filter_file(filenames, output, threshold):
    '''
    concatenate text files
    '''
    with open(output, 'w') as outfile:
        for fname in filenames:
            print "merge %s" % (fname)
            json_fname = load_json(fname)
            filter_results = filter(json_fname, threshold)
            for json_list in filter_results:
                json.dump(json_list, outfile)  # 不使用indent
                outfile.write('\n')


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


def filter(results, threshold):
    json_lists = []
    for result in results:
        index = int(result.values()[0]['Top-1 Index'])
        prob = result.values()[0]['Confidence'][index]
        if index <= 17:
            if threshold <= float(prob):
                url = result.values()[0]['File Name']
                cls = result.values()[0]['Top-1 Class']
                result_labelX = make_labelX_json_cls(url, cls)
                json_lists.append(result_labelX)
    return json_lists

def get_file_list(path, num, gpuNumber):
    filenames = []
    for i in range(num):
        folder = os.path.join(path,'job-0' + str(i))
        for j in range(gpuNumber):
            filename = os.path.join(folder, 'split_file-0'+str(j)+'_0-result.json')
            if os.path.isfile(filename):
                filenames.append(filename)
    return filenames

# 使用argparse
def parse_args():
    parser = argparse.ArgumentParser(description="生成图片分类和检测的jsonlist")
    parser.add_argument('--dataPath', required=True,type=str)
    parser.add_argument('--output', type=str, help = 'set <infile>_result.json by default')
    parser.add_argument('--num', type=int, default=1000)
    parser.add_argument('--gpuNumber', type=int, default=4)
    parser.add_argument('--threshold', type=float, default=0.9, help='model threshold')
    parser.add_argument('--index', type=int, default=17)
    return parser.parse_args()

args = parse_args()
def main():
    path = args.dataPath
    output = args.output if args.output else '{}_results.json'.format(
        os.path.join(args.dataPath, os.path.dirname(args.dataPath).split('/')[-1]))

    filenames = get_file_list(path, args.num, args.gpuNumber)

    #merge_file(filenames, output)
    #results = load_json(output)
    #filter_result = filter(results, args.threshold)
    output_thresh = args.output if args.output else '{}_results_threshold_{}.json'.format(
        os.path.join(args.dataPath, os.path.dirname(args.dataPath).split('/')[-1]), str(args.threshold))
    merge_filter_file(filenames, output_thresh, args.threshold)

    #write_to_json(filter_result, output_thresh)

if __name__ == '__main__':
    print 'Start processing'
    main()
    print 'End ...'

