
"""
Created on Mon Aug 14 19:43:16 2017

@author: Shuo Zhou, University of Sheffield

USAGE: python <PROGRAM> options
ACTION: make mask for the run 1 and run 2 data
OPTIONS: 
    -m: path of fsl standard mask
        default path is '/usr/share/fsl/data/standard/MNI152_T1_2mm_brain_mask.nii.gz'
    -o: output directory
        default path is current working directory
    -h: print help
    
Ref: Poldrack, R. A., Barch, D. M., Mitchell, J., Wager, T., Wagner, A. D., Devlin, J.T., 
    Cumba, C., Koyejo, O., and Milham, M. Toward open sharing of task-based fmri data: 
    the openfmri project. Frontiers in neuroinformatics 7 (2013), 12.
"""

import nibabel as nib
import os
import numpy as np
import sys, getopt


#outdir='/home/sz144/openfMRI_data/basedir/data_prep'



class commandline:
    def __init__(self):
        opts,args = getopt.getopt(sys.argv[1:],'m:o:h')
        opts = dict(opts)        
        # default mask path
        self.mask = '/usr/share/fsl/data/standard/MNI152_T1_2mm_brain_mask.nii.gz'    
        self.outdir = os.getcwd()
        
        if '-h' in opts:
            self.printHelp()
        
        if '-m' in opts:
            self.mask = opts['-m']
        
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
    mask = config.mask
    outdir = config.outdir
    m=nib.load(mask)
    maskdata=m.get_data()
    maskvox=np.where(maskdata>0)
    
    badsubthresh=3
    for run in [1,2]:
        print('processing run %s'%run)
        goodvox=np.zeros(maskdata.shape)
        missing_count=np.zeros(maskdata.shape)
        if 1:
            i=nib.load(os.path.join(outdir,'zstat_run%d.nii.gz'%run))
            d=i.get_data()
        for v in range(len(maskvox[0])):
            x=maskvox[0][v]
            y=maskvox[1][v]
            z=maskvox[2][v]
            if not np.sum(d[x,y,z,:]==0.0)>badsubthresh:
                goodvox[x,y,z]=1
            missing_count[x,y,z]= np.sum(d[x,y,z,:]==0.0)
        #newimg=nib.Nifti1Image(goodvox,m.get_affine())
        #newimg.to_filename(os.path.join(outdir,'zstat_run%d_goodvoxmask.nii.gz'%run))
        #newimg=nib.Nifti1Image(missing_count,m.get_affine())
        #newimg.to_filename(os.path.join(outdir,'zstat_run%d_missingcount.nii.gz'%run))
        
    print('Creating mask image...')
    new_mask=nib.Nifti1Image(goodvox,m.get_affine())
    new_mask.to_filename(os.path.join(outdir,'goodvoxmask.nii.gz')) 
    print('Done!')
    
    
if __name__ == '__main__':
    main()
