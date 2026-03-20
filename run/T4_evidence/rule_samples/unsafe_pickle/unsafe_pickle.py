"""Skill with unsafe pickle - HIGH violation."""

SKILL_NAME = "unsafe_pickle"
SKILL_VERSION = "1.0.0"

import pickle

def load_data(data_string):
    """E422: unsafe pickle deserialization - HIGH"""
    return pickle.loads(data_string)
