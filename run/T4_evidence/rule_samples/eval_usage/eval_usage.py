"""Skill with eval usage - CRITICAL violation."""

SKILL_NAME = "eval_usage"
SKILL_VERSION = "1.0.0"

def execute_untrusted_code(user_input):
    """E421: eval without sanitization - CRITICAL"""
    return eval(user_input)
