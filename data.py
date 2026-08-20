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
# PLAYER MAP
# ============================================================

def build_player_map(players):
    """
    Create:

        player_id -> raw player data
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
    Build a clean internal player dataset
    from the raw FPL API data.
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

        team_id = player["team"]


        player_record = {

            "player_id":
                player_id,

            "player":
                player["web_name"],

            "team_id":
                team_id,

            "team":
                team_map.get(
                    team_id,
                    "Unknown"
                ),

            "position":
                position_map.get(
                    player["element_type"],
                    "Unknown"
                ),

            "price":
                player["now_cost"] / 10,

            "total_points":
                player.get(
                    "total_points",
                    0
                ),

            "form":
                float(
                    player.get(
                        "form",
                        0
                    ) or 0
                ),

            "points_per_game":
                float(
                    player.get(
                        "points_per_game",
                        0
                    ) or 0
                ),

            "minutes":
                player.get(
                    "minutes",
                    0
                ),

            "goals":
                player.get(
                    "goals_scored",
                    0
                ),

            "assists":
                player.get(
                    "assists",
                    0
                ),

            "bonus":
                player.get(
                    "bonus",
                    0
                ),

            "bps":
                player.get(
                    "bps",
                    0
                ),

            "ownership":
                float(
                    player.get(
                        "selected_by_percent",
                        0
                    ) or 0
                ),

            "expected_goals":
                float(
                    player.get(
                        "expected_goals",
                        0
                    ) or 0
                ),

            "expected_assists":
                float(
                    player.get(
                        "expected_assists",
                        0
                    ) or 0
                ),

            "expected_goal_involvements":
                float(
                    player.get(
                        "expected_goal_involvements",
                        0
                    ) or 0
                ),

            "expected_goals_conceded":
                float(
                    player.get(
                        "expected_goals_conceded",
                        0
                    ) or 0
                ),

            "chance_next_round":
                player.get(
                    "chance_of_playing_next_round"
                ),

            "chance_this_round":
                player.get(
                    "chance_of_playing_this_round"
                ),

            "status":
                player.get(
                    "status"
                ),

            "news":
                player.get(
                    "news",
                    ""
                ),

            "fixture_score":
                None,

            "eligibility":
                None,

            "minutes_ratio":
                None,
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

    Each fixture creates two records:

        Home team perspective
        Away team perspective
    """

    fixture_dataset = []


    for fixture in fixtures:

        if fixture.get(
            "event"
        ) is None:

            continue


        gameweek = fixture[
            "event"
        ]


        home_team_id = fixture[
            "team_h"
        ]


        away_team_id = fixture[
            "team_a"
        ]


        home_team = team_map.get(
            home_team_id,
            "Unknown"
        )


        away_team = team_map.get(
            away_team_id,
            "Unknown"
        )


        # ----------------------------------------------------
        # HOME TEAM
        # ----------------------------------------------------

        fixture_dataset.append({

            "fixture_id":
                fixture["id"],

            "gameweek":
                gameweek,

            "team_id":
                home_team_id,

            "team":
                home_team,

            "opponent_id":
                away_team_id,

            "opponent":
                away_team,

            "home":
                True,

            "difficulty":
                fixture.get(
                    "team_h_difficulty"
                ),

            "kickoff_time":
                fixture.get(
                    "kickoff_time"
                ),

            "finished":
                fixture.get(
                    "finished",
                    False
                ),
        })


        # ----------------------------------------------------
        # AWAY TEAM
        # ----------------------------------------------------

        fixture_dataset.append({

            "fixture_id":
                fixture["id"],

            "gameweek":
                gameweek,

            "team_id":
                away_team_id,

            "team":
                away_team,

            "opponent_id":
                home_team_id,

            "opponent":
                home_team,

            "home":
                False,

            "difficulty":
                fixture.get(
                    "team_a_difficulty"
                ),

            "kickoff_time":
                fixture.get(
                    "kickoff_time"
                ),

            "finished":
                fixture.get(
                    "finished",
                    False
                ),
        })


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
    Return fixtures for one team
    within the requested Gameweek range.
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


# ============================================================
# SQUAD DATASET
# ============================================================

def build_squad_dataset(
    my_team,
    player_dataset
):
    """
    Combine the manager's current squad
    with the enriched player dataset.
    """

    player_map = {

        player["player_id"]:
            player

        for player in player_dataset
    }


    squad_dataset = []


    for pick in my_team.get(
        "picks",
        []
    ):

        player_id = pick[
            "element"
        ]


        player = player_map.get(
            player_id
        )


        if not player:

            continue


        squad_player = player.copy()


        squad_player["squad_position"] = (
            pick["position"]
        )


        squad_player["multiplier"] = (
            pick.get(
                "multiplier",
                1
            )
        )


        squad_player["is_captain"] = (
            pick.get(
                "is_captain",
                False
            )
        )


        squad_player["is_vice_captain"] = (
            pick.get(
                "is_vice_captain",
                False
            )
        )


        squad_player["purchase_price"] = (
            pick.get(
                "purchase_price"
            )
        )


        squad_player["selling_price"] = (
            pick.get(
                "selling_price"
            )
        )


        squad_dataset.append(
            squad_player
        )


    squad_dataset.sort(
        key=lambda player:
            player["squad_position"]
    )


    return squad_dataset