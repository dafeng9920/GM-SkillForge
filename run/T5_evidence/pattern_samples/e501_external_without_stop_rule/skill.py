"""
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
