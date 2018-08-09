#coding=utf-8
'''
Make confusion matrix.
Created by Riheng 08/05/2018

Todo:
    - support getting classes with automatique.
'''

import json
import os
import argparse
from collections import Counter

import matplotlib.pyplot as plt
import numpy as np
import itertools
from sklearn.metrics import confusion_matrix, classification_report

def parse_args():
    parser = argparse.ArgumentParser(description='Prediction evaluate')
    parser.add_argument('ground_truth', help='ground truth',
                        default=None, type=str)
    parser.add_argument('prediction', help='prediction',
                        default=None, type=str)
    return parser.parse_args()

def load_lst(path):
    dic = {}
    with open(path, 'r') as f:
        for line in f:
            key, value = line.strip().split(' ')
            dic[key] = value
    return dic


def plot_confusion_matrix(cm, classes, normalize=False, title='Confusion matrix', cmap=plt.cm.Blues, figsize=None):
    """
    This function prints and plots the confusion matrix.
    Normalization can be applied by setting `normalize=True`.
    (This function is copied from the scikit docs.)
    """
    plt.figure(figsize=figsize)
    plt.imshow(cm, interpolation='nearest', cmap=cmap)
    plt.title(title)
    plt.colorbar()
    tick_marks = np.arange(len(classes))
    plt.xticks(range(cm.shape[0]), classes, rotation=45)
    plt.yticks(range(cm.shape[1]), classes)

    if normalize:
        cm = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]
    print(cm)
    thresh = cm.max() / 2.
    for i, j in itertools.product(range(cm.shape[0]), range(cm.shape[1])):
        plt.text(j, i, cm[i, j], horizontalalignment="center",
                 color="white" if cm[i, j] > thresh else "black")

    plt.tight_layout()
    plt.ylabel('True label')
    plt.xlabel('Predicted label')
    plt.show()


def convert(ground_truth, prediction, classes):
    preds = []  # save prediciton label index
    y = []  # save ground truth index

    for video in prediction.keys():
        try:
            gt = ground_truth[video]
            pred = prediction[video]
            preds.append(classes.index(pred))
            y.append(classes.index(gt))
        except Exception as e:
            print(Exception, ":", e)
            continue
    return y, preds


def main():
    args = parse_args()
    ground_truth = load_lst(args.ground_truth)
    prediction = load_lst(args.prediction)
    classes = ['normal', 'terror']

    y, preds = convert(ground_truth, prediction, classes)
    # 1. statistical result
    print('Groud Truth: %s' % str(Counter(y)))
    print('Predictions: %s' % str(Counter(preds)))
    # 2.calculate precison_recall
    precison_recall = classification_report(y, preds, target_names=classes)
    print(precison_recall)
    # 3.plot confusion matrix
    cm = confusion_matrix(y, preds, labels=np.arange(len(classes)))
    plot_confusion_matrix(cm, classes, normalize=False)


if __name__ == '__main__':
    print("Start processing")
    main()
    print("End processing")
