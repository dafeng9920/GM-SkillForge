"""
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
