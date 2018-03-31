#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Fri Jul 21 14:58:51 2017

@author: Shuo Zhou, University of Sheffield

USAGE: python <PROGRAM> options
ACTION: generate scripts for running motion correction by fsl
OPTIONS:
    -d: dataset number e.g. ds001
    -b: base directory of the dataset
    -l: reconst
    -s: directory for freesurfer format files
    -h: print help
"""


import os,glob
import sys,getopt

class commandline:
    def __init__(self):
        opts,args = getopt.getopt(sys.argv[1:],'d:b:s:l:qh')
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
        
        if '-l' in opts:
            if isinstance(opts['-l'],int):
                self.level = opts['-l']
            else:
                print 'Parameter for level must be int!'
                self.printHelp
        
        if '-q' in opts:
            self.qsub = True
        
        
            
    def printHelp(self):
        helpinfo = __doc__.replace('<PROGRAM>',sys.argv[0],1)
        print helpinfo
        print sys.stderr
        sys.exit()
            
            
def main():
    config = commandline()
    script_name = 'autorecon_%s_%s.sh'%(config.dataset,config.level)
    script_file =open(script_name,'w')
    
    #write command to script file  
    for anat in glob.glob(os.path.join(config.basedir,config.dataset,'sub*/anatomy/highres001.nii.gz')):
        sub_num=int(anat.split('/')[-3].replace('sub',''))
        script_file.write('recon-all -autorecon%d -subjid %s_sub%03d -sd %s\n'%(config.level,config.dataset,sub_num,config.fs_dir))

   
    script_file.close()
  
    full_path = os.path.dirname(os.path.realpath(__file__))
    
    if config.qsub:
        qsub_name = 'recon_%s_%s_qsub.sh'%(config.dataset,config.level)
        qsub_file = open(qsub_name,'w')
        commands = open(script_name,'r')
        i = 0
        for command in commands:
            sub_name = 'recon_%s_%s_%s.sh'%(config.dataset,config.level,i)
            sub_file = open(sub_name,'w')
            sub_file.write('#!/bin/bash\n')
            sub_file.write('#$ -l rmem=8G\n')
            sub_file.write('singularity exec /usr/local/packages/singularity/images/freesurfer/freesurfer-2017-07-07.img %s'%command)
            sub_file.close()
            qsub_file.write('qsub %s\n'%sub_name)
            i+=1
        qsub_file.close()
        print 'run bash %s/%s to submit job to HPC'%(full_path,qsub_name)
    else:
        print 'now run: bash %s/%s'%(full_path,script_name)
    
if __name__ == '__main__':
    main()
