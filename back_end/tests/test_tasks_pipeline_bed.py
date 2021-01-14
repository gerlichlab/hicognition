import sys
import io
import unittest
from unittest.mock import patch
from test_helpers import LoginTestCase, TempDirTestCase

# add path to import app
sys.path.append("./")
from app import db
from app.models import Dataset
from app.tasks import pipeline_bed, bed_preprocess_pipeline_step


class TestPipelineBed(LoginTestCase, TempDirTestCase):
    """Tests whether pipelin_bed task calls
    the pipeline steps correctly"""

    @patch("app.tasks.bedpe_preprocess_pipeline_step")
    @patch("app.tasks.io_helpers.convert_bed_to_bedpe")
    @patch("app.tasks.io_helpers.sort_bed")
    @patch("app.tasks._set_task_progress")
    @patch("app.tasks.bed_preprocess_pipeline_step")
    def test_helper_calls_dispatched_correctly(
        self,
        mock_bed_pipeline_step,
        mock_set_progress,
        mock_sort_bed,
        mock_convert_bed,
        mock_bedpe_preprocess,
    ):
        """Tests whether the functions that execute the different pipeline steps are called
        correctly."""
        # authenticate
        token = self.add_and_authenticate("test", "asdf")
        # create token_header
        token_headers = self.get_token_header(token)
        # add content-type
        token_headers["Content-Type"] = "multipart/form-data"
        # add dataset
        dataset = Dataset(
            dataset_name="test3",
            file_path="/test/path/test3.bed",
            higlass_uuid="fdsa8765",
            filetype="bedfile",
            processing_state="finished",
            user_id=1,
        )
        db.session.add(dataset)
        db.session.commit()
        # launch task
        pipeline_bed(1)
        # check whether bed_preprocess was called correctly
        mock_bed_pipeline_step.assert_called_with(1)
        # check whether sort_bed was called correctly
        mock_sort_bed.assert_called_with(
            *[
                "/test/path/test3.bed",
                "/test/path/test3_sorted.bed",
                self.app.config["CHROM_SIZES"],
            ]
        )
        # check whether convert_bed_to_bedpe and bedpe_preprocess_pipline_step was called correctly
        for window in self.app.config["WINDOW_SIZES"]:
            target_file = "/test/path/test3_sorted.bed" + f".{window}" + ".bedpe"
            mock_convert_bed.assert_any_call(
                *["/test/path/test3_sorted.bed", target_file, window]
            )
            mock_bedpe_preprocess.assert_any_call(*[target_file, 1, window])
        # check whether set_progress was called with 100 last
        mock_set_progress.assert_called_with(100)

    @patch("app.tasks.higlass_interface.add_tileset")
    @patch("app.tasks.higlass_interface.preprocess_dataset")
    def test_bed_preprocess_pipline_step(
        self, mock_preprocess_higlass, mock_add_tileset
    ):
        """Test whether components of bed_preprocess_pipline_step are called correctly."""
        mock_preprocess_higlass.return_value = 0
        mock_add_tileset.return_value = {"uuid": "higlass_uuid"}
        # authenticate
        token = self.add_and_authenticate("test", "asdf")
        # create token_header
        token_headers = self.get_token_header(token)
        # add content-type
        token_headers["Content-Type"] = "multipart/form-data"
        # add dataset
        dataset = Dataset(
            dataset_name="test3",
            file_path="/test/path/test3.bed",
            higlass_uuid="fdsa8765",
            filetype="bedfile",
            processing_state="finished",
            user_id=1,
        )
        db.session.add(dataset)
        db.session.commit()
        # call function
        bed_preprocess_pipeline_step(1)
        # check whether preprocess dataset was called correctly
        mock_preprocess_higlass.assert_called_with(
            *[
                "bedfile",
                self.app.config["CHROM_SIZES"],
                "/test/path/test3.bed",
                "/test/path/test3.bed.beddb",
            ]
        )
        # check whether add tileset was called correctly
        credentials = {
            "user": self.app.config["HIGLASS_USER"],
            "password": self.app.config["HIGLASS_PWD"],
        }
        mock_add_tileset.assert_called_with(
            *[
                "bedfile",
                "/test/path/test3.bed.beddb",
                self.app.config["HIGLASS_API"],
                credentials,
                "test3",
            ]
        )
        # check whether uuid was added to bedfile
        check_dataset = Dataset.query.get(1)
        self.assertEqual(check_dataset.higlass_uuid, "higlass_uuid")


if __name__ == "__main__":
    res = unittest.main(verbosity=3, exit=False)
