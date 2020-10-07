"""Tasks for the redis-queue"""
import os
import time
import logging
from hicognition import io_helpers, higlass_interface
from requests.exceptions import HTTPError
from rq import get_current_job
from . import create_app, db
from .models import Dataset, Pileupregion

# get logger
log = logging.getLogger('rq.worker')

# setup app context

app = create_app(os.getenv('FLASK_CONFIG') or 'default')
app.app_context().push()


def pipeline_bed(dataset_id, window_sizes):
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
    - Indicate in Job table in database that job is complete.
    Output-folder is not needed for this since the file_path
    of Dataset entry contains it.
    """
    # bed-file preprocessing: sorting, clodius, uploading to higlass
    bed_preprocess_pipeline_step(dataset_id)
    for window in window_sizes:
        file_path = Dataset.query.get(dataset_id).file_path
        log.info(f"Converting to bed, windowsize {window}")
        target_file = file_path + f".{window}" + ".bedpe"
        io_helpers.convert_bed_to_bedpe(
            file_path, target_file, window
        )
        bedpe_preprocess_pipeline_step(target_file, dataset_id, window)




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
    log.info(seconds)
    log.info('Starting task')
    for i in range(seconds):
        log.info(f"     {i}")
        time.sleep(1)
    log.info('Task completed')


# helpers

def bed_preprocess_pipeline_step(dataset_id):
    """Runs bed-preprocess pipeline step of pipeline_bed:
        - sort bedfile associated with dataset_id
        - run clodius on sorted bedfile
        - upload clodius result to higlass
        - store higlass_uuid in Dataset db entry
        - replace filepath with sorted bedfile
    """
    log.info(f"Running bed-preprocessing for ID {dataset_id}")
    # get dataset, this is not sorted, not preprocessed for higlass
    current_dataset = Dataset.query.get(dataset_id)
    # sort dataset
    log.info("      Sorting...")
    dataset_file = current_dataset.file_path
    sorted_file_name = dataset_file.split(".")[0] + "_sorted.bed"
    io_helpers.sort_bed(
        dataset_file,
        sorted_file_name,
        app.config["CHROM_SIZES"]
    )
    # preprocess with clodius
    log.info("Clodius preprocessing...")
    output_path = sorted_file_name + ".beddb"
    exit_code = higlass_interface.preprocess_dataset(
                "bedfile", app.config["CHROM_SIZES"], sorted_file_name, output_path
            )
    if exit_code != 0:
        log.error("Clodius failed!")
        return
    # add to higlass
    log.info("      Add to higlass...")
    credentials = {
            "user": app.config["HIGLASS_USER"],
            "password": app.config["HIGLASS_PWD"],
    }
    try:
        result = higlass_interface.add_tileset(
            "bedfile",
            output_path,
            app.config["HIGLASS_API"],
            credentials,
            current_dataset.dataset_name,
        )
    except HTTPError:
        log.error("Higlass upload of bedfile failed")
        return
    # upload succeeded, add uuid of higlass to dataset
    uuid = result['uuid']
    current_dataset.higlass_uuid = uuid
    current_dataset.file_path = sorted_file_name
    db.session.commit()
    log.info("      Success!")


def bedpe_preprocess_pipeline_step(file_path, dataset_id=None, windowsize=None):
    """
    Performs bedpe preprocessing pipeline step:
    * run clodius on bedpe file
    * upload result to higlass
    * add Pileupregion dataset entry
    """
    log.info(f"Bedpe-preprocess: {file_path} with {windowsize}")
    # run clodius
    log.info(f"     Running clodius...")
    clodius_output = file_path + ".bed2ddb"
    higlass_interface.preprocess_dataset(
            "bedpe", app.config["CHROM_SIZES"], file_path, clodius_output
        )
    # add to higlass
    log.info("      Adding to higlass...")
    credentials = {
            "user": app.config["HIGLASS_USER"],
            "password": app.config["HIGLASS_PWD"],
    }
    dataset_name = clodius_output.split("/")[-1]
    try:
        result = higlass_interface.add_tileset(
            "bedpe",
            clodius_output,
            app.config["HIGLASS_API"],
            credentials,
            dataset_name,
        )
    except HTTPError:
        log.error("Higlass upload failed!")
        return
    # upload succeeded, add things to database
    uuid = result["uuid"]
    new_entry = Pileupregion(
        dataset_id=dataset_id,
        name=dataset_name,
        file_path=clodius_output,
        higlass_uuid=uuid,
        windowsize=windowsize,
    )
    db.session.add(new_entry)
    db.session.commit()
    log.info("      Success!")
