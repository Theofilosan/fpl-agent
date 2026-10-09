import os
import requests
from dotenv import load_dotenv


# ============================================================
# CONFIGURATION
# ============================================================

BASE_URL = "https://fantasy.premierleague.com/api"


# ============================================================
# ENVIRONMENT
# ============================================================

load_dotenv()

FPL_AUTH_TOKEN = os.getenv(
    "FPL_AUTH_TOKEN"
)


# ============================================================
# HTTP SESSION
# ============================================================

session = requests.Session()

session.headers.update({
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) "
        "AppleWebKit/537.36 "
        "(KHTML, like Gecko) "
        "Chrome/150.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json",
    "Referer": "https://fantasy.premierleague.com/",
    "Origin": "https://fantasy.premierleague.com",
})





# ============================================================
# API HELPER
# ============================================================

def get_json(endpoint, *, authenticated=False):
    """
    Send a GET request to an FPL API endpoint.
    """

    url = f"{BASE_URL}{endpoint}"
    headers = {}
    if authenticated:
        if not FPL_AUTH_TOKEN:
            raise RuntimeError("FPL_AUTH_TOKEN is missing.")
        headers["X-API-Authorization"] = FPL_AUTH_TOKEN

    # Requests are read-only; do not print URLs or authenticated response bodies.


    try:

        response = session.get(
            url,
            headers=headers,
            timeout=(5, 20),
            allow_redirects=False
        )

    except requests.RequestException as error:

        raise RuntimeError(
            "Network error while calling FPL API. Try again later."
        ) from error


    if response.status_code == 200:

        try:
            payload = response.json()
        except ValueError as error:
            raise RuntimeError("FPL API returned invalid JSON.") from error
        if not isinstance(payload, (dict, list)):
            raise RuntimeError("FPL API returned an unexpected response shape.")
        return payload


    if response.status_code in (401, 403):

        raise RuntimeError(
            f"\nFPL API returned HTTP "
            f"{response.status_code}.\n"
            "This endpoint requires authentication.\n"
            "Check FPL_AUTH_TOKEN in your .env file."
        )


    if response.status_code == 404:

        raise RuntimeError(
            f"\nFPL API returned HTTP 404.\n"
            f"Endpoint not found:\n{url}"
        )


    if response.status_code == 429:

        raise RuntimeError(
            "\nFPL API rate limit reached (HTTP 429)."
        )


    raise RuntimeError(
        f"\nFPL API request failed.\n"
        f"HTTP status: {response.status_code}"
    )


# ============================================================
# BOOTSTRAP
# ============================================================

def get_bootstrap():
    """
    Get the main FPL dataset.
    """

    return get_json(
        "/bootstrap-static/"
    )


# ============================================================
# FIXTURES
# ============================================================

def get_fixtures():
    """
    Get all FPL fixtures.
    """

    return get_json(
        "/fixtures/"
    )


# ============================================================
# MANAGER
# ============================================================

def get_manager(manager_id):
    """
    Get public manager information.
    """

    return get_json(
        f"/entry/{manager_id}/"
    )


# ============================================================
# CURRENT TEAM
# ============================================================

def get_my_team(manager_id):
    """
    Get the authenticated manager's current squad.
    """

    if not FPL_AUTH_TOKEN:

        raise RuntimeError(
            "\nFPL_AUTH_TOKEN is missing.\n\n"
            "Add it to your .env file:\n\n"
            "FPL_AUTH_TOKEN=Bearer YOUR_TOKEN_HERE"
        )


    return get_json(
        f"/my-team/{manager_id}/",
        authenticated=True
    )
