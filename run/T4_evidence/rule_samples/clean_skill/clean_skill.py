"""Clean skill following best practices."""

SKILL_NAME = "clean_skill"
SKILL_VERSION = "1.0.0"

def process_data(data):
    """Process data with validation"""
    if not isinstance(data, dict):
        raise ValueError("Invalid input")
    return {"result": data.get("value", 0) * 2}
