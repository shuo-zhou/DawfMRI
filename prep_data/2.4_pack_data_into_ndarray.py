
"""
Created on Mon Aug 14 19:43:16 2017

@author: Shuo Zhou, University of Sheffield

USAGE: python <PROGRAM> options
ACTION: save whole brain data in numpy format file
OPTIONS: 
    -d: path of data directory
    -h: print help
    
Ref: Poldrack, R. A., Barch, D. M., Mitchell, J., Wager, T., Wagner, A. D., Devlin, J.T., 
    Cumba, C., Koyejo, O., and Milham, M. Toward open sharing of task-based fmri data: 
    the openfmri project. Frontiers in neuroinformatics 7 (2013), 12.
"""


import numpy as np
import nibabel as nib
import os, sys
import getopt

class commandline:
    def __init__(self):
        opts,args = getopt.getopt(sys.argv[1:],'d:h')
        opts = dict(opts)        
        self.datadir = '/home/shuoz/data/openfmri/'
        
        if '-h' in opts:
            self.printHelp()
        
        if '-d' in opts:
            self.datadir = opts['-d']
            if self.datadir[-1]!='/':
                self.datadir+='/';
            if not os.path.exists(self.datadir):
                print 'data directory %s does not exist!'%self.datadir
                self.printHelp()
            
    def printHelp(self):
        helpinfo = __doc__.replace('<PROGRAM>',sys.argv[0],1)
        print helpinfo
        print sys.stderr
        sys.exit()
        
def main():
    config = commandline()
    datadir = config.datadir
    datafile={1:os.path.join(datadir,'zstat_run1.nii.gz'),
              2:os.path.join(datadir,'zstat_run2.nii.gz')}
   
    mask=os.path.join(datadir,'goodvoxmask.nii.gz')
#    mask_file={1:os.path.join(datadir,'zstat_run1_goodvoxmask.nii.gz'),
#               2:os.path.join(datadir,'zstat_run2_goodvoxmask.nii.gz')}
    
    maskimg=nib.load(mask)
    maskdata=maskimg.get_data()
    maskvox=np.where(maskdata)
    
    print('processing...')
    for run in [1,2]:
        #mask = mask_file[run]
        #maskimg=nib.load(mask)
        #maskdata=maskimg.get_data()
        #maskvox=N.where(maskdata)
        dataimg=nib.load(datafile[run])
    
        data=dataimg.get_data()[maskvox]
    
        np.save(os.path.join(datadir,'zstat_run%d.npy'%run),data)
        
    print('Done!')

if __name__ == '__main__':
    main()    
