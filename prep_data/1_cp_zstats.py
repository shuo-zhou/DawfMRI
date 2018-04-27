#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Mon Jul 24 21:52:10 2017

@author: Shuo Zhou, University of Sheffield

USAGE: python <PROGRAM> options
ACTION: copy z-statistics data to a given directory
OPTIONS:
    -d: dataset number e.g. ds001
    -b: base directory of the dataset
    -z: directory for zstat data
    -q: submit job to the University of Sheffield HPC
    -h: print help
    
Ref: Poldrack, R. A., Barch, D. M., Mitchell, J., Wager, T., Wagner, A. D., Devlin, J.T., 
    Cumba, C., Koyejo, O., and Milham, M. Toward open sharing of task-based fmri data: 
    the openfmri project. Frontiers in neuroinformatics 7 (2013), 12.
"""

import os,glob
import sys,getopt

class commandline:
    def __init__(self):
        opts,args = getopt.getopt(sys.argv[1:],'d:b:o:qh')
        opts = dict(opts)
        self.qsub = False
        self.basedir = os.getcwd()
        self.outdir = os.getcwd()
        self.dataset = 'ds001'

        if '-h' in opts:
            self.printHelp()

        if '-b' in opts:
            self.basedir = opts['-b']
            if self.basedir[-1]!='/':
                self.basedir+='/';
            if not os.path.exists(self.basedir):
                print 'basedir %s does not exist!'%self.basedir
                self.printHelp()

        if '-d' in opts:
            self.dataset = opts['-d']
            if not os.path.exists(self.basedir+self.dataset):
                print 'dataset %s does not exist!'%self.dataset
                self.printHelp()

        if '-o' in opts:
            self.zstat_dir = opts['-o']
            if self.zstat_dir[-1]!='/':
                self.zstat_dir+='/';
            if not os.path.exists(self.zstat_dir):
                print 'output directory for zstat data does not exist!'
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
    full_path = os.path.dirname(os.path.realpath(__file__))
    dataset = config.dataset
    basedir = config.basedir
    zstat_dir = config.zstat_dir
    ds_path = basedir + dataset
    script_name = 'cp_zstat_%s.sh'%dataset
    script_file = open(script_name,'w')
    if config.qsub:
        script_file.write('#!/bin/bash\n')
        script_file.write('#$ -l rmem=8G\n')
    for subject in os.listdir(ds_path):
        if subject[0:3]=='sub':
            #print subject
            sub_path = ds_path+'/'+subject+'/'
            feat_dirs=[x for x in os.listdir(sub_path+'model/model001') if x.find('.feat')>0]
            #print feat_dirs
            for feat_dir in feat_dirs:
                task_run = feat_dir[0:14]
                #print feat_path
                zstat_path = sub_path + 'model/model001/' + feat_dir + '/reg_standard/stats/'
                zstats = [x for x in os.listdir(zstat_path) if x[0:5]=='zstat']
                #print zstats
                for zstat in zstats:
                    script_file.write('cp %s%s %s%s_%s_%s_%s \n'%(zstat_path,zstat,zstat_dir,dataset,subject,task_run,zstat))

    script_file.close()
    if config.qsub:
        print('now run: qsub %s/%s'%(full_path,script_name))
    else:
        print('now run: bash %s/%s'%(full_path,script_name))

if __name__ == '__main__':
    main()
