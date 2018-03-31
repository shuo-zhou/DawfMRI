#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sun Jul 23 11:45:18 2017

@author: Shuo Zhou, University of Sheffield

USAGE: python <PROGRAM> options
ACTION: generate scripts for running motion correction by fsl
OPTIONS:
    -d: dataset number e.g. ds001
    -b: base directory of the dataset
    -q: submit job to the University of Sheffield HPC
    -h: print help

"""

import os,glob
import sys,getopt

class commandline:
    def __init__(self):
        opts,args = getopt.getopt(sys.argv[1:],'d:b:qh')
        opts = dict(opts)        
        self.qsub = False
        
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
    ds_path = basedir + dataset
    script_name = 'featregapply_%s.sh'%dataset
    script_file = open(script_name,'w')
    script_file.write('#!/bin/bash\n')
    script_file.write('#$ -l rmem=8G\n')
    for subject in os.listdir(ds_path):
        if subject[0:3]=='sub':
            #print subject
            sub_path = ds_path+'/'+subject+'/'
            feat_dirs=[x for x in os.listdir(sub_path+'model/model001') if x.find('.feat')>0]
            #print feat_dirs
            for feat_dir in feat_dirs:
                feat_path = sub_path + 'model/model001/' + feat_dir + '/'
                #print feat_path
                zstats = [x for x in os.listdir(feat_path+'stats') if x[0:5]=='zstat']
                #print zstats
                for zstat in zstats:
                    script_file.write('singularity exec /home/acp16sz/fsl.img featregapply %s -l stats/%s\n'%(feat_path,zstat))
                    
    script_file.close()
    print 'now run: qsub %s/%s'%(full_path,script_name)
    
if __name__ == '__main__':
    main()
                
            
            