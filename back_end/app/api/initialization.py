"""Helpers to populate database"""
from ..models import Organism, Assembly, Dataset, dataset_preprocessing_table, collections_preprocessing_table
from . import api
from flask.globals import current_app
from .. import db


def create_hg19():
    """creates entry for standard hg19 assembly and
    associates it with all available datasets."""
    if Assembly.query.first() is None:
        org = Organism(name="Human")
        db.session.add(org)
        db.session.commit()
        assembly = Assembly(
            name="hg19",
            chrom_sizes=current_app.config["CHROM_SIZES"],
            chrom_arms=current_app.config["CHROM_ARMS"],
            organism_id=org.id,
        )
        db.session.add_all([org, assembly])
        db.session.commit()
        # add assembly id to all datasets
        for dataset in Dataset.query.all():
            dataset.assembly = assembly.id
        db.session.commit()

def drop_preprocessing_tables():
    """deletes entries in preprocessing tables."""
    stmt = dataset_preprocessing_table.delete()
    db.session.execute(stmt)
    stmt = collections_preprocessing_table.delete()
    db.session.execute(stmt)
    db.session.commit()


@api.before_app_first_request
def init_database():
    """Populate database"""
    if not current_app.config["TESTING"]:
        create_hg19()
        drop_preprocessing_tables()
