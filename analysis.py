from data import get_team_fixtures


# ============================================================
# FIXTURE SCORE
# ============================================================

def calculate_fixture_score(
    team_fixtures
):
    """
    Calculate Fixture Score from 0 to 10.

    FPL difficulty:

        1 -> 5
        2 -> 4
        3 -> 3
        4 -> 2
        5 -> 1
    """

    if not team_fixtures:

        return None


    difficulty_scores = {

        1: 5,
        2: 4,
        3: 3,
        4: 2,
        5: 1,
    }


    scores = []


    for fixture in team_fixtures:

        difficulty = fixture.get(
            "difficulty"
        )


        if difficulty not in difficulty_scores:

            continue


        scores.append(
            difficulty_scores[
                difficulty
            ]
        )


    if not scores:

        return None


    average_score = (
        sum(scores)
        / len(scores)
    )


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
# ALL TEAM FIXTURE SCORES
# ============================================================

def calculate_all_fixture_scores(
    fixture_dataset,
    teams,
    start_gameweek,
    number_of_gameweeks=5
):
    """
    Calculate Fixture Score for all teams.

    Returns a list sorted from best to worst.
    """

    team_scores = []


    for team in teams:

        team_id = team["id"]

        team_name = team["name"]


        team_fixtures = get_team_fixtures(
            fixture_dataset=fixture_dataset,

            team_id=team_id,

            start_gameweek=start_gameweek,

            number_of_gameweeks=number_of_gameweeks
        )


        fixture_score = calculate_fixture_score(
            team_fixtures
        )


        team_scores.append({

            "team_id": team_id,

            "team": team_name,

            "fixture_score": fixture_score,

            "fixtures": team_fixtures,
        })


    team_scores.sort(
        key=lambda team: (
            team["fixture_score"]
            if team["fixture_score"] is not None
            else -1
        ),
        reverse=True
    )


    return team_scores


# ============================================================
# ADD FIXTURE SCORE TO PLAYERS
# ============================================================

def add_fixture_scores_to_players(
    player_dataset,
    team_fixture_scores
):
    """
    Add the Fixture Score of each player's team
    to the player's dataset record.
    """

    # --------------------------------------------------------
    # Create:
    #
    # team_id -> fixture_score
    # --------------------------------------------------------

    fixture_score_map = {

        team["team_id"]:
            team["fixture_score"]

        for team in team_fixture_scores
    }


    # --------------------------------------------------------
    # Add score to each player
    # --------------------------------------------------------

    for player in player_dataset:

        team_id = player["team_id"]


        player["fixture_score"] = (
            fixture_score_map.get(
                team_id
            )
        )


    return player_dataset
# ============================================================
# PRICE BRACKET
# ============================================================

def get_price_bracket(price):
    """
    Assign a player to a price bracket.

    The brackets are intentionally simple for now.
    We can make them position-specific later.

    Examples:

        £4.5m  -> £4-5m
        £5.0m  -> £5-6m
        £6.7m  -> £6-7m
        £7.5m  -> £7-8m
        £9.5m  -> £8-10m
        £10.5m -> £10m+
    """

    if price < 5.0:

        return "£4-5m"

    elif price < 6.0:

        return "£5-6m"

    elif price < 7.0:

        return "£6-7m"

    elif price < 8.0:

        return "£7-8m"

    elif price < 10.0:

        return "£8-10m"

    else:

        return "£10m+"


# ============================================================
# PLAYER BENCHMARKS
# ============================================================

def calculate_player_benchmarks(
    player_dataset
):
    """
    Calculate statistical benchmarks for players grouped by:

        Position
        +
        Price Bracket

    Example group:

        Midfielder | £6-7m

    The benchmark currently includes:

        - Number of players
        - Average PPG
        - Average Form
        - Average xG
        - Average xA
        - Average Minutes
        - Average Ownership

    Returns
    -------
    dict

        {
            ("Midfielder", "£6-7m"): {
                ...
            }
        }
    """

    # --------------------------------------------------------
    # Create empty groups
    # --------------------------------------------------------

    groups = {}


    # --------------------------------------------------------
    # Group players
    # --------------------------------------------------------

    for player in player_dataset:

        position = player["position"]

        price_bracket = get_price_bracket(
            player["price"]
        )


        group_key = (
            position,
            price_bracket
        )


        if group_key not in groups:

            groups[group_key] = []


        groups[group_key].append(
            player
        )


    # --------------------------------------------------------
    # Calculate averages
    # --------------------------------------------------------

    benchmarks = {}


    for group_key, players in groups.items():

        number_of_players = len(
            players
        )


        # ----------------------------------------------------
        # Helper for calculating averages
        # ----------------------------------------------------

        def average(field):

            values = [

                player.get(
                    field,
                    0
                )

                for player in players
            ]


            if not values:

                return 0


            return (
                sum(values)
                / len(values)
            )


        # ----------------------------------------------------
        # Store benchmark
        # ----------------------------------------------------

        benchmarks[group_key] = {

            "position":
                group_key[0],

            "price_bracket":
                group_key[1],

            "players":
                number_of_players,

            "avg_ppg":
                average(
                    "points_per_game"
                ),

            "avg_form":
                average(
                    "form"
                ),

            "avg_xg":
                average(
                    "expected_goals"
                ),

            "avg_xa":
                average(
                    "expected_assists"
                ),

            "avg_minutes":
                average(
                    "minutes"
                ),

            "avg_ownership":
                average(
                    "ownership"
                ),
        }


    return benchmarks