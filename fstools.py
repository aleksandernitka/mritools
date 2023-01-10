

class seg:
    """
    Runs the segmentation algorithms on a set of freesurfer data. Extracts stats to a separate directory for easier access.
    The script will check if the subject has been processed before, and if so it will skip it.
    The script will also check if the subject has a PD image, and if not it will skip it.
    """
    def __init__(self, subjects_dir, analysis_id, pd_images_dir, threads=40, telegram=True, skip_existing=True):

        from os.path import exists, expanduser
        from time import perf_counter as ptime
        from datetime import datetime

        # add time to printout of the analysis so we know what time we started.
        
        self.subjects_dir = subjects_dir
        self.analysis_id = analysis_id
        self.pd_images_dir = pd_images_dir
        self.telegram = telegram
        self.threads = threads
        self.skip_existing = skip_existing
        self.ptime = ptime
        self.dt = datetime
        self.timings = [] # keep the durations for each subject
        self.errlog = f'{self.analysis_id}_errlog.txt'

        if self.telegram:
            try:
                from send_telegram import sendtel
                self.tgsend = sendtel
                print('Telegram notifications enabled')
            except:
                self.telegram = False
                self.tgsend = None
                print("Could not import send_telegram")

        # Get full paths for PD image and Freesurfer subjects_dir
        self.subjects_dir = expanduser(self.subjects_dir)
        self.pd_images_dir = expanduser(self.pd_images_dir)
        
        # Check if the subjects_dir exists
        if not exists(self.subjects_dir):
            raise Exception("Subjects directory does not exist")

        # Check if the pd_images_dir exists
        if not exists(self.pd_images_dir):
            raise Exception("PD images directory does not exist")

    def log_error(self, subject_id, error):
        
        "Log the error to a file"
        from datetime import datetime as dt
        with open(self.errlog, 'a') as f:
            f.write(f'{dt.now()}\t{subject_id}\t{error}\n')
            f.close()

    def check_exists(self, subject_id, seg_type):
        
        """
        Check if the subject has been processed before
        seg_type is the three-letter code of module, eg., HPC, THN, etc
        """
        from os.path import exists, join, expanduser

        # check if there was an error with this sub and so the segmentation was not performed
        if exists(f'{subject_id}_{seg_type}_seg_err.txt'):
            return True
        
        if exists(join(expanduser(self.subjects_dir), subject_id, 'mri', f'{self.analysis_id}.FSspace.mgz')):
            return True
        else:
            return False

    def data_info(self, list_ids=False):
        """
        Print information about the data. What has and what has not been processed so far.
        """
        from os import listdir as ls
        from os.path import exists

        # Get the subjects from the FS subjects_dir
        allSubjects = [s for s in ls(self.subjects_dir) if s.startswith('sub-')]
        print(f'Data info for {self.analysis_id}.')
        print(f'Found a total of {len(allSubjects)} subjects in {self.subjects_dir}.')

        # Get the subjects that have been processed
        processedSubjects = [s for s in allSubjects if self.check_exists(s)]
        print(f'{len(processedSubjects)} subjects have been processed.')

        # Get the subjects that have not been processed
        unprocessedSubjects = [s for s in allSubjects if not self.check_exists(s)]
        print(f'{len(unprocessedSubjects)} subjects have not been processed.')

        # List previous errors:
        err_logged = [s for s in ls() if s.endswith('_seg_err.txt')]
        print(f'Found {len(err_logged)} error logs.')
        if list_ids:
            print('details:')
            for s in err_logged:
                print(s)
        
        errSubjects = [s for s in unprocessedSubjects if s in err_logged]
        print(f'That includes: {len(errSubjects)} subjects have not been processed due to a previous error.')
        # IF details are required, print them
        if list_ids:
            print('details:')
            for s in errSubjects:
                print(s)

        # List not processed:
        unprocessedSubjects = [s for s in unprocessedSubjects if not s in errSubjects]
        print(f'That includes: {len(unprocessedSubjects)} subjects have not been processed.')
        # IF details are required, print them
        if list_ids:
            print('details:')
            for s in unprocessedSubjects:
                print(s)
        
    def progress_info(self, iteration):

        "Print progress info"
        from statistics import median as median
        from datetime import timedelta as td

        # Print the mean time and how much time is left
        if len(self.timings) > 2:
            print(f'M time per sub: {median(self.timings)/60} minutes. ETA: {self.dt.now() + td(minutes=((len(self.subjects)-iteration)*median(self.timings))/60)}')
        
    def run_hpc_sub(self, subject_id, print_count=True):

        import subprocess as sp
        from os.path import join, exists
        from os import listdir as ls

        # Check subject id
        if not subject_id.startswith('sub-'):
            subject_id = f'sub-{subject_id}'

        # Check if the subject exists
        if not exists(join(self.subjects_dir, subject_id)):
            self.log_error(subject_id, 'Subject dir does not exist')
            print(f"Subject {subject_id} does not exist")
            return None
        
        # Check if the subject has a PD image
        # list all PD images in mpm dir
        pd_images = [f for f in ls(join(self.pd_images_dir, subject_id, 'Results')) if f.endswith('PD.nii')]
        if len(pd_images) == 0:
            self.log_error(subject_id, 'PD image does not exist')
            print(f"Subject {subject_id} does not have a PD image")
            return None
        elif len(pd_images) > 1:
            self.log_error(subject_id, 'Multiple PD images')
            print(f"Subject {subject_id} has multiple PD images")
            return None
        # otherwise we will have exactly one image -> pd_images[0]
        if print_count:
            print(f'Running HPC/AMG segmentation on {subject_id}, starting at {self.dt.now()}')

        # start timing
        tstart = self.ptime()

        # run the segmentation
        process = sp.run(f'export ITK_GLOBAL_DEFAULT_NUMBER_OF_THREADS={self.threads}; segmentHA_T2.sh {subject_id} \
            {join(self.pd_images_dir, subject_id, "Results", pd_images[0])} \
            {self.analysis_id} \
            1 \
            {self.subjects_dir}', shell=True, capture_output=True)
        
        # Above sp.run will suppress the output from the subprocess, capture it and print it if there is an error
        # If all is well we can access the log file in the subject's directory, but errors may get lost. 

        if process.returncode != 0:
            self.log_error(subject_id, 'Segmentation failed')
            print(f"Subject {subject_id} segmentation failed: {process.stderr.decode('utf-8')}")
            # Also save it for later
            with open(f'{subject_id}_hpc_seg_err.txt', 'w') as f:
                f.write(process.stderr.decode('utf-8'))
                f.close()
            return None
        
        # end time
        tend = self.ptime()
        self.timings.append(tend-tstart)
        print(f'Finished HPC/AMG segmentation on {subject_id}, it took {(tend-tstart)/60} minutes')

        return None
 
    def run_hpc_list(self, subject_list):
        
        "Run for subjects in a given list"
        
        if len(subject_list) == 0:
            raise Exception("No subjects found in subject_list")

        self.subjects = subject_list

        print(f'Running HPC/AMG segmentation on {len(self.subjects)} subjects')
        
        for i, subject in enumerate(self.subjects):
            
            # check if sub has been processed before
            if self.skip_existing:
                if self.check_exists(subject, 'hpc'):
                    print(f'Subject {subject} has been processed before, skipping')
                    continue
            
            print(f'\nRunning HPC/AMG segmentation on {subject} ({i+1}/{len(self.subjects)})\n')
            self.run_hpc_sub(subject, print_count=False)

            # print progress info
            self.progress_info(i)

        print(f'Finished HPC/AMG segmentation on {len(self.subjects)} subjects')
        if self.telegram:
            self.tgsend(f'Finished HPC/AMG segmentation on {len(self.subjects)} subjects')

    def run_thn_sub(self, subject_id, print_count=True):

        import subprocess as sp
        from os.path import join, exists
        from os import listdir as ls

        # Check subject id
        if not subject_id.startswith('sub-'):
            subject_id = f'sub-{subject_id}'

        # Check if the subject exists
        if not exists(join(self.subjects_dir, subject_id)):
            self.log_error(subject_id, 'Subject dir does not exist')
            print(f"Subject {subject_id} does not exist")
            return None
        
        # Check if the subject has a PD image
        # list all PD images in mpm dir
        pd_images = [f for f in ls(join(self.pd_images_dir, subject_id, 'Results')) if f.endswith('PD.nii')]
        if len(pd_images) == 0:
            self.log_error(subject_id, 'PD image does not exist')
            print(f"Subject {subject_id} does not have a PD image")
            return None
        elif len(pd_images) > 1:
            self.log_error(subject_id, 'Multiple PD images')
            print(f"Subject {subject_id} has multiple PD images")
            return None
        # otherwise we will have exactly one image -> pd_images[0]
        if print_count:
            print(f'Running THN segmentation on {subject_id}, starting at {self.dt.now()}')

        # start timing
        tstart = self.ptime()

        # run the segmentation
        # segmentThalamicNuclei.sh bert  [SUBJECTS_DIR]  FILE_ADDITIONAL_SCAN   ANALYSIS_ID
        process = sp.run(f'export ITK_GLOBAL_DEFAULT_NUMBER_OF_THREADS={self.threads}; \
            segmentThalamicNuclei.sh {subject_id} \
            {self.subjects_dir} \
            {join(self.pd_images_dir, subject_id, "Results", pd_images[0])} \
            {self.analysis_id} \
            t2', shell=True, capture_output=True)
        
        # Above sp.run will suppress the output from the subprocess, capture it and print it if there is an error
        # If all is well we can access the log file in the subject's directory, but errors may get lost. 

        if process.returncode != 0:
            self.log_error(subject_id, 'THN Segmentation failed')
            print(f"Subject {subject_id} THN segmentation failed: {process.stderr.decode('utf-8')}")
            # Also save it for later
            with open(f'{subject_id}_thn_seg_err.txt', 'w') as f:
                f.write(process.stderr.decode('utf-8'))
                f.close()
            return None
        
        # end time
        tend = self.ptime()
        self.timings.append(tend-tstart)
        print(f'Finished THN segmentation on {subject_id}, it took {(tend-tstart)/60} minutes')

        return None

    def run_thn_list(self, subject_list):
    
        "Run for subjects in a given list"
        
        if len(subject_list) == 0:
            raise Exception("No subjects found in subject_list")

        self.subjects = subject_list

        print(f'Running THN segmentation on {len(self.subjects)} subjects')
        
        for i, subject in enumerate(self.subjects):
            
            # check if sub has been processed before
            if self.skip_existing:
                if self.check_exists(subject, 'thn'):
                    print(f'Subject {subject} has been processed before, skipping')
                    continue
            
            print(f'\nRunning THN segmentation on {subject} ({i+1}/{len(self.subjects)})\n')
            self.run_hpc_sub(subject, print_count=False)

            # print progress info
            self.progress_info(i)

        print(f'Finished THN segmentation on {len(self.subjects)} subjects')
        if self.telegram:
            self.tgsend(f'Finished THN segmentation on {len(self.subjects)} subjects')
