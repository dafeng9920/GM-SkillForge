"""
T5 Pattern Sample Generator

Generates sample skills demonstrating each of the 4 anti-patterns and a clean sample.

T5 Scope:
- E501: External action without stop rule
- E502: Retry without idempotency protection
- E503: High-privilege call without boundary
- E504: Missing auditable exit
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "skillforge" / "src"))

from skillforge.src.contracts.pattern_matcher import PatternMatcher

# Output directories
SAMPLES_DIR = project_root / "run" / "T5_evidence" / "pattern_samples"
CLEAN_DIR = project_root / "run" / "T5_evidence" / "clean_sample"


def create_e501_sample() -> Path:
    """Create sample demonstrating E501: External action without stop rule."""
    code = '''"""
Sample demonstrating E501: External action without stop rule.

This skill makes HTTP requests without any permission check or authorization.
Expected Finding: E501_EXTERNAL_WITHOUT_STOP_RULE (CRITICAL)
"""
import requests


def fetch_user_data(user_id: str) -> dict:
    """
    Fetch user data from external API.

    E501 Finding: No @require_permission decorator or authorization check
    before making external HTTP request.
    """
    # Missing: @require_permission("api_call")
    # Missing: if not has_permission("api_call"): raise PermissionError

    url = f"https://api.example.com/users/{user_id}"
    response = requests.get(url)  # E501: External action without stop rule
    return response.json()


def sync_with_external_service():
    """
    Sync data with external service.

    E501 Finding: No governance check before network access.
    """
    # Missing: check_authorization("external_sync")

    data = requests.post("https://api.partner.com/sync", json={})
    return data


if __name__ == "__main__":
    # This would execute without any permission check
    result = fetch_user_data("user123")
    print(result)
'''
    sample_dir = SAMPLES_DIR / "e501_external_without_stop_rule"
    sample_dir.mkdir(parents=True, exist_ok=True)

    sample_file = sample_dir / "skill.py"
    sample_file.write_text(code)

    return sample_file


def create_e502_sample() -> Path:
    """Create sample demonstrating E502: Retry without idempotency protection."""
    code = '''"""
Sample demonstrating E502: Retry without idempotency protection.

This skill implements retry logic for financial transfers without idempotency keys.
Expected Finding: E502_RETRY_WITHOUT_IDEMPOTENCY (HIGH)
"""
import requests


def retry_transfer(amount: float, to_account: str) -> dict:
    """
    Execute financial transfer with retry logic.

    E502 Finding: Retry loop without idempotency protection.
    Risk: Network retry could cause duplicate transfers (double-charging).
    """
    # Missing: idempotency_key parameter
    # Missing: deduplication check before retry
    # Missing: transaction_guard

    for attempt in range(3):
        try:
            # E502: No idempotency_key in request
            response = requests.post(
                "https://api.bank.com/transfer",
                json={
                    "amount": amount,
                    "to_account": to_account,
                    # Missing: "idempotency_key": generate_key()
                },
                timeout=30
            )
            if response.status_code == 200:
                return response.json()
        except requests.Timeout:
            continue
        except requests.ConnectionError:
            continue

    return {"error": "Transfer failed after 3 attempts"}


def retry_api_call(endpoint: str, data: dict) -> dict:
    """
    Generic retry wrapper for API calls.

    E502 Finding: No idempotency protection in retry loop.
    """
    for i in range(5):
        try:
            # E502: Each retry could execute operation multiple times
            response = requests.post(endpoint, json=data)
            return response.json()
        except Exception:
            pass

    return {}


if __name__ == "__main__":
    # Risk: Calling this multiple times could transfer money multiple times
    result = retry_transfer(100.0, "ACC-12345")
    print(result)
'''
    sample_dir = SAMPLES_DIR / "e502_retry_without_idempotency"
    sample_dir.mkdir(parents=True, exist_ok=True)

    sample_file = sample_dir / "skill.py"
    sample_file.write_text(code)

    return sample_file


def create_e503_sample() -> Path:
    """Create sample demonstrating E503: High-privilege call without boundary."""
    code = '''"""
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
'''
    sample_dir = SAMPLES_DIR / "e503_high_priv_without_boundary"
    sample_dir.mkdir(parents=True, exist_ok=True)

    sample_file = sample_dir / "skill.py"
    sample_file.write_text(code)

    return sample_file


def create_e504_sample() -> Path:
    """Create sample demonstrating E504: Missing auditable exit."""
    code = '''"""
Sample demonstrating E504: Missing auditable exit.

This skill performs sensitive operations without audit logging.
Expected Finding: E504_MISSING_AUDITABLE_EXIT (HIGH)
"""


def execute_market_order(symbol: str, quantity: int, price: float) -> dict:
    """
    Execute market order.

    E504 Finding: No audit log written after order execution.
    Risk: No traceability for post-mortem analysis or compliance.
    """
    # Execute order
    order_id = broker.place_order(symbol, quantity, price)

    # Missing: write_audit_event("ORDER_EXECUTED", order_id, symbol, quantity)
    # Missing: capture_gate_event(decision="PASS", metadata={...})
    # Missing: save_evidence(...)

    return {
        "order_id": order_id,
        "symbol": symbol,
        "quantity": quantity,
        "status": "FILLED"
    }


def approve_loan_application(application_id: str) -> dict:
    """
    Approve loan application.

    E504 Finding: No audit trail for approval decision.
    Risk: Cannot verify who approved what and when.
    """
    # Process approval
    loan = database.approve_loan(application_id)

    # Missing: log_event("LOAN_APPROVED", application_id, approver=current_user)
    # Missing: emit_audit("APPROVAL", loan_id=application_id)

    return {"status": "approved", "loan_id": application_id}


def delete_user_account(user_id: str) -> dict:
    """
    Delete user account.

    E504 Finding: No audit record for account deletion.
    Risk: Cannot investigate accidental deletions.
    """
    # Delete account
    database.delete_user(user_id)

    # Missing: write_audit("USER_DELETED", user_id=user_id, timestamp=now())

    return {"status": "deleted", "user_id": user_id}


if __name__ == "__main__":
    # Risk: These operations leave no audit trail
    result = execute_market_order("AAPL", 100, 150.0)
    print(result)
'''
    sample_dir = SAMPLES_DIR / "e504_missing_auditable_exit"
    sample_dir.mkdir(parents=True, exist_ok=True)

    sample_file = sample_dir / "skill.py"
    sample_file.write_text(code)

    return sample_file


def create_clean_sample() -> Path:
    """Create clean sample with proper governance controls."""
    code = '''"""
Clean sample demonstrating proper governance controls.

This skill follows best practices with:
- Stop rules before external actions
- Idempotency protection in retry logic
- Boundary limits on high-privilege operations
- Audit logging for sensitive operations

Expected Finding: No E501-E504 patterns detected.
"""
import requests
import os
from typing import Optional


# ============================================================================
# E501 Compliance: External Action WITH Stop Rule
# ============================================================================

@require_permission("api_call")
def fetch_user_data_safe(user_id: str) -> dict:
    """
    Fetch user data with proper authorization check.

    ✓ Has stop rule: @require_permission decorator
    """
    url = f"https://api.example.com/users/{user_id}"
    response = requests.get(url)
    return response.json()


# ============================================================================
# E502 Compliance: Retry WITH Idempotency Protection
# ============================================================================

def process_transfer_with_idempotency(amount: float, to_account: str, idempotency_key: str) -> dict:
    """
    Execute financial transfer with idempotency protection.

    ✓ Has idempotency_key parameter
    ✓ Checks for duplicate execution
    """
    # Check if already processed
    if idempotency_key in seen_keys:
        return get_cached_result(idempotency_key)

    for attempt in range(3):
        try:
            response = requests.post(
                "https://api.bank.com/transfer",
                json={
                    "amount": amount,
                    "to_account": to_account,
                    "idempotency_key": idempotency_key  # ✓ Idempotency
                },
                timeout=30
            )
            if response.status_code == 200:
                seen_keys.add(idempotency_key)  # ✓ Deduplication
                return response.json()
        except requests.Timeout:
            continue

    return {"error": "Transfer failed"}


# ============================================================================
# E503 Compliance: High-Privilege WITH Boundary
# ============================================================================

def remove_files_with_limit(file_paths: list[str], max_count: int = 1000) -> int:
    """
    Delete files with boundary limit.

    ✓ Has max_count parameter
    ✓ Enforces upper bound
    """
    if len(file_paths) > max_count:
        raise ValueError(f"Cannot delete more than {max_count} files")

    deleted_count = 0
    for file_path in file_paths[:max_count]:  # ✓ Boundary enforcement
        os.remove(file_path)
        deleted_count += 1

    return deleted_count


# ============================================================================
# E504 Compliance: Sensitive Operation WITH Audit Exit
# ============================================================================

def handle_market_order(symbol: str, quantity: int, price: float) -> dict:
    """
    Execute market order with audit logging.

    ✓ Writes audit event before returning
    """
    order_id = broker.place_order(symbol, quantity, price)

    # ✓ Audit exit
    emit_audit_log(
        event_type="ORDER_EXECUTED",
        order_id=order_id,
        symbol=symbol,
        quantity=quantity,
        price=price,
        timestamp=now()
    )

    return {
        "order_id": order_id,
        "symbol": symbol,
        "quantity": quantity,
        "status": "FILLED"
    }


# Mock implementations for governance controls
def require_permission(permission: str):
    """Mock permission decorator."""
    def decorator(func):
        return func
    return decorator


seen_keys = set()


def get_cached_result(key: str) -> dict:
    """Mock cache lookup."""
    return {"cached": True}


def emit_audit_log(**kwargs):
    """Mock audit writer."""
    print(f"AUDIT: {kwargs}")


def now():
    """Mock timestamp."""
    return "2026-03-15T00:00:00Z"


if __name__ == "__main__":
    # These operations follow proper governance
    result = handle_market_order("AAPL", 100, 150.0)
    print(result)
'''
    CLEAN_DIR.mkdir(parents=True, exist_ok=True)

    sample_file = CLEAN_DIR / "clean_skill.py"
    sample_file.write_text(code)

    return sample_file


def run_pattern_analysis(sample_path: Path) -> dict:
    """Run pattern matcher on sample and save report."""
    sample_dir = sample_path.parent

    matcher = PatternMatcher()
    result = matcher.match_patterns(sample_dir)

    # Save report
    report_path = sample_dir / "pattern_detection_report.json"
    result.save(report_path)

    print(f"✓ Generated: {report_path}")
    print(f"  Files: {result.files_analyzed}, Matches: {result.total_matches}")

    return result.to_dict()


def generate_summary():
    """Generate summary of all pattern samples."""
    summary = {
        "generated_at": "2026-03-15T00:00:00Z",
        "pattern_set_version": "1.0.0-t5",
        "samples": [
            {
                "pattern_code": "E501_EXTERNAL_WITHOUT_STOP_RULE",
                "name": "External Action Without Stop Rule",
                "directory": "e501_external_without_stop_rule/",
                "expected_findings": ["E501_EXTERNAL_WITHOUT_STOP_RULE"],
                "severity": "CRITICAL"
            },
            {
                "pattern_code": "E502_RETRY_WITHOUT_IDEMPOTENCY",
                "name": "Retry Without Idempotency Protection",
                "directory": "e502_retry_without_idempotency/",
                "expected_findings": ["E502_RETRY_WITHOUT_IDEMPOTENCY"],
                "severity": "HIGH"
            },
            {
                "pattern_code": "E503_HIGH_PRIV_WITHOUT_BOUNDARY",
                "name": "High-Privilege Call Without Boundary",
                "directory": "e503_high_priv_without_boundary/",
                "expected_findings": ["E503_HIGH_PRIV_WITHOUT_BOUNDARY"],
                "severity": "CRITICAL"
            },
            {
                "pattern_code": "E504_MISSING_AUDITABLE_EXIT",
                "name": "Missing Auditable Exit",
                "directory": "e504_missing_auditable_exit/",
                "expected_findings": ["E504_MISSING_AUDITABLE_EXIT"],
                "severity": "HIGH"
            },
            {
                "pattern_code": "CLEAN_SAMPLE",
                "name": "Clean Sample (No Patterns)",
                "directory": "../clean_sample/",
                "expected_findings": [],
                "severity": "N/A"
            }
        ]
    }

    summary_path = project_root / "run" / "T5_evidence" / "pattern_sample_summary.json"
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    print(f"✓ Generated: {summary_path}")
    return summary_path


def main():
    """Generate all pattern samples and run analysis."""
    print("T5 Pattern Sample Generator")
    print("=" * 50)

    # Generate all samples
    print("\n1. Creating pattern samples...")

    e501_path = create_e501_sample()
    print(f"  ✓ E501 sample: {e501_path}")

    e502_path = create_e502_sample()
    print(f"  ✓ E502 sample: {e502_path}")

    e503_path = create_e503_sample()
    print(f"  ✓ E503 sample: {e503_path}")

    e504_path = create_e504_sample()
    print(f"  ✓ E504 sample: {e504_path}")

    clean_path = create_clean_sample()
    print(f"  ✓ Clean sample: {clean_path}")

    # Run pattern analysis on each sample
    print("\n2. Running pattern analysis...")

    run_pattern_analysis(e501_path)
    run_pattern_analysis(e502_path)
    run_pattern_analysis(e503_path)
    run_pattern_analysis(e504_path)
    run_pattern_analysis(clean_path)

    # Generate summary
    print("\n3. Generating summary...")
    generate_summary()

    print("\n" + "=" * 50)
    print("T5 Sample generation complete!")
    print(f"Sample directory: {SAMPLES_DIR}")
    print(f"Clean sample: {CLEAN_DIR}")


if __name__ == "__main__":
    main()
