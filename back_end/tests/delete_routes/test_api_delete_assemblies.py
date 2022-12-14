"""Tests for deletion of assemblies."""
import os
import unittest
from tests.test_utils.test_helpers import LoginTestCase, TempDirTestCase

# add path to import app
# import sys
# sys.path.append("./")
from app import db
from app.models import (
    Dataset,
    Assembly,
)


class TestDeleteAssembly(LoginTestCase, TempDirTestCase):
    """Tests for deletion of assemblies."""

    def _create_empty_file_in_tempdir(self, file_name):
        file_path = os.path.join(self.TEMP_PATH, file_name)
        open(file_path, "w").close()
        return file_path

    def setUp(self):
        super().setUp()
        # define Assemblies
        self.assembly_user_1 = Assembly(
            id=1,
            user_id=1,
            name="test",
            chrom_sizes=self._create_empty_file_in_tempdir("hg19.txt"),
            chrom_arms=self._create_empty_file_in_tempdir("arms.txt"),
        )
        self.assembly_user_1_w_datasets = Assembly(
            id=2,
            user_id=1,
            name="test",
            chrom_sizes=self._create_empty_file_in_tempdir("hg1.txt"),
            chrom_arms=self._create_empty_file_in_tempdir("arms2.txt"),
        )
        self.assembly_user_2 = Assembly(
            id=3,
            user_id=2,
            name="test2",
            chrom_sizes=self._create_empty_file_in_tempdir("hg38.txt"),
            chrom_arms=self._create_empty_file_in_tempdir("arms38.txt"),
        )
        # define associted datasets
        self.dataset1 = Dataset(id=1, assembly=2)
        # aut
        token = self.add_and_authenticate("test", "asdf")
        # create token_headers
        self.token_headers = self.get_token_header(token)

    def test_no_auth(self):
        """No authentication provided, response should be 401"""
        # protected route
        response = self.client.delete(
            "/api/assemblies/1/", content_type="application/json"
        )
        self.assertEqual(response.status_code, 401)

    def test_no_confirmation(self):
        # aut
        token = self.add_and_authenticate("test2", "asdf", confirmed=False)
        # create token_headers
        self.token_headers = self.get_token_header(token)
        response = self.client.delete(
            "/api/assemblies/500/",
            headers=self.token_headers,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.get_json()['message'], 'Unconfirmed')

    def test_delete_wo_id(self):
        """Should return 405 since delete is not allowed for /api/assemblies"""
        response = self.client.delete(
            "/api/assemblies/", content_type="application/json"
        )
        self.assertEqual(response.status_code, 405)

    def test_delete_assembly_does_not_exist(self):
        """test deletion of collection that does not exist."""
        # by user id 2
        response = self.client.delete(
            "/api/assemblies/500/",
            headers=self.token_headers,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 404)

    def test_delete_assembly_wo_permission(self):
        """Should return 403 since assembly is not owned."""
        # add session
        db.session.add(self.assembly_user_2)
        db.session.commit()
        # by user id 2
        response = self.client.delete(
            "/api/assemblies/3/",
            headers=self.token_headers,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 403)

    def test_delete_owned_assembly(self):
        """Check whether owned assembly is deleted correctly."""
        # add session
        db.session.add_all([self.assembly_user_1])
        db.session.commit()
        # by user id 2
        response = self.client.delete(
            "/api/assemblies/1/",
            headers=self.token_headers,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(Assembly.query.all()), 0)
        self.assertEqual(len(os.listdir(self.TEMP_PATH)), 4)

    def test_delete_assembly_w_associated_datasets_forbidden(self):
        """Tests whether deletion of assembly is forbidden if there are associated datasets."""
        # add session
        db.session.add_all([self.assembly_user_1_w_datasets, self.dataset1])
        db.session.commit()
        # make call
        response = self.client.delete(
            "/api/assemblies/2/",
            headers=self.token_headers,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 403)


if __name__ == "__main__":
    res = unittest.main(verbosity=3, exit=False)
