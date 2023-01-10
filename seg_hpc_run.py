from fstools import seg
from os import listdir as ls
segment = seg(subjects_dir='/mnt/clab/COST_mri/derivatives/freesurfer/',\
        analysis_id='cost2022',\
        pd_images_dir='/mnt/clab/COST_mri/derivatives/hMRI/')

plist = [f for f in ls('/mnt/clab/COST_mri/derivatives/freesurfer/') if 'sub-' in f]

print(len(plist))

#segment.data_info(True)
segment.run_hpc_list(plist)
