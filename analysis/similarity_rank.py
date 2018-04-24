# -*- coding: utf-8 -*-
"""
Created on Sun Apr 22 20:50:06 2018

@author: sz144
"""

import pandas as pd
import matplotlib.pyplot as plt

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

def metric(s1, s2, s3, s4, metric = 'sum'):
    m = 0
    if metric == 'sum':
        m = s1 + s2 + s3 +s4
    elif metric == 'x':
        m = s1 * s2 *s3 *s4
    elif metric == 'xsum':
        m  =  s1 * s2 + s3 * s4
    elif metric == 'sumx':
        m = (s1 + s2) * (s3 + s4)
    elif metric == '-x':
        m = (s1-s2) * (s3-s4)
    return m


def get_src_pairs(tar):
    pairs = []
    for i in range(len(TASK_LIST)):
        src1 = TASK_LIST[i]
        for j in range(i+1, len(TASK_LIST)):
            src2 = TASK_LIST[j]
            if src1 not in tar and src2 not in tar:
                pairs.append([src1, src2])
    return pairs


sim_df = pd.read_csv('task_similarity.csv', header=0, index_col=0)

res_df = pd.read_csv('10fold_adaptation_matrix.csv', header=0, index_col=0)

tar = [1, 22]

src_pairs = get_src_pairs(tar)
src_pairstr = pair_to_str(src_pairs)

pair_sim_list = []
for sp in src_pairs:
    s1 = sim_df.loc[tar[0], str(sp[0])]
    s2 = sim_df.loc[tar[1], str(sp[0])]
    s3 = sim_df.loc[tar[0], str(sp[1])]
    s4 = sim_df.loc[tar[1], str(sp[1])]
    pair_sim_list.append(metric(s1, s2, s3, s4, metric = 'sum'))
    
pair_sim_df = pd.DataFrame(data=pair_sim_list, index=src_pairstr)
sort_src = pair_sim_df.sort_values(0, ascending=False).index.values.astype(str)
acc_list = []
sort_src_list = []
for s in sort_src:
    acc_list.append(abs(res_df.loc[str(tar[0])+','+str(tar[1]), s]))
    sort_src_list.append(s)
    
plt.plot(acc_list, 'o')
plt.xticks(range(len(sort_src_list)), sort_src_list, rotation=50, 
           horizontalalignment='right')
plt.show()
    
#sim_dict = {}
#
#sim_dict[tar[0]] = get_sim_dict(tar[0], tar[1], sim_df)
#sim_dict[tar[1]] = get_sim_dict(tar[1], tar[0], sim_df)     