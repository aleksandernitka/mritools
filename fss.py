#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
from os.path import join, exists
import subprocess as sb

parser = argparse.ArgumentParser(description = 'This is a script to help with plotting of freesurfer outputs, pass subject id and the it will take care of plotting for you. Optionally you can add an argument to show the 3d render of the brain as infalted. @author: aleksander nitka')

parser.add_argument('id', help = 'Subject id, must be specified as first argument')
parser.add_argument('-i', '--inflated', help = 'Show the inflated surface, no aseg, just pial surface', action = 'store_true', required = False, default = False)
parser.add_argument('-o', '--holes', help = 'Dedicated mode for showing holes in the surface; no aseg just WM in yellow and Pial in Blue', action = 'store_true', required = False, default = False)
parser.add_argument('-a', '--aparc', help = 'Load default with aparc aseg', action = 'store_true', required = False, default = False)
parser.add_argument('-r', '--ras', help = 'Go to given RAS coordinate x y z', required = False, nargs=3, metavar=('x', 'y', 'z'), type = float)
parser.add_argument('-c', '--compare', help = 'Loads WM and Pial surfaces for both uncorrected (backup) and corrected data', required=False, default=False, action='store_true')
parser.add_argument('-m', '--machine', help = 'Specify mechine, default is kraken, kpc will set the paths accordingly', required=False, default='kraken')
parser.add_argument('-l', '--linew', help = 'Specify line width for the Pial/WM plotting, default is 1', required=False, default=1)
args = parser.parse_args()

sub = args.id
if 'sub-' not in sub:
    sub = 'sub-' + sub

if args.machine == 'kpc':
    mnt = '/mnt/clab/'
elif args.machine == 'kraken':
    mnt = '/mnt/nasips/'
else:
    print(f'Error: {parser.machine} is not recognised, please use kraken or kpc')
    exit(1)

ssbck = join(mnt, 'aleksander', 'FreeSurfer_20220527', sub)
ssdir = join(mnt, 'COST_mri', 'derivatives', 'freesurfer', sub)
    
if exists(ssdir) == False:
    print(f'Error: {ssdir} does not exist!')
        
else:
    # Build the cmd
    st1 = join(ssdir, 'mri', 'brainmask.mgz')

    if args.aparc:
        a09 = join(ssdir, 'mri', 'aparc.a2009s+aseg.mgz')
        lhp = join(ssdir, 'surf', 'lh.pial')
        rhp = join(ssdir, 'surf', 'rh.pial')
        lhw = join(ssdir, 'surf', 'lh.white')
        rhw = join(ssdir, 'surf', 'rh.white')
        annots = 'aparc.a2009s.annot'
        
        cmd = f'freeview -v {st1} -v {a09}:colormap=LUT:opacity=0.3 \
                -f {lhp}:edgecolor=blue:annot={annots}:edgethickness={args.linew} \
                -f {rhp}:edgecolor=blue:annot={annots}:edgethickness={args.linew} \
                -f {lhw}:edgecolor=yellow:edgethickness={args.linew} \
                -f {rhw}:edgecolor=yellow:edgethickness={args.linew}'


    elif args.inflated:
        lhp = join(ssdir, 'surf', 'lh.inflated')
        rhp = join(ssdir, 'surf', 'rh.inflated')
        cmd = f'freeview -f {lhp}:overlay=lh.thickness:visible=1:overlay_threshold=0,5\
                -f {rhp}:overlay=rh.thickness:visible=1:overlay_threshold=0,5 -layout 1 -view lateral -viewport 3d'


    elif args.holes:

        lhp = join(ssdir, 'surf', 'lh.pial')
        rhp = join(ssdir, 'surf', 'rh.pial')
        lhw = join(ssdir, 'surf', 'lh.white')
        rhw = join(ssdir, 'surf', 'rh.white')
        
        cmd = f'freeview -v {st1}:visible=0 \
                -f {lhp}:edgecolor=blue:edgethickness={args.linew}:color=darkblue:curvature_method=off \
                -f {rhp}:edgecolor=blue:edgethickness={args.linew}:color=darkblue:curvature_method=off \
                -f {lhw}:edgecolor=yellow:edgethickness={args.linew}:color=yellow:curvature_method=off \
                -f {rhw}:edgecolor=yellow:edgethickness={args.linew}:color=yellow:curvature_method=off -view left -viewport 3d'

    
    elif args.compare:
        # This assumes that NEW is the fixed volume and OLD is in backup folder
        lhpN = join(ssdir, 'surf', 'lh.pial')
        rhpN = join(ssdir, 'surf', 'rh.pial')
        lhwN = join(ssdir, 'surf', 'lh.white')
        rhwN = join(ssdir, 'surf', 'rh.white')

        lhpO = join(ssbck, 'surf', 'lh.pial')
        rhpO = join(ssbck, 'surf', 'rh.pial')
        lhwO = join(ssbck, 'surf', 'rh.white')
        rhwO = join(ssbck, 'surf', 'rh.white')

        cmd = f'freeview -v {st1}:visible=1 \
                -f {lhpN}:edgecolor=darkgreen:edgethickness={args.linew}:color=darkgreen:curvature_method=off:name=L_Pial_Corrected \
                -f {rhpN}:edgecolor=darkgreen:edgethickness={args.linew}:color=darkgreen:curvature_method=off:name=R_Pial_Corrected \
                -f {lhwN}:edgecolor=green:edgethickness={args.linew}:color=green:curvature_method=off:name=L_WM_Corrected \
                -f {rhwN}:edgecolor=green:edgethickness={args.linew}:color=green:curvature_method=off:name=L_WM_Corrected \
                -f {lhpO}:edgecolor=darkred:edgethickness={args.linew}:color=darkred:curvature_method=off:name=L_Pial_Old \
                -f {rhpO}:edgecolor=darkred:edgethickness={args.linew}:color=darkred:curvature_method=off:name=R_Pial_Old \
                -f {lhwO}:edgecolor=red:edgethickness={args.linew}:color=red:curvature_method=off:name=L_WM_Old \
                -f {rhwO}:edgecolor=red:edgethickness={args.linew}:color=red:curvature_method=off:name=R_WM_Old'

    else:
        lhp = join(ssdir, 'surf', 'lh.pial')
        rhp = join(ssdir, 'surf', 'rh.pial')
        lhw = join(ssdir, 'surf', 'lh.white')
        rhw = join(ssdir, 'surf', 'rh.white')
        
        cmd = f'freeview -v {st1} \
                -f {lhp}:edgecolor=blue:edgethickness={args.linew}:curvature_method=off \
                -f {rhp}:edgecolor=blue:edgethickness={args.linew}:curvature_method=off \
                -f {lhw}:edgecolor=yellow:edgethickness={args.linew} \
                -f {rhw}:edgecolor=yellow:edgethickness={args.linew} -viewport coronal -layout 4'

    if args.ras:
        cmd = cmd + f' -ras {args.ras[0]} {args.ras[1]} {args.ras[2]}' 
    
    sb.run(cmd, shell=True)
