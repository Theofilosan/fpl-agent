import os
import requests
from dotenv import load_dotenv


# ============================================================
# CONFIGURATION
# ============================================================

BASE_URL = "https://fantasy.premierleague.com/api"


# ============================================================
# LOAD ENVIRONMENT VARIABLES
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


if FPL_AUTH_TOKEN:

    session.headers.update({
        "X-API-Authorization": FPL_AUTH_TOKEN
    })


# ============================================================
# API HELPER
# ============================================================

def get_json(endpoint):
    """
    Send a GET request to an FPL API endpoint.

    Returns:
        Parsed JSON response.
    """

    url = f"{BASE_URL}{endpoint}"

    print(f"\nGET {url}")

    try:

        response = session.get(
            url,
            timeout=15
        )

    except requests.RequestException as error:

        raise RuntimeError(
            f"Network error while calling FPL API: {error}"
        ) from error


    # --------------------------------------------------------
    # Successful request
    # --------------------------------------------------------

    if response.status_code == 200:

        return response.json()


    # --------------------------------------------------------
    # Authentication error
    # --------------------------------------------------------

    if response.status_code in (401, 403):

        raise RuntimeError(
            f"\nFPL API returned HTTP {response.status_code}.\n"
            "This endpoint requires authentication.\n"
            "Check FPL_AUTH_TOKEN in your .env file."
        )


    # --------------------------------------------------------
    # Not found
    # --------------------------------------------------------

    if response.status_code == 404:

        raise RuntimeError(
            f"\nFPL API returned HTTP 404.\n"
            f"Endpoint not found or data is not currently available:\n"
            f"{url}"
        )


    # --------------------------------------------------------
    # Rate limit
    # --------------------------------------------------------

    if response.status_code == 429:

        raise RuntimeError(
            "\nFPL API rate limit reached (HTTP 429).\n"
            "Wait a little before making more requests."
        )


    # --------------------------------------------------------
    # Other errors
    # --------------------------------------------------------

    raise RuntimeError(
        f"\nFPL API request failed.\n"
        f"HTTP status: {response.status_code}\n"
        f"Response: {response.text[:500]}"
    )


# ============================================================
# BOOTSTRAP
# ============================================================

def get_bootstrap():
    """
    Get the main FPL dataset.

    Contains:
        - Players
        - Teams
        - Gameweeks
        - Player statistics
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
        f"/my-team/{manager_id}/"
    )