#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Apr  5 14:25:49 2018

@author: shuoz
"""


import numpy as np
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import accuracy_score, roc_auc_score
from sklearn.svm import SVC
import load_data
import create_domain


# load data
data, label = load_data.load_whole_brain()
#data, label = load_data.load_ica()

k_fold = 5

# create target and source domain data
src_pos = 21
src_neg = 9
tar_pos = 3
tar_neg = 6

Xs, ys = create_domain.create(data, label, src_pos, src_neg)
Xt, yt = create_domain.create(data, label, tar_pos, tar_neg)
ns = len(ys)
nt = len(yt)

# set k-fold cv
skf = StratifiedKFold(n_splits=k_fold, shuffle=True, random_state=100)

pred = np.zeros(len(yt))
dec = np.zeros(len(yt))

# init clf
svm = SVC(kernel='linear', max_iter = 1000)

for train, test in skf.split(Xt,yt):
    # use source domain data as additional samples for training
    X_train = np.vstack((Xs,Xt[train]))
    y_train = np.hstack((ys,yt[train]))

    svm.fit(X_train, y_train)
    
    # use target domain data only for training
    # svm.fit(Xt[train], yt[train])
    
    pred[test] = svm.predict(Xt[test])
    dec[test] = svm.decision_function(Xt[test])
 
print(accuracy_score(yt,pred))
print(roc_auc_score(yt,dec))
