import os
import requests
from dotenv import load_dotenv


# ============================================================
# CONFIGURATION
# ============================================================

BASE_URL = "https://fantasy.premierleague.com/api"

# Your FPL Manager ID
MANAGER_ID = 6829404


# ============================================================
# LOAD ENVIRONMENT VARIABLES
# ============================================================

load_dotenv()

FPL_AUTH_TOKEN = os.getenv("FPL_AUTH_TOKEN")


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
    """Send a GET request to an FPL API endpoint."""

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

    if response.status_code == 200:
        return response.json()

    if response.status_code in (401, 403):
        raise RuntimeError(
            f"\nFPL API returned HTTP {response.status_code}.\n"
            "This endpoint requires authentication.\n"
            "Check FPL_AUTH_TOKEN in your .env file."
        )

    if response.status_code == 404:
        raise RuntimeError(
            f"\nFPL API returned HTTP 404.\n"
            f"Endpoint not found or data is not currently available:\n"
            f"{url}"
        )

    if response.status_code == 429:
        raise RuntimeError(
            "\nFPL API rate limit reached (HTTP 429).\n"
            "Wait a little before making more requests."
        )

    raise RuntimeError(
        f"\nFPL API request failed.\n"
        f"HTTP status: {response.status_code}\n"
        f"Response: {response.text[:500]}"
    )


# ============================================================
# GET BOOTSTRAP DATA
# ============================================================

def get_bootstrap():
    """Get the main FPL dataset."""

    return get_json("/bootstrap-static/")


# ============================================================
# GAMEWEEK STATUS
# ============================================================

def get_gameweek_status(bootstrap):
    """Find the current and next gameweek."""

    events = bootstrap["events"]

    current_events = [
        event
        for event in events
        if event.get("is_current")
    ]

    next_events = [
        event
        for event in events
        if event.get("is_next")
    ]

    current = current_events[0] if current_events else None
    next_gameweek = next_events[0] if next_events else None

    return current, next_gameweek


# ============================================================
# BUILD LOOKUP DICTIONARIES
# ============================================================

def build_team_map(teams):
    """Create team_id -> team_name lookup."""

    return {
        team["id"]: team["name"]
        for team in teams
    }


def build_player_map(players):
    """Create player_id -> player_data lookup."""

    return {
        player["id"]: player
        for player in players
    }


# ============================================================
# GET MANAGER INFORMATION
# ============================================================

def get_manager(manager_id):
    """Get public information about the FPL manager."""

    return get_json(
        f"/entry/{manager_id}/"
    )


# ============================================================
# GET CURRENT TEAM
# ============================================================

def get_my_team(manager_id):
    """
    Get the authenticated manager's current squad.

    Requires FPL_AUTH_TOKEN.
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


# ============================================================
# PRINT MANAGER INFORMATION
# ============================================================

def print_manager_info(manager):

    print("\n" + "=" * 30)
    print("       MANAGER INFORMATION")
    print("=" * 30)

    print(
        f"Manager: "
        f"{manager.get('player_first_name', '')} "
        f"{manager.get('player_last_name', '')}"
    )

    print(
        f"Team name: "
        f"{manager.get('name', 'N/A')}"
    )

    print(
        f"Overall points: "
        f"{manager.get('summary_overall_points', 'N/A')}"
    )

    print(
        f"Overall rank: "
        f"{manager.get('summary_overall_rank', 'N/A')}"
    )

    print(
        f"Gameweek started: "
        f"{manager.get('started_event', 'N/A')}"
    )


# ============================================================
# PRINT GAMEWEEK INFORMATION
# ============================================================

def print_gameweek_info(current, next_gameweek):

    print("\n" + "=" * 30)
    print("        GAMEWEEK STATUS")
    print("=" * 30)

    if current:

        print(
            f"Current GW: "
            f"{current['id']} - "
            f"{current['name']}"
        )

        print(
            f"Finished: "
            f"{current['finished']}"
        )

        print(
            f"Deadline: "
            f"{current['deadline_time']}"
        )

    else:
        print("Current GW: None")

    if next_gameweek:

        print(
            f"Next GW: "
            f"{next_gameweek['id']} - "
            f"{next_gameweek['name']}"
        )

        print(
            f"Deadline: "
            f"{next_gameweek['deadline_time']}"
        )

    else:
        print("Next GW: None")


# ============================================================
# PRINT PLAYER DATA
# ============================================================

def print_player_summary(players, team_map):

    print("\n" + "=" * 30)
    print("       PLAYER DATA TEST")
    print("=" * 30)

    print(
        f"Total players: {len(players)}"
    )

    print("\nFirst 10 players:")

    for player in players[:10]:

        price = player["now_cost"] / 10

        team_name = team_map.get(
            player["team"],
            "Unknown"
        )

        print(
            f"{player['web_name']:15} | "
            f"{team_name:20} | "
            f"£{price:.1f}m | "
            f"{player['total_points']} pts"
        )


# ============================================================
# PRINT CURRENT SQUAD
# ============================================================

def print_my_team(my_team, player_map, team_map):

    print("\n" + "=" * 30)
    print("          YOUR SQUAD")
    print("=" * 30)

    picks = my_team.get("picks", [])

    if not picks:
        print("No squad data returned.")
        return

    print(
        f"Players returned: {len(picks)}\n"
    )

    for pick in picks:

        player_id = pick["element"]

        player = player_map.get(player_id)

        if not player:
            print(
                f"Unknown player ID: {player_id}"
            )
            continue

        player_name = player["web_name"]

        team_name = team_map.get(
            player["team"],
            "Unknown"
        )

        price = player["now_cost"] / 10

        position = pick["position"]

        if pick.get("is_captain"):
            status = " (C)"

        elif pick.get("is_vice_captain"):
            status = " (VC)"

        else:
            status = ""

        print(
            f"{position:2}. "
            f"{player_name:15} | "
            f"{team_name:20} | "
            f"£{price:.1f}m"
            f"{status}"
        )


# ============================================================
# MAIN
# ============================================================

def main():

    print("\n")
    print("=" * 50)
    print("          FPL AGENT - API TEST")
    print("=" * 50)

    # --------------------------------------------------------
    # 1. Load global FPL data
    # --------------------------------------------------------

    print("\nLoading FPL data...")

    bootstrap = get_bootstrap()

    print("✓ Bootstrap data loaded")

    # --------------------------------------------------------
    # 2. Extract players and teams
    # --------------------------------------------------------

    players = bootstrap["elements"]
    teams = bootstrap["teams"]

    team_map = build_team_map(teams)
    player_map = build_player_map(players)

    print(
        f"✓ {len(players)} players loaded"
    )

    print(
        f"✓ {len(teams)} teams loaded"
    )

    # --------------------------------------------------------
    # 3. Gameweek status
    # --------------------------------------------------------

    current_gameweek, next_gameweek = (
        get_gameweek_status(bootstrap)
    )

    print_gameweek_info(
        current_gameweek,
        next_gameweek
    )

    # --------------------------------------------------------
    # 4. Test player data
    # --------------------------------------------------------

    print_player_summary(
        players,
        team_map
    )

    # --------------------------------------------------------
    # 5. Get manager information
    # --------------------------------------------------------

    print("\nFetching manager information...")

    manager = get_manager(
        MANAGER_ID
    )

    print("✓ Manager data loaded")

    print_manager_info(
        manager
    )

    # --------------------------------------------------------
    # 6. Get authenticated current squad
    # --------------------------------------------------------

    print("\nFetching your current squad...")

    try:

        my_team = get_my_team(
            MANAGER_ID
        )

        print(
            "✓ Current squad loaded"
        )

        print_my_team(
            my_team,
            player_map,
            team_map
        )

    except RuntimeError as error:

        print(
            "\n⚠ Could not retrieve current squad."
        )

        print(error)

        print(
            "\nPublic FPL data is working."
        )

        print(
            "The problem is with the "
            "authenticated endpoint."
        )

    # --------------------------------------------------------
    # DONE
    # --------------------------------------------------------

    print("\n" + "=" * 50)
    print("             API TEST COMPLETE")
    print("=" * 50)


# ============================================================
# PYTHON ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()