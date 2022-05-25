#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import sys
import argparse
import os
import subprocess as sb

parser = argparse.ArgumentParser(description = 'This is a script to help with plotting of freesurfer outputs, pass subject id and the it will take care of plotting for you. Optionally you can add an argument to show the 3d render of the brain as infalted. @author: aleksander nitka')

parser.add_argument('id', help = 'Subject id')
parser.add_argument('-i', '--inflated', help = 'Show the inflated surface', action = 'store_true', required = False, default = False)
parser.add_argument('-b', '--brain', help = 'Import skull stripped image as base for 2D', action = 'store_true', required = False, default = False)
parser.add_argument('-n', '--nu', help = 'Show the nu.mgz file as base image', action = 'store_true', required = False, default = False)
parser.add_argument('-to', '--thickness', help = 'Only for the inflated display option, use thickness of the surface as an overlay', action = 'store_true', required = False, default = False)
parser.add_argument('-pt', '--pialth', help = 'Show the pial surface with thickness overlay (not inflated mode)', action = 'store_true', required = False, default = False)

args = parser.parse_args()

sub = args.id
if 'sub-' not in sub:
    sub = 'sub-' + sub

fsdir = '/mnt/nasips/COST_mri/derivatives/freesurfer/'
    
ssdir = os.path.join(fsdir, sub)
    
if os.path.exists(ssdir) == False:
    print(f'Error: {ssdir} does not exist!')
        
else:
    # Build the cmd

    if args.brain == True:
        st1 = os.path.join(ssdir, 'mri','brain.mgz')
    elif args.nu == True:
        st1 = os.path.join(ssdir, 'mri','nu.mgz')
    else:
        st1 = os.path.join(ssdir, 'mri', 'orig.mgz')
    
    asg = os.path.join(ssdir, 'mri', 'aseg.mgz')
    a09 = os.path.join(ssdir, 'mri', 'aparc.a2009s+aseg.mgz')
            
    if args.inflated == True:
        # This is loading the inflated surface but also aseg but invisible
        lhp = os.path.join(ssdir, 'surf', 'lh.inflated')
        rhp = os.path.join(ssdir, 'surf', 'rh.inflated')
        cmd = f'freeview -v {st1}:visible=0 {asg}:colormap=LUT:opacity=0.3:visible=0\
                {a09}:colormap=LUT:opacity=0.3:visible=0 '
        
        if args.thickness == True:
            # display thickness on inflated surface
            cmd += f'-f {lhp}:overlay=lh.thickness:visible=1:overlay_threshold=0.1,3 \
                    -f {rhp}:overlay=rh.thickness:visible=1:overlay_threshold=0.1,3'
        else:
            cmd += f'-f {lhp}:visible=1 \
                    -f {rhp}:visible=1'

    else:
        lhp = os.path.join(ssdir, 'surf', 'lh.pial')
        rhp = os.path.join(ssdir, 'surf', 'rh.pial')
        lhw = os.path.join(ssdir, 'surf', 'lh.white')
        rhw = os.path.join(ssdir, 'surf', 'rh.white')
        
        annots = 'aparc.a2009s.annot'
        
        if args.pialth == True:
            # display thickness on pial surface
            cmd = f'freeview -v {st1} {asg}:colormap=LUT:opacity=0.3 {a09}:colormap=LUT:opacity=0.3:visible=0 \
                    -f {lhp}:overlay=lh.thickness:visible=1:overlay_threshold=0.1,3:edgecolor=blue \
                    -f {rhp}:overlay=rh.thickness:visible=1:overlay_threshold=0.1,3:edgecolor=blue \
                    -f {lhw}:edgecolor=yellow \
                    -f {rhw}:edgecolor=yellow'

        else:
            cmd = f'freeview -v {st1} {asg}:colormap=LUT:opacity=0.3 {a09}:colormap=LUT:opacity=0.3:visible=0 \
                -f {lhp}:edgecolor=blue:annot={annots} \
                -f {rhp}:edgecolor=blue:annot={annots} \
                -f {lhw}:edgecolor=yellow \
                -f {rhw}:edgecolor=yellow'
        
    sb.run(cmd, shell = True)       
    

