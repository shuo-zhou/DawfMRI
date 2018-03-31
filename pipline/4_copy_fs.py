#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Fri Jul 21 15:47:55 2017

@author: Shuo Zhou, University of Sheffield


"""

import os,glob
import sys,getopt

class commandline:
    def __init__(self):
        opts,args = getopt.getopt(sys.argv[1:],'d:b:s:qh')
        opts = dict(opts)        
        # default do not submit jod to HPC
        self.qsub = False
        self.level = 1
        
        if '-h' in opts:
            self.printHelp()
        
        if '-b' in opts:
            self.basedir = opts['-b']
            if self.basedir[-1]!='/':
                self.basedir+='/';
            if not os.path.exists(self.basedir):
                print 'basedir %s does not exist!'%self.basedir
                self.printHelp()
        else:
            print '***Error: basedir argument not given ***'
            self.printHelp()
        
        if '-d' in opts:
            self.dataset = opts['-d']
            if not os.path.exists(self.basedir+self.dataset):
                print 'dataset %s does not exist!'%self.dataset
                self.printHelp()
        else:
            print '***Error: dataset argument not given ***'
            self.printHelp()
            
        if '-s' in opts:
            self.fs_dir = opts['-s']
            if not os.path.exists(self.fs_dir):
                print 'Directory for freesurfer format files not exists!'
                self.printHelp()
        else:
            print '***Error: directory for freesurfer format files not given ***'
            self.printHelp()

        
        if '-q' in opts:
            self.qsub = True
        
        
            
    def printHelp(self):
        helpinfo = __doc__.replace('<PROGRAM>',sys.argv[0],1)
        print helpinfo
        print sys.stderr
        sys.exit()
            
            
def main():
    config = commandline()
    
    #write command to script file  

    full_path = os.path.dirname(os.path.realpath(__file__))
    
    dataset_path = os.path.join(config.basedir,config.dataset)
    if config.qsub:
        qsub_name = 'copy_fs_%s_qsub.sh'%(config.dataset)
        qsub_file = open(qsub_name,'w')
        i = 0
        for root,dirs,files in os.walk(dataset_path):
            for f in files:
                if f.rfind('highres001.nii.gz')>-1 and root.find(config.dataset)>-1:
                    path_split=root.split('/')
                    sub_name = 'autorecon_%s_%s_%s.sh'%(config.dataset,config.level,i)
                    sub_file = open(sub_name,'w')
                    _sub_name = 'autorecon_%s_%s_%s_fsl.sh'%(config.dataset,config.level,i)
                    _sub_file = open(_sub_name,'w')
                    sub_file.write('#!/bin/bash\n')
                    sub_file.write('#$ -l rmem=8G\n')
                    sub_file.write('singularity exec /usr/local/packages/singularity/images/freesurfer/freesurfer-2017-07-07.img ')
                    sub_file.write('mri_convert --out_orientation LAS %s/%s_%s/mri/brainmask.mgz --reslice_like %s/highres001.nii.gz  %s/highres001_brain.nii\n'%(config.fs_dir,path_split[-3],path_split[-2],root,root))
                    sub_file.write('gzip %s/highres001_brain.nii\n'%root)
                    sub_file.write('qsub %s\n'%_sub_name)
                    sub_file.close()
                    _sub_file.write('#!/bin/bash\n')
                    _sub_file.write('#$ -l rmem=8G\n')
                    _sub_file.write('singularity exec /home/acp16sz/fsl.img fslmaths %s/highres001_brain.nii.gz -thr 1 -bin %s/highres001_brain_mask.nii.gz\n'%(root,root))
                    qsub_file.write('qsub %s\n'%sub_name)
                    i+=1
        qsub_file.close()
        print 'run "bash %s/%s" to submit job to HPC'%(full_path,qsub_name)
    else:
        script_name = 'autorecon_%s_%s.sh'%(config.dataset,config.level)
        script_file =open(script_name,'w')
        for root,dirs,files in os.walk(dataset_path):
            for f in files:
                if f.rfind('highres001.nii.gz')>-1 and root.find(config.dataset)>-1:
                    path_split=root.split('/')
                    script_file.write('mri_convert --out_orientation LAS %s/%s_%s/mri/brainmask.mgz --reslice_like %s/highres001.nii.gz  %s/highres001_brain.nii\n'%(config.fs_dir,path_split[-3],path_split[-2],root,root))
                    script_file.write('gzip %s/highres001_brain.nii\n'%root)
                    script_file.write('fslmaths %s/highres001_brain.nii.gz -thr 1 -bin %s/highres001_brain_mask.nii.gz\n'%(root,root))
        script_file.close()
        print 'now run: bash %s/%s'%(full_path,script_name)
    
if __name__ == '__main__':
    main()