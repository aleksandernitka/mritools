from fstools import seg

segment = seg(subjects_dir='/Volumes/clab/aleksander/tmp_fshpc/subs/',\
        stats_output_dir='/Volumes/clab/aleksander/tmp_fshpc/stats/',\
        analysis_id='testPy2',\
        pd_images_dir='/Volumes/clab/aleksander/tmp_fshpc/pds/')

segment.run_hpc_list(['sub-', 'sub-'])
