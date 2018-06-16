#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Fri Apr 27 19:06:33 2018

@author: shuoz
"""

import os
import numpy as np
import nibabel as nib
#from nilearn import plotting
from sklearn.model_selection import StratifiedKFold
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score
from utils.cmdline import commandline
import utils.load_data as load_data
import da_tool.tca
from da_tool.cdsvm import CDSVM

# =============================================================================
# 
# =============================================================================
def plot_coef(coef, img_name, maskimg, maskvox, thre_rate = 0.05):
    coef = coef.reshape(-1)
    n_voxel_th = int(coef.shape[0] * thre_rate)
    top_voxel_idx = (abs(coef)).argsort()[::-1][:n_voxel_th]
    thre = coef[top_voxel_idx[n_voxel_th-1]]
#    coef_to_plot = np.zeros(coef.shape[0])
#    coef_to_plot[top_voxel_idx] = coef[top_voxel_idx]
#    thre = np.amax(abs(coef)) * thre_rate # high absulte value times threshold rate
    coef_array = np.zeros((91, 109, 91))
    coef_array[maskvox] = coef
    coef_img = nib.Nifti1Image(coef_array, maskimg.affine)
    coef_img_file = '/shared/tale2/Shared/szhou/openfmri/coef_img/%s.nii.gz'%img_name
    nib.save(coef_img, coef_img_file)
    #plotting.plot_glass_brain(coef_img_file, output_file='%s.svg'%img_name)
    
#    plotting.plot_stat_map(coef_img, display_mode='x', threshold = thre,
#                           cut_coords=range(-50, 51, 10), output_file='%s.pdf'%img_name)
#    plotting.plot_stat_map(coef_img, display_mode='x', threshold = thre,
#                           cut_coords=range(-50, 51, 10), output_file='%s.png'%img_name)
# =============================================================================
# 
# =============================================================================
def overlap(pair1, pair2):
    overlapped = False
    for i in pair1:
        if i in pair2:
            overlapped = True
    return overlapped
# =============================================================================
# 
# =============================================================================
config = commandline()
target = config.target
source = config.source
basedir = load_data.BASEDIR

# load brain mask
mask=os.path.join(basedir,'goodvoxmask.nii.gz')
maskimg=nib.load(mask)
maskdata=maskimg.get_data()
maskvox=np.where(maskdata)

# get data
if config.clf_ica:
    data, label= load_data.load_ica(dim = config.dim, data_path=config.ica_dir,
                                    label_path = config.label_dir)
else:
    data, label = load_data.load_whole_brain(data_path = config.wb_dir, 
                                             label_path = config.label_dir)


task_ids = [1,2,3,4,5,6,8,9,10,21,22]

task_pairs = []

for i in task_ids:
    for j in task_ids:
        if i!=j:
            task_pairs.append([i,j])

for target in task_pairs:
    Xt, yt = load_data.get_domain_data(target, data, label)
    svm = SVC(kernel='linear')
    svm.fit(Xt, yt)
    coef_ = svm.coef_
    img_name = 'svm%svs%s'%(target[0], target[1])
    plot_coef(coef_, img_name, maskimg, maskvox)
    for source in task_pairs:
        if not overlap(target, source):
            Xs, ys = load_data.get_domain_data(source, data, label)
            # perform tca
            my_tca = da_tool.tca.TCA(n_components=50,kernel='linear')
            Xtcs, Xtct = my_tca.fit_transform(Xs, Xt)
            U = my_tca.U
            W = np.dot(np.vstack((Xs, Xt)).T, U)
            
            # tca+svm
            Xall = np.vstack((Xtcs, Xtct))
            yall = np.hstack((ys, yt))
            svm = SVC(kernel='linear', max_iter = 5000)
            svm.fit(Xall, yall)
            coef_ = np.dot(W, svm.coef_.T)[:,0]
            img_name = 'tca+svm%svs%s_%svs%s'%(target[0], target[1], source[0], source[1])
            plot_coef(coef_, img_name, maskimg, maskvox)    
            
            # tca + cdsvm
            svm.fit(Xtcs, ys)
            cdsvm = CDSVM(svm.support_vectors_, ys[svm.support_],C=10, beta=1)
            cdsvm.fit(Xtct, yt)
            coef_ = np.dot(W, cdsvm.coef_.T)[:,0]
            img_name = 'tca+cdsvm%svs%s_%svs%s'%(target[0], target[1], source[0], source[1])
            plot_coef(coef_, img_name, maskimg, maskvox)
            
