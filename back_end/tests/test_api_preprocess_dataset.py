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