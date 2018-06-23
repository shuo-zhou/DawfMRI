# -*- coding: utf-8 -*-
"""
Created on Fri Aug 11 16:47:24 2017

@author: Shuo Zhou, the University of sheffield

"""

from sklearn.svm import SVC
from sklearn.model_selection import StratifiedKFold

import numpy as np

from da.tca import TCA
from da.cdsvm import CDSVM
from sklearn.metrics import accuracy_score, roc_auc_score
import pandas as pd
from utils.cmdline import commandline
from utils import load_data

def overlap(domain1, domain2):
    overlap = False
    for item in domain1:
        if item in domain2:
            overlap = True
            break
    return overlap

def pair_switch(pair_list):
    swithed_pairs = []
    for p in pair_list:
        swithed_pairs.append([p[1], p[0]])
    return swithed_pairs

def pair2str(pair_list):
    pair_str = []
    for t in pair_list:
        pair_str.append(str(t[0])+','+str(t[1]))
    return pair_str

config = commandline()
#basedir = config.basedir
kfold = config.kfold

# get data
if config.clf_ica:
    data, label= load_data.load_ica(dim = config.dim, data_path=config.ica_dir,
                                    label_path = config.label_dir)
else:
    data, label = load_data.load_whole_brain(data_path = config.wb_dir,
                                             label_path = config.label_dir)

TCs=[2,10,20,50,100]#,200]
tc_id = 3
tc_dim = TCs[tc_id]

task_ids = [1,2,3,4,5,6,8,9,10,21,22]
task_pairs = []
#for i in range(len(task_ids)):
    #for j in range(len(task_ids)):
for i in range(len(task_ids)-1):
    for j in range (i+1,len(task_ids)):
        task_pairs.append([task_ids[i],task_ids[j]])

acc_all = []
auc_all = []

src_pairs = task_pairs + pair_switch(task_pairs)

for tar_domain in task_pairs:
    #tar_data, tar_labels = get_data(tar_domain, data, labels)
    Xt, yt = load_data.get_domain_data(tar_domain, data, label)
    acc_row = []
    auc_row = []
    #pred = np.zeros(len(tar_labels))
    for src_domain in src_pairs:
        acc = []
        auc = []

        pred = np.zeros(len(yt))
        prob = np.zeros(len(yt))
        if tar_domain!=src_domain:
            if overlap(tar_domain, src_domain):
                acc_row.append(0)
                auc_row.append(0)
                continue
            else:
                Xs, ys = load_data.get_domain_data(src_domain, data, label)
                my_tca = TCA(n_components=tc_dim,kernel='linear')
                src_tca, tar_tca = my_tca.fit_transform(Xs, Xt)
                src_clf = SVC(kernel='linear', probability=True, max_iter =5000)
                src_clf.fit(src_tca, ys)
                for run_time in range(10):
                    skf = StratifiedKFold(n_splits=kfold, shuffle=True,random_state=100*run_time)
                    for train, test in skf.split(Xt, yt):
                        clf = CDSVM(src_clf.support_vectors_, ys[src_clf.support_],C=10, beta=1)
#                        X_train = np.vstack((src_tca,tar_tca[train]))
#                        y_train = np.hstack((ys, yt[train]))
                        clf.fit(tar_tca[train], yt[train])
                        pred[test] = clf.predict(tar_tca[test])
                        prob[test] = clf.decision_function(tar_tca[test])
                    acc.append(accuracy_score(yt,pred))
                    auc.append(roc_auc_score(yt,prob))

        else:
            svm =  SVC(kernel='linear', probability=True, max_iter=5000)
            for run_time in range(10):
                skf = StratifiedKFold(n_splits=kfold, shuffle=True,random_state=100*run_time)
                for train, test in skf.split(Xt, yt):
                    svm.fit(Xt[train],yt[train])
                    pred[test] = svm.predict(Xt[test])
                    prob[test] = svm.predict_proba(Xt[test])[:,1]
                acc.append(accuracy_score(yt, pred))
                auc.append(roc_auc_score(yt, prob))
        acc_row.append(np.mean(acc))
        auc_row.append(np.mean(auc))

    acc_all.append(acc_row)
    auc_all.append(auc_row)

target_str = pair2str(task_pairs)
source_str = pair2str(src_pairs)

df = pd.DataFrame(acc_all, index = target_str, columns = source_str)
df.to_csv("%sfold_transfer_matrix.csv"%kfold)

auc_df = pd.DataFrame(auc_all, index = target_str, columns = source_str)
auc_df.to_csv("%sfold_transfer_matrix_auc.csv"%kfold)
