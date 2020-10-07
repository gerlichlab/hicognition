"""Tasks for the redis-queue"""
import os
import time
import logging
import hicognition
from rq import get_current_job
from . import create_app, db

# setup app context

app = create_app(os.getenv('FLASK_CONFIG') or 'default')
app.app_context().push()


def pipeline_bed(dataset_id, window_sizes, outputfolder):
    """Starts the pipeline for
    bed-files. Pipeline:
    - sort bedfile associated with dataset_id
    - run clodius on sorted bedfile
    - upload clodius result to higlass
    - store higlass_uuid in Dataset db entry
    - For each windowsize in window_sizes, do:
        * convert bed to bedpe
        * run clodius on bedpe
        * upload result to higlass
        * Add PileupRegion dataset entry
    - Indicate in Job table in database that job is complete
    """


def pipeline_cooler(dataset_id, binsizes):
    """Starts the pipeline for
    cooler-files. Pipeline:
    - For each binsize in binsizes
        - For each pileupregion
            * Pileup ICCF and write to csv-file
            * Pileup Obs/Exp and write to csv-file
            * add to Pileup database table
    - Indicate in Job table in database that job is complete
    """

def example(seconds):
    logging.info('Starting task')
    for i in range(seconds):
        logging.info(f"     {i}")
        time.sleep(1)
    logging.info('Task completed')