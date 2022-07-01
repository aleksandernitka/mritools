#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import subprocess as sp
import argparse
from os.path import exists, join
from shutil import which

args=argparse.ArgumentParser(description='This function helps with the reprocessing with recon-all.')

args.add_argument('subjectsDir', help='The directory where the subjects are stored. Remote drive is ok.', metavar='[path]')
args.add_argument('-s', '--subjects', help='Subject ID', required=True, nargs='+')
args.add_argument('-p', '--parallel', help='Use parallel processing, specify number of threads', required=False, default=None, metavar='[threads]')
args.add_argument('-t', '--telegram', help='Send telegram messages', required=False, default=False, action='store_true')

args.add_argument('-np', '--noarpial', help='Do not run: pial surface fix, FreeSurfer\'s -autorecon-pial flag', required=False, default=False, action='store_true')
args.add_argument('-nw', '--noar2cp', help='Do not run: white surface fix, FreeSurfer\'s -autorecon2-cp flag', required=False, default=False, action='store_true')
args.add_argument('-na', '--noar3', help='Do not run: autorecon3, FreeSurfer\'s -autorecon3 flag', required=False, default=False, action='store_true')
args.add_argument('-debug', help='Debug mode, passes onto the freesurfer', required=False, default=False, action='store_true')
args.add_argument('-tmux', '--tmux', help='Use tmux split for every job (gnu parallel option)', required=False, default=False, action='store_true')
args = args.parse_args()

### Checks before the run
if not which('recon-all'):
    print('recon-all not found, please check your local installation of Freesurfer.')
    exit(1)

# add sub prefix to the subjects, if required
for s in args.subjects:
    if not s.startswith('sub-'):
        args.subjects[args.subjects.index(s)] = 'sub-' + s

# check if number of threads is specified
if args.parallel:
    if not args.parallel.isdigit():
        print('Parallel threads must be a number.')
        exit(1)

# for parallel processing, write all subjects to a file, then pipe with cat
if args.parallel:
    with open('subjects.txt', 'w') as f:
        for s in args.subjects:
            f.write(s + '\n')

# Check for telegram module, if not found, do not send messages
if args.telegram:
    if not exists('telegram.py'):
        print('Telegram module not found, messages will not be sent.')
        args.telegram = False

### Format the command
cmd1 = f'recon-all -sd {args.subjectsDir} -s'

cmd2 = ''
# Build the command, WM
if not args.noar2cp:
    cmd2 += '-autorecon2-cp '

# build the command, pial
if not args.noarpial:
    cmd2 += '-autorecon-pial '

# build the command, autorecon3
if not args.noar3:
    cmd2 += '-autorecon3 '

# Add other flags
cmd2 += '-3T -qcache '

# debug mode
if args.debug:
    cmd2 += '-debug '

### Run the command
if args.parallel:
    ### ----> PARALLEL
    if which('parallel') is None:
        print('GNU parallel is not installed. Please install it or run subjects in sequence.')
        exit(1)
    else:
        print(f'GNU parallel is installed in {which("parallel")} Proceeding.')
        # thanks to https://andysbrainbook.readthedocs.io/en/latest/FreeSurfer/FS_ShortCourse/FS_04_ReconAllParallel.html
        # ls *.nii | parallel --jobs 8 recon-all -s {.} -i {} -all -qcache
        cmd = f'cat subjects.txt | parallel --jobs {args.parallel} --progress ' 
        if args.tmux:
            cmd += '--tmux '
        cmd += f'{cmd1} {{}} {cmd2}'
        print(f'Running: {cmd}')
        sp.run(cmd, shell=True)

else:
    ### ----> SEQUENTIAL
    if args.telegram:       
        sp.run(f'python telegram.py -m "Running recon-all on {args.subjects}"', shell=True)

    for i, s in enumerate(args.subjects):
        # run the command
        cmd = f'{cmd1} {s} {cmd2}' 
        print(f'Running {i+1} from {len(args.subjects)} {s}')
        sp.run(cmd, shell=True)

# send telegram when done
if args.telegram:
    sp.run(f'python telegram.py -m "Finished recon-all on {args.subjects}"', shell=True)
