"""Test getting genome assemblies."""
import unittest
from unittest.mock import MagicMock, patch
from tests.test_utils.test_helpers import LoginTestCase



class TestGetFiletypes(LoginTestCase):
    """Test getting filetypes."""

    def setUp(self):
        super().setUp()

        self.token = self.add_and_authenticate("test", "asdf")
        self.token_headers = self.get_token_header(self.token)
        
        self.data = {
            "test1": {
                "Nested Dict": {
                    "And A String": "this is a value",
                    "And A List": ["this", "is", 1, "list"]
                },
                "Plus": "a string"
            },
        }

    def test_get_config(self):
        from flask.globals import current_app
        current_app.config['FILETYPES'] = self.data['test1']
        response = self.client.get(
            "/api/filetypes/", headers=self.token_headers, content_type="application/json"
        )
        # check response
        self.assertEqual(response.json, self.data['test1'])


if __name__ == "__main__":
    res = unittest.main(verbosity=3, exit=False)
