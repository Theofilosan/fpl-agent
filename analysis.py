from data import get_team_fixtures


# ============================================================
# FIXTURE SCORE
# ============================================================

def calculate_fixture_score(team_fixtures):
    """
    Calculate Fixture Score from 0 to 10.

    Difficulty:

        1 -> 5 points
        2 -> 4 points
        3 -> 3 points
        4 -> 2 points
        5 -> 1 point
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
    Calculate Fixture Score for every team.

    Returns a list sorted from best to worst.
    """

    team_scores = []


    for team in teams:

        team_id = team["id"]

        team_name = team["name"]


        # Get fixtures

        team_fixtures = get_team_fixtures(
            fixture_dataset=fixture_dataset,

            team_id=team_id,

            start_gameweek=start_gameweek,

            number_of_gameweeks=number_of_gameweeks
        )


        # Calculate score

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


    # Sort best -> worst

    team_scores.sort(
        key=lambda team: (
            team["fixture_score"]
            if team["fixture_score"] is not None
            else -1
        ),
        reverse=True
    )


    return team_scores