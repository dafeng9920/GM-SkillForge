"""
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
