"""
LLM Module for SkillForge L4 API.

Provides a unified LLM adapter for generating 10-dimensional cognition assessments.
"""
from .client import generate_10d, LLMConfigError, LLMCallError

__all__ = ["generate_10d", "LLMConfigError", "LLMCallError"]
