#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Apr  5 15:59:59 2018

@author: shuoz
"""


import numpy as np
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import accuracy_score, roc_auc_score
from sklearn.svm import SVC
import load_data
import da_tool.tca
import create_domain
import pandas as pd

def cal_meanstd(alist):
    mean = np.mean(alist)
    std = np.std(alist)
    alist.append(mean)
    alist.append(std)
    return np.asarray(alist)

kfold = 5

# load data
data, label = load_data.load_whole_brain()
#data, label = load_data.load_ica()


# create target and source domain data
src_pos = 2
src_neg = 9
tar_pos = 3
tar_neg = 6

Xs, ys = create_domain.create(data, label, src_pos, src_neg)
Xt, yt = create_domain.create(data, label, tar_pos, tar_neg)
ns = len(ys)
nt = len(yt)

# apply tca
my_tca = da_tool.tca.TCA(dim=100, kerneltype='linear')
src_tca, tar_tca, tar_o_tca, V, obj, obj_tca = my_tca.fit_transform(Xs, Xt)


acc_all = []
auc_all = []
pred_all = []
dec_all = []

for _iter in range(10):
    # set k-fold cv
    rand_seed = (_iter + 5) * 10
    skf = StratifiedKFold(n_splits=kfold, shuffle=True, random_state= rand_seed)
    
    pred = np.zeros(nt)
    dec = np.zeros(nt)
    
    # init clf
    svm = SVC(kernel='linear', max_iter = 1000)
    
    for train, test in skf.split(tar_tca,yt):
        y_train = np.hstack((ys,yt[train]))
        tca_train = np.vstack((src_tca,tar_tca[train]))
        #Z_train = np.vstack((Zs,Zt[train]))
        
        svm.fit(tca_train, y_train)
        pred[test] = svm.predict(tar_tca[test])
        dec[test] = svm.decision_function(tar_tca[test])
        
    acc_all.append(accuracy_score(yt,pred))
    auc_all.append(roc_auc_score(yt,dec))
    pred_all.append(pred)
    dec_all.append(dec)
    
#pred_all = np.asanyarray(pred_all)
dec_all = np.asarray(dec_all)
acc_all = cal_meanstd(acc_all)
auc_all = cal_meanstd(auc_all)
print('mean accuracy: %s'%acc_all[len(acc_all)-2])
print('mean auc: %s'%auc_all[len(auc_all)-2])
# save result
df1 = pd.DataFrame(dec_all)
df2 = pd.concat([pd.DataFrame(acc_all), pd.DataFrame(auc_all)], axis=0)

df1.to_csv("tca_%sfold_dec_%svs%swith%svs%s.csv"%(kfold, tar_pos, tar_neg, src_pos, src_neg))
df1.to_csv("tca_%sfold_acc_%svs%swith%svs%s.csv"%(kfold, tar_pos, tar_neg, src_pos, src_neg))  
