from rich.console import Console
from rich.table import Table
from rich import box


# ============================================================
# RICH CONSOLE
# ============================================================

console = Console()


# ============================================================
# DIFFICULTY COLOR
# ============================================================

def get_difficulty_style(difficulty):
    """
    Return a Rich style based on FPL difficulty.

        1-2 -> green
        3   -> yellow
        4-5 -> red
    """

    if difficulty in (1, 2):

        return "green"

    if difficulty == 3:

        return "yellow"

    if difficulty in (4, 5):

        return "red"

    return "white"


# ============================================================
# FIXTURE DATASET TEST
# ============================================================

def print_fixture_dataset_test(
    fixture_dataset,
    number_of_records=10
):
    """
    Display first fixture records.
    """

    console.print()
    console.print(
        "=" * 50
    )

    console.print(
        "[bold]FIXTURE DATASET TEST[/bold]"
    )

    console.print(
        "=" * 50
    )


    console.print(
        f"Total fixture records: "
        f"{len(fixture_dataset)}"
    )


    table = Table(
        box=box.SIMPLE
    )


    table.add_column("GW")
    table.add_column("Team")
    table.add_column("Venue")
    table.add_column("Opponent")
    table.add_column("Difficulty")


    for fixture in fixture_dataset[
        :number_of_records
    ]:

        location = (
            "HOME"
            if fixture["home"]
            else "AWAY"
        )


        difficulty = fixture[
            "difficulty"
        ]


        style = get_difficulty_style(
            difficulty
        )


        table.add_row(

            str(
                fixture["gameweek"]
            ),

            fixture["team"],

            location,

            fixture["opponent"],

            f"[{style}]"
            f"{difficulty}/5"
            f"[/{style}]"
        )


    console.print(table)


# ============================================================
# TEAM FIXTURES
# ============================================================

def print_team_fixtures(
    team_fixtures,
    team_name
):
    """
    Display fixtures for one team.
    """

    console.print()

    console.print(
        f"[bold]{team_name.upper()} "
        f"- NEXT FIXTURES[/bold]"
    )


    if not team_fixtures:

        console.print(
            "[yellow]No fixtures found.[/yellow]"
        )

        return


    table = Table(
        box=box.SIMPLE
    )


    table.add_column("GW")
    table.add_column("Venue")
    table.add_column("Opponent")
    table.add_column("Difficulty")


    for fixture in team_fixtures:

        location = (
            "HOME"
            if fixture["home"]
            else "AWAY"
        )


        difficulty = fixture[
            "difficulty"
        ]


        style = get_difficulty_style(
            difficulty
        )


        table.add_row(

            str(
                fixture["gameweek"]
            ),

            location,

            fixture["opponent"],

            f"[{style}]"
            f"{difficulty}/5"
            f"[/{style}]"
        )


    console.print(table)


# ============================================================
# FIXTURE SCORE RANKING
# ============================================================

def print_fixture_score_ranking(
    team_scores,
    number_of_gameweeks=5
):
    """
    Display Fixture Score ranking.
    """

    console.print()

    console.print(
        "=" * 65
    )

    console.print(
        f"[bold]"
        f"FIXTURE SCORE - NEXT "
        f"{number_of_gameweeks} GAMEWEEKS"
        f"[/bold]"
    )

    console.print(
        "=" * 65
    )


    table = Table(
        box=box.SIMPLE
    )


    table.add_column(
        "Rank",
        justify="right"
    )

    table.add_column(
        "Team"
    )

    table.add_column(
        "Score",
        justify="right"
    )


    for rank, team in enumerate(
        team_scores,
        start=1
    ):

        score = team[
            "fixture_score"
        ]


        if score is None:

            score_display = "[dim]N/A[/dim]"

        elif score >= 8:

            score_display = (
                f"[green bold]"
                f"{score:.1f}/10"
                f"[/green bold]"
            )

        elif score >= 6:

            score_display = (
                f"[yellow]"
                f"{score:.1f}/10"
                f"[/yellow]"
            )

        else:

            score_display = (
                f"[red]"
                f"{score:.1f}/10"
                f"[/red]"
            )


        table.add_row(

            str(rank),

            team["team"],

            score_display
        )


    console.print(table)


# ============================================================
# GAMEWEEK INFORMATION
# ============================================================

def print_gameweek_info(
    current,
    next_gameweek
):

    console.print()

    console.print(
        "[bold]GAMEWEEK STATUS[/bold]"
    )


    if current:

        console.print(
            f"Current GW: "
            f"{current['id']} - "
            f"{current['name']}"
        )

        console.print(
            f"Finished: "
            f"{current['finished']}"
        )

        console.print(
            f"Deadline: "
            f"{current['deadline_time']}"
        )

    else:

        console.print(
            "Current GW: None"
        )


    if next_gameweek:

        console.print(
            f"Next GW: "
            f"{next_gameweek['id']} - "
            f"{next_gameweek['name']}"
        )

        console.print(
            f"Deadline: "
            f"{next_gameweek['deadline_time']}"
        )

    else:

        console.print(
            "Next GW: None"
        )


# ============================================================
# MANAGER INFORMATION
# ============================================================

def print_manager_info(manager):

    console.print()

    console.print(
        "[bold]MANAGER INFORMATION[/bold]"
    )


    console.print(
        f"Manager: "
        f"{manager.get('player_first_name', '')} "
        f"{manager.get('player_last_name', '')}"
    )


    console.print(
        f"Team name: "
        f"{manager.get('name', 'N/A')}"
    )


    console.print(
        f"Overall points: "
        f"{manager.get('summary_overall_points', 'N/A')}"
    )


    console.print(
        f"Overall rank: "
        f"{manager.get('summary_overall_rank', 'N/A')}"
    )


    console.print(
        f"Gameweek started: "
        f"{manager.get('started_event', 'N/A')}"
    )


# ============================================================
# PLAYER SUMMARY
# ============================================================

def print_player_summary(
    players,
    team_map
):

    console.print()

    console.print(
        "[bold]PLAYER DATA TEST[/bold]"
    )


    console.print(
        f"Total players: "
        f"{len(players)}"
    )


    table = Table(
        box=box.SIMPLE
    )


    table.add_column("Player")
    table.add_column("Team")
    table.add_column("Price")
    table.add_column("Points")


    for player in players[:10]:

        price = (
            player["now_cost"]
            / 10
        )


        team_name = team_map.get(
            player["team"],
            "Unknown"
        )


        table.add_row(

            player["web_name"],

            team_name,

            f"£{price:.1f}m",

            str(
                player["total_points"]
            )
        )


    console.print(table)


# ============================================================
# CURRENT SQUAD
# ============================================================

def print_my_team(
    my_team,
    player_map,
    team_map
):

    console.print()

    console.print(
        "[bold]YOUR SQUAD[/bold]"
    )


    picks = my_team.get(
        "picks",
        []
    )


    if not picks:

        console.print(
            "[yellow]"
            "No squad data returned."
            "[/yellow]"
        )

        return


    console.print(
        f"Players returned: "
        f"{len(picks)}"
    )


    table = Table(
        box=box.SIMPLE
    )


    table.add_column("Pos")
    table.add_column("Player")
    table.add_column("Team")
    table.add_column("Price")
    table.add_column("Status")


    for pick in picks:

        player_id = pick[
            "element"
        ]


        player = player_map.get(
            player_id
        )


        if not player:

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


        if pick.get("is_captain"):

            status = "[bold red]C[/bold red]"

        elif pick.get(
            "is_vice_captain"
        ):

            status = "[yellow]VC[/yellow]"

        else:

            status = ""


        table.add_row(

            str(
                pick["position"]
            ),

            player_name,

            team_name,

            f"£{price:.1f}m",

            status
        )


    console.print(table)
    # ============================================================
# PLAYER DATASET
# ============================================================

def print_player_dataset(
    player_dataset,
    number_of_players=20
):
    """
    Display a sample of the structured player dataset.
    """

    console.print()

    console.print(
        "=" * 90
    )

    console.print(
        "[bold]PLAYER DATASET TEST[/bold]"
    )

    console.print(
        "=" * 90
    )


    console.print(
        f"Total players: "
        f"{len(player_dataset)}"
    )


    table = Table(
        box=box.SIMPLE
    )


    table.add_column("Player")
    table.add_column("Team")
    table.add_column("Pos")
    table.add_column("Price")
    table.add_column("Pts")
    table.add_column("Form")
    table.add_column("PPG")
    table.add_column("Min")
    table.add_column("xG")
    table.add_column("xA")
    table.add_column("Own%")


    for player in player_dataset[
        :number_of_players
    ]:

        table.add_row(

            player["player"],

            player["team"],

            player["position"],

            f"£{player['price']:.1f}m",

            str(
                player["total_points"]
            ),

            f"{player['form']:.1f}",

            f"{player['points_per_game']:.1f}",

            str(
                player["minutes"]
            ),

            f"{player['expected_goals']:.2f}",

            f"{player['expected_assists']:.2f}",

            f"{player['ownership']:.1f}%"
        )


    console.print(table)