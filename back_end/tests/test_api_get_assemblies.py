import unittest
from test_helpers import LoginTestCase

# add path to import app
import sys

sys.path.append("./")
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
        # protected route
        response = self.client.get("/api/assemblies/", content_type="application/json")
        self.assertEqual(response.status_code, 401)

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
            "/api/assemblies/",
            headers=token_headers,
            content_type="application/json",
        )
        # check response
        self.assertEqual(response.status_code, 200)
        expected = {
            "Human": [{"id": 1, "name": "hg19"}, {"id": 2, "name": "hg38"}],
            "Drosophila": [{"id": 3, "name": "dm1"}, {"id": 4, "name": "dm2"}],
        }
        self.assertEqual(expected, response.json)


if __name__ == "__main__":
    res = unittest.main(verbosity=3, exit=False)
