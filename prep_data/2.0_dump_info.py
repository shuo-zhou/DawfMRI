#!/usr/bin/env python2

"""
Created on Mon Jul 26 11:32:10 2017

@author: Shuo Zhou, University of Sheffield

USAGE: python <PROGRAM> options
ACTION: dump the label infromation to a given directory
OPTIONS:
    -b: base directory of the dataset
    -i: output directory for dump info
    -h: print help
    
Ref: Poldrack, R. A., Barch, D. M., Mitchell, J., Wager, T., Wagner, A. D., Devlin, J.T., 
    Cumba, C., Koyejo, O., and Milham, M. Toward open sharing of task-based fmri data: 
    the openfmri project. Frontiers in neuroinformatics 7 (2013), 12.
"""

import os,glob
import sys,getopt
import pickle

from openfmri_utils import * 
#https://github.com/poldrack/openfmri/blob/master/nidm/openfmri_utils.py


class commandline:
    def __init__(self):
        opts,args = getopt.getopt(sys.argv[1:],'b:o:qh')
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

        if '-o' in opts:
            self.output_dir = opts['-o']
            if self.output_dir[-1]!='/':
                self.output_dir+='/';
            if not os.path.exists(self.output_dir):
                print 'output directory does not exist!'
                self.printHelp()
        else:
            print '***Error: output directory for dump info not given ***'
            self.printHelp()



    def printHelp(self):
        helpinfo = __doc__.replace('<PROGRAM>',sys.argv[0],1)
        print helpinfo
        print sys.stderr
        sys.exit()

def main():
    datasets=['ds001','ds002','ds003','ds005','ds006A','ds007','ds008','ds011','ds017A','ds051','ds052','ds101','ds102','ds107','ds108','ds109','ds110']
    config = commandline()
    #full_path = os.path.dirname(os.path.realpath(__file__))

    basedir = config.basedir
    output_dir = config.output_dir
    task_keys={}
    condition_keys={}
    contrasts={}
    ds_dump = []
    for ds in datasets:
        ds_path = basedir+ds+'/'
        if os.path.exists(ds_path):
            ds_dump.append(ds)
            task_keys[ds] = load_taskkey(os.path.join(ds_path,'task_key.txt'))
            condition_keys[ds]=load_condkey(os.path.join(ds_path,'models/model001/condition_key.txt'))
            contrasts[ds]={}
            for t in task_keys[ds].iterkeys():
                contrasts[ds][t]=load_fsl_design_con(os.path.join(ds_path,'sub001/model/model001/%s_run001.feat/design.con'%t))

    f=open(os.path.join(output_dir,'task_keys.pkl'),'wb')
    pickle.dump(task_keys,f)
    f.close()

    f=open(os.path.join(output_dir,'task_contrasts.pkl'),'wb')
    pickle.dump(contrasts,f)
    f.close()

    f=open(os.path.join(output_dir,'task_conditions.pkl'),'wb')
    pickle.dump(condition_keys,f)
    f.close()

    print 'Info of the following datasets have been dumped:'
    for ds in ds_dump:
        print ds


if __name__ == '__main__':
    main()
