#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 19 16:22:15 2018

@author: Shuo Zhou, the University of sheffield

USAGE: python <PROGRAM> options
ACTION: read options from cmd input
OPTIONS:
    -w: specify the directory for whole brain data
    -i: specify the directory for ICA data ('d' for using default path)
    -l: specify the directory for labels
    -t: specify the task id for target domain (e.g. 3vs6)
    -k: specify the number of k for k-fold cv
    -d: specify the dimension of ica data
    -h: print help
"""

import sys,os
import getopt
import load_data

class commandline:
    def __init__(self):
        opts,args = getopt.getopt(sys.argv[1:],'w:i:l:k:t:s:d:h')
        opts = dict(opts)        
        # default do not submit jod to HPC
        self.kfold = 5
        self.target = [3,6]
        self.source = [22,9]
        self.wb_dir = load_data.WHOLE_BRAIN_PATH
        self.ica_dir = load_data.ICA_PATH
        self.label_dir = load_data.LABEL_PATH
        self.clf_ica = False
        self.dim = 100
        
        if '-h' in opts:
            self.printHelp()

        if '-w' in opts:
            self.wb_dir = opts['-w']
            if self.wb_dir[-1]!='/':
                self.wb_dir+='/';
            if not os.path.exists(self.wd_ir):
                print ('directory for whole brain data %s does not exist!'
                       %self.wb_dir)
                self.printHelp()

            
        if '-i' in opts:
            self.clf_ica = True
            if opts['-i']!='d':
                self.ica_dir = opts['-i']
                if self.ica_dir[-1]!='/':
                    self.ica_dir+='/';
                if not os.path.exists(self.ica_dir):
                    print ('directory for ica brain %s does not exist!'
                           %self.ica_dir)
                    self.printHelp()
                
        if '-l' in opts:
            self.label_dir = opts['-l']
            if self.label_dir[-1]!='/':
                self.label_dir+='/';
            if not os.path.exists(self.label_dir):
                print ('directory for labels %s does not exist!'
                       %self.label_dir)
                self.printHelp()
                
        if '-t' in opts:
            self.target = opts['-t'].split("vs")
            self.target[0] = int(self.target[0])
            self.target[1] = int(self.target[1])
        
        if '-s' in opts:
            self.source = opts['-s'].split("vs")
            self.source[0] = int(self.source[0])
            self.source[1] = int(self.source[1])
        
        if '-k' in opts:
            self.kfold = int(opts['-k'])
            
        if '-d' in opts:
            self.dim = int(opts['-d'])

            
    def printHelp(self):
        helpinfo = __doc__.replace('<PROGRAM>',sys.argv[0],1)
        print (helpinfo)
        print (sys.stderr)
        sys.exit()