#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 30 18:03:57 2018

@author: shuoz
"""

import numpy as np
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import confusion_matrix, accuracy_score, roc_auc_score
from sklearn.svm import SVC
import sklearn
import load_data
from JDA.JDA import JDA
import da_tool.tca
import create_domain


# load data
data, label = load_data.load_whole_brain()

# create target and source domain data
src_pos = 21
src_neg = 2
tar_pos = 3
tar_neg = 6

Xs, ys = create_domain.create(data, label, src_pos, src_neg)
Xt, yt = create_domain.create(data, label, tar_pos, tar_neg)
ns = len(ys)
nt = len(yt)
# set k-fold cv
skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=600)

# init DA method

# tca
my_tca = da_tool.tca.TCA(dim=100, kerneltype='linear')
src_tca, tar_tca, tar_o_tca, V, obj, obj_tca = my_tca.fit_transform(Xs, Xt)
# jda
options = {"k": 100, "lmbda": 800, "ker": 'linear', "gamma": 1.0}
Z, A = JDA(Xs.T, Xt.T, ys, yt, options)
Zs = Z[:, :ns].T
Zt = Z[:, ns:].T

# init clf
svm = SVC(kernel='linear')


pred1 = np.zeros(len(yt))
dec1 = np.zeros(len(yt))

dec2 = np.zeros(len(yt))
pred2 = np.zeros(len(yt))

for train, test in skf.split(tar_tca,yt):
    y_train = np.hstack((ys,yt[train]))
    tca_train = np.vstack((src_tca,tar_tca[train]))
    Z_train = np.vstack((Zs,Zt[train]))
    
    svm.fit(tca_train, y_train)
    pred1[test] = svm.predict(tar_tca[test])
    dec1[test] = svm.decision_function(tar_tca[test])
    
    # jda
    options = {"k": 100, "lmbda": 800, "ker": 'linear', "gamma": 1.0}
    Z, A = JDA(Xs.T, Xt[train].T, ys, yt[train], options)
    Zs = Z[:, :ns].T
    Zt = Z[:, ns:].T
    
    Xtt = Xt[test].T
    Zt_test = np.matmul(Xtt.T, Xtt)
    Zt_test = np.matmul(A.T, Zt_test)
    Zt_test = Zt_test.T
    
    svm.fit(Zt, yt[train])
    pred2[test] = svm.predict(Zt_test)
    dec2[test] = svm.decision_function(Zt_test)


print(accuracy_score(yt,pred1))
print(roc_auc_score(yt,dec1))
print(accuracy_score(yt,pred2))
print(roc_auc_score(yt,dec2))