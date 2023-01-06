import os
import unittest
from tests.test_utils.test_helpers import LoginTestCase

class TestUnconfirmedUser(LoginTestCase):
    """Tests to check whehther unconfirmed user
    cannot access most api routes"""

    def setUp(self):
        super().setUp()
        token = self.add_and_authenticate("test2", "asdf", confirmed=False)
        self.unconfirmed_token = self.get_token_header(token)

    def _test_route(self, params):
        # get client method
        method_call = getattr(self.client, params['method'])
        response = method_call(
            params['route'],
            headers=self.unconfirmed_token
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.get_json()['message'], 'Unconfirmed')

    def test_unconfirmed_user_cannot_access_api(self):
        test_cases = {
            'delete_assemblies': {
                "method": 'delete',
                "route": '/api/assemblies/500/'
            },
            'delete_collections': {
                "method": 'delete',
                "route": '/api/collections/500/'
            },
            'delete_datasets': {
                "method": 'delete',
                "route": '/api/datasets/500/' 
            },
            'delete_sessions': {
                "method": 'delete',
                "route": '/api/sessions/500/'  
            },
            'assemblies': {
                "method": "get",
                "route": "/api/assemblies/"
            },
            "association_data": {
                "method": "get",
                "route": "/api/associationIntervalData/1/"
            },
            "average_data": {
                "method": "get",
                "route": "/api/averageIntervalData/500/"
            },
            "collections": {
                "method": "get",
                "route": "/api/collections/"
            },
            "datasets": {
                "method": "get",
                "route": "/api/datasets/"
            },
            "embedding_interval_data": {
                "method": "get",
                "route": "/api/embeddingIntervalData/500/0/"
            },
            "encode_meta_data": {
                "method": "get",
                "route": "/api/ENCODE/nonexistantrepo/sampleid/"
            },
            "intervals": {
                "method": "get",
                "route": "/api/intervals/"
            },
            "processed_dataset_map": {
                "method": "get",
                "route": "/api/datasets/1/processedDataMap/"
            },
            "session_token": {
                "method": "get",
                "route": "/api/sessions/500/sessionToken/"
            },
            "sessions": {
                "method": "get",
                "route": "/api/sessions/"
            },
            "stackups": {
                "method": "get",
                "route": "/api/individualIntervalData/1/"
            },
            "add_assemblies": {
                "method": "post",
                "route": "/api/assemblies/"
            },
            "add_collections": {
                "method": "post",
                "route": "/api/collections/"
            },
            "add_datasets_encode": {
                "method": "post",
                "route": "/api/datasets/encode/"
            },
            "add_dataset_url": {
                "method": "post",
                "route": "/api/datasets/URL/"
            },
            "add_datasets": {
                "method": "post",
                "route": "/api/datasets/"
            },
            "add_metadata": {
                "method": "post",
                "route": "/api/bedFileMetadata/"
            },
            "add_session": {
                "method": "post",
                "route": "/api/sessions/"
            },
            "create_regions_from_embedding": {
                "method": "post",
                "route": "/api/embeddingIntervalData/500/createRegion/"
            },
            "modify_dataset": {
                "method": "put",
                "route": "/api/datasets/500/"
            },
            "preprocess_collection": {
                "method": "post",
                "route": "/api/preprocess/collections/"
            },
            "preprocess_dataset": {
                "method": "post",
                "route": "/api/preprocess/datasets/"
            }
        }
        for key, params in test_cases.items():
            with self.subTest(key):
                self._test_route(params)
