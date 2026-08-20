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

# Authentication token for private FPL endpoints
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
    """

    return get_json(
        "/fixtures/"
    )


# ============================================================
# BUILD TEAM LOOKUP
# ============================================================

def build_team_map(teams):
    """
    Create:

        team_id -> team_name
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
    Create:

        player_id -> player_data
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

    Each fixture becomes TWO records:

        Home team perspective
        Away team perspective
    """

    fixture_dataset = []


    # --------------------------------------------------------
    # Process every fixture
    # --------------------------------------------------------

    for fixture in fixtures:

        # Skip fixtures without a Gameweek
        if fixture.get("event") is None:
            continue


        gameweek = fixture["event"]

        home_team_id = fixture["team_h"]

        away_team_id = fixture["team_a"]


        # Convert team IDs into names

        home_team = team_map.get(
            home_team_id,
            "Unknown"
        )

        away_team = team_map.get(
            away_team_id,
            "Unknown"
        )


        # Difficulty ratings

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


    # VERY IMPORTANT:
    # Return the completed dataset.

    return fixture_dataset


# ============================================================
# GET TEAM FIXTURES
# ============================================================

def get_team_fixtures(
    fixture_dataset,
    team_id,
    start_gameweek,
    number_of_gameweeks=5
):
    """
    Get fixtures for one specific team.

    Example:

        start_gameweek = 1
        number_of_gameweeks = 5

    returns:

        GW1 -> GW5
    """

    end_gameweek = (
        start_gameweek
        + number_of_gameweeks
        - 1
    )


    # Filter fixtures

    team_fixtures = [

        fixture

        for fixture in fixture_dataset

        if (
            fixture["team_id"] == team_id
            and
            start_gameweek
            <= fixture["gameweek"]
            <= end_gameweek
        )
    ]


    # Sort by Gameweek and kickoff time

    team_fixtures.sort(
        key=lambda fixture: (
            fixture["gameweek"],
            fixture["kickoff_time"] or ""
        )
    )


    return team_fixtures


# ============================================================
# CALCULATE FIXTURE SCORE
# ============================================================

def calculate_fixture_score(team_fixtures):
    """
    Calculate a Fixture Score from 0 to 10.

    FPL difficulty:

        1 = very easy
        2 = easy
        3 = medium
        4 = difficult
        5 = very difficult

    Converted score:

        Difficulty 1 -> 5
        Difficulty 2 -> 4
        Difficulty 3 -> 3
        Difficulty 4 -> 2
        Difficulty 5 -> 1
    """

    # --------------------------------------------------------
    # No fixtures
    # --------------------------------------------------------

    if not team_fixtures:

        return None


    # --------------------------------------------------------
    # Difficulty conversion
    # --------------------------------------------------------

    difficulty_scores = {

        1: 5,
        2: 4,
        3: 3,
        4: 2,
        5: 1,
    }


    scores = []


    # --------------------------------------------------------
    # Calculate score for every fixture
    # --------------------------------------------------------

    for fixture in team_fixtures:

        difficulty = fixture.get(
            "difficulty"
        )


        if difficulty not in difficulty_scores:

            continue


        fixture_score = difficulty_scores[
            difficulty
        ]


        scores.append(
            fixture_score
        )


    # --------------------------------------------------------
    # No valid difficulty scores
    # --------------------------------------------------------

    if not scores:

        return None


    # --------------------------------------------------------
    # Average score
    # --------------------------------------------------------

    average_score = (
        sum(scores)
        / len(scores)
    )


    # --------------------------------------------------------
    # Convert 1-5 to 0-10
    # --------------------------------------------------------

    final_score = (
        average_score
        / 5
        * 10
    )


    return round(
        final_score,
        1
    )


# ============================================================
# CALCULATE ALL TEAM FIXTURE SCORES
# ============================================================

def calculate_all_fixture_scores(
    fixture_dataset,
    teams,
    start_gameweek,
    number_of_gameweeks=5
):
    """
    Calculate Fixture Score for all Premier League teams.

    Returns a list sorted from BEST to WORST fixture score.
    """

    team_scores = []


    # --------------------------------------------------------
    # Process every team
    # --------------------------------------------------------

    for team in teams:

        team_id = team["id"]

        team_name = team["name"]


        # Get this team's fixtures

        team_fixtures = get_team_fixtures(
            fixture_dataset=fixture_dataset,

            team_id=team_id,

            start_gameweek=start_gameweek,

            number_of_gameweeks=number_of_gameweeks
        )


        # Calculate Fixture Score

        fixture_score = calculate_fixture_score(
            team_fixtures
        )


        # Store result

        team_scores.append({

            "team_id": team_id,

            "team": team_name,

            "fixture_score": fixture_score,

            "fixtures": team_fixtures,
        })


    # --------------------------------------------------------
    # Sort BEST -> WORST
    # --------------------------------------------------------

    team_scores.sort(
        key=lambda team: (
            team["fixture_score"]
            if team["fixture_score"] is not None
            else -1
        ),
        reverse=True
    )


    # VERY IMPORTANT:
    # Return the complete ranking.

    return team_scores


# ============================================================
# PRINT FIXTURE DATASET TEST
# ============================================================

def print_fixture_dataset_test(
    fixture_dataset,
    number_of_records=10
):
    """
    Print the first few fixture records.
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
# PRINT TEAM FIXTURES
# ============================================================

def print_team_fixtures(
    team_fixtures,
    team_name
):
    """
    Print fixtures for one team.
    """

    print("\n" + "=" * 50)
    print(
        f"       {team_name.upper()} - NEXT FIXTURES"
    )
    print("=" * 50)


    if not team_fixtures:

        print(
            "No fixtures found."
        )

        return


    for fixture in team_fixtures:

        location = (
            "HOME"
            if fixture["home"]
            else "AWAY"
        )


        print(
            f"GW{fixture['gameweek']:2} | "
            f"{location:4} | "
            f"{fixture['opponent']:20} | "
            f"Difficulty: "
            f"{fixture['difficulty']}/5"
        )


# ============================================================
# PRINT FIXTURE SCORE RANKING
# ============================================================

def print_fixture_score_ranking(
    team_scores,
    number_of_gameweeks=5
):
    """
    Print the Fixture Score ranking.
    """

    print("\n" + "=" * 65)

    print(
        f"       FIXTURE SCORE - NEXT "
        f"{number_of_gameweeks} GAMEWEEKS"
    )

    print("=" * 65)


    print(
        f"{'Rank':<6}"
        f"{'Team':<22}"
        f"{'Score':>10}"
    )


    print("-" * 65)


    # --------------------------------------------------------
    # Print every team
    # --------------------------------------------------------

    for rank, team in enumerate(
        team_scores,
        start=1
    ):

        score = team["fixture_score"]


        if score is None:

            score_display = "N/A"

        else:

            score_display = (
                f"{score:.1f}/10"
            )


        print(
            f"{rank:<6}"
            f"{team['team']:<22}"
            f"{score_display:>10}"
        )


# ============================================================
# GAMEWEEK STATUS
# ============================================================

def get_gameweek_status(bootstrap):
    """
    Find current and next Gameweek.
    """

    events = bootstrap["events"]


    # Current Gameweek

    current_events = [

        event

        for event in events

        if event.get("is_current")
    ]


    # Next Gameweek

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
    Get public information about the manager.
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

        # FPL stores prices in tenths.
        # Example:
        # 60 -> £6.0m

        price = (
            player["now_cost"]
            / 10
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

        player_id = pick["element"]


        player = player_map.get(
            player_id
        )


        if not player:

            print(
                f"Unknown player ID: "
                f"{player_id}"
            )

            continue


        player_name = (
            player["web_name"]
        )


        team_name = team_map.get(
            player["team"],
            "Unknown"
        )


        price = (
            player["now_cost"]
            / 10
        )


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


    # Build lookups BEFORE processing fixtures

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
    # 4. BUILD FIXTURE DATASET
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
    # 7. CALCULATE ALL FIXTURE SCORES
    # ========================================================

    if next_gameweek:

        team_fixture_scores = (
            calculate_all_fixture_scores(
                fixture_dataset=fixture_dataset,

                teams=teams,

                start_gameweek=next_gameweek["id"],

                number_of_gameweeks=5
            )
        )


        print_fixture_score_ranking(
            team_fixture_scores,

            number_of_gameweeks=5
        )


    else:

        print(
            "\nNo next Gameweek available."
        )


    # ========================================================
    # 8. TEST ARSENAL FIXTURES
    # ========================================================

    if next_gameweek:

        arsenal = next(
            (
                team
                for team in teams
                if team["name"] == "Arsenal"
            ),
            None
        )


        if arsenal:

            arsenal_fixtures = (
                get_team_fixtures(
                    fixture_dataset=fixture_dataset,

                    team_id=arsenal["id"],

                    start_gameweek=next_gameweek["id"],

                    number_of_gameweeks=5
                )
            )


            print_team_fixtures(
                arsenal_fixtures,

                arsenal["name"]
            )


            arsenal_fixture_score = (
                calculate_fixture_score(
                    arsenal_fixtures
                )
            )


            print(
                f"\nArsenal Fixture Score: "
                f"{arsenal_fixture_score}/10"
            )


    # ========================================================
    # 9. PLAYER DATA TEST
    # ========================================================

    print_player_summary(
        players,
        team_map
    )


    # ========================================================
    # 10. MANAGER INFORMATION
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
    # 11. CURRENT SQUAD
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