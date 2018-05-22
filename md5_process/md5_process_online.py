# -*- coding: utf-8 -*-
# created 2018/04/02 @Riheng
# get md5 of online images

# TODO:
# 针对线程中断的两个问题更新代码
#   1. 连接超时
#   2. 进程退出错误 


from __future__ import print_function  # 引入python3中的print()函数
from __future__ import with_statement  # with 语句替换try...catch语句，且出问题时自动调用close方法

import os, sys
import requests
import threading
import Queue
import json
import argparse
import time
from collections import OrderedDict

# globale vars initialization
GLOBAL_LOCK = threading.Lock()
ERROR_NUMBER = 0
FILE_NAME = str()


class request_err(Exception):
    '''
    Catch qhash request error 
    '''
    pass


class prod_worker(threading.Thread):
    """
    producing worker
    """
    global GLOBAL_LOCK

    def __init__(self, queue, infile):
        threading.Thread.__init__(self)
        self.queue = queue
        self.infile = infile

    def run(self):
        for buff in self.infile:
            temp = dict()
            # skip blank line
            if not buff.strip():
                continue
            # 1. 只有url的list
            #file_tmp = buff.strip().split()[0]

            # 2. 读取原始的json文件
            line = buff.strip()
            temp = json.loads(line)
            url = temp['url']
            image_name = url.split('images/')[-1]
            file_tmp = image_name

            GLOBAL_LOCK.acquire()
            self.queue.put(file_tmp)
            GLOBAL_LOCK.release()
        GLOBAL_LOCK.acquire()
        print('thread:', self.name, 'successfully quit')
        GLOBAL_LOCK.release()


class cons_worker(threading.Thread):
    global GLOBAL_LOCK

    def __init__(self, queue, hash_dic, hash_alg_list, prefix=None):
        threading.Thread.__init__(self)
        self.queue = queue
        self.hash_dic = hash_dic
        self.hash_alg_list = hash_alg_list
        self.prefix = prefix

    def get_qhash(self, url, alg, err_num):
        req = '{}?qhash/{}'.format(url, alg)
        ret = requests.get(req)
        if ret.status_code != 200:
            # raise request_err
            print('return error:', req)
            err_num += 1
            return None, err_num
        else:
            return json.loads(ret.text), err_num

    def run(self):
        global ERROR_NUMBER
        err_num = 0
        while(not self.queue.empty()):
            if GLOBAL_LOCK.acquire(False):
                # customized code
                file_tmp = self.queue.get()
                print('processing:', file_tmp)
                self.hash_dic[file_tmp] = dict()
                GLOBAL_LOCK.release()
                if self.prefix:
                    url_tmp = os.path.join(self.prefix, file_tmp)
                else:
                    url_tmp = file_tmp
                for hash_alg in self.hash_alg_list:
                    result, err_num = self.get_qhash(
                        url_tmp, hash_alg, err_num)
                    if result:
                        GLOBAL_LOCK.acquire()
                        self.hash_dic[file_tmp][hash_alg] = result['hash']
                        GLOBAL_LOCK.release()
            else:
                pass
        GLOBAL_LOCK.acquire()
        ERROR_NUMBER += err_num
        print('thread:', self.name, 'successfully quit')
        GLOBAL_LOCK.release()


def parse_args():
    parser = argparse.ArgumentParser(description='get md5 of online images')
    parser.add_argument('src', help='input file list', type = str)
    parser.add_argument('thread_number', help='number of processing thread', type=int)
    parser.add_argument('-p', '--prefix', help='add url prefix if needed', type=str)
    parser.add_argument(
        '-o', '--output', 
        help='output json file path, will be saved as <infile>_hash.json path by default', 
        type=str)
    parser.add_argument(
        '--hash_alg', 
        help='hash algorithm, md5, sha1 or both [default: md5]',
        default = ['md5'],
        type=list)
    parser.add_argument('-d', '--depot', help='depot file', type=str)

    return parser.parse_args()

def make_json(url, md5, category):
    #label_json = []
    # 只考虑类别信息
    #for catg in category :
        #lab = {"class": catg}
        #label_json.append(lab)
    # 考虑类别信息以及bbox
    ava_json = OrderedDict()
    ava_json['url'] = url
    ava_json['md5'] = md5
    ava_json['label'] = category
    #ava_json = {"url": url, "md5": md5, "label": label_json}
    return ava_json

def get_categ(path):
    category = {}
    with open(path, 'r') as fo:
        for line in fo:
            line = line.strip()
            temp = json.loads(line)
            url = temp['url']
            image_name = url.split('images/')[-1]
            cate = temp['label'][0]['data']  # ['data'][0]['class']
            if cate:
                labels = []
                for c in cate:
                    labels.append(c['class'])
                category[image_name] = list(set(labels))
            else:
                category[image_name] = ['normal']
    return category


def md5(infile, thread_count, prefix):
    args = parse_args()
    queue = Queue.Queue(0)
    hash_dic = dict()
    hash_alg_list = args.hash_alg
    for check in hash_alg_list:
        assert check in ['md5', 'sha1'], 'invalid hash algorithm: {}'.format(check)
    # 多线程 
    thread_prod = prod_worker(queue, infile)
    thread_prod.start()
    print('thread:', thread_prod.name, 'successfully started')
    ## 统计时间
    time.sleep(1)
    tic = time.time()
    for i in xrange(thread_count):
        exec('thread_cons_{} = cons_worker(queue, hash_dic, hash_alg_list, prefix)'.format(i))
        eval('thread_cons_{}.start()'.format(i))
    thread_prod.join()
    for i in xrange(thread_count):
        eval('thread_cons_{}.join()'.format(i))
    toc = time.time()
    print('total error number:', ERROR_NUMBER)
    print('processing time:', (toc-tic), 's')
    infile.close()

    return hash_dic

def main():
    args = parse_args()
    # 读取参数
    infile = open(args.src, 'r')
    output = args.output if args.output else '{}_hash.json'.format(
        os.path.splitext(args.src)[0])
    thread_count = args.thread_number
    prefix = args.prefix

    hash_dic = md5(infile, thread_count, prefix)

    category = get_categ(args.src)
    json_array = []
    
    for url, val in hash_dic.items():
        if val :
            array = make_json(url, val['md5'], category[url])
            json_array.append(array)
        #else:
            #print(url)
            #print("*************************")

    # 输出到文件中
    with open(output, 'w') as fi:
        for line in json_array:
            json.dump(line, fi)
            fi.write('\n')
        #json.dump(hash_dic, f)  # 不使用indent

if __name__ == '__main__':
    print("Start md5 processing:")
    main()
    print("md5 processing done...")
