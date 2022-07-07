import argparse
import subprocess as sp
from datetime import datetime as dt
from os.path import join
import tarfile

# TODO - expect one argument, the subject ID and fix
args=argparse.ArgumentParser(description='This function helps with the reprocessing with recon-all.')
args.add_argument('sub', help='The subject ID', required=True)
args.add_argument('fix', help='The fix to run; either cp, wm or gm', required=True, choices=['cp', 'wm', 'gm'])
args.add_argument('-sd', '--subjectsDir', help='The directory where the subjects are stored. Remote drive is ok.', metavar='[path]',\
    default='/mnt/clab/COST_mri/derivatives/freesurfer', required=False)
args.add_argument('-td', '--tmpdir', help='The directory where the temporary files are stored on the local machine', metavar='[path]',\
    default='tmp/', required=False)')
args.add_argument('-bd', '--backupDir', help='The directory where the backup files are stored. Remote drive is ok.', metavar='[path]',\
    default='/mnt/clab/COST_mri/derivatives/qa/fs', required=False)
args.add_argument('-t', '--telegram', help='Send telegram messages', required=False, default=True, action='store_true')

for s in args.sub:
    if not s.startswith('sub-'):
        args.sub[args.sub.index(s)] = 'sub'

if not exists('telegram.py'):
    print('Telegram module not found, messages will not be sent.')
    args.telegram = False

# cp to local
try:
    print(f'Compressing and moving {args.sub} data to {zfile}')
    sp.run(f'cp -RL {join(args.subjectsDir, args.sub)} {args.tempDir}', shell=True)
    # backup the subject data on nasips
    d2zip = join(tmp, args.sub)
    zfile = join(bckdir, f'{args.sub}_{dt.now().strftime("%Y%m%d%H%M%S")}_{args.fix}.tar.gz')
    tar = tarfile.open(zfile, mode="w:gz")
    tar.add(d2zip)
    tar.close()
except Exception as e:
    if args.telegram:
        sp.run(f'python telegram.py -m "Error recon-all for {args.sub} {args.fix}: could not copy or compress files for \
            backup: {e}"', shell=True)
    print(e)
    print('Something went wrong with the copy to local or tar compression.')
    exit(1)

if args.telegram:
    sp.run(f'python telegram.py -m "Done recon-all for {args.sub} {args.fix}"', shell=True)

# run recon-all
try:
    if args.fix == 'cp':
        sp.run(f'recon-all -subjid {args.sub} -sd {args.tmpDir} -autorecon2-cp -autorecon3', shell=True)
    elif args.fix == 'wm':
        sp.run(f'recon-all -subjid {args.sub} -sd {args.tmpDir} -autorecon2-wm -autorecon3', shell=True)
    elif args.fix == 'gm':
        sp.run(f'recon-all -subjid {args.sub} -sd {args.tmpDir} -autorecon-pial', shell=True)
except Exception as e:
    if args.telegram:
        sp.run(f'python telegram.py -m "Error recon-all for {args.sub} {args.fix}: recon all failed: {e}"', shell=True)
    print(e)
    print('Something went wrong with the recon-all command.')
    exit(1)
    
# rm old on nasips
sp.run(f'rm -rf {join(args.subjectsDir, args.sub)}', shell=True)
# cp to nasips
sp.run(f'cp -RL {join(args.tmpDir, args.sub)} {args.subjectsDir}', shell=True)
# rm local
sp.join(f'rm -rf {join(args.tmpDir, args.sub)}', shell=True)

# send telegram message
if args.telegram:
    sp.run(f'python telegram.py -m "Done recon-all for {args.sub} {args.fix}"', shell=True)