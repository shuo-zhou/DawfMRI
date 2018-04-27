
"""
Created on Mon Aug 14 19:43:16 2017

@author: Shuo Zhou, University of Sheffield

USAGE: python <PROGRAM> options
ACTION: Create scripts for running ICA
OPTIONS: 
    -m: path of fsl standard mask file
        default path is '/usr/share/fsl/data/standard/MNI152_T1_2mm_brain_mask.nii.gz'
    -s: path of fsl standard image
        default path is '/usr/share/fsl/data/standard/MNI152_T1_2mm_brain.nii.gz'
    -d: path of data directory
    -o: output directory
    -h: print help
"""


import os, sys
import getopt


class commandline:
    def __init__(self):
        opts,args = getopt.getopt(sys.argv[1:],'m:s:d:o:h')
        opts = dict(opts)
        # default mask and standard image
        self.mask = '/usr/share/fsl/data/standard/MNI152_T1_2mm_brain_mask.nii.gz'
        self.standard_img = '/usr/share/fsl/data/standard/MNI152_T1_2mm_brain.nii.gz'
        
        if '-h' in opts:
            self.printHelp()

        
        if '-m' in opts:
            self.mask = opts['-m']
            
        if '-s' in opts:
            self.standard_img = opts['-s']
        
        if '-d' in opts:
            self.basedir = opts['-d']
            if self.basedir[-1]!='/':
                self.basedir+='/';
            if not os.path.exists(self.basedir):
                print 'basedir %s does not exist!'%self.basedir
                self.printHelp()
        else:
            print '***Error: basedir not given ***'
            self.printHelp()
        
        if '-o' in opts:
            self.outdir = opts['-o']
            if self.outdir[-1]!='/':
                self.outdir+='/';
            if not os.path.exists(self.outdir):
                print 'output directory %s does not exist!'%self.outdir
                self.printHelp()
        else:
            print '***Error: ouput directory not given ***'
            self.printHelp()

    def printHelp(self):
        helpinfo = __doc__.replace('<PROGRAM>',sys.argv[0],1)
        print helpinfo
        print sys.stderr
        sys.exit()


def main():
    config = commandline()
    datadir = config.basedir
    outdir = config.outdir
    mask = config.mask
    standard_img = config.standard_img
    full_path = os.path.dirname(os.path.realpath(__file__))
    #datadir='/home/sz144/openfMRI_data/basedir/data_prep'
    
    #outdir='/home/sz144/openfMRI_data/ICA'
    
    # melodic command:
    # melodic -i 9tasks_add1000.nii.gz -o ica_9tasks_120comp -v --report --Oall -d 120 --nobet -m /scratch/01329/poldrack/fsl-4.1.7/data/standard/MNI152_T1_2mm_brain_mask.nii.gz
    
    ncomps=[2,10,20,50,100]#,200]
    
    f=open('run_melodic_smoothed.sh','w')
    
    for run in [1,2]:
        for c in ncomps:
            #cmd='melodic -i %s/zstat_run%d_add10000_smoothed.nii.gz -o %s/ica_run%d_%dcomp -v --report --Oall -d %d --nobet -m /usr/share/fsl/data/standard/MNI152_T1_2mm_brain_mask.nii.gz --bgimage=/usr/share/fsl/data/standard/MNI152_T1_2mm_brain.nii.gz'%(datadir,run,outdir,run,c,c)
            cmd='melodic -i %s/zstat_run%d_add10000_smoothed.nii.gz -o %s/ica_run%d_%dcomp -v --report --Oall -d %d --nobet -m %s --bgimage=%s'%(datadir,run,outdir,run,c,c,mask,standard_img)            
            f.write(cmd+'\n')
    f.close()
    
    print 'Now run: "bash %s/run_melodic_smoothed.sh" in command line for running ICA'%full_path


if __name__ == '__main__':
    main()  