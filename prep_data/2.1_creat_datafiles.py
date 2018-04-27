
"""
Created on Mon Aug 14 14:53:10 2017

@author: Shuo Zhou, University of Sheffield

USAGE: python <PROGRAM> options
ACTION: package the zstat of selected contrast to across datasets to a single file
OPTIONS:
    -b: base directory of the dataset
    -o: output directory 
    -h: print help
    
Ref: Poldrack, R. A., Barch, D. M., Mitchell, J., Wager, T., Wagner, A. D., Devlin, J.T., 
    Cumba, C., Koyejo, O., and Milham, M. Toward open sharing of task-based fmri data: 
    the openfmri project. Frontiers in neuroinformatics 7 (2013), 12.
"""

import os
import sys,getopt
import numpy as np
import nibabel as nib
from get_contrasts_to_use import get_contrasts_to_use
#https://github.com/poldrack/openfmri/blob/master/openfmri_paper/get_contrasts_to_use.py


class commandline:
    def __init__(self):
        opts,args = getopt.getopt(sys.argv[1:],'b:o:h')
        opts = dict(opts)        
        # default do not submit jod to HPC
        self.basedir = os.getcwd()
        self.outdir = os.getcwd()
        
        if '-h' in opts:
            self.printHelp()

        if '-b' in opts:
            self.basedir = opts['-b']
            if self.basedir[-1]!='/':
                self.basedir+='/';
            if not os.path.exists(self.basedir):
                print 'basedir %s does not exist!'%self.basedir
                self.printHelp()

        if '-o' in opts:
            self.outdir = opts['-o']
            if self.outdir[-1]!='/':
                self.outdir+='/';
            if not os.path.exists(self.outdir):
                print 'output directory %s does not exist!'%self.outdir
                self.printHelp()

    def printHelp(self):
        helpinfo = __doc__.replace('<PROGRAM>',sys.argv[0],1)
        print helpinfo
        print sys.stderr
        sys.exit()


def main():
    config = commandline()
    basedir = config.basedir
    zstatdir=os.path.join(basedir,'zstats')
    outdir=config.outdir
    
    
    contrasts_to_use=get_contrasts_to_use()
    
    zstats=os.listdir(zstatdir)
    #data_file=os.listdir(basedir)
    
    zstat_input = {}
    for z in zstats:
        #print z
        if z[-6:]=='nii.gz':
            z_split=z.split('_')
            ds = z_split[0]
            sub = z_split[1]
            task = z_split[2]
            run = z_split[3]
            zstat = z_split[4]
            if ds not in zstat_input: 
                zstat_input[ds] = {}
            if sub not in zstat_input[ds]:
                zstat_input[ds][sub] = {}
            if task not in zstat_input[ds][sub]:
                zstat_input[ds][sub][task] = {}
            if run not in zstat_input[ds][sub][task]:
                zstat_input[ds][sub][task][run] = {}
            if zstat not in zstat_input[ds][sub][task][run]:
                zstat_input[ds][sub][task][run] = zstat
                    
    subnums={}
    #for ds in contrasts_to_use.iterkeys():
    for ds in zstat_input:
        print ds
        subnums[ds] = zstat_input[ds]
        #subnums[ds]=[int(file_subctr[i]) for i,x in enumerate(file_ds) if x.find(ds)>-1 and file_task[i].find('task001')>-1 and file_run[i].find('run001')>-1 and file_zstat[i].find('zstat001')>-1]
    
    
    taskctr={'ds001': {1: 1},
     'ds002': {1: 2, 2: 3, 3: 4},
     'ds003': {1: 5},
     'ds005': {1: 6},
     'ds006A': {1: 7},
     'ds007': {1: 8, 2: 9, 3: 10},
     'ds008': {1: 11, 2: 12},
     'ds011': {1: 13, 2: 14, 3: 15, 4: 16},
     'ds017A': {2: 17},
     'ds051': {1: 18},
     'ds052': {1: 19, 2: 20},
     'ds101': {1: 21},
     'ds102': {1: 22},
     'ds107': {1: 23},
     'ds108': {1: 24},
     'ds109': {1: 25},
     'ds110': {1: 26}}
    
    zstat_files={1:[],2:[]}  # index across runs
    
    taskinfo={}

    #for ds in contrasts_to_use.iterkeys():
    for ds in zstat_input:
        taskinfo[ds]={}
        print contrasts_to_use[ds]
        for t in contrasts_to_use[ds].iterkeys():
            print 't:',t
            for s in subnums[ds]:
                print 's:',s
                for cope in contrasts_to_use[ds][t]:
                    print 'cope:',cope
                    for run in [1,2]:
                        cf='%s_%s_task%03d_run%03d_zstat%d.nii.gz'%(ds,s,t,run,cope)
                        #cf='%s_subctr%03d_task%03d_run%03d_zstat%03d.nii.gz'%(ds,s,t,run,cope)
                        if os.path.exists(os.path.join(zstatdir,cf)):
                            zstat_files[run].append(cf)
                    #print copefiles[-1]
                        else:
                            print 'problem with %s'%cf
            
    
    for run in [1,2]:
        #print run
        npts=len(zstat_files[run])
        ctr=0
        infofile=open(os.path.join(outdir,'data_key_run%d.txt'%run),'w')
        #print infofile
        alldata=np.zeros((91,109,91,npts))
        for z in zstat_files[run]:
            print 'processing %s'%z
            i=nib.load(os.path.join(zstatdir,z))
            #print os.path.join(zstatdir,z)
            ds,subctr,task,runctr,zstatctr=z.replace('.nii.gz','').split('_')
            alldata[:,:,:,ctr]=i.get_data()        
            #print i.get_data()
            infofile.write('%d\t%d\t%d\t%d\t%d\t%d\n'%(taskctr[ds][int(task.replace('task',''))],int(subctr.replace('sub','')),int(ds.replace('ds','').replace('A','')),int(task.replace('task','')),int(runctr.replace('run','')),int(zstatctr.replace('zstat',''))))
            ctr=ctr+1
            d=nib.Nifti1Image(alldata,i.get_affine())
            d.to_filename(os.path.join(outdir,'zstat_run%d.nii.gz'%run))
    
        infofile.close()


if __name__ == '__main__':
    main()