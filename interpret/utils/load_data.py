#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 30 17:13:15 2018

@author: shuoz
"""

import numpy as np
import os

# default data path
BASEDIR = '/home/shuoz/data/openfmri/'
WHOLE_BRAIN_PATH = '/home/shuoz/data/openfmri/whole/'
ICA_PATH = '/home/shuoz/data/openfmri/ica/'
LABEL_PATH = '/home/shuoz/data/openfmri/label/'

# path on HPC
#WHOLE_BRAIN_PATH = '/shared/tale2/Shared/szhou/preprocessed/whole/'
#ICA_PATH = '/shared/tale2/Shared/szhou/preprocessed/ica/ica_all/'
#LABEL_PATH = '/shared/tale2/Shared/szhou/preprocessed/whole/'

def load_whole_brain(data_path = WHOLE_BRAIN_PATH, label_path = LABEL_PATH):
    data_run1=np.load(os.path.join(data_path,'zstat_run1.npy'))
    data_run2=np.load(os.path.join(data_path,'zstat_run2.npy'))
    data = np.hstack((data_run1,data_run2))
    data = data.T
    
    labels_run1=np.loadtxt(os.path.join(label_path,'data_key_run1.txt'))[:,0]
    labels_run2=np.loadtxt(os.path.join(label_path,'data_key_run2.txt'))[:,0]
    labels = np.hstack((labels_run1,labels_run2))
    
    return data, labels

def load_ica(dim = 100, data_path = ICA_PATH, label_path = LABEL_PATH):
    data = np.genfromtxt(os.path.join(data_path,'ica_%scomp.txt'%dim))
    labels = np.loadtxt(os.path.join(label_path,'data_key_all.txt'))[:,0]
    return data, labels
    
def get_domain_data(domain, data, label):
    n = len(label)
    data_ = []
    label_ = []
    for i in range(n):
        if label[i] == domain[0]:
            data_.append(data[i,:])
            label_.append(1)
        elif label[i] == domain[1]:
            data_.append(data[i,:])
            label_.append(-1)
    data_ = np.asarray(data_)
    label_ = np.asarray(label_)
    return data_, label_