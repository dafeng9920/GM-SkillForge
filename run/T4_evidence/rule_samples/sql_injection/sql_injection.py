"""Skill with SQL injection risk - CRITICAL violation."""

SKILL_NAME = "sql_injection"
SKILL_VERSION = "1.0.0"

def get_user_data(user_id):
    """E413: SQL injection via string formatting - CRITICAL"""
    return execute("SELECT * FROM users WHERE id=%s" % user_id)
