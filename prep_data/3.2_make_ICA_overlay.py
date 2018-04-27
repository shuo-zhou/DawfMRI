# -*- coding: utf-8 -*-
"""
Created on Wed Aug 16 14:09:41 2017

@author: Shuo Zhou, University of Sheffield

USAGE: python <PROGRAM> options
ACTION: Create scripts for making ICA overlay
OPTIONS: 
    -s: path of fsl standard image file
        default path is '/usr/share/fsl/data/standard/MNI152_T1_2mm_brain.nii.gz'
    -i: directory of ICA data
    -r: number of run
    -c: number of components
    -h: print help
    
Ref: Poldrack, R. A., Barch, D. M., Mitchell, J., Wager, T., Wagner, A. D., Devlin, J.T., 
    Cumba, C., Koyejo, O., and Milham, M. Toward open sharing of task-based fmri data: 
    the openfmri project. Frontiers in neuroinformatics 7 (2013), 12.
"""


import os, sys
import getopt


class commandline:
    def __init__(self):
        opts,args = getopt.getopt(sys.argv[1:],'s:i:r:c:h')
        opts = dict(opts)
        # default mask and standard image
        self.standard_img = '/usr/share/fsl/data/standard/MNI152_T1_2mm_brain.nii.gz'
        self.run = 1
        self.comp = 20
        
        if '-h' in opts:
            self.printHelp()
        
        if '-s' in opts:
            self.standard_img = opts['-s']
            
        if '-r' in opts:
            self.run = int(opts['-r'])
            
        if '-c' in opts:
            self.comp = int(opts['-c'])
       
        if '-i' in opts:
            self.outdir = opts['-i']
            if self.outdir[-1]!='/':
                self.outdir+='/';
            if not os.path.exists(self.outdir):
                print 'ICA directory %s does not exist!'%self.outdir
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
    run = config.run
    comp = config.comp
    #ncomps=[2,10,20,50,100]#,200]
    #datadir=os.path.join(BASEDIR,'data_prep/')
    #icadir='/home/sz144/openfMRI_data/ICA'
    icadir = os.path.join(config.outdir,'ica_run%s_%scomp/'%(run,comp))
    standard_img = config.standard_img
    full_path = os.path.dirname(os.path.realpath(__file__))
       
    outdir=os.path.join(config.outdir,'ICA_components_figure')
    print outdir
    #if not os.path.exists(outdir):
        #os.mkdir(outdir)
        
    script_name = 'make_ICA_overlays.sh'
    
    scripts=open(script_name,'w')
    for v in range(1,21):
        cmd='overlay 0 0 %s -a  %s/stats/thresh_zstat%d.nii.gz 2 6 %s/rend%04d'%(standard_img,icadir,v,outdir,v)
        scripts.write(cmd+'\n')
        cmd='slicer %s/rend%04d -S 5 100 %s/comp%04d.png'%(outdir,v,outdir,v)       
        scripts.write(cmd+'\n')
    
    cmd='pngappend '
    for v in range(1,21):
        cmd=cmd+' %s/comp%04d.png +'%(outdir,v)
    cmd=cmd.rstrip('+')
    cmd=cmd + ' %s/all_comps.png'%outdir
    
    scripts.write(cmd+'\n')
    
    scripts.close()
    
    print 'Now run: "bash %s/%s" in command line to make ICA overlay'%(full_path,script_name)
    
if __name__ == '__main__':
    main()  
