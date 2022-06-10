#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import subprocess as sp
import argparse
from os.path import exists, join
from shutil import which

args=argparse.ArgumentParser(description='This function helps with the reprocessing with recon-all.')
args.add_argument('subjectsDir', help='The directory where the subjects are stored. Remote drive is ok.', metavar='[path]')
args.add_argument('tmpDir', help='The directory where the temporary files will be processed.', metavar='[path]')
args.add_argument('-s', '--subjects', help='Subject ID', required=True, nargs='+')
args.add_argument('-p', '--arpial', help='Pial surface fix, FreeSurfer\'s -autorecon-pial flag', required=False, default=False, action='store_true')
args.add_argument('-w', '--ar2cp', help='White surface fix, FreeSurfer\'s -autorecon2-cp flag', required=False, default=False, action='store_true')
args.add_argument('-a', '--ar3', help='Autorecon3, FreeSurfer\'s -autorecon3 flag', required=False, default=False, action='store_true')
args.add_argument('-t', '--telegram', help='Send telegram messages', required=False, default=False, action='store_true')
args.add_argument('-noclean', help='Do not clean up the temporary directory', required=False, default=False, action='store_true')
args.add_argument('-nocopyin', help='Do not copy the output to the subjects directory', required=False, default=False, action='store_true')
args.add_argument('-nocopyout', help='Do not copy the output to the subjects directory', required=False, default=False, action='store_true')
args.add_argument('-parallel', help='Use parallel processing, specify number of threads', required=False, default=None, metavar='[threads]')
args.add_argument('-debug', help='Debug mode, passes onto the freesurfer', required=False, default=False, action='store_true')
args.add_argument('-no3T', help='Do not add the 3T flag to recon-all', required=False, default=False, action='store_true')
args.add_argument('-noqcache', help='Do not add the -qcache flag to recon-all', required=False, default=False, action='store_true')
args.add_argument('-c', '--container', help='Container path (Freesurfer, Singularity) if no path is set the script will \
    assume local installation of Freesurfer.', required=False, default=None, metavar='[path]')
args.add_argument('-m', '--mail', help='Send mail to this address when done', required=False, default=False, metavar='[email]')
args = args.parse_args()

# Stop if you want to run both; singularity and parallel, unless I am mistaken this will fail TODO
if args.parallel and args.container:
    print('Parallel processing is not supported with containers.')
    exit(1)

# Check if we have local FS
if not args.container:
    if not which('recon-all'):
        print('recon-all not found, please check your local installation of Freesurfer.')
        exit(1)
else:
    if not which('singularity'):
        print('singularity not found, please check your local installation of Singularity.')
        exit(1)
    else:
        if not exists(args.container):
            print('Container not found, please check the path.')
            exit(1)
        else:
            # TODO Test and adjust this --> if returns None, as in recon-all not found --> exit, else silent
            sp.run(f'singularity exec {args.container} which recon-all', shell=True, \
                stdout=sp.PIPE, stderr=sp.PIPE, text=True)
            print(result.stdout)
            print(result.stderr)


if args.parallel:
    if which('parallel') is None:
        print('GNU parallel is not installed. Please install it or run subjects in sequence.')
        exit(1)
    else:
        print(f'GNU parallel is installed in {which("parallel")} Proceeding.')
        # thanks to https://andysbrainbook.readthedocs.io/en/latest/FreeSurfer/FS_ShortCourse/FS_04_ReconAllParallel.html
        # TODO Not tested yet!
        cmd = f'parallel --jobs {args.parallel} '

# Check for telegram module, if not found, do not send messages
if args.telegram:
    if not exists('telegram.py'):
        print('Telegram module not found, messages will not be sent.')
        args.telegram = False

# add sub prefix to the subjects, if required
for s in args.subjects:
    if not s.startswith('sub-'):
        args.subjects[args.subjects.index(s)] = 'sub-' + s

# If args.container is not None, then we are running in a container.
# In this case, we need to mount the paths TODO

# Set tmpDir as SUBJECTS_DIR
cmd = f'recon-all -sd {args.tmpDir} '

# Copy all the subjects to the tmpDir, but only if all are needed at once, that is in parallel mode
if args.parallel is not None:
    for s in args.subjects:
        sp.run(f'cp -r {join(args.subjectsDir, s)} {join(args.tmpDir, s)}', shell=True)

# Build the command, WM
if args.ar2cp:
    cmd += '-autorecon2-cp '

# build the command, pial
if args.arpial:
    cmd += '-autorecon-pial '

# build the command, autorecon3
if args.ar3:
    cmd += '-autorecon3 '

# build the command, add 3T flag
if not args.no3T:
    cmd += '-3T '

# build the command, add qcache flag
if not args.noqcache:
    cmd += '-qcache '

# debug mode
if args.debug:
    cmd += '-debug '

# mail
if args.mail:
    cmd += f'-m {args.mail} '

#### EXECUTE THE COMMAND ####
if len(args.subjects) > 1:
    # Run multiple subjects, can be parallel or sequential

    # do a loop if we have more than one subject
    if not args.parallel:

        if args.telegram:       
            sp.run(f'python telegram.py -m "Running recon-all on {args.subjects} in sequence."', shell=True)
        
        for i, s in enumerate(args.subjects):
            # add single sub to the command

            # send mail if last subject
            if i == len(args.subjects) - 1:
                cmd += f'-m {args.mail} '

            # copy required files to the tmpDir
            if not args.nocopyin:
                sp.run(f'cp -r {join(args.subjectsDir, s)} {join(args.tmpDir, s)}', shell=True)
            
            # run the command
            sp.run(f'', shell=True, stdout=sp.PIPE, stderr=sp.PIPE, text=True)
            print(result.stdout)
            print(result.stderr)
            
            # copy the output to the subjectsDir
            if not args.nocopyout:
                sp.run(f'cp -r {join(args.tmpDir, s)} {join(args.subjectsDir, s)}', shell=True)
            
            # clean up the tmpDir
            if not args.noclean:
                sp.run(f'rm -rf {join(args.tmpDir, s)}', shell=True)

    else:
        # TODO RUN as parallel:
        if args.telegram:       
            sp.run(f'python telegram.py -m "Running recon-all on {args.subjects} in parallel on {args.parallel} threads."', shell=True)
        
        # TODO
        # run the command
        # sp.run(f'{cmd} {args.subjects}', shell=True, stdout=sp.PIPE, stderr=sp.PIPE, text=True)
else:
    # do a single subject
    if args.telegram:       
        sp.run(f'python telegram.py -m "Running recon-all on {args.subjects[0]}"', shell=True)

    cmd += f'-s {args.subjects[0]} '
    
    # RUN THE COOKED COMMAND
    sp.run(cmd, shell=True)
    
    if not args.nocopyout:
        sp.run(f'cp -r {join(args.tmpDir, args.subjects[0])} {join(args.subjectsDir, args.subjects[0])}', shell=True)
    if not args.noclean:
        sp.run(f'rm -rf {join(args.tmpDir, args.subjects[0])}', shell=True)
    
    

# send telegram when done
if args.telegram:
    # FIXME - the below is cool, but the telegram script is not adjusted yet
    sp.run(f'python telegram.py -m "Finished recon-all on {args.subjects}"', shell=True)
