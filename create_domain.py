#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sat Mar 31 17:34:30 2018

@author: shuoz
"""

import numpy as np

    
def create(X, y, pos_id, neg_id):
    X_ = []
    y_ = []
    n = X.shape[0]
    if n != len(y):
        print("Error, the input data and label have different size")
        return False
    else:
        for i in range(n):
            if y[i] == pos_id:
                X_.append(X[i,:])
                y_.append(1)
            elif y[i] == neg_id:
                X_.append(X[i,:])
                y_.append(-1)
        X_ = np.asarray(X_)
        y_ = np.asarray(y_)
        return X_, y_