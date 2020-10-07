"""Tasks for the redis-queue"""
import os
import time
import logging
import pandas as pd
from ngs import HiCTools as HT
import cooler
from hicognition import io_helpers, higlass_interface
from requests.exceptions import HTTPError
from rq import get_current_job
from . import create_app, db
from .models import Dataset, Pileupregion, Pileup

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
    log.info(f"Bed pipeline started for {dataset_id} with {window_sizes}")
    # bed-file preprocessing: sorting, clodius, uploading to higlass
    bed_preprocess_pipeline_step(dataset_id)
    for window in window_sizes:
        file_path = Dataset.query.get(dataset_id).file_path
        log.info(f"  Converting to bed, windowsize {window}")
        target_file = file_path + f".{window}" + ".bedpe"
        io_helpers.convert_bed_to_bedpe(
            file_path, target_file, window
        )
        bedpe_preprocess_pipeline_step(target_file, dataset_id, window)
    # TODO: set task to complete


def pipeline_cooler(dataset_id, binsizes):
    """Starts the pipeline for
    cooler-files. Pipeline:
    - Add to higlass and update uuid
    - For each binsize in binsizes
        - For each pileupregion
            * Pileup ICCF and write to csv-file
            * Pileup Obs/Exp and write to csv-file
            * add to Pileup database table
    - Indicate in Job table in database that job is complete
    """
    log.info(f"Cooler pipeline started for {dataset_id} with {binsizes}")
    current_dataset = Dataset.query.get(dataset_id)
    # upload to higlass
    log.info("  Uploading to higlass...")
    credentials = {
            "user": app.config["HIGLASS_USER"],
            "password": app.config["HIGLASS_PWD"],
    }
    try:
        result = higlass_interface.add_tileset(
            "bedfile",
            current_dataset.file_path,
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
    db.session.commit()
    # get all pileup regions
    pileup_regions = Pileupregion.query.all()
    # get arms
    arms = HT.get_arms_hg19()
    # perform pileups
    for binsize in binsizes:
        for pileup_region in pileup_regions:
            perform_pileup_iccf(current_dataset, pileup_region, binsize, arms)
    # TODO: set task to complete



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


def perform_pileup_iccf(cooler_dataset, pileup_region, binsize, arms):
    """Performs iccf pileup of cooler_dataset on
    pileup_region with resolution binsize."""
    log.info(f"  Doing pileup on cooler {cooler_dataset.id} with pileupregion {pileup_region.id} on binsize {binsize}")
    # get path to dataset
    file_path = pileup_region.source_dataset.file_path
    # get windowsize
    window_size = pileup_region.windowsize
    # load bedfile
    log.info("      Loading regions...")
    regions = pd.read_csv(file_path, sep="\t", header=None)
    if len(regions.columns) > 2:
        # region definition with start and end
        regions = regions.rename(columns={0: "chrom", 1: "start", 2: "end"})
        regions.loc[:, "pos"] = (regions["start"] + regions["end"])//2
    else:
        # region definition with start
        regions = regions.rename(columns={0: "chrom", 1: "pos"})
    # do pileup
    log.info("      Doing pileup...")
    cooler_file = cooler.Cooler(cooler_dataset.file_path + f"::/resolutions/{binsize}")
    pileup_windows = HT.assign_regions(window_size, int(binsize), regions["chrom"], regions["pos"], arms).dropna()
    pileup_array = HT.do_pileup_iccf(cooler_file, pileup_windows, proc=2)
    # prepare dataframe for js reading
    log.info("      Writing output...")
    output_frame = pd.DataFrame(pileup_array)
    output_molten = output_frame.stack().reset_index().rename(columns={"level_0": "variable", "level_1": "group", 0: "value"})
    # scale output so that colormap can be adjusted in integer steps
    output_molten.loc[:, "value"] = output_molten["value"] * 10000
    # stitch together filepath
    basedir = os.path.abspath(os.path.dirname(__file__))
    static_dir = os.path.join(basedir, "static")
    file_name = file_path.split("/")[-1] + f".{window_size}" + f".{binsize}.csv"
    # write to file
    output_molten.to_csv(os.path.join(static_dir, file_name), index=False)
    # add this to database
    log.info("      Adding database entry...")
    new_entry = Pileup(binsize=int(binsize),
                        name=file_name,
                        file_path=file_name,
                        pileupregion_id=pileup_region.id,
                        cooler_id=cooler_dataset.id)
    db.session.add(new_entry)
    db.session.commit()
    log.info("      Success!")
