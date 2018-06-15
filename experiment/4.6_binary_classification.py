# -*- coding: utf-8 -*-
"""
Created on Fri Aug 11 16:47:24 2017

@author: Shuo Zhou, the University of sheffield

USAGE: python <PROGRAM> options
ACTION: classify the ICA data
OPTIONS:
    -b: specify the basedir (contains data labels)
    -k: specify kfold for cross validation (default = 50)
    -t: specify target domain labels, format AvsB, e.g. 3vs6
    -d: specify dimension for transfer components
    -h: print help

"""

from sklearn.svm import SVC
from sklearn.model_selection import StratifiedKFold
import pickle
import numpy as np
import sys,os
import getopt
#import matplotlib.pyplot as plt
import da.tca
#from asvm import A_SVM
from da.cdsvm import CDSVM
from sklearn.metrics import confusion_matrix,accuracy_score,classification_report, roc_auc_score
import pandas as pd

from apply_tca import get_src_domains, extract_domain_data

class commandline:
    def __init__(self):
        opts,args = getopt.getopt(sys.argv[1:],'b:k:t:d:h')
        opts = dict(opts)

        self.kfold = 10
        self.tar_domain = [3,6]
	self.dim = 50
        self.basedir = '/shared/tale2/Shared/szhou/openfmri/preprocessed/whole/'

        if '-h' in opts:
            self.printHelp()

        if '-b' in opts:
            self.basedir = opts['-b']
            if self.basedir[-1]!='/':
                self.basedir+='/';
            if not os.path.exists(self.basedir):
                print 'basedir %s does not exist!'%self.basedir
                self.printHelp()

        if '-t' in opts:
            self.tar_domain = opts['-t'].split("vs")
            self.tar_domain[0] = int(self.tar_domain[0])
            self.tar_domain[1] = int(self.tar_domain[1])

	if '-d' in opts:
	    self.dim = int(opts['-d'])

        if '-k' in opts:
            self.kfold = int(opts['-k'])

    def printHelp(self):
        helpinfo = __doc__.replace('<PROGRAM>',sys.argv[0],1)
        print(helpinfo)
        print(sys.stderr)
        sys.exit()

def load_tca(basedir, tc_dim, tar_domain, src_domain):
    data = np.load(os.path.join(basedir,'TCA_/%sd_tar%s_%ssrc%s_%s.npy'%(tc_dim,tar_domain[0],tar_domain[1],src_domain[0],src_domain[1])))
    tca = data[:,0:-1]
    labels = data[:,-1]
    src_tca = []
    src_labels = []
    tar_tca = []
    tar_labels = []
    tar_labels_ = []
    n_samples = len(labels)
    
    # source domain label can be swapped here
    for i in range(n_samples):
        if labels[i]==tar_domain[0]:
            tar_tca.append(tca[i,:])
            tar_labels.append(1)
        if labels[i]==tar_domain[1]:
            tar_tca.append(tca[i,:])
            tar_labels.append(-1)
        if labels[i]==src_domain[0]:
            src_tca.append(tca[i,:])
            src_labels.append(1)
        if labels[i]==src_domain[1]:
            src_tca.append(tca[i,:])
            src_labels.append(-1)

    tar_tca = np.array(tar_tca)
    tar_labels = np.array(tar_labels)
    src_tca = np.array(src_tca)
    src_labels = np.array(src_labels)

    return tar_tca, tar_labels, src_tca, src_labels



config = commandline()
#icadir = config.icadir
basedir = config.basedir
kfold = config.kfold
tar_domain= config.tar_domain
tc_dim = config.dim
# load data

'''
data=np.load(os.path.join(basedir,'zstat_run1.npy'))
labels=np.loadtxt(os.path.join(basedir,'data_key_run1.txt'))[:,0]
'''
data_run1=np.load(os.path.join(basedir,'zstat_run1.npy'))
data_run2=np.load(os.path.join(basedir,'zstat_run2.npy'))
data = np.hstack((data_run1,data_run2))

labels_run1=np.loadtxt(os.path.join(basedir,'data_key_run1.txt'))[:,0]
labels_run2=np.loadtxt(os.path.join(basedir,'data_key_run2.txt'))[:,0]
labels = np.hstack((labels_run1,labels_run2))

data = data.T


#initilize accuracy

n_samples = len(labels)


# biased sample size for each class
target_data = []
target_labels = []
for i in range(n_samples):
    if labels[i]==tar_domain[0]:
        target_data.append(data[i])
        target_labels.append(-1)
    if labels[i]==tar_domain[1]:
        target_data.append(data[i])
        target_labels.append(1)

target_data = np.array(target_data)
target_labels = np.array(target_labels)

###################################

acc_all = {}
acc_all['svm'] = []
acc_all['cdsvm'] = []
acc_all['whole'] = []
auc_all = {}
auc_all['svm'] = []
auc_all['cdsvm'] = []
auc_all['whole'] = []

src_domains, src_list = get_src_domains(tar_domain)
dec ={}
dec['whole'] = []
dec['svm'] = []
dec['cdsvm'] = []

for i in dec:
    dec[i].append(target_labels)
# use whole brain data for classification
for run_time in range(10):
    skf = StratifiedKFold(n_splits=kfold, shuffle=True,random_state=run_time*100)

    pred3 = np.zeros(len(target_labels))
    dec3 = np.zeros(len(target_labels))
    svm_whole = SVC(kernel='linear')

    for train, test in skf.split(target_data,target_labels):
        svm_whole.fit(target_data[train],target_labels[train])
        pred3[test] = svm_whole.predict(target_data[test])
        dec3[test] = svm_whole.decision_function(target_data[test])
    acc_all['whole'].append(accuracy_score(target_labels,pred3))
    auc_all['whole'].append(roc_auc_score(target_labels,dec3))
    dec['whole'].append(dec3)

for src_domain in src_domains:
    tar_tca, tar_labels, src_tca, src_labels = load_tca(basedir, tc_dim, tar_domain, src_domain)
    acc={}
    acc['svm']=[]
    acc['cdsvm']=[]
    acc['whole'] = []

    auc = {}
    auc['svm'] = []
    auc['cdsvm'] = []
    auc['whole'] = []

    for run_time in range(10):
        skf = StratifiedKFold(n_splits=kfold, shuffle=True,random_state=run_time*100)
        svm = SVC(kernel='linear', max_iter = 5000)
        src_clf =  SVC(kernel='linear', max_iter = 5000)
        src_clf.fit(src_tca,src_labels)
        #asvm = A_SVM(src_clf.coef_,C=50)
        cdsvm = CDSVM(src_clf.support_vectors_, src_labels[src_clf.support_],C=10, beta=1)

        pred1 = np.zeros(len(tar_labels))
        dec1 = np.zeros(len(tar_labels))

        dec2 = np.zeros(len(tar_labels))
        pred2 = np.zeros(len(tar_labels))

        for train, test in skf.split(tar_tca,tar_labels):
            cdsvm.fit(tar_tca[train],tar_labels[train])
            pred1[test] = cdsvm.predict(tar_tca[test])
            dec1[test] = cdsvm.decision_function(tar_tca[test])

            train_data = np.vstack((src_tca,tar_tca[train]))
            train_labels = np.hstack((src_labels,tar_labels[train]))

            svm.fit(train_data,train_labels)
            pred2[test] = svm.predict(tar_tca[test])
            dec2[test] = svm.decision_function(tar_tca[test])

        acc['cdsvm'].append(accuracy_score(tar_labels,pred1))
        dec['cdsvm'].append(dec1)
        auc['cdsvm'].append(roc_auc_score(tar_labels,dec1))

        acc['svm'].append(accuracy_score(tar_labels,pred2))
        dec['svm'].append(dec2)
        auc['svm'].append(roc_auc_score(tar_labels,dec2))

    acc_all['cdsvm'].append(acc['cdsvm'])
    auc_all['cdsvm'].append(auc['cdsvm'])

    acc_all['svm'].append(acc['svm'])
    auc_all['svm'].append(auc['svm'])

acc_std = {}
acc_mean = {}
auc_std = {}
auc_mean = {}

acc_all['cdsvm'] = np.array(acc_all['cdsvm'])
acc_mean['cdsvm'] = np.mean(acc_all['cdsvm'],axis=1)
acc_std['cdsvm'] = np.std(acc_all['cdsvm'],axis=1)
auc_all['cdsvm'] = np.array(auc_all['cdsvm'])
auc_mean['cdsvm'] = np.mean(auc_all['cdsvm'],axis=1)
auc_std['cdsvm'] = np.std(auc_all['cdsvm'],axis=1)

acc_all['svm'] = np.array(acc_all['svm'])
acc_mean['svm'] = np.mean(acc_all['svm'],axis=1)
acc_std['svm'] = np.std(acc_all['svm'],axis=1)
auc_all['svm'] = np.array(auc_all['svm'])
auc_mean['svm'] = np.mean(auc_all['svm'],axis=1)
auc_std['svm'] = np.std(auc_all['svm'],axis=1)

acc_all['whole'] = np.array(acc_all['whole']).reshape((1,10))
acc_mean['whole'] = np.array([np.mean(acc_all['whole'])])
acc_std['whole'] = np.array([np.std(acc_all['whole'])])
auc_all['whole'] = np.array(auc_all['whole']).reshape((1,10))
auc_mean['whole'] = np.array([np.mean(auc_all['whole'])])
auc_std['whole'] = np.array([np.std(auc_all['whole'])])

source_list = np.array(src_list).T

cdsvm_result = pd.concat([pd.DataFrame(source_list), pd.DataFrame(acc_all['cdsvm']),
                          pd.DataFrame(acc_mean['cdsvm']),pd.DataFrame(acc_std['cdsvm']),
                          pd.DataFrame(auc_all['cdsvm']),pd.DataFrame(auc_mean['cdsvm']),
                          pd.DataFrame(auc_std['cdsvm'])], axis=1)

svm_result = pd.concat([pd.DataFrame(source_list), pd.DataFrame(acc_all['svm']),
                          pd.DataFrame(acc_mean['svm']),pd.DataFrame(acc_std['svm']),
                          pd.DataFrame(auc_all['svm']),pd.DataFrame(auc_mean['svm']),
                          pd.DataFrame(auc_std['svm'])], axis=1)

result_whole = pd.concat([pd.DataFrame(np.zeros(1)), pd.DataFrame(acc_all['whole']),
                          pd.DataFrame(acc_mean['whole']),pd.DataFrame(acc_std['whole']),
                          pd.DataFrame(auc_all['whole']),pd.DataFrame(auc_mean['whole']),
                          pd.DataFrame(auc_std['whole'])], axis=1)

df = pd.concat([cdsvm_result, svm_result, result_whole],axis=0)
#df = pd.concat([cdsvm_result, svm_result],axis=0)
df.to_csv("%sfold_result_%s_%s.csv"%(kfold, tar_domain[1],tar_domain[0]))

for i in dec:
    pd.DataFrame(np.array(dec[i])).to_csv('dec_%s_%s_%s.csv'%(i,tar_domain[1],tar_domain[0]))
