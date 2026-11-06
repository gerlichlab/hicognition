"""Runs every preprocessing step on the synthetic genome and collects what each one stores.

The window and bin sizes are those of v0.8.0's PREPROCESSING_MAP, copied below, and so are the
other settings the steps read. So the reference stays put when the configuration changes, and a
difference means the code or a library computes differently.

Region files go through tasks.pipeline_bed, as on upload. The feature steps are the ones the
workers run (pipeline_steps), called as tasks.py calls them: both sides of a BEDPE, and the
missing stackups before a 1D embedding. tasks.py's own functions for features aren't used,
because they finish by marking their rq job done, which needs a running job.

compute() returns a dict from a key such as
"AverageIntervalData/cooler_a/query_points/100000/5000/ICCF/None/None/None/file_path" to the
stored array, from "cleaned/query/points.bed" to the cleaned BED file's text, and from a key
such as "error/pileup/cooler_a/query_loops/10000/1000/ICCF/None" to the type and message of
the exception a step raised. A step that fails stores nothing, as on a worker, and the
remaining steps still run.
"""
import os
import shutil

import numpy as np
import pandas as pd

INPUT_FILES = os.path.join(os.path.dirname(__file__), "..", "testfiles", "reference")

# v0.8.0's PREPROCESSING_MAP; app_config.py defines 50000 twice, and Python keeps the second
PREPROCESSING_MAP = {
    1000: {"cooler": [], "bigwig": [100, 500], "collections": {"regions": [1000], "1d-features": [100, 500]}},
    2000: {"cooler": [], "bigwig": [100, 500], "collections": {"regions": [1000], "1d-features": [100, 500]}},
    5000: {"cooler": [], "bigwig": [100, 500], "collections": {"regions": [1000], "1d-features": [100, 500]}},
    10000: {"cooler": [1000], "bigwig": [100, 500], "collections": {"regions": [1000], "1d-features": [100, 500]}},
    20000: {
        "cooler": [1000],
        "bigwig": [200, 500, 1000],
        "collections": {"regions": [1000], "1d-features": [2000, 5000, 10000]},
    },
    50000: {
        "cooler": [1000, 5000],
        "bigwig": [500, 1000, 2000],
        "collections": {"regions": [2000], "1d-features": [1000, 2000]},
    },
    100000: {
        "cooler": [1000, 5000],
        "bigwig": [1000, 2000, 5000, 10000],
        "collections": {"regions": [5000], "1d-features": [2000, 5000, 10000]},
    },
    400000: {
        "cooler": [10000],
        "bigwig": [2000, 5000, 10000, 20000],
        "collections": {"regions": [10000, 20000], "1d-features": [5000, 10000, 20000]},
    },
    1000000: {
        "cooler": [20000, 25000],
        "bigwig": [10000, 20000, 50000, 100000],
        "collections": {"regions": [20000, 50000], "1d-features": [20000, 50000, 100000]},
    },
    2000000: {
        "cooler": [50000],
        "bigwig": [20000, 50000, 100000, 200000],
        "collections": {"regions": [50000, 100000, 200000], "1d-features": [50000, 100000, 200000]},
    },
    "variable": {
        "cooler": [5],
        "bigwig": [1, 2, 5],
        "collections": {"regions": [1, 2, 5], "1d-features": [1, 2, 5]},
    },
}

# the other settings the steps read, as in v0.8.0; the stackup threshold is the testing one,
# so that the region sets are subsampled
SETTINGS = {
    "PREPROCESSING_MAP": PREPROCESSING_MAP,
    "STACKUP_THRESHOLD": 10,
    "VARIABLE_SIZE_EXPANSION_FACTOR": 0.2,
    "CLUSTER_NUMBER_LARGE": 20,
    "CLUSTER_NUMBER_SMALL": 10,
    "OBS_EXP_PROCESSES": 10,
    "PILEUP_PROCESSES": 5,
}

COOLERS = ["cooler_a.mcool", "cooler_b.mcool"]
BIGWIGS = ["peaks.bw", "domains.bw", "dips.bw"]
# region sets the features are computed on: file name, size type
QUERY_REGIONS = [
    ("points.bed", "Point"),
    ("tads.bed", "Interval"),
    ("domains.bed", "Interval"),
    ("loops.bedpe", "Point"),
]
# region sets that only make up the collection for the enrichment analysis
COLLECTION_REGIONS = ["points.bed", "shifted.bed", "random.bed"]
# files in which each table keeps its arrays
TABLE_FILES = {
    "AverageIntervalData": ["file_path"],
    "IndividualIntervalData": ["file_path", "file_path_small"],
    "AssociationIntervalData": ["file_path"],
    "EmbeddingIntervalData": [
        "file_path",
        "file_path_feature_values",
        "thumbnail_path",
        "cluster_id_path",
        "feature_distribution_path",
    ],
}


def stem(file_name):
    return file_name.split(".")[0]


def compute(work_dir, input_dir=INPUT_FILES):
    """Runs every step in a fresh in-memory database, with its files in work_dir."""
    # imported here, so that make_reference can set the log paths first
    from app import create_app, db, tasks
    from app import pipeline_steps
    from app.models import (
        Assembly,
        AssociationIntervalData,
        AverageIntervalData,
        Collection,
        Dataset,
        EmbeddingIntervalData,
        IndividualIntervalData,
        Intervals,
        Organism,
        User,
    )

    os.makedirs(work_dir, exist_ok=True)
    app = create_app("testing")
    app.config.update(SETTINGS, UPLOAD_DIR=work_dir)
    results = {}
    with app.app_context():
        db.create_all()
        user = User(username="reference")
        organism = Organism(name="synthetic")
        db.session.add_all([user, organism])
        db.session.commit()
        assembly = Assembly(
            name="synthetic",
            chrom_sizes=os.path.join(input_dir, "synthetic.chrom.sizes"),
            chrom_arms=os.path.join(input_dir, "arms.synthetic"),
            organism_id=organism.id,
            user_id=user.id,
        )
        db.session.add(assembly)
        db.session.commit()
        arms = pd.read_csv(assembly.chrom_arms)

        def add_dataset(name, filetype, file_path, size_type="undefined", dimension="1d"):
            dataset = Dataset(
                dataset_name=name,
                filetype=filetype,
                file_path=file_path,
                assembly=assembly.id,
                user_id=user.id,
                sizeType=size_type,
                dimension=dimension,
                public=False,
                upload_state="uploaded",
                processing_state="new",
            )
            db.session.add(dataset)
            db.session.commit()
            return dataset

        def add_region_set(file_name, size_type, label):
            # the BED pipeline deletes the file it cleans, so it gets a copy
            copy = os.path.join(work_dir, label + "_" + file_name)
            shutil.copy(os.path.join(input_dir, file_name), copy)
            dimension = "2d" if file_name.endswith(".bedpe") else "1d"
            dataset = add_dataset(label + "_" + stem(file_name), "bedfile", copy, size_type, dimension)
            tasks.pipeline_bed(dataset.id)
            with open(dataset.file_path, encoding="utf-8") as f:
                results["cleaned/" + label + "/" + file_name] = f.read()
            return dataset

        def run(key, step, *args, **kwargs):
            """Runs a step; an exception it raises is kept as a result, with the work directory left out."""
            try:
                step(*args, **kwargs)
            except Exception as error:
                db.session.rollback()
                message = str(error).replace(work_dir, "<work_dir>")
                results["error/" + "/".join(str(part) for part in key)] = type(error).__name__ + ": " + message

        coolers = [add_dataset(stem(f), "cooler", os.path.join(input_dir, f)) for f in COOLERS]
        bigwigs = [add_dataset(stem(f), "bigwig", os.path.join(input_dir, f)) for f in BIGWIGS]
        queries = [add_region_set(f, size_type, "query") for f, size_type in QUERY_REGIONS]
        region_collection = Collection(
            name="regions",
            kind="regions",
            user_id=user.id,
            datasets=[add_region_set(f, "Point", "collection") for f in COLLECTION_REGIONS],
        )
        feature_collection = Collection(name="features", kind="1d-features", user_id=user.id, datasets=bigwigs)
        db.session.add_all([region_collection, feature_collection])
        db.session.commit()

        for query in queries:
            sides = [None] if query.dimension == "1d" else ["left", "right"]
            for intervals in Intervals.query.filter(Intervals.dataset_id == query.id).order_by(Intervals.id):
                window = intervals.windowsize if intervals.windowsize is not None else "variable"
                binsizes = PREPROCESSING_MAP[window]
                where = (query.dataset_name, window)
                for cooler_dataset in coolers:
                    for binsize in binsizes["cooler"]:
                        for pileup_type in ("ICCF", "Obs/Exp"):
                            run(
                                ("pileup", cooler_dataset.dataset_name) + where + (binsize, pileup_type, None),
                                pipeline_steps.pileup_pipeline_step,
                                cooler_dataset.id,
                                intervals.id,
                                binsize,
                                arms,
                                pileup_type,
                            )
                for binsize in binsizes["bigwig"]:
                    for bigwig in bigwigs:
                        for side in sides:
                            run(
                                ("stackup", bigwig.dataset_name) + where + (binsize, side),
                                pipeline_steps.stackup_pipeline_step,
                                bigwig.id,
                                intervals.id,
                                binsize,
                                region_side=side,
                            )
                for binsize in binsizes["collections"]["regions"]:
                    for side in sides:
                        run(
                            ("enrichment", region_collection.name) + where + (binsize, side),
                            pipeline_steps.enrichment_pipeline_step,
                            region_collection.id,
                            intervals.id,
                            binsize,
                            region_side=side,
                        )
                for binsize in binsizes["collections"]["1d-features"]:
                    for side in sides:
                        for bigwig in bigwigs:
                            exists = IndividualIntervalData.query.filter(
                                (IndividualIntervalData.dataset_id == bigwig.id)
                                & (IndividualIntervalData.intervals_id == intervals.id)
                                & (IndividualIntervalData.binsize == binsize)
                                & (IndividualIntervalData.region_side == side)
                            ).first()
                            if exists is None:
                                run(
                                    ("stackup", bigwig.dataset_name) + where + (binsize, side),
                                    pipeline_steps.stackup_pipeline_step,
                                    bigwig.id,
                                    intervals.id,
                                    binsize,
                                    region_side=side,
                                )
                        run(
                            ("embedding_1d", feature_collection.name) + where + (binsize, side),
                            pipeline_steps.embedding_1d_pipeline_step,
                            feature_collection.id,
                            intervals.id,
                            binsize,
                            region_side=side,
                        )

        names = {dataset.id: dataset.dataset_name for dataset in Dataset.query.all()}
        collection_names = {collection.id: collection.name for collection in Collection.query.all()}
        windows = {intervals.id: (names[intervals.dataset_id], intervals.windowsize) for intervals in Intervals.query.all()}
        tables = {
            "AverageIntervalData": AverageIntervalData,
            "IndividualIntervalData": IndividualIntervalData,
            "AssociationIntervalData": AssociationIntervalData,
            "EmbeddingIntervalData": EmbeddingIntervalData,
        }
        for table_name, table in tables.items():
            for row in table.query.all():
                region_name, window = windows[row.intervals_id]
                if getattr(row, "collection_id", None) is not None:
                    source = collection_names[row.collection_id]
                else:
                    source = names[row.dataset_id]
                parts = [
                    table_name,
                    source,
                    region_name,
                    "variable" if window is None else str(window),
                    str(row.binsize),
                    str(row.value_type),
                    str(row.region_side),
                    str(getattr(row, "normalization", None)),
                    str(getattr(row, "cluster_number", None)),
                ]
                for column in TABLE_FILES[table_name]:
                    path = getattr(row, column, None)
                    if path:
                        results["/".join(parts + [column])] = np.load(path, allow_pickle=False)
        db.session.remove()
        db.drop_all()
    return results
