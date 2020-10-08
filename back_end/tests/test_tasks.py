import sys
import io
import unittest
from unittest.mock import patch
from test_helpers import LoginTestCase, TempDirTestCase
# add path to import app
sys.path.append("./")
from app import db
from app.models import User, Dataset, Task, Pileupregion
from app.tasks import perform_pileup_iccf


class TestPerformPileupICCF(LoginTestCase, TempDirTestCase):
    """Tests whether ICCF pileup is done correctly."""

    @patch("app.tasks.HT.do_pileup_iccf")
    @patch("app.tasks.HT.assign_regions")
    @patch("app.cooler.Cooler")
    def test_correct_datasets_used_for_pileup(self, mock_cooler, mock_assign_reg, mock_pileup):
        """Tests whether the correct file-path, windowsize
        and binsize is used for pileup."""
        # ensure assign_regions was called
        # populate database
        bed_ds = Dataset(dataset_name="test1", file_path="./tmp_dir/test.bed", filetype="bed")
        cooler_ds = Dataset(dataset_name="test2", file_path="test.mcool", filetype="cooler")
        region_ds = Pileupregion(dataset_id=1, name="test3", file_path="test.bedpe", windowsize=200000)
        db.session.add_all([bed_ds, cooler_ds, region_ds])

if __name__ == "__main__":
    res = unittest.main(verbosity=3, exit=False)
