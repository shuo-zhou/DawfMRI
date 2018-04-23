# -*- coding: utf-8 -*-
"""
Created on Sun Apr 22 20:50:06 2018

@author: sz144
"""

import pandas as pd

TASK_LIST = [1, 2, 3, 4, 5, 6, 8, 9, 10, 21, 22]

def get_sim_dict(tar1, tar2, sim_df):
    sim_dict = {}
    for t in TASK_LIST:
        if t != tar1 and t != tar2:
            sim_dict[t] = sim_df.loc[tar1, str(t)] - sim_df.loc[tar2, str(t)]
    return sim_dict
sim_df = pd.read_csv('task_similarity.csv', header=0, index_col=0)



tar = [3, 6]

sim_dict = {}

sim_dict[tar[0]] = get_sim_dict(tar[0], tar[1], sim_df)
sim_dict[tar[1]] = get_sim_dict(tar[1], tar[0], sim_df)     