#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Wed Jul 19 23:42:25 2017

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
        # default do not submit jod to HPC
        self.qsub = False
        
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
            
        if '-h' in opts:
            self.printHelp()
            
    def printHelp(self):
        helpinfo = __doc__.replace('<PROGRAM>',sys.argv[0],1)
        print helpinfo
        print sys.stderr
        sys.exit()
            
            
def main():
    config = commandline()
    script_name = 'mcflirt_%s.sh'%config.dataset
    scripts =open (script_name,'w')
    bold=glob.glob(os.path.join(config.basedir,config.dataset,'sub*/BOLD/*/bold.nii.gz'))

    if len(bold)==0:
        print 'no bold images found!'
        config.printHelp()
        return
    #write command to script file    
    for i in bold:
        scripts.write('mcflirt -in %s -sinc_final -plots\n'%i)
    scripts.close()
    
    full_path = os.path.dirname(os.path.realpath(__file__))
    if config.qsub:
        qsub_name = 'mcflirt_%s_qsub.sh'%config.dataset
        qsub_file = open(qsub_name,'w')
        commands = open(script_name,'r')
        i=0
        for command in commands:
            sub_name = 'mcflirt_%s_qsub_%s.sh'%(config.dataset,i)
            sub_file = open(sub_name,'w')
            sub_file.write('#!/bin/bash\n')
            sub_file.write('#$ -l rmem=8G\n')
            sub_file.write('singularity exec /home/acp16sz/fsl.img %s'%command)
            sub_file.close()
            qsub_file.write('qsub %s\n'%sub_name)
            i+=1
        qsub_file.close()
        print 'run "bash %s/%s" to submit job to HPC'%(full_path,qsub_name)
    else:
        print 'now run: bash %s/%s'%(full_path,script_name)
    
if __name__ == '__main__':
    main()
