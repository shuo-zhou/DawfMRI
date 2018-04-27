#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Fri Apr 27 19:06:33 2018

@author: shuoz
"""

import os
import numpy as np
import nibabel as nib
from nilearn import plotting
from sklearn.model_selection import StratifiedKFold
from sklearn.svm import SVC

from cmdline import commandline
import load_data
import da_tool.tca
import da_tool.cdsvm

def get_domain_data(domain, data, label):
    n = len(label)
    data_ = []
    label_ = []
    for i in range(n):
        if label[i] == domain[0]:
            data_.append(data[i,:])
            label_.append(1)
        elif label[i] == domain[1]:
            data_.append(data[i,:])
            label_.append(-1)
    data_ = np.asarray(data_)
    label_ = np.asarray(label_)
    return data_, label_

config = commandline()
target = config.target
source = config.source
basedir = load_data.BASEDIR

# load brain mask
mask=os.path.join(basedir,'goodvoxmask.nii.gz')
maskimg=nib.load(mask)
maskdata=maskimg.get_data()
maskvox=np.where(maskdata)


if config.clf_ica:
    data, label= load_data.load_ica(dim = config.dim, data_path=config.ica_dir,
                                    label_path = config.label_dir)
else:
    data, label = load_data.load_whole_brain(data_path = config.wb_dir, 
                                             label_path = config.label_dir)

Xt, yt = get_domain_data(target, data, label)
Xs, ys = get_domain_data(source, data, label)

# k-fold cv
skf = StratifiedKFold(n_splits=config.kfold)

my_tca = da_tool.tca.TCA(dim=50,kerneltype='linear')
Xtcs, Xtct, tar_o_tca, V, obj, obj_tca = my_tca.fit_transform(Xs, Xt)
V = V[:, :50]
W = np.dot(np.vstack((Xs, Xt)).T, V)

src_clf =  SVC(kernel='linear')
src_clf.fit(Xtcs, ys)
cdsvm = da_tool.cdsvm.CDSVM(src_clf.support_vectors_, ys[src_clf.support_],C=10, beta=1)
cdsvm.fit(Xtct, yt)
coef_cd = cdsvm.coef_
coefmap_cd = np.dot(W, coef_cd.T)[:,0]

Xall = np.vstack((Xtcs, Xtct))
yall = np.hstack((ys, yt))
svm = SVC(kernel='linear')
svm.fit(Xall, yall)
coef_svm = svm.coef_
coefmap_svm = np.dot(W, coef_svm.T)[:,0]

coef_brain = np.zeros((91, 109, 91))
coef_brain[maskvox] = coefmap_cd
coef_img = nib.Nifti1Image(coef_brain, maskimg.get_affine())

nib.save(coef_img, 'coef_img.nii.gz')

plotting.plot_glass_brain('coef_img.nii.gz')

plotting.plot_stat_map('coef_img.nii.gz', display_mode='x', threshold=0.0002,
                       cut_coords=range(0, 51, 10), title='Slices')