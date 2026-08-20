from fpl_api import (
    get_bootstrap,
    get_fixtures,
    get_manager,
    get_my_team,
)

from data import (
    build_team_map,
    build_player_map,
    build_player_dataset,
    build_fixture_dataset,
    get_team_fixtures,
)

from analysis import (
    calculate_fixture_score,
    calculate_all_fixture_scores,
    add_fixture_scores_to_players,
)

from display import (
    console,
    print_fixture_dataset_test,
    print_team_fixtures,
    print_fixture_score_ranking,
    print_player_dataset,
    print_gameweek_info,
    print_manager_info,
    print_player_summary,
    print_my_team,
)


# ============================================================
# CONFIGURATION
# ============================================================

MANAGER_ID = 6829404


# ============================================================
# GAMEWEEK STATUS
# ============================================================

def get_gameweek_status(
    bootstrap
):
    """
    Find current and next Gameweek.
    """

    events = bootstrap[
        "events"
    ]


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
# MAIN
# ============================================================

def main():

    console.print()

    console.print(
        "=" * 50
    )

    console.print(
        "[bold]FPL AGENT - API TEST[/bold]"
    )

    console.print(
        "=" * 50
    )


    # ========================================================
    # 1. BOOTSTRAP DATA
    # ========================================================

    console.print(
        "\nLoading FPL data..."
    )


    bootstrap = get_bootstrap()


    console.print(
        "[green]✓ Bootstrap data loaded[/green]"
    )


    # ========================================================
    # 2. PLAYERS + TEAMS
    # ========================================================

    players = bootstrap[
        "elements"
    ]


    teams = bootstrap[
        "teams"
    ]


    team_map = build_team_map(
        teams
    )


    player_map = build_player_map(
        players
    )


    console.print(
        f"[green]✓ {len(players)} "
        f"players loaded[/green]"
    )


    console.print(
        f"[green]✓ {len(teams)} "
        f"teams loaded[/green]"
    )


    # ========================================================
    # 3. BUILD PLAYER DATASET
    # ========================================================

    player_dataset = build_player_dataset(
        players,
        team_map
    )


    # ========================================================
    # 4. LOAD FIXTURES
    # ========================================================

    console.print(
        "\nLoading fixtures..."
    )


    fixtures = get_fixtures()


    console.print(
        f"[green]✓ {len(fixtures)} "
        f"fixtures loaded[/green]"
    )


    # ========================================================
    # 5. BUILD FIXTURE DATASET
    # ========================================================

    fixture_dataset = build_fixture_dataset(
        fixtures,
        team_map
    )


    console.print(
        f"[green]✓ {len(fixture_dataset)} "
        f"fixture records created[/green]"
    )


    # ========================================================
    # 6. FIXTURE DATASET TEST
    # ========================================================

    print_fixture_dataset_test(
        fixture_dataset,
        number_of_records=10
    )


    # ========================================================
    # 7. GAMEWEEK STATUS
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
    # 8. TEAM FIXTURE SCORES
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


        # ====================================================
        # 9. ADD FIXTURE SCORE TO PLAYERS
        # ====================================================

        player_dataset = (
            add_fixture_scores_to_players(
                player_dataset=player_dataset,

                team_fixture_scores=team_fixture_scores
            )
        )


        # ====================================================
        # 10. DISPLAY ENRICHED PLAYER DATASET
        # ====================================================

        print_player_dataset(
            player_dataset,

            number_of_players=20
        )


    else:

        console.print(
            "\n[yellow]"
            "No next Gameweek available."
            "[/yellow]"
        )


    # ========================================================
    # 11. ARSENAL TEST
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


            arsenal_score = (
                calculate_fixture_score(
                    arsenal_fixtures
                )
            )


            console.print(
                f"\nArsenal Fixture Score: "
                f"{arsenal_score}/10"
            )


    # ========================================================
    # 12. PLAYER DATA TEST
    # ========================================================

    print_player_summary(
        players,
        team_map
    )


    # ========================================================
    # 13. MANAGER
    # ========================================================

    console.print(
        "\nFetching manager information..."
    )


    manager = get_manager(
        MANAGER_ID
    )


    console.print(
        "[green]✓ Manager data loaded[/green]"
    )


    print_manager_info(
        manager
    )


    # ========================================================
    # 14. CURRENT SQUAD
    # ========================================================

    console.print(
        "\nFetching your current squad..."
    )


    try:

        my_team = get_my_team(
            MANAGER_ID
        )


        console.print(
            "[green]✓ Current squad loaded[/green]"
        )


        print_my_team(
            my_team,

            player_map,

            team_map
        )


    except RuntimeError as error:

        console.print(
            "\n[yellow]"
            "⚠ Could not retrieve current squad."
            "[/yellow]"
        )


        console.print(
            str(error)
        )


    # ========================================================
    # DONE
    # ========================================================

    console.print()

    console.print(
        "=" * 50
    )

    console.print(
        "[bold]API TEST COMPLETE[/bold]"
    )

    console.print(
        "=" * 50
    )


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":

    main()