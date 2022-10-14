"""Test getting genome assemblies."""
import unittest
from unittest.mock import MagicMock, patch
from hicognition.test_helpers import LoginTestCase



class TestGetFiletypes(LoginTestCase):
    """Test getting filetypes."""

    def setUp(self):
        super().setUp()

        self.token = self.add_and_authenticate("test", "asdf")
        self.token_headers = self.get_token_header(self.token)
        
        self.data = {
            "human": {
                "Nested Dict": {
                    "And A String": "this is a value",
                    "And A List": ["this", "is", 1, "list"]
                },
                "Plus": "a string"
            },
            "camelCase": {
                "nestedDict": {
                    "andAString": "this is a value",
                    "andAList": ["this", "is", 1, "list"]
                },
                "plus": "a string"
            },
            "snake_case": {
                "nested_dict": {
                    "and_a_string": "this is a value",
                    "and_a_list": ["this", "is", 1, "list"]
                },
                "plus": "a string"
            }
        }

    def test_get_config(self):
        from flask.globals import current_app
        current_app.config['FILETYPES'] = self.data['human']
        response = self.client.get(
            "/api/filetypes/camelCase/", headers=self.token_headers, content_type="application/json"
        )
        # check response
        self.assertEqual(response.status_code, 200)
        expected = self.data['camelCase']
        self.assertEqual(response.json, expected)


if __name__ == "__main__":
    res = unittest.main(verbosity=3, exit=False)
