"""Collection of data structures"""
from collections import defaultdict
from collections.abc import Iterable
import logging


def recDict():
    """Recursive defaultdict that allows deep
    assignment. recDict[0][1][2] will
    create all intermediate dictionaries."""
    return defaultdict(recDict)

# class DeepUpdateDict(defaultdict):
#     """Dictionary with update overwritten.
#     Updates also nested dicts and sets, and lists.
#     """
#     def update_json(self, json):
#         self.update(dict.from_json(json))
    
#     def update(self, dictionary):
#         for key, value in dictionary.items():
#             if isinstance(value, dict) and not isinstance(value, DeepUpdateDict):
#                 value = DeepUpdateDict(value)
            
            
#             if key not in self or not isinstance(value, dict) or not isinstance(value, set):
#                 self[key] = value
#             elif isinstance(value, dict) and isinstance(self.get(key), dict):
#                 self[key].update(value)
#             elif isinstance(value, set) and isinstance(self.get(key), set):
#                 self[key].update(value)
#             else:
#                 logging.warning("REACHED END")
    
#     pass
