class seg:
    """
    Runs the segmentation algorithms on a set of freesurfer data.
    The script will check if the subject has been processed before, and if so it will skip it.
    The script will also check if the subject has a PD image, and if not it will skip it, in case when such image is required. 

    Parameters
    ----------
    subjects_dir    : str   location of freesurfer subjects_dir
    analysis_id     : str   name of the analysis
    pd_images_dir   : str   location of the PD images
    threads         : int   number of threads to use
    telegram        : bool  send notifications to telegram
    skip_existing   : bool  skip subjects that have been processed before
    hpc             : bool  run HPC segmentation
    thn             : bool  run Thalamic Nuclei segmentation
    bss             : bool  run Brainstem segmentation
    hts             : bool  run Hypothalamus segmentation
    scl             : bool  run Subcortical Limbic segmentation


    """
    def __init__(self, subjects_dir, analysis_id, pd_images_dir, threads=40, telegram=True, skip_existing=True, \
        hpc=False, thn=False, bss=False, hts=False, scl=False):

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

        self.hpc = hpc # HPC segmentation
        self.thn = thn # Thalamic Nuclei segmentation
        self.bss = bss # Brainstem segmentation
        self.hts = hts # Hypothalamus segmentation
        self.scl = scl # Subcortical Limbic segmentation

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

    def check_exists(self, subject_id, seg_type):
        
        """
        Check if the subject has been processed before
        seg_type is the three-letter code of module, eg., HPC, THN, etc
        """
        from os.path import exists, join, expanduser

        # check if there was an error with this sub and so the segmentation was not performed
        if exists(f'{subject_id}_{seg_type}_seg_err.txt'):
            return True
        # FIXME the below is not good, requires analysisIDs to be different for each module,
        # on the other hand, separare ids help when something has to be removed en masse
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
   
    def log_results(self, subject_id, segmentation, result):
        # pass result from the subprocess, it will save something if there was an error
        from datetime import datetime as dt

        if result.returncode != 0:
            with open(self.errlog, 'a') as f:
                f.write(f'{dt.now()}\t{subject_id}\t{segmentation} segmentation failed\n')
                f.close()

            print(f"Subject {subject_id} {segmentation} segmentation failed: {result.stderr.decode('utf-8')}")
            # Also save it for later
            with open(f'{subject_id}_{segmentation}_seg_err.txt', 'w') as f:
                f.write(result.stderr.decode('utf-8'))
                f.close()
            return None

    def run_segmentation(self, subject_id):

        # Runs a single subject through all specified segmentations

        import subprocess as sp
        from os.path import join, exists, abspath
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

        # Only run the PD check for analyses that require it
        # TODO

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
        
        # Start the timer
        tstart = self.ptime()

        if self.hpc:
            # Run the HPC segmentation with additional PD scan
            process = sp.run(f'export ITK_GLOBAL_DEFAULT_NUMBER_OF_THREADS={self.threads}; segmentHA_T2.sh {subject_id} \
            {join(self.pd_images_dir, subject_id, "Results", pd_images[0])} \
            {self.analysis_id} \
            1 \
            {self.subjects_dir}', shell=True, capture_output=True)

            self.log_results(subject_id, 'HPC', process)

        if self.thn:
            # Run the THN segmentation with additional PD scan
            process = sp.run(f'export ITK_GLOBAL_DEFAULT_NUMBER_OF_THREADS={self.threads}; \
            segmentThalamicNuclei.sh {subject_id} \
            {self.subjects_dir} \
            {join(self.pd_images_dir, subject_id, "Results", pd_images[0])} \
            {self.analysis_id} \
            t2', shell=True, capture_output=True)

            self.log_results(subject_id, 'THN', process)

        if self.bss:
            # TODO
            # Run the BS segmentation
            # simple process, does not require any additional scans and does not take analysis ID
            process = sp.run(f'export ITK_GLOBAL_DEFAULT_NUMBER_OF_THREADS={self.threads}; \
            segmentBS.sh {subject_id} {self.subjects_dir}', shell=True, capture_output=True)
            
            self.log_results(subject_id, 'BSS', process)

        if self.hts:
            # only in FS 7.2+, use singularity container maybe?
            pass

        if self.scl:
            # Run the sclimbic segmentation, it is relatively new and requires dev version of freesurfer or
            # a standalone toolbox, that this will download if not found in the dir.
            # TODO checking of prior files in the fs dir will not work here, can be skipped. 
            
            if not exists ('sclimbic'):
                # Get the toolbox
                sp.run('wget https://surfer.nmr.mgh.harvard.edu/pub/dist/sclimbic/sclimbic-linux-20210725.tar.gz', shell=True)
                sp.run('tar -xvf sclimbic-linux-20210725.tar.gz', shell=True)
                sp.run('rm sclimbic-linux-20210725.tar.gz', shell=True)

            # get the dir of the extracted toolbox
            scli_dir = abspath('sclimbic')

            # Set the paths to the files
            t1_mgz = join(self.subjects_dir, subject_id, 'mri', 'T1.mgz')
            sclimbic_mgz = join(self.subjects_dir, subject_id, 'mri', f'{subject_id}_sclimbic.mgz')

            # source the toolbox each time
            process = sp.run(f'export FREESURFER_HOME={scli_dir}; \
                source $FREESURFER_HOME/setup.sh; \
                mri_sclimbic_seg --i {t1_mgz} --o {sclimbic_mgz} \
                --write_volumes --write_qa_stats --etiv --threads {self.threads}', shell=True, capture_output=True)

            self.log_results(subject_id, 'SCL', process)

        # end time
        tend = self.ptime()
        self.timings.append(tend-tstart)
        print(f'Finished segmentation on {subject_id}, it took {(tend-tstart)/60} minutes')

        return None
