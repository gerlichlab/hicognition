"""Module with the tests for the stackup creation realted tasks."""
import unittest
from unittest.mock import patch
import pandas as pd
import numpy as np
from hicognition.test_helpers import LoginTestCase, TempDirTestCase
from hicognition import interval_operations

# add path to import app
# import sys
# sys.path.append("./")
from app import db
from app.models import Dataset, Intervals, Assembly, Task
from app.tasks import pipeline_stackup
from app.pipeline_steps import stackup_pipeline_step

from app.pipeline_worker_functions import (
    _do_stackup_fixed_size,
    _do_stackup_variable_size,
)


class TestDownloadDatasetFile(LoginTestCase, TempDirTestCase):
    """Tests for pipeline stackup"""

    def setUp(self):
        super().setUp()
        # add assembly
        self.hg19 = Assembly(
            id=1,
            name="hg19",
            chrom_sizes=self.app.config["CHROM_SIZES"],
            chrom_arms=self.app.config["CHROM_ARMS"],
        )
        db.session.add(self.hg19)
        db.session.commit()
        # maker users
        # user1
        # user2
        
        # make repos
        # repo1: empty repo (takes urls)
        # repo2: 4dn repo (takes url/id)
        
        # make repo_user_credentials
        # user1_4dn
        # user2_4dn (wrong credentials)
        # user1_none
        
        # make datasets for these test cases:
        
        # dataset w/o authentication needed 
        # dataset w/ authentication needed from 4dn
        # dataset w/ authentication needed from 4dn, auth fail
        # dataset w/ malformed bed file
        # dataset w/ malformed mcooler file
        # dataset w/ malformed cooler file
        # dataset w/ malformed bigwig file
        # dataset w/ wrong url/id
        # dataset w/ no internet connection (e.g. if server is in intranet)
        
        


if __name__ == "__main__":
    res = unittest.main(verbosity=3, exit=False)
