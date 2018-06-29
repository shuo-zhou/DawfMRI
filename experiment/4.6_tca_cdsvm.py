# -*- coding: utf-8 -*-
"""
Created on Fri Aug 11 16:47:24 2017

@author: Shuo Zhou, the University of sheffield

USAGE: python <PROGRAM> options
ACTION: classify the ICA data
OPTIONS:
    -b: specify the basedir (contains data labels)
    -i: specify the directory of ICA data
    -h: print help

"""

from sklearn.svm import SVC
from sklearn.model_selection import StratifiedKFold, GridSearchCV
from sklearn.linear_model import LogisticRegression, Lasso

import numpy as np
#import matplotlib.pyplot as plt
from sklearn.metrics import confusion_matrix,accuracy_score, roc_auc_score
import pandas as pd

from utils.cmdline import commandline
from utils import load_data
from da.cdsvm import CDSVM
from da.tca import TCA

TASK_LIST = [1, 2, 3, 4, 5, 6, 8, 9, 10, 21, 22]

def get_src_pairs(target=[], exclude = []):
    pairs = []
    for i in range(len(TASK_LIST)):
        src1 = TASK_LIST[i]
        if src1 not in target and src1 not in exclude:
            for j in range(i+1, len(TASK_LIST)):
                src2 = TASK_LIST[j]
                if src2 not in target and src2 not in exclude:
                    pairs.append([src1, src2])
    return pairs

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
target = config.target
kfold = config.kfold

if config.clf_ica:
    data, label= load_data.load_ica(dim = config.dim, data_path=config.ica_dir,
                                    label_path = config.label_dir)
else:
    data, label = load_data.load_whole_brain(data_path = config.wb_dir,
                                             label_path = config.label_dir)

params = {'TCdim':[2,10,20,50,100], 'C':[0.001, 0.01, 0.1, 1, 10, 100, 1000], 
          'lambda': [0.00001, 0.0001, 0.001, 0.01, 0.1, 1, 10, 100, 1000, 10000, 100000],
          'beta': [0.001, 0.01, 0.1, 1, 10, 100, 1000]}
tc_id = 4
tcdim = params['TCdim'][tc_id]
# load target data
Xt, yt = load_data.get_domain_data(target, data, label)

src_list = get_src_pairs(target=target)
src_full = src_list + pair_switch(src_list)
src_str_list = pair2str(src_full)
# 10 fold cross-validation

###################################

acc_all = {}
acc_all['svm'] = []
acc_all['cdsvm'] = []

auc_all = {}
auc_all['svm'] = []
auc_all['cdsvm'] = []

dec ={}

dec['svm'] = []
dec['cdsvm'] = []


# use whole brain data for classification

for src_domain in src_full:
    Xs, ys = load_data.get_domain_data(src_domain, data, label)
# =============================================================================
#     # param tuning
#     best_acc = 0
#     best_params = {'TCdim':0, 'C_src_svm':0, 'C_cdsvm':0, 'mu': 0, 'beta': 0}
#     for tcdim in params['TCdim']:
#         for lambda_ in params['lambda']:
#             tune_tca = TCA(n_components = tcdim, lambda_ = lambda_, kernel='linear')
#             Xtcs, Xtct = tune_tca.fit_transform(Xs, Xt)
#             tune_src_svm = GridSearchCV(SVC(kernel='linear', max_iter = 5000),
#                                         {'C': params['C']})
#             tune_src_svm.fit(Xtcs, ys)
#             best_src_svm = tune_src_svm.best_estimator_
#             
#             tune_cdsvm = GridSearchCV(CDSVM(best_src_svm.support_vectors_, 
#                                             ys[best_src_svm.support_]), 
#                                     {'C': params['C'], 'beta':params['beta']})
#             tune_cdsvm.fit(Xtct, yt)
#             if tune_cdsvm.best_score_ > best_acc:
#                 best_acc = tune_cdsvm.best_score_
#                 best_params['TCdim'] = tcdim
#                 best_params['lambda'] = lambda_
#                 best_params['C_src_svm'] = tune_src_svm.best_params_['C']
#                 best_params['C_cdsvm'] = tune_cdsvm.best_params_['C']
#                 best_params['beta'] = tune_cdsvm.best_params_['beta']
#                 
#     print(target, src_domain, best_params)
#     # tuning end
# =============================================================================
            
            
    my_tca = TCA(n_components = tcdim, kernel='linear', lambda_ = 1)
    src_tca, tar_tca = my_tca.fit_transform(Xs, Xt)
    acc={}
    acc['svm']=[]
    acc['cdsvm']=[]

    auc = {}
    auc['svm'] = []
    auc['cdsvm'] = []
    
# =============================================================================
    tune_src_svm = GridSearchCV(SVC(kernel='linear', max_iter = 5000),
                                         {'C': params['C']})

    tune_src_svm.fit(src_tca, ys)
    best_src_svm = tune_src_svm.best_estimator_
  
    tune_cdsvm = GridSearchCV(CDSVM(best_src_svm.support_vectors_, 
                                 ys[best_src_svm.support_]), 
                          {'C': params['C'], 'beta':params['beta']})
    tune_cdsvm.fit(tar_tca, yt)
# 
# =============================================================================
    src_clf =  SVC(kernel='linear', C = tune_src_svm.best_params_['C'], max_iter=5000)
    src_clf.fit(src_tca, ys)
    print(src_clf.score(src_tca, ys))
    for run_time in range(10):
        skf = StratifiedKFold(n_splits=kfold, shuffle=True,random_state=run_time*100)
        svm = SVC(kernel='linear', C = tune_cdsvm.best_params_['C'], max_iter=5000)
        cdsvm = CDSVM(src_clf.support_vectors_, ys[src_clf.support_],
                      C = tune_cdsvm.best_params_['C'], 
                      beta=tune_cdsvm.best_params_['beta'])

        pred1 = np.zeros(len(yt))
        dec1 = np.zeros(len(yt))

        dec2 = np.zeros(len(yt))
        pred2 = np.zeros(len(yt))

        for train, test in skf.split(tar_tca, yt):
            cdsvm.fit(tar_tca[train],yt[train])
            pred1[test] = cdsvm.predict(tar_tca[test])
            dec1[test] = cdsvm.decision_function(tar_tca[test])

            train_data = np.vstack((src_tca,tar_tca[train]))
            train_labels = np.hstack((ys, yt[train]))

            svm.fit(train_data,train_labels)
            pred2[test] = svm.predict(tar_tca[test])
            dec2[test] = svm.decision_function(tar_tca[test])

        acc['cdsvm'].append(accuracy_score(yt,pred1))
        dec['cdsvm'].append(dec1)
        auc['cdsvm'].append(roc_auc_score(yt,dec1))

        acc['svm'].append(accuracy_score(yt,pred2))
        dec['svm'].append(dec2)
        auc['svm'].append(roc_auc_score(yt,dec2))

    acc_all['cdsvm'].append(acc['cdsvm'])
    auc_all['cdsvm'].append(auc['cdsvm'])

    acc_all['svm'].append(acc['svm'])
    auc_all['svm'].append(auc['svm'])

acc_std = {}
acc_mean = {}
auc_std = {}
auc_mean = {}

acc_all['cdsvm'] = np.array(acc_all['cdsvm'])
acc_mean['cdsvm'] = np.mean(acc_all['cdsvm'],axis=1).reshape((len(src_full),1))
acc_std['cdsvm'] = np.std(acc_all['cdsvm'],axis=1).reshape((len(src_full),1))
auc_all['cdsvm'] = np.array(auc_all['cdsvm'])
auc_mean['cdsvm'] = np.mean(auc_all['cdsvm'],axis=1).reshape((len(src_full),1))
auc_std['cdsvm'] = np.std(auc_all['cdsvm'],axis=1).reshape((len(src_full),1))

acc_all['svm'] = np.array(acc_all['svm'])
acc_mean['svm'] = np.mean(acc_all['svm'],axis=1).reshape((len(src_full),1))
acc_std['svm'] = np.std(acc_all['svm'],axis=1).reshape((len(src_full),1))
auc_all['svm'] = np.array(auc_all['svm'])
auc_mean['svm'] = np.mean(auc_all['svm'],axis=1).reshape((len(src_full),1))
auc_std['svm'] = np.std(auc_all['svm'],axis=1).reshape((len(src_full),1))

source_list = np.array(src_list).T

cdsvm_result = np.hstack((acc_all['cdsvm'], acc_mean['cdsvm'], acc_std['cdsvm'],
                          auc_all['cdsvm'], auc_mean['cdsvm'], auc_std['cdsvm']))
cdsvm_df = pd.DataFrame(cdsvm_result, index = src_str_list)
cdsvm_df.to_csv("%sfold_tca+cdsvm_result_%s_%s.csv"%(kfold, target[0], target[1]))

svm_result = np.hstack((acc_all['svm'], acc_mean['svm'], acc_std['svm'],
                        auc_all['svm'], auc_mean['svm'], auc_std['svm']))
svm_df = pd.DataFrame(svm_result, index = src_str_list)

svm_df.to_csv("%sfold_tca+svm_result_%s_%s.csv"%(kfold, target[0], target[1]))
#df = pd.concat([cdsvm_result, svm_result],axis=0)
#df.to_csv("%sfold_result_%s_%s.csv"%(kfold, target[0], target[1]))

#for i in dec:
#    dec[i].append(yt)
#    pd.DataFrame(np.array(dec[i])).to_csv('%sfold_dec_%s_%s_%s.csv'%(kfold,i,target[0], target[1]))
