"""
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
