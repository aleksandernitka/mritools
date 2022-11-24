"""
Runs the HPC/AMG segmentation algorithm on a set of freesurfer data. Extracts stats to a separate directory for easier access.
"""

class seg:
    def __init__(self, subjects_dir, stats_output_dir, analysis_id, pd_images_dir, telegram_bot=None):

        import subprocess as sp
        from os.path import join, exists, expanduser
        # TODO add time to measure the duration and ETA
        
        self.subjects_dir = subjects_dir
        self.stats_output_dir = stats_output_dir
        self.analysis_id = analysis_id
        self.pd_images_dir = pd_images_dir
        self.telegram_bot = telegram_bot # TODO: implement

        # Get full path
        self.subjects_dir = expanduser(self.subjects_dir)
        self.stats_output_dir = expanduser(self.stats_output_dir)
        self.pd_images_dir = expanduser(self.pd_images_dir)
        
        # Check if the subjects_dir exists
        if not exists(self.subjects_dir):
            raise Exception("Subjects directory does not exist")

        # Check if the pd_images_dir exists
        if not exists(self.pd_images_dir):
            raise Exception("PD images directory does not exist")

        if not exists(self.stats_output_dir):
            sp.run(f'mkdir {self.stats_output_dir}', shell=True)
            print(f'Created {self.stats_output_dir}')
        if not exists(join(self.stats_output_dir, self.analysis_id)):
            sp.run(f'mkdir {join(self.stats_output_dir, self.analysis_id)}', shell=True)
            print(f'Created {join(self.stats_output_dir, self.analysis_id)}')
        if not exists(join(self.stats_output_dir, self.analysis_id, 'stats')):
            sp.run(f'mkdir {join(self.stats_output_dir, self.analysis_id, "stats")}', shell=True)
            print(f'Created {join(self.stats_output_dir, self.analysis_id, "stats")}')
        if not exists(join(self.stats_output_dir, self.analysis_id, 'logs')):
            sp.run(f'mkdir {join(self.stats_output_dir, self.analysis_id, "logs")}', shell=True)
            print(f'Created {join(self.stats_output_dir, self.analysis_id, "logs")}')

    def run_hpc_sub(self, subject_id, print_count=True):

        import subprocess as sp
        from os.path import join, exists
        
        # Check subject id
        if not subject_id.startswith('sub-'):
            subject_id = f'sub-{subject_id}'
        
        # Check if the subject exists
        if not exists(join(self.subjects_dir, subject_id)):
            raise Exception(f"Subject {subject_id} does not exist")

        # Check if the subject has a PD image
        if not exists(join(self.pd_images_dir, subject_id, 'Results', f'{subject_id}_PD_iPAT2_23_1_RFSC_PD.nii')):
            raise Exception(f"Subject {subject_id} does not have a PD image")
        
        if print_count:
            print(f'Running HPC/AMG segmentation on {subject_id}')
        
        # all good to go
        # run the segmentation
        sp.run(f'segmentHA_T2.sh {subject_id} \
            {join(self.pd_images_dir, subject_id, "Results", f"{subject_id}_PD_iPAT2_23_1_RFSC_PD.nii")} \
            {self.analysis_id} \
            1 \
            {self.subjects_dir}', shell=True)

        # extract log file
        sp.run(f'cp {join(self.subjects_dir, subject_id, "scripts", f"hippocampal-subfields-T2.{self.analysis_id}.log")} \
            {join(self.stats_output_dir, self.analysis_id, "logs", f"{subject_id}_hippocampal-subfields-T2.{self.analysis_id}.log")}', shell=True)

        # extract stats
        stats_files = [f'amygdalar-nuclei.rh.T2.v21.{self.analysis_id}.stats', \
        f'hipposubfields.rh.T2.v21.{self.analysis_id}.stats', \
        f'amygdalar-nuclei.lh.T2.v21.{self.analysis_id}.stats', \
        f'hipposubfields.lh.T2.v21.{self.analysis_id}.stats']

        for stats_file in stats_files:
            sp.run(f'cp {join(self.subjects_dir, subject_id, "stats", stats_file)} \
                {join(self.stats_output_dir, self.analysis_id, "stats", "{subject_id}_{stats_file}")}', shell=True)
      
        print(f'Finished HPC/AMG segmentation on {subject_id}')

    def run_hpc_all(self):
        "Run for all subjects in FS subjects_dir"
        from os import listdir as ls
        
        subjects = [s for s in ls(self.subjects_dir) if s.startswith('sub-')]
        
        if len(subjects) == 0:
            raise Exception("No subjects found in subjects_dir")

        print(f'Running HPC/AMG segmentation on {len(subjects)} subjects')
        for i, subject in enumerate(subjects):
            print(f'\nRunning HPC/AMG segmentation on {subject} ({i+1}/{len(subjects)})\n')
            self.run_hpc_sub(subject, print_count=False)

        print(f'Finished HPC/AMG segmentation on {len(subjects)} subjects')
        # TODO add telegram bot message
        
    def run_hpc_list(self, subject_list):
        "Run for subjects in a given list"
        if len(subject_list) == 0:
            raise Exception("No subjects found in subject_list")

        print(f'Running HPC/AMG segmentation on {len(subject_list)} subjects')
        for i, subject in enumerate(subject_list):
            print(f'\nRunning HPC/AMG segmentation on {subject} ({i+1}/{len(subject_list)})\n')
            self.run_hpc_sub(subject, print_count=False)

        print(f'Finished HPC/AMG segmentation on {len(subject_list)} subjects')
        # TODO add telegram bot message

class seg_tha(seg):
    pass