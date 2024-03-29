"""Test getting genome assemblies."""
import unittest
from unittest.mock import patch
from tests.test_utils.test_helpers import LoginTestCase

# add path to import app
# import sys
# sys.path.append("./")
from app import db
from app.models import Organism, Assembly


class TestGetAssemblies(LoginTestCase):
    """Test getting genome assemblies."""

    def setUp(self):
        super().setUp()
        # add organisms
        self.human = Organism(id=1, name="Human")
        self.drosophila = Organism(id=2, name="Drosophila")
        # add assemblies
        self.hg19 = Assembly(name="hg19", organism_id=1)
        self.hg38 = Assembly(name="hg38", organism_id=1)
        self.dm1 = Assembly(name="dm1", organism_id=2)
        self.dm2 = Assembly(name="dm2", organism_id=2)

    def test_no_auth(self):
        """No authentication provided, response should be 401"""
        response = self.client.get("/api/assemblies/", content_type="application/json")
        self.assertEqual(response.status_code, 401)

    def test_no_auth_required_showcase(self):
        """No authentication required showcase user"""
        # protected route
        app_config = self.app.config.copy()
        app_config["SHOWCASE"] = True
        with patch("app.api.authentication.current_app.config") as mock_config:
            mock_config.__getitem__.side_effect = app_config.__getitem__
            # dispatch call
            response = self.client.get(
                "/api/assemblies/", content_type="application/json"
            )
            self.assertEqual(response.status_code, 200)

    def test_right_assemblies_returned(self):
        """test whether correct assebmlies are returned."""
        # add things
        db.session.add_all(
            [self.human, self.drosophila, self.hg19, self.hg38, self.dm1, self.dm2]
        )
        db.session.commit()
        # authenticate
        token = self.add_and_authenticate("test", "asdf")
        # create token header
        token_headers = self.get_token_header(token)
        # get datasets
        response = self.client.get(
            "/api/assemblies/", headers=token_headers, content_type="application/json"
        )
        # check response
        self.assertEqual(response.status_code, 200)
        expected = {
            "Human": [
                {"id": 1, "name": "hg19", "user_id": None, "dependent_datasets": 0},
                {"id": 2, "name": "hg38", "user_id": None, "dependent_datasets": 0},
            ],
            "Drosophila": [
                {"id": 3, "name": "dm1", "user_id": None, "dependent_datasets": 0},
                {"id": 4, "name": "dm2", "user_id": None, "dependent_datasets": 0},
            ],
        }
        self.assertEqual(expected, response.json)


if __name__ == "__main__":
    res = unittest.main(verbosity=3, exit=False)
