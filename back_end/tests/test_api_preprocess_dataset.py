import sys
import io
import unittest
from unittest.mock import patch
from test_helpers import LoginTestCase, TempDirTestCase

# add path to import app
sys.path.append("./")
from app.models import Dataset


class TestPreprocessDataset(LoginTestCase, TempDirTestCase):
    """Tests correct launching of
    pipelines after posting parameters to /preprocess route.
    Inherits both from LoginTest and TempDirTestCase
    to be able to login and make temporary directory"""

    @patch("app.models.User.launch_task")
    def test_pipeline_pileup_is_called_correctly(self, mock_launch):
        """Tests whether cooler pipeline to do pileups is called correctly."""
        # authenticate
        token = self.add_and_authenticate("test", "asdf")
        token_headers = self.get_token_header(token)
        data = {
            "dataset_id": "1",
            "pileup_region_ids": "[1, 2, 3, 4]",
            "binsizes": "[10000, 20000, 40000]",
        }
        # dispatch post request
        response = self.client.post(
            "/api/preprocess/",
            data=data,
            headers=token_headers,
            content_type="multipart/form-data",
        )
        self.assertEqual(response.status_code, 200)
        # check whether pipeline has been called with right parameters
        mock_launch.assert_called_with(
            "pipeline_pileup",
            "run pileup pipeline",
            1,
            [10000, 20000, 40000],
            [1, 2, 3, 4],
        )

