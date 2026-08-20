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


    return round(
        average_score / 5 * 10,
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
    """

    team_scores = []


    for team in teams:

        team_id = team["id"]


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

            "team_id":
                team_id,

            "team":
                team["name"],

            "fixture_score":
                fixture_score,

            "fixtures":
                team_fixtures,
        })


    team_scores.sort(

        key=lambda team:
            (
                team["fixture_score"]
                if team["fixture_score"] is not None
                else -1
            ),

        reverse=True
    )


    return team_scores


# ============================================================
# ADD FIXTURE SCORES TO PLAYERS
# ============================================================

def add_fixture_scores_to_players(
    player_dataset,
    team_fixture_scores
):
    """
    Add each team's Fixture Score
    to its players.
    """

    fixture_score_map = {

        team["team_id"]:
            team["fixture_score"]

        for team in team_fixture_scores
    }


    for player in player_dataset:

        player["fixture_score"] = (
            fixture_score_map.get(
                player["team_id"]
            )
        )


    return player_dataset


# ============================================================
# PLAYER ELIGIBILITY
# ============================================================

def classify_player_eligibility(
    minutes
):
    """
    Classify players according to
    historical minutes.
    """

    if minutes < 450:

        return "Limited"

    elif minutes < 1350:

        return "Rotation"

    elif minutes < 2250:

        return "Regular"

    else:

        return "Established"


# ============================================================
# ADD PLAYER ELIGIBILITY
# ============================================================

def add_player_eligibility(
    player_dataset
):
    """
    Add eligibility and minutes ratio
    to every player.
    """

    MAX_MINUTES = 3420


    for player in player_dataset:

        minutes = player.get(
            "minutes",
            0
        )


        player["eligibility"] = (
            classify_player_eligibility(
                minutes
            )
        )


        minutes_ratio = (
            minutes
            / MAX_MINUTES
        )


        player["minutes_ratio"] = max(
            0.0,
            min(
                minutes_ratio,
                1.0
            )
        )


    return player_dataset


# ============================================================
# SQUAD ANALYSIS
# ============================================================

def analyze_squad(
    squad_dataset
):
    """
    Perform a simple analysis of the
    current squad.

    This is intentionally NOT making
    transfer recommendations yet.
    """

    analysis = {

        "total_players":
            len(squad_dataset),

        "captain":
            None,

        "vice_captain":
            None,

        "difficult_fixtures":
            [],

        "favourable_fixtures":
            [],

        "watchlist":
            [],
    }


    for player in squad_dataset:

        fixture_score = player.get(
            "fixture_score"
        )


        # ----------------------------------------------------
        # Captain
        # ----------------------------------------------------

        if player.get(
            "is_captain"
        ):

            analysis["captain"] = player


        # ----------------------------------------------------
        # Vice captain
        # ----------------------------------------------------

        if player.get(
            "is_vice_captain"
        ):

            analysis["vice_captain"] = player


        # ----------------------------------------------------
        # Fixture analysis
        # ----------------------------------------------------

        if fixture_score is not None:

            if fixture_score < 5.5:

                analysis[
                    "difficult_fixtures"
                ].append(player)


            elif fixture_score >= 7.0:

                analysis[
                    "favourable_fixtures"
                ].append(player)


        # ----------------------------------------------------
        # Historical sample warning
        # ----------------------------------------------------

        if player.get(
            "eligibility"
        ) == "Limited":

            analysis[
                "watchlist"
            ].append(player)


    return analysis