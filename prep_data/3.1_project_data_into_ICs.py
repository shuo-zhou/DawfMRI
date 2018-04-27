""" 
Created on Mon Aug 14 19:43:16 2017

@author: Shuo Zhou, University of Sheffield

USAGE: python <PROGRAM> options
ACTION: Create scripts for projecting image data into ICs
OPTIONS: 
    -m: path of fsl standard mask file
        default path is '/usr/share/fsl/data/standard/MNI152_T1_2mm_brain_mask.nii.gz'
    -d: path of data directory
    -o: output directory for ICs
    -h: print help
    
Ref: Poldrack, R. A., Barch, D. M., Mitchell, J., Wager, T., Wagner, A. D., Devlin, J.T., 
    Cumba, C., Koyejo, O., and Milham, M. Toward open sharing of task-based fmri data: 
    the openfmri project. Frontiers in neuroinformatics 7 (2013), 12.
"""


import os, sys
import getopt


class commandline:
    def __init__(self):
        opts,args = getopt.getopt(sys.argv[1:],'m:d:o:h')
        opts = dict(opts)
        # default mask and standard image
        self.mask = '/usr/share/fsl/data/standard/MNI152_T1_2mm_brain_mask.nii.gz'
        
        if '-h' in opts:
            self.printHelp()

        
        if '-m' in opts:
            self.mask = opts['-m']

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
    mask = config.mask
    datadir = config.basedir
    ncomps=[2,10,20,50,100]#,200]
    #datadir=os.path.join(BASEDIR,'data_prep/')
    #icadir='/home/sz144/openfMRI_data/ICA'
    icadir = config.outdir
    full_path = os.path.dirname(os.path.realpath(__file__))
    f=open('project_data_across_runs.sh','w')
    
    for icarun in range(1,3):
      for datarun in range(1,3):
        for c in ncomps:
            cmd = 'fsl_glm -i %szstat_run%d_add10000.nii.gz -d %sica_run%d_%dcomp/melodic_IC.nii.gz -o %sdatarun%d_icarun%d_%dcomp.txt --demean -m %s'%(datadir,datarun,icadir,icarun,c,icadir,datarun,icarun,c,mask)
            f.write(cmd+'\n')
    f.close()
    
    print 'Now run: "bash %s/project_data_across_runs.sh" in command line to project image data into ICs'%full_path
    
if __name__ == '__main__':
    main()  
