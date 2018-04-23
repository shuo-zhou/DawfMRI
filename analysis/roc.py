# -*- coding: utf-8 -*-
"""
Created on Thu Nov 23 16:54:07 2017

@author: sz144
"""
import pickle
import pandas as pd
import numpy as np
from sklearn.metrics import confusion_matrix,accuracy_score,classification_report, roc_auc_score, roc_curve
from scipy.stats import ttest_ind
from sklearn.model_selection import StratifiedKFold

skf = StratifiedKFold(n_splits=10)
def get_src_domains(tar_domain):
    #task_ids = [1,2,3,4,6,8,9,10,21,22] # exclude task 5
    task_ids = [1,2,3,4,5,6,8,9,10,21,22]
    src_domain_pool = list(set(task_ids) - set(tar_domain))
    src_list = []
    src_domains = []
    for i in range(len(src_domain_pool)-1):
        for j in range (i+1,len(src_domain_pool)):
            src_domains.append([src_domain_pool[i],src_domain_pool[j]])
            src_list.append('%s_%s'%(src_domain_pool[i],src_domain_pool[j]))
    return src_domains, src_list

def switch_df_label(df):
    for i in df.index:
        if i != 56:
            df.loc[i,'0'] = switch_label(df.loc[i,'0'])
    return df

def switch_label(domain):
    domain_list = domain.split("_")
    domain = domain_list[1]+'_'+domain_list[0]
    return domain

def dec_to_dict(dec_dict,df,src_list,rev=False):
    if rev:
        dec_dict['_true_label'] = df.iloc[0,:].as_matrix()
    else:
        dec_dict['true_label'] = df.iloc[0,:].as_matrix()
    c = 0
    for src in src_list:
        if rev:
            rev_src = switch_label(src)
            dec_dict[rev_src] = df.iloc[c*10+1:c*10+11,:].as_matrix()
        else:
            dec_dict[src] = df.iloc[c*10+1:c*10+11,:].as_matrix()
        c+=1
    return dec_dict
#def dec_dict(dec_dict, src_list):
    
def sen_spe(cm):
    tp = cm[0,0]
    fp = cm[0,1]
    fn = cm[1,0]
    tn = cm[1,1]
    sen = tp/(tp+fn)
    spe = tn/(tn+fp)
    acc = (tp+tn)/(tp+tn+fp+fn)
    return sen, spe, acc

def rev(domain):
    rev = False
    tasks = domain.split('_')
    if int(tasks[0])>int(tasks[1]):
        rev = True
    return rev

tar_domain = [3,6]
#tar_domain = [6,22]
#tar_domain = [1,22]

f=open('src_dict/src_dict%s_%stca.pkl'%(tar_domain[0],tar_domain[1]),'rb')
src_dict=pickle.load(f)
f.close()

src_domains, src_list = get_src_domains(tar_domain)
f = open("results.txt",'w')
## domain adaptation
dec_da = {}
clf_list = ['cdsvm','svm']

for i in clf_list:
    dec_da[i] = {}
    dec_df = pd.read_csv('decisions/tca/dec_%s_%s_%s.csv'
                        %(i,tar_domain[0],tar_domain[1])).drop('Unnamed: 0',axis=1)
    dec_da[i] = dec_to_dict(dec_da[i], dec_df, src_list)
    dec_df_rev = pd.read_csv('decisions/tca/dec_%s_%s_%s.csv'
                            %(i,tar_domain[1],tar_domain[0])).drop('Unnamed: 0',axis=1)
    dec_da[i] = dec_to_dict(dec_da[i], dec_df_rev, src_list,rev=True)


acc_m = {}
acc_m['cdsvm'] = {}
for i in clf_list:
    print(i)
    print(i, file=f)
    for src in src_dict[i]:
        print(src)
        print(src, file=f)
        sen_list = []
        spe_list = []
        acc_list = []
        acc_m['cdsvm'][src] = []
        for j in range(10):
            dec_temp = dec_da[i][src][j,:]
            y_ = dec_da[i]['true_label']
            for train, test in skf.split(dec_temp,y_):
                pred_temp = np.sign(dec_temp[test])
                acc_m['cdsvm'][src].append()
            pred = np.sign(dec_da[i][src][j,:])
            if rev(src):
                pred = - pred           
            cm = confusion_matrix(dec_da[i]['true_label'],pred)
            print(cm, file=f)
            sen, spe, acc = sen_spe(cm)
            print(sen,spe,acc,file=f)
            #tpr, fpr, thr = roc_curve(dec_dict[i]['true_label'],np.sign(dec_dict[i][src][j,:]))
            sen_list.append(sen)
            spe_list.append(spe)
            acc_list.append(acc)
        print(np.mean(sen_list),np.mean(spe_list),np.mean(acc_list))
        
## non-adaptation 

dec_svm_df = pd.read_csv('decisions/tca/dec_whole_%s_%s.csv'
                        %(tar_domain[0],tar_domain[1])).drop('Unnamed: 0',axis=1)
dec_icasvm_df = pd.read_csv('decisions/ica/dec_icasvm_%s_%s.csv'
                        %(tar_domain[0],tar_domain[1])).drop('Unnamed: 0',axis=1)

dec_non_da = {}
dec_non_da['svm']= dec_svm_df.as_matrix()
dec_non_da['ivasvm'] = dec_icasvm_df.as_matrix()

for i in dec_non_da:
    print(i)
    print(i, file=f)
    y_true = dec_non_da[i][0,:]
    sen_list = []
    spe_list = []
    acc_list = []
    for j in range(1,11):
        pred = np.sign(dec_non_da[i][j,:])
        cm = confusion_matrix(y_true,pred)
        sen, spe, acc = sen_spe(cm)
        print(cm, file=f)
        print(sen,spe,acc,file=f)
        sen_list.append(sen)
        spe_list.append(spe)
        acc_list.append(acc)
    print(np.mean(sen_list),np.mean(spe_list),np.mean(acc_list))
f.close()