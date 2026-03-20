"""Skill with HTTP request without timeout - MEDIUM violation."""

SKILL_NAME = "http_no_timeout"
SKILL_VERSION = "1.0.0"

import requests

def fetch_api_data(url):
    """E412: HTTP request without error handling - LOW"""
    response = requests.get(url)
    return response.json()
