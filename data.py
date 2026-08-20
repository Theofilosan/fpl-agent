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
# PLAYER DATASET
# ============================================================

def build_player_dataset(
    players,
    team_map
):
    """
    Build a structured player dataset.

    This function extracts the player statistics
    that will later be used by the analysis engine.
    """

    player_dataset = []


    position_map = {
        1: "Goalkeeper",
        2: "Defender",
        3: "Midfielder",
        4: "Forward",
    }


    for player in players:

        player_id = player["id"]

        player_name = player["web_name"]

        team_id = player["team"]

        team_name = team_map.get(
            team_id,
            "Unknown"
        )


        position = position_map.get(
            player["element_type"],
            "Unknown"
        )


        price = (
            player["now_cost"]
            / 10
        )


        total_points = player.get(
            "total_points",
            0
        )


        form = float(
            player.get(
                "form",
                0
            ) or 0
        )


        points_per_game = float(
            player.get(
                "points_per_game",
                0
            ) or 0
        )


        minutes = player.get(
            "minutes",
            0
        )


        goals = player.get(
            "goals_scored",
            0
        )


        assists = player.get(
            "assists",
            0
        )


        bonus = player.get(
            "bonus",
            0
        )


        bps = player.get(
            "bps",
            0
        )


        ownership = float(
            player.get(
                "selected_by_percent",
                0
            ) or 0
        )


        expected_goals = float(
            player.get(
                "expected_goals",
                0
            ) or 0
        )


        expected_assists = float(
            player.get(
                "expected_assists",
                0
            ) or 0
        )


        expected_goal_involvements = float(
            player.get(
                "expected_goal_involvements",
                0
            ) or 0
        )


        expected_goals_conceded = float(
            player.get(
                "expected_goals_conceded",
                0
            ) or 0
        )


        chance_next_round = player.get(
            "chance_of_playing_next_round"
        )


        chance_this_round = player.get(
            "chance_of_playing_this_round"
        )


        status = player.get(
            "status"
        )


        news = player.get(
            "news",
            ""
        )


        player_record = {

            "player_id": player_id,

            "player": player_name,

            "team_id": team_id,

            "team": team_name,

            "position": position,

            "price": price,

            "total_points": total_points,

            "form": form,

            "points_per_game": points_per_game,

            "minutes": minutes,

            "goals": goals,

            "assists": assists,

            "bonus": bonus,

            "bps": bps,

            "ownership": ownership,

            "expected_goals": expected_goals,

            "expected_assists": expected_assists,

            "expected_goal_involvements":
                expected_goal_involvements,

            "expected_goals_conceded":
                expected_goals_conceded,

            "chance_next_round":
                chance_next_round,

            "chance_this_round":
                chance_this_round,

            "status": status,

            "news": news,

            # This will be populated later
            # by the analysis layer.
            "fixture_score": None,
        }


        player_dataset.append(
            player_record
        )


    return player_dataset


# ============================================================
# FIXTURE DATASET
# ============================================================

def build_fixture_dataset(
    fixtures,
    team_map
):
    """
    Convert raw FPL fixtures into a team-centric dataset.

    Each fixture becomes TWO records:
        - Home team perspective
        - Away team perspective
    """

    fixture_dataset = []


    for fixture in fixtures:

        if fixture.get("event") is None:

            continue


        gameweek = fixture["event"]

        home_team_id = fixture["team_h"]

        away_team_id = fixture["team_a"]


        home_team = team_map.get(
            home_team_id,
            "Unknown"
        )


        away_team = team_map.get(
            away_team_id,
            "Unknown"
        )


        home_difficulty = fixture.get(
            "team_h_difficulty"
        )


        away_difficulty = fixture.get(
            "team_a_difficulty"
        )


        # ====================================================
        # HOME RECORD
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
        # AWAY RECORD
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
    Get fixtures for one specific team.
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


    team_fixtures.sort(
        key=lambda fixture: (
            fixture["gameweek"],
            fixture["kickoff_time"] or ""
        )
    )


    return team_fixtures