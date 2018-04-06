#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Fri Aug 18 14:55:11 2017

@author: Shuo Zhou, University of Sheffield

Linear Cross domain SVM

Ref: Jiang, W., Zavesky, E., Chang, S.-F., and Loui, A. Cross-domain learning methods 
    for high-level visual concept classification. In Image Processing, 2008. ICIP
    2008. 15th IEEE International Conference on (2008), IEEE, pp. 161-164.
"""
import numpy as np
from cvxopt import matrix, solvers
from sklearn.metrics import accuracy_score

class CD_SVM(object):
    def __init__(self,support_vectors, support_vector_labels,C=0.1, beta=0.5):
        self.C = C
        self.beta = beta
        self.support_vectors = support_vectors
        self.support_vector_labels = support_vector_labels
        
    def fit(self,X,y):
        n_support = len(self.support_vector_labels)
        n_samples = X.shape[0]
        n_features = X.shape[1]
        X = X.reshape((n_samples,n_features))
        y = y.reshape((n_samples,1))
        self.support_vector_labels = self.support_vector_labels.reshape((n_support,1))
        shift_w = 0
        
        
        #create matrix Q
        paramCount = n_support + n_samples + n_features
        Q = np.zeros((paramCount,paramCount))
        for row in range(n_features):
            Q[shift_w+row,shift_w+row] = 1
            
            
        # create vector p
        p = np.zeros((n_features,1))
        p = np.vstack((p,self.C * np.ones((n_samples,1))))
        p_ = np.zeros((n_support,1))
        for row in range(n_support):
            p_[row,0] = self.C * self.sigma(self.support_vectors[row,:],X)
        p = np.vstack((p,p_))
        
        
        # create the Matrix of SVM contraints
        G = np.zeros((n_samples*2,paramCount))
        for row in range(n_samples):
            for col in range(n_features):
                G[row,col] = -X[row,col] * y[row,0]
            G[row,n_features+row] = -1
            G[n_samples+row,n_features+row] = -1
        G_ = np.zeros((n_support*2,paramCount))
        for row in range(n_support):
            for col in range(n_features):
                G_[row,col] = -self.support_vectors[row,col] * self.support_vector_labels[row,0]
            G_[row,n_features+n_samples+row] = -1
            G_[n_support+row,n_features+n_samples+row] = -1
        G = np.vstack((G,G_))
            
        #create vector of h
        h = np.ones((n_samples,1))
        h = np.vstack((-h,np.zeros((n_samples,1))))
        h = np.vstack((h,-np.ones((n_support,1))))
        h = np.vstack((h,np.zeros((n_support,1))))
        
        # convert numpy matrix to cvxopt matrix
        Q = 2*matrix(Q)
        p = matrix(p)
        G = matrix(G)
        h = matrix(h)
        #print Q
        #print p
        #print G
        #print h
        solvers.options['show_progress'] = False
        sol = solvers.qp(Q,p,G,h)
        
        self.coef_ = sol['x'][0:n_features]
        self.coef_ = np.array(self.coef_).T
        
        
    def sigma(self,support_vector, X):
        n_samples = X.shape[0]
        sigma = 0
        for i in range(n_samples):
            sigma +=  np.exp(-self.beta * np.linalg.norm(support_vector-X[i,:]))
        sigma = sigma / n_samples
        return sigma
        
    def predict(self,X):
        pred = np.sign(self.decision_function(X))
        
        return pred
        
    def decision_function(self,X):
        decision = np.dot(X,self.coef_.T)
        #print 'src:',np.dot(X,self.source_w.T)
        #print 'adaptive:',np.dot(X,self.source_w.T)+np.dot(X,self.coef_)
        return decision[:,0]
    
    def score(self,X,y):
        pred = self.predict(X)
        return accuracy_score(pred,y)
    
    def get_params(self,deep=True):
        out = '(C='+str(self.C)+', beta='+str(self.beta)+')'
        return out
