"""
Sample demonstrating E503: High-privilege call without boundary.

This skill performs high-privilege operations without rate limiting or resource caps.
Expected Finding: E503_HIGH_PRIV_WITHOUT_BOUNDARY (CRITICAL)
"""
import os
import subprocess
import sqlite3


def batch_delete_files(file_paths: list[str]) -> int:
    """
    Delete multiple files.

    E503 Finding: No limit on number of files deleted.
    Risk: Could delete unlimited files, causing resource exhaustion.
    """
    # Missing: max_count limit
    # Missing: rate_limit check
    # Missing: resource_quota check

    deleted_count = 0
    for file_path in file_paths:
        # E503: os.remove without boundary limit
        os.remove(file_path)
        deleted_count += 1

    return deleted_count


def bulk_database_insert(records: list[dict]) -> int:
    """
    Insert records into database.

    E503 Finding: No limit on number of records inserted.
    Risk: Could write unlimited records, causing disk exhaustion.
    """
    # Missing: max_records limit
    # Missing: check_quota before insert

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    inserted = 0
    for record in records:
        # E503: db.execute without boundary
        cursor.execute("INSERT INTO data VALUES (?)", (record,))
        inserted += 1

    conn.commit()
    conn.close()
    return inserted


def run_batch_commands(commands: list[str]) -> list[str]:
    """
    Execute multiple system commands.

    E503 Finding: No limit on command execution.
    Risk: Could execute unlimited commands.
    """
    # Missing: semaphore or circuit_breaker
    # Missing: throttle mechanism

    results = []
    for cmd in commands:
        # E503: subprocess.run without boundary
        result = subprocess.run(cmd, shell=True, capture_output=True)
        results.append(result.stdout.decode())

    return results


if __name__ == "__main__":
    # Risk: These operations have no upper bound
    files_to_delete = [f"/tmp/file{i}.txt" for i in range(1000000)]
    batch_delete_files(files_to_delete)
