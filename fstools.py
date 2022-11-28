"""
Runs the HPC/AMG segmentation algorithm on a set of freesurfer data. Extracts stats to a separate directory for easier access.
"""

class seg:
    def __init__(self, subjects_dir, stats_output_dir, analysis_id, pd_images_dir, threads=40, telegram=True):

        import subprocess as sp
        from os.path import join, exists, expanduser
        from statistics import mean as mean
        from time import perf_counter as ptime
        
        self.subjects_dir = subjects_dir
        self.stats_output_dir = stats_output_dir
        self.analysis_id = analysis_id
        self.pd_images_dir = pd_images_dir
        self.telegram = telegram
        self.thread = threads
        self.mean = mean
        self.ptime = ptime
        self.timings = [] # keep the durations for each subject

        if self.telegram:
            try:
                from send_telegram import sendtel
                self.tgsend = sendtel()
            except:
                print("Could not import send_telegram")
                self.telegram = False
                self.tgsend = None

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

        # start timing
        tstart = self.ptime()

        # run the segmentation
        sp.run(f'export ITK_GLOBAL_DEFAULT_NUMBER_OF_THREADS={self.threads}; segmentHA_T2.sh {subject_id} \
            {join(self.pd_images_dir, subject_id, "Results", f"{subject_id}_PD_iPAT2_23_1_RFSC_PD.nii")} \
            {self.analysis_id} \
            1 \
            {self.subjects_dir}', shell=True)
        
        # end time
        tend = self.ptime()
        self.timings.append(tend-tstart)
        print(f'Finished HPC/AMG segmentation on {subject_id}, it took {(tend-tstart)/60} minutes')

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

            # Print the mean time and how much time is left
            if len(self.timings) > 2:
                print(f'Average time per subject: {self.mean(self.timings)/60} minutes')
                print(f'Estimated time remaining: {((len(subjects)-i)*self.mean(self.timings))/60} minutes')

        print(f'Finished HPC/AMG segmentation on {len(subjects)} subjects')
        if self.telegram:
            self.tgsend(f'Finished HPC/AMG segmentation on {len(subject_list)} subjects')
 
    def run_hpc_list(self, subject_list):
        "Run for subjects in a given list"
        if len(subject_list) == 0:
            raise Exception("No subjects found in subject_list")

        print(f'Running HPC/AMG segmentation on {len(subject_list)} subjects')
        for i, subject in enumerate(subject_list):
            print(f'\nRunning HPC/AMG segmentation on {subject} ({i+1}/{len(subject_list)})\n')
            self.run_hpc_sub(subject, print_count=False)
            
            # Print the mean time and how much time is left
            if len(self.timings) > 2:
                print(f'Average time per subject: {self.mean(self.timings)/60} minutes')
                print(f'Estimated time remaining: {((len(subject_list)-i)*self.mean(self.timings))/60} minutes')

        print(f'Finished HPC/AMG segmentation on {len(subject_list)} subjects')
        if self.telegram:
            self.tgsend(f'Finished HPC/AMG segmentation on {len(subject_list)} subjects')


class seg_tha(seg):
    pass
