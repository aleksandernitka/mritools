#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import sys
import argparse
import os
import subprocess as sb

parser = argparse.ArgumentParser(description = 'This is a script to help with plotting of freesurfer outputs, pass subject id and the it will take care of plotting for you. Optionally you can add an argument to show the 3d render of the brain as infalted. @author: aleksander nitka')

parser.add_argument('id', help = 'Subject id, must be specified as first argument')
parser.add_argument('-in', '--inflated', help = 'Show the inflated surface, no aseg, just pial surface', action = 'store_true', required = False, default = False)
parser.add_argument('-ho', '--holes', help = 'Dedicated mode for showing holes in the surface; no aseg just WM in yellow and Pial in Blue', action = 'store_true', required = False, default = False)
parser.add_argument('-ap', '--aparc', help = 'Load default with aparc aseg', action = 'store_true', required = False, default = False)
parser.add_argument('-ras', '--ras', help = 'Go to given RAS coordinate x y z', required = False, nargs=3, metavar=('x', 'y', 'z'), type = float)
args = parser.parse_args()

sub = args.id
if 'sub-' not in sub:
    sub = 'sub-' + sub

#fsdir = '/mnt/nasips/COST_mri/derivatives/freesurfer/'
fsdir = '/Volumes/clab/COST_mri/derivatives/freesurfer/'

ssdir = os.path.join(fsdir, sub)
    
if os.path.exists(ssdir) == False:
    print(f'Error: {ssdir} does not exist!')
        
else:
    # Build the cmd
    
    st1 = os.path.join(ssdir, 'mri', 'orig.mgz')

    if args.aparc:
        a09 = os.path.join(ssdir, 'mri', 'aparc.a2009s+aseg.mgz')
        lhp = os.path.join(ssdir, 'surf', 'lh.pial')
        rhp = os.path.join(ssdir, 'surf', 'rh.pial')
        lhw = os.path.join(ssdir, 'surf', 'lh.white')
        rhw = os.path.join(ssdir, 'surf', 'rh.white')
        annots = 'aparc.a2009s.annot'
        
        cmd = f'freeview -v {st1} -v {a09}:colormap=LUT:opacity=0.3 \
                -f {lhp}:edgecolor=blue:annot={annots}:edgethickness=1 \
                -f {rhp}:edgecolor=blue:annot={annots}:edgethickness=1 \
                -f {lhw}:edgecolor=yellow:edgethickness=1 \
                -f {rhw}:edgecolor=yellow:edgethickness=1'


    elif args.inflated:
        lhp = os.path.join(ssdir, 'surf', 'lh.inflated')
        rhp = os.path.join(ssdir, 'surf', 'rh.inflated')
        cmd = f'freeview -f {lhp}:overlay=lh.thickness:visible=1:overlay_threshold=0,5\
                -f {rhp}:overlay=rh.thickness:visible=1:overlay_threshold=0,5 -layout 1 -view lateral -viewport 3d'


    elif args.holes:

        lhp = os.path.join(ssdir, 'surf', 'lh.pial')
        rhp = os.path.join(ssdir, 'surf', 'rh.pial')
        lhw = os.path.join(ssdir, 'surf', 'lh.white')
        rhw = os.path.join(ssdir, 'surf', 'rh.white')
        
        cmd = f'freeview -v {st1}:visible=0 \
                -f {lhp}:edgecolor=blue:edgethickness=1:color=darkblue:curvature_method=off \
                -f {rhp}:edgecolor=blue:edgethickness=1:color=darkblue:curvature_method=off \
                -f {lhw}:edgecolor=yellow:edgethickness=1:color=yellow:curvature_method=off \
                -f {rhw}:edgecolor=yellow:edgethickness=1:color=yellow:curvature_method=off -view left -viewport 3d'

    
    else:
        lhp = os.path.join(ssdir, 'surf', 'lh.pial')
        rhp = os.path.join(ssdir, 'surf', 'rh.pial')
        lhw = os.path.join(ssdir, 'surf', 'lh.white')
        rhw = os.path.join(ssdir, 'surf', 'rh.white')
        
        cmd = f'freeview -v {st1} \
                -f {lhp}:edgecolor=blue:edgethickness=1:curvature_method=off:overlay=lh.thickness:overlay_threshold=0,2.5 \
                -f {rhp}:edgecolor=blue:edgethickness=1:curvature_method=off:overlay=rh.thickness:overlay_threshold=0,2.5 \
                -f {lhw}:edgecolor=yellow:edgethickness=1 \
                -f {rhw}:edgecolor=yellow:edgethickness=1 -viewport coronal -layout 4'

    if args.ras:
        cmd = cmd + f' -ras {args.ras[0]} {args.ras[1]} {args.ras[2]}' 
    
    sb.run(cmd, shell=True)
