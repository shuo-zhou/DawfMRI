# -*- coding: utf-8 -*-
"""
Created on Sun Apr 22 20:50:06 2018

@author: sz144
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics.pairwise import cosine_similarity
from task2vec import task2vec
from scipy.stats import kendalltau

TASK_LIST = [1, 2, 3, 4, 5, 6, 8, 9, 10, 21, 22]

def get_sim_dict(tar1, tar2, sim_df):
    sim_dict = {}
    for t in TASK_LIST:
        if t != tar1 and t != tar2:
            sim_dict[t] = sim_df.loc[tar1, str(t)] - sim_df.loc[tar2, str(t)]
    return sim_dict

def pair_to_str(pair_list):
    str_list = []
    for p in pair_list:
        str_list.append(str(p[0])+','+str(p[1]))
    return str_list

<<<<<<< HEAD
def metric(task_vec1, task_vec2, task_vec3, task_vec4):
=======
def metric(task_vec1, task_vec2, task_vec3, task_vec4, lmbda = 0.3):
#    clf_task1 = task_vec1-task_vec2 + np.multiply(task_vec1, task_vec2)*2
#    clf_task2 = task_vec3-task_vec4 + np.multiply(task_vec3, task_vec4)*2
#    sim1 = cosine_similarity(task_vec1, task_vec3)
#    sim2 = cosine_similarity(task_vec2, task_vec4)
    
#    sim_diff = cosine_similarity((task_vec1 - task_vec2), (task_vec3 - task_vec4))
#    sim_sum = cosine_similarity((task_vec1 + task_vec2), (task_vec3 + task_vec4))
#    return  sim_diff[0,0] + sim_sum[0,0] * lmbda
#    #return sim_sum[0,0]
    
#    clf_task1 = task_vec1-task_vec2
#    clf_task2 = task_vec3-task_vec4
#    clf_task1[np.where(overlap1==2)] = 2
#    clf_task2[np.where(overlap2==2)] = 2
#    #sim_diff = cosine_similarity(clf_task1, clf_task2)
#    #sim_sum = cosine_similarity((task_vec1 + task_vec2), (task_vec3 + task_vec4))
#    return cosine_similarity(clf_task1, clf_task2)[0,0]#np.correlate(clf_task1[0], clf_task2[0])# sim_diff[0,0]# + sim_sum[0,0] * lmbda
#    #return sim_sum[0,0]
#    return sim1[0,0] + sim2[0,0]
>>>>>>> master
    tar_vec = np.hstack((task_vec1, task_vec2))
    src_vec = np.hstack((task_vec3, task_vec4))

    return cosine_similarity(tar_vec, src_vec)[0,0]


def get_src_pairs(tar):
    pairs = []
    for i in range(len(TASK_LIST)):
        src1 = TASK_LIST[i]
        for j in range(i+1, len(TASK_LIST)):
            src2 = TASK_LIST[j]
            if src1 not in tar and src2 not in tar:
                pairs.append([src1, src2])
    return pairs

def pair_switch(pair_list):
    swithed_pairs = []
    for p in pair_list:
        swithed_pairs.append([p[1], p[0]])
    return swithed_pairs


sim_df = pd.read_csv('task_similarity.csv', header=0, index_col=0)

res_df = pd.read_csv('10fold_adapmat_full.csv', header=0, index_col=0)

targets = [[1, 22], [3, 6], [6, 22]]

task_vecs, id_ar, func_list = task2vec()

for tar in targets:
    src_pairs = get_src_pairs(tar)
    src_pairs = src_pairs + pair_switch(src_pairs)
    src_pairstr = pair_to_str(src_pairs)
    tar_str = str(tar[0])+','+str(tar[1])
    baseline = np.ones(len(src_pairs)) * res_df.loc[tar_str, tar_str]
    t1_idx = np.where(id_ar == tar[0])[0]
    t2_idx = np.where(id_ar == tar[1])[0]
    task_vec1 = task_vecs[t1_idx,:]
    task_vec2 = task_vecs[t2_idx,:]

    pair_sim_list = []
    for sp in src_pairs:
        t3_idx = np.where(id_ar == sp[0])[0]
        t4_idx = np.where(id_ar == sp[1])[0]
        task_vec3 = task_vecs[t3_idx,:]
        task_vec4 = task_vecs[t4_idx,:]
        pair_sim_list.append(metric(task_vec1, task_vec2, task_vec3, task_vec4))
        
    pair_sim_df = pd.DataFrame(data=pair_sim_list, index=src_pairstr)
    sort_src = pair_sim_df.sort_values(0, ascending=False).index.values.astype(str)
    acc_list = []
    sort_src_list = []
    for s in sort_src:
        acc_list.append(abs(res_df.loc[tar_str, s]))
        sort_src_list.append(s)
        
    plt.figure(figsize = (16,9))
    plt.plot(acc_list, 'o', label='TCA+CDSVM')
    plt.plot(baseline, 'r-', label = 'SVM')
    plt.xticks(range(len(sort_src_list)), sort_src_list, rotation=50, 
               horizontalalignment='right')
    plt.title('Target:%s'%tar_str)
    plt.xlabel('Source Domain')
    plt.ylabel('Accuracy')
    plt.legend()
    plt.savefig('Target:%s.eps'%tar_str,format='eps')
    plt.show()

    
#sim_dict = {}
#
#sim_dict[tar[0]] = get_sim_dict(tar[0], tar[1], sim_df)
#sim_dict[tar[1]] = get_sim_dict(tar[1], tar[0], sim_df)     