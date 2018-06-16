# -*- coding: utf-8 -*-
"""
Created on Fri Aug 11 16:47:24 2017

@author: Shuo Zhou, the University of sheffield

USAGE: python <PROGRAM> options
ACTION: Multi-class classification
OPTIONS: 
    -b: specify the basedir (contains data labels)
    -i: specify the directory of ICA data
    -h: print help
    
"""

from sklearn.svm import LinearSVC,SVC
from sklearn.model_selection import StratifiedKFold,LeaveOneOut
#import da_tool.tca
import pickle
import numpy as np
import sys,os
import getopt
import matplotlib.pyplot as plt
from sklearn.metrics import confusion_matrix,accuracy_score,classification_report
import itertools


class commandline:
    def __init__(self):
        opts,args = getopt.getopt(sys.argv[1:],'b:h')
        opts = dict(opts)        
        # default do not submit jod to HPC
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

            
    def printHelp(self):
        helpinfo = __doc__.replace('<PROGRAM>',sys.argv[0],1)
        print helpinfo
        print sys.stderr
        sys.exit()

def plot_confusion_matrix(cm, classes,
                          normalize=False,
                          title='Confusion matrix',
                          cmap=plt.cm.Blues):
    """
    This function prints and plots the confusion matrix.
    Normalization can be applied by setting `normalize=True`.
    """
    if normalize:
        cm = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]
        print("Normalized confusion matrix")
    else:
        print('Confusion matrix, without normalization')

    print(cm)

    plt.imshow(cm, interpolation='nearest', cmap=cmap)
    plt.title(title)
    plt.colorbar()
    tick_marks = np.arange(len(classes))
    plt.xticks(tick_marks, classes, rotation=45)
    plt.yticks(tick_marks, classes)

    fmt = '.2f' if normalize else 'd'
    thresh = cm.max() / 2.
    for i, j in itertools.product(range(cm.shape[0]), range(cm.shape[1])):
        plt.text(j, i, format(cm[i, j], fmt),
                 horizontalalignment="center",
                 color="white" if cm[i, j] > thresh else "black")

    
    plt.xlabel('Predicted Label') 
    plt.tight_layout()
    plt.ylabel('True Label')
    plt.savefig('cm11.pdf', format='pdf', dpi=1000)      
        

config = commandline()
#icadir = config.icadir
basedir = config.basedir
# load data

task_ids = [1,2,3,4,5,6,8,9,10,21,22]

data_run1=np.load(os.path.join(basedir,'zstat_run1.npy'))  
data_run2=np.load(os.path.join(basedir,'zstat_run2.npy'))  
data = np.hstack((data_run1,data_run2))

labels_run1=np.loadtxt(os.path.join(basedir,'data_key_run1.txt'))[:,0]
labels_run2=np.loadtxt(os.path.join(basedir,'data_key_run2.txt'))[:,0]
labels = np.hstack((labels_run1,labels_run2))

#data=np.load(os.path.join(basedir,'zstat_run1.npy'))  
#labels=np.loadtxt(os.path.join(basedir,'data_key_run1.txt'))[:,0]
data = data.T

#initilize accuracy
acc={}


class_names = ['Task 1','Task 2','Task 3','Task 4','Task 5','Task 6','Task 8','Task 9','Task 10','Task 21','Task 22',]

# 10 fold cross-validation
skf = StratifiedKFold(n_splits=10)

svm = SVC(kernel='linear',C=100)
whole_pred = np.zeros(len(labels))
for train, test in skf.split(data,labels):
    svm.fit(data[train],labels[train])
    whole_pred[test] = svm.predict(data[test])
acc['whole'] = accuracy_score(whole_pred,labels)  
print classification_report(labels,whole_pred)
cm =  confusion_matrix(labels,whole_pred)
# Plot normalized confusion matrix
plt.figure()
plot_confusion_matrix(cm, classes=class_names, #normalize=True,
                      title='Confusion matrix (Whole-brain data classification)')
plt.savefig('cm1.pdf', format='pdf', dpi=1000)
plt.show()


