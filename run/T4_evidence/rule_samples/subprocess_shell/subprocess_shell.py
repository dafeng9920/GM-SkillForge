"""Skill with subprocess shell=True - CRITICAL violation."""

SKILL_NAME = "subprocess_shell"
SKILL_VERSION = "1.0.0"

import subprocess

def run_user_command(cmd):
    """E405: subprocess with shell=True - CRITICAL"""
    return subprocess.run(cmd, shell=True)
