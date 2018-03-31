#!/usr/bin/env python
""" 

@author: Shuo Zhou, University of Sheffield

USAGE: python <PROGRAM> options
ACTION: generate fsf files for all subjects in a dataset
OPTIONS:
    -d: dataset number e.g. ds001
    -b: base directory of the dataset
    -h: print help
"""



import os
from mk_level1_fsf import *
import sys,getopt


class commandline:
    def __init__(self):
        opts,args = getopt.getopt(sys.argv[1:],'d:b:s:m:n:t:u:qh')
        opts = dict(opts)        
        
        # default 
        self.qsub = False
        self.task_num = 0
        self.smoothing = 0
        self.nonlinear = 1
        self.model_num = 1
        self.use_inplane=1
        
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
            
        if '-m' in opts:
            self.model_num = int(opts['-m'])
            
        if '-s' in opts:
            self.smoothing=int(opts['-s'])
            
        if '-t' in opts:
            self.task_num = int(opts['-t'])
            
        if '-n' in opts:
            self.nonlinear = int(opts['-n'])
            if self.nonlinear == 0:
                print 'using linear registration'
        
        if '-u' in opts:
            self.use_inplane = int(opts['-u'])
            
        if '-q' in opts:
            self.qsub = True


    def printHelp(self):
        helpinfo = __doc__.replace('<PROGRAM>',sys.argv[0],1)
        print helpinfo
        print sys.stderr
        sys.exit()

def usage():
    """Print the docstring and exit with error."""
    sys.stdout.write(__doc__)
    sys.exit(2)

def main():
    config = commandline()
    basedir = config.basedir
    dataset = config.dataset
    model_num = config.model_num
    nonlinear = config.nonlinear
    use_inplane = config.use_inplane
    smoothing = config.smoothing
    full_path = os.path.dirname(os.path.realpath(__file__))
    #outfile=open('mk_all_level1_%s.sh'%dataset,'w')
    if config.qsub:
        qsub_name = 'feat_level1_%s_qsub.sh'%dataset
        qsub_file = open(qsub_name,'w')
        fsl_container = '/home/acp16sz/fsl.img'
    else:
        script_name = 'feat_level1_%s.sh'%dataset
        script_file = open(script_name,'w')



    for subject in os.listdir(basedir+dataset):
        if subject[0:3]=='sub':
            for bold in os.listdir('%s/%s/BOLD/'%(basedir+dataset,subject)):
                for image in os.listdir('%s/%s/BOLD/%s/'%(basedir+dataset,subject,bold)):
                    # TBD: add checking to handle case with no viable data
                    if image=='bold_mcf_brain.nii.gz':
                        path='%s/%s/BOLD/%s/'%(basedir+dataset,subject,bold)
                        path_split=path.split('/')
                        scankey = basedir + dataset+'/scan_key.txt'
                        ds_id = dataset
                        for i in path_split:
                            if i[0:3]=='sub':
                                sub_num=int(i.lstrip('sub'))
                            if i[0:4]=='task':
                                task_run = i.split('_')
                                task_num = int(task_run[0].lstrip('task'))
                                if config.task_num != 0 and task_num != config.task_num:
                                    continue
                                run_num = int(task_run[1].lstrip('run'))
                        tr=float(load_scankey(scankey)['TR'])
                        inplane= basedir + dataset + '/anatomy/inplane001_brain.nii.gz'
                        if os.path.exists(inplane):
                            use_inplane=1
                        else:
                            use_inplane=0
                        feat_name=mk_level1_fsf(ds_id,sub_num,task_num,run_num,smoothing,use_inplane,basedir,nonlinear,model_num)
                        if config.qsub:
                            sub_job_name = 'feat_level1_%s_sub00%s_task00%s_run00%s.sh'%(ds_id,sub_num,task_num,run_num)
                            sub_job_file = open(sub_job_name,'w')
                            sub_job_file.write('#!/bin/bash\n')
                            sub_job_file.write('#$ -l rmem=8G\n')
                            sub_job_file.write('singularity exec %s feat %s\n'%(fsl_container,feat_name))
                            sub_job_file.close()
                            qsub_file.write('qsub %s\n'%sub_job_name)
                        else:
                            script_file.write('feat %s\n'%feat_name)
    
    if config.qsub:
        qsub_file.close()
        print 'run "bash %s/%s" to submit job to HPC'%(full_path,qsub_name)
    else:
        script_file.close()
        print 'now run: "bash %s/%s"'%(full_path,script_name)
        
                    #print 'f_split:',f_split
                    #scankey='/'+'/'.join(f_split[1:5])+'/scan_key.txt'
                    #print 'scankey:',scankey
                    #taskid=f_split[4]
                    #print 'taskid:',taskid
                    #subnum=int(f_split[5].lstrip('sub'))
                    #taskinfo=f_split[7].split('_')
                    #print 'taskinfo:',taskinfo
                    #tasknum=int(taskinfo[0].lstrip('task'))
                    #if (tasknum_spec>0) and not (tasknum==tasknum_spec):
                        #continue
                    #runnum=int(taskinfo[1].lstrip('run'))
                        
                    # check for inplane
                    #inplane='/'+'/'.join(f_split[1:6])+'/anatomy/inplane001_brain.nii.gz'
                    #print inplane
                    
                    #print 'mk_level1_fsf("%s",%d,%d,%d,%d,%d,"%s",%d)'%(taskid,subnum,tasknum,runnum,smoothing,use_inplane,basedir,modelnum)
                    #fname=mk_level1_fsf(taskid,subnum,tasknum,runnum,smoothing,use_inplane,basedir,nonlinear,modelnum)
                    #outfile.write('feat %s\n'%fname)
    #outfile.close()
    
    #print 'now launching all feats:'
    #print "find %s/sub*/model/*.fsf |sed 's/^/feat /' > run_all_feats.sh; sh run_all_feats.sh"%taskid
    #f=open('mk_all_level1_%s.sh'%dataset)
    #l=f.readlines()
    #f.close()
    #njobs=len(l)
    #ncores=(njobs/2)*12
    #launch_qsub.launch_qsub(script_name='mk_all_level1_%s.sh'%dataset,runtime='04:00:00',jobname='%sl1'%dataset,email=False,parenv='2way',ncores=ncores)


if __name__ == '__main__':
    main()
