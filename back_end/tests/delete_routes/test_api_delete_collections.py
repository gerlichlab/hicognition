"""Tests for deletion of collections."""
import os
import unittest
from hicognition.test_helpers import LoginTestCase, TempDirTestCase
# add path to import app
# import sys
# sys.path.append("./")
from app import db
from app.models import Collection, AssociationIntervalData


class TestDeleteCollection(LoginTestCase, TempDirTestCase):
    """Tests for deletion of collections."""

    def _create_empty_file_in_tempdir(self, file_name):
        file_path = os.path.join(self.TEMP_PATH, file_name)
        open(file_path, "w").close()
        return file_path

    def setUp(self):
        super().setUp()
        # define datasets
        self.collection_user_1 = Collection(id=1, user_id=1, name="test")
        self.collection_user_1_2 = Collection(id=2, user_id=1, name="test2")
        self.collection_user_2 = Collection(id=3, user_id=2, name="test3")
        # define associated data
        self.assoc_path = self._create_empty_file_in_tempdir("test.npy")
        self.assocData = AssociationIntervalData(
            file_path=self.assoc_path, collection_id=self.collection_user_1.id
        )

    def test_no_auth(self):
        """No authentication provided, response should be 401"""
        # protected route
        response = self.client.delete(
            "/api/collections/1/", content_type="application/json"
        )
        self.assertEqual(response.status_code, 401)

    def test_delete_wo_collection_id(self):
        """Should return 405 since delete is not allowed for /api/collections"""
        response = self.client.delete(
            "/api/collections/", content_type="application/json"
        )
        self.assertEqual(response.status_code, 405)

    def test_delete_collection_does_not_exist(self):
        """test deletion of collection that does not exist."""
        token = self.add_and_authenticate("test", "asdf")
        # create token_headers
        token_headers = self.get_token_header(token)
        # by user id 2
        response = self.client.delete(
            "/api/collections/500/",
            headers=token_headers,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 404)

    def test_delete_collection_wo_permission(self):
        """Should return 403 since collection is not owned."""
        token = self.add_and_authenticate("test", "asdf")
        # create token_headers
        token_headers = self.get_token_header(token)
        # add session
        db.session.add(self.collection_user_2)
        db.session.commit()
        # by user id 2
        response = self.client.delete(
            "/api/collections/3/",
            headers=token_headers,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 403)

    def test_delete_owned_collection(self):
        """Check whether owned dataset is deleted correctly."""
        token = self.add_and_authenticate("test", "asdf")
        # create token_headers
        token_headers = self.get_token_header(token)
        # add session
        db.session.add_all([self.collection_user_1, self.collection_user_1_2])
        db.session.commit()
        # by user id 2
        response = self.client.delete(
            "/api/collections/1/",
            headers=token_headers,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(Collection.query.all()), 1)
        self.assertEqual(Collection.query.first(), self.collection_user_1_2)

    def test_delete_collection_deletes_associated_entries(self):
        """Tests whether deletion of collection causes deletion of associated entries."""
        token = self.add_and_authenticate("test", "asdf")
        # create token_headers
        token_headers = self.get_token_header(token)
        # add session
        db.session.add_all([self.collection_user_1, self.assocData])
        db.session.commit()
        # make call
        response = self.client.delete(
            "/api/collections/1/",
            headers=token_headers,
            content_type="application/json",
        )
        # check whether associated data was deleted
        self.assertEqual(len(Collection.query.all()), 0)
        self.assertEqual(len(AssociationIntervalData.query.all()), 0)
        # check wehtehr tempdir is empty
        self.assertEqual(len(os.listdir(self.TEMP_PATH)), 0)


if __name__ == "__main__":
    res = unittest.main(verbosity=3, exit=False)
