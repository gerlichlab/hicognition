"""Helpers to populate database"""
from ..models import Organism, Assembly
from . import api
from flask.globals import current_app
from .. import db


def create_hg19():
    """creates entry for standard hg19 assembly."""
    if Assembly.query.first() is None:
        # load chromosome sizes
        chromsizes = open(current_app.config["CHROM_SIZES"], "r").read()
        org = Organism(name="Human")
        assembly = Assembly(name="hg19", chrom_sizes=chromsizes, organism_id=org.id)
        db.session.add_all([org, assembly])
        db.session.commit()


@api.before_app_first_request
def init_database():
    """Populate database"""
    create_hg19()
