# ============================================================
# TEAM DATA
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
# PLAYER DATA
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
# FIXTURE DATASET
# ============================================================

def build_fixture_dataset(fixtures, team_map):
    """
    Convert raw FPL fixtures into a team-centric dataset.

    Each fixture becomes TWO records:

        Home team perspective
        Away team perspective
    """

    fixture_dataset = []


    for fixture in fixtures:

        # Skip fixtures without a Gameweek

        if fixture.get("event") is None:

            continue


        gameweek = fixture["event"]

        home_team_id = fixture["team_h"]

        away_team_id = fixture["team_a"]


        # Convert IDs to names

        home_team = team_map.get(
            home_team_id,
            "Unknown"
        )

        away_team = team_map.get(
            away_team_id,
            "Unknown"
        )


        # Difficulty

        home_difficulty = fixture.get(
            "team_h_difficulty"
        )

        away_difficulty = fixture.get(
            "team_a_difficulty"
        )


        # ====================================================
        # HOME TEAM
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
        # AWAY TEAM
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
# TEAM FIXTURES
# ============================================================

def get_team_fixtures(
    fixture_dataset,
    team_id,
    start_gameweek,
    number_of_gameweeks=5
):
    """
    Get fixtures for one team.
    """

    end_gameweek = (
        start_gameweek
        + number_of_gameweeks
        - 1
    )


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


    # Sort chronologically

    team_fixtures.sort(
        key=lambda fixture: (
            fixture["gameweek"],
            fixture["kickoff_time"] or ""
        )
    )


    return team_fixtures