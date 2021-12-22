import sys
import os
import unittest
from hicognition.test_helpers import LoginTestCase, TempDirTestCase

# add path to import app
sys.path.append("./")
from app import db
from app.models import Organism, Assembly


class TestAddAssembly(LoginTestCase, TempDirTestCase):
    """Tests whether adding a genome assembly works"""

    def setUp(self):
        super().setUp()
        # authenticate
        token = self.add_and_authenticate("test", "asdf")
        # create token_header
        self.token_headers = self.get_token_header(token)
        self.token_headers["Content-Type"] = "multipart/form-data"
        # create datasets
        self.human = Organism(id=1, name="Human")
        db.session.add(self.human)
        db.session.commit()

    def test_badform_no_organism_id(self):
        """Tests whether form without file is rejected"""
        # add datasets
        db.session.add(self.human)
        db.session.commit()
        # construct form data
        data = {
            "name": "test",
            "chromSizes": (
                open("tests/testfiles/hg19.chrom.sizes", "rb"),
                "hg19.chrom.sizes",
            ),
            "chromArms": (open("tests/testfiles/arms.hg19", "rb"), "arms.hg19"),
        }
        # dispatch post request
        response = self.client.post(
            "/api/assemblies/",
            data=data,
            headers=self.token_headers,
            content_type="multipart/form-data",
        )
        self.assertEqual(response.status_code, 400)

    def test_badform_no_name(self):
        """Tests whether form without file is rejected"""
        # add datasets
        db.session.add(self.human)
        db.session.commit()
        # construct form data
        data = {
            "organism": "1",
            "chromSizes": (
                open("tests/testfiles/hg19.chrom.sizes", "rb"),
                "hg19.chrom.sizes",
            ),
            "chromArms": (open("tests/testfiles/arms.hg19", "rb"), "arms.hg19"),
        }
        # dispatch post request
        response = self.client.post(
            "/api/assemblies/",
            data=data,
            headers=self.token_headers,
            content_type="multipart/form-data",
        )
        self.assertEqual(response.status_code, 400)

    def test_badform_organism_does_not_exist(self):
        """Tests whether form without file is rejected"""
        # add datasets
        db.session.add(self.human)
        db.session.commit()
        # construct form data
        data = {
            "organism": "5",
            "name": "hg19",
            "chromSizes": (
                open("tests/testfiles/hg19.chrom.sizes", "rb"),
                "hg19.chrom.sizes",
            ),
            "chromArms": (open("tests/testfiles/arms.hg19", "rb"), "arms.hg19"),
        }
        # dispatch post request
        response = self.client.post(
            "/api/assemblies/",
            data=data,
            headers=self.token_headers,
            content_type="multipart/form-data",
        )
        self.assertEqual(response.status_code, 400)

    def test_badform_no_chrom_sizes(self):
        """Tests whether form without file is rejected"""
        # add datasets
        db.session.add(self.human)
        db.session.commit()
        # construct form data
        data = {
            "organism": "1",
            "name": "hg19",
            "chromArms": (open("tests/testfiles/arms.hg19", "rb"), "arms.hg19"),
        }
        # dispatch post request
        response = self.client.post(
            "/api/assemblies/",
            data=data,
            headers=self.token_headers,
            content_type="multipart/form-data",
        )
        self.assertEqual(response.status_code, 400)

    def test_badform_no_chrom_arms(self):
        """Tests whether form without file is rejected"""
        # add datasets
        db.session.add(self.human)
        db.session.commit()
        # construct form data
        data = {
            "organism": "1",
            "name": "hg19",
            "chromSizes": (
                open("tests/testfiles/hg19.chrom.sizes", "rb"),
                "hg19.chrom.sizes",
            ),
        }
        # dispatch post request
        response = self.client.post(
            "/api/assemblies/",
            data=data,
            headers=self.token_headers,
            content_type="multipart/form-data",
        )
        self.assertEqual(response.status_code, 400)

    def test_badform_wrong_format(self):
        """Tests whether form without file is rejected"""
        # add datasets
        db.session.add(self.human)
        db.session.commit()
        # construct form data
        data = {
            "organism": "1",
            "name": "hg19",
            "chromSizes": (
                open("tests/testfiles/hg19.chrom.sizes", "rb"),
                "hg19.chrom.sizes",
            ),
        }
        # dispatch post request
        response = self.client.post(
            "/api/assemblies/",
            data=data,
            headers=self.token_headers,
            content_type="multipart/form-data",
        )
        self.assertEqual(response.status_code, 400)

    def test_good_form_added_correctly(self):
        # construct form data
        data = {
            "organism": "1",
            "name": "test",
            "chromSizes": (
                open("tests/testfiles/hg19.chrom.sizes", "rb"),
                "hg19.chrom.sizes",
            ),
            "chromArms": (open("tests/testfiles/arms.hg19", "rb"), "arms.hg19"),
        }
        # dispatch post request
        response = self.client.post(
            "/api/assemblies/",
            data=data,
            headers=self.token_headers,
            content_type="multipart/form-data",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(1, len(Assembly.query.all()))
        assembly = Assembly.query.first()
        self.assertEqual(
            assembly.chrom_sizes,
            os.path.join(self.TEMP_PATH, f"{assembly.id}_hg19.chrom.sizes"),
        )
        self.assertEqual(
            assembly.chrom_arms,
            os.path.join(self.TEMP_PATH, f"{assembly.id}_arms.hg19"),
        )
        self.assertEqual(assembly.name, "test")
        self.assertEqual(Organism.query.first().assemblies[0], assembly)


if __name__ == "__main__":
    res = unittest.main(verbosity=3, exit=False)
