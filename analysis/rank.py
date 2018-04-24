# -*- coding: utf-8 -*-
"""
Created on Mon Nov 13 11:59:35 2017

@author: sz144
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import kendalltau
import random


def switch_df_label(df):
    for i in df.index:
        if i != 56:
            df.loc[i,'0'] = switch_label(df.loc[i,'0'])
    return df

def switch_label(domain):
    domain_list = domain.split("_")
    domain = domain_list[1]+'_'+domain_list[0]
    return domain

def get_result(df1,df2):
    result={}
    result['cdsvm'] = merge_result(df1.loc[0:27],df2.loc[0:27])
    result['svm'] = merge_result(df1.loc[28:55],df2.loc[28:55])
    result['whole'] = df1.loc[56]
    return result

def merge_result(df, df_rev, mean_col='0.2',src_col='0'):
    df.is_copy= False
    for i in df.index:
        if df.loc[i,mean_col] < df_rev.loc[i,mean_col]:
            df.loc[i,:]=df_rev.loc[i,:]
            #df.loc[i,src_col] = switch_label(df.loc[i,src_col])
    return df
        

def rank_acc(top_rank, full_rank, tol):
    lower_bound = 0
    upper_bound = len(full_rank)
    count = 0
    for i in range(len(top_rank)):
        rank_rev = switch_label(top_rank[i])
        if i - tol > 0:
            lower_bound = i-tol
        if i + tol < len(full_rank):
            upper_bound = i+tol
        if tol == 0:
            upper_bound = i+1   
        tol_range = full_rank[lower_bound:upper_bound]
        if top_rank[i] in tol_range or rank_rev in tol_range:
            count+=1
    return count/len(top_rank)

def get_rank_list(df,by_col,value_col,asc=False):
    df = df.sort_values(by=[by_col],ascending=asc)
    rank_list = []
    for i in range(len(df)):
        rank_list.append(df.iloc[i,value_col])
    return rank_list

#tar_domain = [3,6]
#tar_domain = [6,22]
tar_domain = [1,22]
result_df = pd.read_csv('Results/5fold_result_%s_%s.csv'
                        %(tar_domain[0],tar_domain[1])).drop('Unnamed: 0',axis=1)
result_df_rev = pd.read_csv('Results/5fold_result_%s_%s.csv'
                            %(tar_domain[1],tar_domain[0])).drop('Unnamed: 0',axis=1)
mmd_df = pd.read_csv('Results/mmd_%s_%s.csv'
                            %(tar_domain[0],tar_domain[1])).drop('Unnamed: 0',axis=1)
#result_1_22 = pd.read_csv('Results/5fold_result_1_22.csv').drop('Unnamed: 0',axis=1)
#result_6_22 = pd.read_csv('Results/5fold_result_6_22.csv').drop('Unnamed: 0',axis=1)
#result_3_6 = pd.read_csv('Results/5fold_result_3_6.csv').drop('Unnamed: 0',axis=1)
#result_22_1 = pd.read_csv('Results/5fold_result_22_1.csv').drop('Unnamed: 0',axis=1)
#result_22_6 = pd.read_csv('Results/5fold_result_22_6.csv').drop('Unnamed: 0',axis=1)
#result_6_3 = pd.read_csv('Results/5fold_result_6_3.csv').drop('Unnamed: 0',axis=1)

#result_df_rev = switch_df_label(result_df_rev)
result_dict = get_result(result_df, result_df_rev)
rank_list = {}
rank_list['svm'] = get_rank_list(result_dict['svm'],'0.2',0)
rank_list['mmd'] = get_rank_list(mmd_df,'0.2',0,asc=True)
cor, p_val = kendalltau(rank_list['svm'], rank_list['mmd'])

rand_list = list(rank_list['mmd'])
rand_tau = []
rand_pval = []
count = 0
for i in range(10000):
    #random.seed(i*100)
    random.shuffle(rand_list)
    tau_i, pval_i = kendalltau(rand_list, rank_list['mmd'])
    rand_tau.append(tau_i)
    rand_pval.append(pval_i)
    if tau_i > 0.3:
        count +=1
        

    

'''
tol_range = [0,2,4,6,8,10,12,14,16,18,20,22,24,26,28,30,32]


top5acc = []
top5mmd = []    
for tol in tol_range:
    top5acc.append(rank_acc(rank_array['svm'][0:5],rank_array['mmd'],tol))
    top5mmd.append(rank_acc(rank_array['mmd'][0:5],rank_array['svm'],tol))
    
plt.title('Rank Match Accuracy for Top Accuracy and MMD')
plt.xlabel('Tolerance')
plt.ylabel('Match Accuracy')
plt.plot(tol_range,top5acc,'ro-',label='Top 5 Acc')
plt.plot(tol_range,top5mmd,'bo-',label='Top 5 MMD')
plt.legend(loc="best")
plt.show()
'''