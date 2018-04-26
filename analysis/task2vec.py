# -*- coding: utf-8 -*-
"""
Created on Wed Apr 25 23:24:33 2018

@author: sz144
"""

import numpy as np
import pandas as pd

def task2vec(task_file='Brain_func.csv'):
    task_df = pd.read_csv(task_file, header = 0)
    id_ar = np.unique(task_df.loc[:,'id']) 
    func_list =  list(set(task_df.loc[:,'func']) )
    func_dict = {}
    for i in task_df.index.values:
        task_id = task_df.loc[i,'id']
        if task_id not in func_dict:
            func_dict[task_id] = []
        func_dict[task_id].append(task_df.loc[i,'func'])
        
    func_vecs = np.zeros((len(id_ar), len(func_list)))
    
    for i in range(len(id_ar)):
        for f in func_dict[id_ar[i]]:
            func_vecs[i, func_list.index(f)] = 1
    vec_df = pd.DataFrame(func_vecs, index = id_ar, columns = func_list)
    vec_df.to_csv('task_vecs.csv')
    return func_vecs, id_ar, func_list
        
    
    

