import os
import requests
from dotenv import load_dotenv


# ============================================================
# CONFIGURATION
# ============================================================

# Base URL for the Fantasy Premier League API
BASE_URL = "https://fantasy.premierleague.com/api"

# Your FPL Manager ID
MANAGER_ID = 6829404


# ============================================================
# LOAD ENVIRONMENT VARIABLES
# ============================================================

# Load variables from .env
load_dotenv()

# Authentication token for private FPL endpoints
FPL_AUTH_TOKEN = os.getenv("FPL_AUTH_TOKEN")


# ============================================================
# HTTP SESSION
# ============================================================

# Create one reusable HTTP session
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


# Add authentication header if token exists
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

    Parameters
    ----------
    endpoint : str
        API endpoint such as:
        /bootstrap-static/

    Returns
    -------
    dict | list
        Parsed JSON response.
    """

    # Build complete URL
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
    # Other HTTP errors
    # --------------------------------------------------------

    raise RuntimeError(
        f"\nFPL API request failed.\n"
        f"HTTP status: {response.status_code}\n"
        f"Response: {response.text[:500]}"
    )


# ============================================================
# GET BOOTSTRAP DATA
# ============================================================

def get_bootstrap():
    """
    Get the main FPL dataset.

    Contains:
        - Players
        - Teams
        - Gameweeks
        - Player statistics
        - Game settings
    """

    return get_json(
        "/bootstrap-static/"
    )


# ============================================================
# GET FIXTURES
# ============================================================

def get_fixtures():
    """
    Get all FPL fixtures.

    This is a public endpoint.
    Authentication is not required.
    """

    return get_json(
        "/fixtures/"
    )


# ============================================================
# BUILD TEAM LOOKUP
# ============================================================

def build_team_map(teams):
    """
    Create a dictionary mapping:

        team_id -> team_name

    Example:

        1 -> Arsenal
        2 -> Aston Villa
    """

    return {
        team["id"]: team["name"]
        for team in teams
    }


# ============================================================
# BUILD PLAYER LOOKUP
# ============================================================

def build_player_map(players):
    """
    Create a dictionary mapping:

        player_id -> player_data

    This allows us to quickly find a player using
    the player ID returned by the squad endpoint.
    """

    return {
        player["id"]: player
        for player in players
    }


# ============================================================
# BUILD FIXTURE DATASET
# ============================================================

def build_fixture_dataset(fixtures, team_map):
    """
    Convert raw FPL fixtures into a team-centric dataset.

    Each fixture is converted into TWO records.

    Example:

        Arsenal vs Manchester United

    becomes:

        Arsenal
            GW1
            vs Manchester United
            HOME
            difficulty = 2

        Manchester United
            GW1
            vs Arsenal
            AWAY
            difficulty = 4

    This structure will later allow us to calculate
    fixture difficulty for every team.
    """

    fixture_dataset = []


    # --------------------------------------------------------
    # Loop through all fixtures
    # --------------------------------------------------------

    for fixture in fixtures:

        # Some fixtures may not have a Gameweek yet.
        # We skip those.
        if fixture.get("event") is None:

            continue


        # ----------------------------------------------------
        # Basic fixture information
        # ----------------------------------------------------

        gameweek = fixture["event"]

        home_team_id = fixture["team_h"]

        away_team_id = fixture["team_a"]


        # Convert team IDs to team names

        home_team = team_map.get(
            home_team_id,
            "Unknown"
        )

        away_team = team_map.get(
            away_team_id,
            "Unknown"
        )


        # ----------------------------------------------------
        # FPL difficulty ratings
        # ----------------------------------------------------

        home_difficulty = fixture.get(
            "team_h_difficulty"
        )

        away_difficulty = fixture.get(
            "team_a_difficulty"
        )


        # ====================================================
        # HOME TEAM RECORD
        # ====================================================

        home_record = {

            "fixture_id": fixture["id"],

            "gameweek": gameweek,

            "team": home_team,

            "team_id": home_team_id,

            "opponent": away_team,

            "opponent_id": away_team_id,

            "home": True,

            "difficulty": home_difficulty,

            "kickoff_time": fixture.get(
                "kickoff_time"
            ),

            "finished": fixture.get(
                "finished",
                False
            ),
        }


        fixture_dataset.append(
            home_record
        )


        # ====================================================
        # AWAY TEAM RECORD
        # ====================================================

        away_record = {

            "fixture_id": fixture["id"],

            "gameweek": gameweek,

            "team": away_team,

            "team_id": away_team_id,

            "opponent": home_team,

            "opponent_id": home_team_id,

            "home": False,

            "difficulty": away_difficulty,

            "kickoff_time": fixture.get(
                "kickoff_time"
            ),

            "finished": fixture.get(
                "finished",
                False
            ),
        }


        fixture_dataset.append(
            away_record
        )


    return fixture_dataset


# ============================================================
# PRINT FIXTURE DATASET TEST
# ============================================================

def print_fixture_dataset_test(
    fixture_dataset,
    number_of_records=10
):
    """
    Print the first few records of the structured
    fixture dataset.

    This is currently only a sanity check.
    """

    print("\n" + "=" * 50)
    print("       FIXTURE DATASET TEST")
    print("=" * 50)

    print(
        f"Total fixture records: "
        f"{len(fixture_dataset)}"
    )

    print(
        f"\nFirst {number_of_records} records:"
    )

    for fixture in fixture_dataset[
        :number_of_records
    ]:

        # Convert True/False to readable text

        location = (
            "HOME"
            if fixture["home"]
            else "AWAY"
        )


        print(
            f"GW{fixture['gameweek']:2} | "
            f"{fixture['team']:20} | "
            f"{location:4} | "
            f"vs {fixture['opponent']:20} | "
            f"Difficulty: "
            f"{fixture['difficulty']}"
        )


# ============================================================
# GAMEWEEK STATUS
# ============================================================

def get_gameweek_status(bootstrap):
    """
    Find the current and next FPL Gameweek.
    """

    events = bootstrap["events"]


    # Find current Gameweek

    current_events = [
        event
        for event in events
        if event.get("is_current")
    ]


    # Find next Gameweek

    next_events = [
        event
        for event in events
        if event.get("is_next")
    ]


    current = (
        current_events[0]
        if current_events
        else None
    )


    next_gameweek = (
        next_events[0]
        if next_events
        else None
    )


    return current, next_gameweek


# ============================================================
# GET MANAGER INFORMATION
# ============================================================

def get_manager(manager_id):
    """
    Get public information about an FPL manager.
    """

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

def print_gameweek_info(
    current,
    next_gameweek
):

    print("\n" + "=" * 30)
    print("        GAMEWEEK STATUS")
    print("=" * 30)


    # Current Gameweek

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

        print(
            "Current GW: None"
        )


    # Next Gameweek

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

        print(
            "Next GW: None"
        )


# ============================================================
# PRINT PLAYER DATA
# ============================================================

def print_player_summary(
    players,
    team_map
):

    print("\n" + "=" * 30)
    print("       PLAYER DATA TEST")
    print("=" * 30)


    print(
        f"Total players: "
        f"{len(players)}"
    )


    print("\nFirst 10 players:")


    for player in players[:10]:

        # FPL stores price in tenths.
        # Example:
        # 60 -> £6.0m

        price = (
            player["now_cost"] / 10
        )


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

def print_my_team(
    my_team,
    player_map,
    team_map
):

    print("\n" + "=" * 30)
    print("          YOUR SQUAD")
    print("=" * 30)


    picks = my_team.get(
        "picks",
        []
    )


    if not picks:

        print(
            "No squad data returned."
        )

        return


    print(
        f"Players returned: "
        f"{len(picks)}\n"
    )


    for pick in picks:

        # Player ID from the squad endpoint

        player_id = pick["element"]


        # Find complete player data

        player = player_map.get(
            player_id
        )


        if not player:

            print(
                f"Unknown player ID: "
                f"{player_id}"
            )

            continue


        # Player name

        player_name = (
            player["web_name"]
        )


        # Premier League team

        team_name = team_map.get(
            player["team"],
            "Unknown"
        )


        # Player price

        price = (
            player["now_cost"] / 10
        )


        # Squad position

        position = pick["position"]


        # Captain / vice captain

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


    # ========================================================
    # 1. LOAD GLOBAL FPL DATA
    # ========================================================

    print(
        "\nLoading FPL data..."
    )


    bootstrap = get_bootstrap()


    print(
        "✓ Bootstrap data loaded"
    )


    # ========================================================
    # 2. EXTRACT PLAYERS AND TEAMS
    # ========================================================

    players = bootstrap["elements"]

    teams = bootstrap["teams"]


    # IMPORTANT:
    #
    # We MUST build team_map BEFORE building
    # the fixture dataset.
    #
    # This was the cause of your UnboundLocalError.

    team_map = build_team_map(
        teams
    )


    player_map = build_player_map(
        players
    )


    print(
        f"✓ {len(players)} players loaded"
    )


    print(
        f"✓ {len(teams)} teams loaded"
    )


    # ========================================================
    # 3. LOAD FIXTURES
    # ========================================================

    print(
        "\nLoading fixtures..."
    )


    fixtures = get_fixtures()


    print(
        f"✓ {len(fixtures)} fixtures loaded"
    )


    # ========================================================
    # 4. BUILD STRUCTURED FIXTURE DATASET
    # ========================================================

    fixture_dataset = build_fixture_dataset(
        fixtures,
        team_map
    )


    print(
        f"✓ {len(fixture_dataset)} "
        f"fixture records created"
    )


    # ========================================================
    # 5. TEST FIXTURE DATASET
    # ========================================================

    print_fixture_dataset_test(
        fixture_dataset,
        number_of_records=10
    )


    # ========================================================
    # 6. GAMEWEEK STATUS
    # ========================================================

    current_gameweek, next_gameweek = (
        get_gameweek_status(
            bootstrap
        )
    )


    print_gameweek_info(
        current_gameweek,
        next_gameweek
    )


    # ========================================================
    # 7. TEST PLAYER DATA
    # ========================================================

    print_player_summary(
        players,
        team_map
    )


    # ========================================================
    # 8. GET MANAGER INFORMATION
    # ========================================================

    print(
        "\nFetching manager information..."
    )


    manager = get_manager(
        MANAGER_ID
    )


    print(
        "✓ Manager data loaded"
    )


    print_manager_info(
        manager
    )


    # ========================================================
    # 9. GET CURRENT SQUAD
    # ========================================================

    print(
        "\nFetching your current squad..."
    )


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
            "\n⚠ Could not retrieve "
            "current squad."
        )


        print(error)


        print(
            "\nPublic FPL data is working."
        )


        print(
            "The problem is with the "
            "authenticated endpoint."
        )


    # ========================================================
    # DONE
    # ========================================================

    print("\n" + "=" * 50)

    print(
        "             API TEST COMPLETE"
    )

    print("=" * 50)


# ============================================================
# PYTHON ENTRY POINT
# ============================================================

if __name__ == "__main__":

    main()