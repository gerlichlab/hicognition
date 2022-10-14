import unittest
from app.utils import convert_format

class TestFormatDict(unittest.TestCase):
    
    def setUp(self):
        self.formats = ['camelCase', 'snake_case', 'human']
        self.data = {
            "human": [{
                "Nested Dict": {
                    "And A String": "this is a value",
                    "And A List": ["this", "is", 1, "list"]
                },
                "Plus": "a string"},
                {"And": "another string"}
            ],
            "camelCase": [{
                "nestedDict": {
                    "andAString": "this is a value",
                    "andAList": ["this", "is", 1, "list"]
                },
                "plus": "a string"},
                {"and": "another string"}
            ],
            "snake_case": [{
                "nested_dict": {
                    "and_a_string": "this is a value",
                    "and_a_list": ["this", "is", 1, "list"]
                },
                "plus": "a string"},
                {"and": "another string"}
            ]
        }
        return super().setUp()

    def test_format_dict(self):
        for k1 in self.formats:
            for k2 in self.formats:
                with self.subTest(k1=k1, k2=k2):
                    formatted = convert_format(self.data[k1], k2)
                    self.assertEqual(formatted, self.data[k2])