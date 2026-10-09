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

def get_difficulty_style(
    difficulty
):
    """
    Return a Rich style based on FPL difficulty.
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

            score_display = (
                "[dim]N/A[/dim]"
            )

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
# PLAYER DATASET
# ============================================================

def print_player_dataset(
    player_dataset,
    number_of_players=20
):
    """
    Display a sample of the structured player dataset.

    The dataset should already contain the team's
    Fixture Score.
    """

    console.print()

    console.print(
        "=" * 110
    )

    console.print(
        "[bold]PLAYER DATASET TEST[/bold]"
    )

    console.print(
        "=" * 110
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
    table.add_column("Fixtures")
    table.add_column("Eligibility")


    for player in player_dataset[
        :number_of_players
    ]:

        # ----------------------------------------------------
        # Fixture Score
        # ----------------------------------------------------

        fixture_score = player.get(
            "fixture_score"
        )


        if fixture_score is None:

            fixture_display = (
                "[dim]N/A[/dim]"
            )

        elif fixture_score >= 8:

            fixture_display = (
                f"[green bold]"
                f"{fixture_score:.1f}"
                f"[/green bold]"
            )

        elif fixture_score >= 6:

            fixture_display = (
                f"[yellow]"
                f"{fixture_score:.1f}"
                f"[/yellow]"
            )

        else:

            fixture_display = (
                f"[red]"
                f"{fixture_score:.1f}"
                f"[/red]"
            )

    
        


        # ----------------------------------------------------
        # Player row
        # ----------------------------------------------------

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

            f"{player['ownership']:.1f}%",

            fixture_display
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

def print_manager_info(
    manager
):

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

            status = (
                "[bold red]C[/bold red]"
            )

        elif pick.get(
            "is_vice_captain"
        ):

            status = (
                "[yellow]VC[/yellow]"
            )

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
# PLAYER BENCHMARKS
# ============================================================

def print_player_benchmarks(
    benchmarks
):
    """
    Display player benchmarks grouped by:

        Position
        +
        Price Bracket
    """

    console.print()

    console.print(
        "=" * 100
    )

    console.print(
        "[bold]PLAYER BENCHMARKS[/bold]"
    )

    console.print(
        "=" * 100
    )


    table = Table(
        box=box.SIMPLE
    )


    table.add_column(
        "Position"
    )

    table.add_column(
        "Price Range"
    )

    table.add_column(
        "Players",
        justify="right"
    )

    table.add_column(
        "Avg PPG",
        justify="right"
    )

    table.add_column(
        "Avg Form",
        justify="right"
    )

    table.add_column(
        "Avg xG",
        justify="right"
    )

    table.add_column(
        "Avg xA",
        justify="right"
    )

    table.add_column(
        "Avg Minutes",
        justify="right"
    )

    table.add_column(
        "Avg Own%",
        justify="right"
    )


    # --------------------------------------------------------
    # Sort groups
    #
    # First by position
    # Then by price bracket
    # --------------------------------------------------------

    position_order = {

        "Goalkeeper": 1,
        "Defender": 2,
        "Midfielder": 3,
        "Forward": 4,
    }


    sorted_benchmarks = sorted(

        benchmarks.values(),

        key=lambda benchmark: (
            position_order.get(
                benchmark["position"],
                99
            ),

            benchmark["price_bracket"]
        )
    )


    # --------------------------------------------------------
    # Display rows
    # --------------------------------------------------------

    for benchmark in sorted_benchmarks:

        table.add_row(

            benchmark["position"],

            benchmark["price_bracket"],

            str(
                benchmark["players"]
            ),

            f"{benchmark['avg_ppg']:.2f}",

            f"{benchmark['avg_form']:.2f}",

            f"{benchmark['avg_xg']:.2f}",

            f"{benchmark['avg_xa']:.2f}",

            f"{benchmark['avg_minutes']:.0f}",

            f"{benchmark['avg_ownership']:.1f}%"
        )


    console.print(table)
    # ============================================================
    # PLAYER ELIGIBILITY SUMMARY
    # ============================================================

def print_eligibility_summary(
    summary
):
    """
    Display the distribution of players across
    eligibility categories.
    """

    console.print()

    console.print(
        "=" * 90
    )

    console.print(
        "[bold]PLAYER ELIGIBILITY SUMMARY[/bold]"
    )

    console.print(
        "=" * 90
    )


    table = Table(
        box=box.SIMPLE
    )


    table.add_column(
        "Category"
    )

    table.add_column(
        "Players",
        justify="right"
    )

    table.add_column(
        "Avg Minutes",
        justify="right"
    )

    table.add_column(
        "Avg PPG",
        justify="right"
    )

    table.add_column(
        "Avg Points",
        justify="right"
    )

    table.add_column(
        "Avg Own%",
        justify="right"
    )


    category_styles = {

        "Established": "green",

        "Regular": "cyan",

        "Rotation": "yellow",

        "Limited": "red",
    }


    for category in [
        "Established",
        "Regular",
        "Rotation",
        "Limited",
    ]:

        data = summary[
            category
        ]


        style = category_styles[
            category
        ]


        table.add_row(

            f"[{style}]"
            f"{category}"
            f"[/{style}]",

            str(
                data["players"]
            ),

            f"{data['avg_minutes']:.0f}",

            f"{data['avg_ppg']:.2f}",

            f"{data['avg_points']:.1f}",

            f"{data['avg_ownership']:.1f}%"
        )


    console.print(table)

# ============================================================
# SQUAD ANALYSIS
# ============================================================

def print_squad_analysis(
    squad_dataset,
    analysis
):
    """
    Display the current squad analysis.
    """

    console.print()

    console.print(
        "=" * 100
    )

    console.print(
        "[bold]SQUAD ANALYSIS[/bold]"
    )

    console.print(
        "=" * 100
    )


    # --------------------------------------------------------
    # Captain / Vice Captain
    # --------------------------------------------------------

    captain = analysis.get(
        "captain"
    )

    vice_captain = analysis.get(
        "vice_captain"
    )


    if captain:

        console.print(
            f"Captain: "
            f"[bold yellow]"
            f"{captain['player']}"
            f"[/bold yellow]"
        )


    if vice_captain:

        console.print(
            f"Vice Captain: "
            f"[yellow]"
            f"{vice_captain['player']}"
            f"[/yellow]"
        )


    # --------------------------------------------------------
    # Squad table
    # --------------------------------------------------------

    table = Table(
        box=box.SIMPLE
    )


    table.add_column("Pos")
    table.add_column("Player")
    table.add_column("Team")
    table.add_column("Price")
    table.add_column("PPG", justify="right")
    table.add_column("Fixtures", justify="right")
    table.add_column("Status")


    for player in squad_dataset:

        fixture_score = player.get(
            "fixture_score"
        )


        if fixture_score is None:

            fixture_display = (
                "[dim]N/A[/dim]"
            )

        elif fixture_score >= 8:

            fixture_display = (
                f"[green bold]"
                f"{fixture_score:.1f}"
                f"[/green bold]"
            )

        elif fixture_score >= 6:

            fixture_display = (
                f"[yellow]"
                f"{fixture_score:.1f}"
                f"[/yellow]"
            )

        else:

            fixture_display = (
                f"[red]"
                f"{fixture_score:.1f}"
                f"[/red]"
            )


        eligibility = player.get(
            "eligibility",
            "Unknown"
        )


        if eligibility == "Established":

            status = (
                "[green]Established[/green]"
            )

        elif eligibility == "Regular":

            status = (
                "[cyan]Regular[/cyan]"
            )

        elif eligibility == "Rotation":

            status = (
                "[yellow]Rotation[/yellow]"
            )

        elif eligibility == "Limited":

            status = (
                "[red]Limited[/red]"
            )

        else:

            status = (
                "[dim]Unknown[/dim]"
            )


        table.add_row(

            str(
                player["squad_position"]
            ),

            player["player"],

            player["team"],

            f"£{player['price']:.1f}m",

            f"{player['points_per_game']:.1f}",

            fixture_display,

            status
        )


    console.print(
        table
    )


    # --------------------------------------------------------
    # Difficult fixtures
    # --------------------------------------------------------

    difficult = analysis.get(
        "difficult_fixtures",
        []
    )


    if difficult:

        console.print()

        console.print(
            "[bold red]"
            "⚠ Players with difficult fixtures"
            "[/bold red]"
        )


        for player in difficult:

            console.print(
                f"  • {player['player']} "
                f"({player['team']}) "
                f"- Fixture Score: "
                f"{player['fixture_score']:.1f}"
            )


    # --------------------------------------------------------
    # Favourable fixtures
    # --------------------------------------------------------

    favourable = analysis.get(
        "favourable_fixtures",
        []
    )


    if favourable:

        console.print()

        console.print(
            "[bold green]"
            "✓ Players with favourable fixtures"
            "[/bold green]"
        )


        for player in favourable:

            console.print(
                f"  • {player['player']} "
                f"({player['team']}) "
                f"- Fixture Score: "
                f"{player['fixture_score']:.1f}"
            )


    # --------------------------------------------------------
    # Watchlist
    # --------------------------------------------------------

    watchlist = analysis.get(
        "watchlist",
        []
    )


    if watchlist:

        console.print()

        console.print(
            "[bold yellow]"
            "👀 Players to monitor"
            "[/bold yellow]"
        )


        for player in watchlist:

            console.print(
                f"  • {player['player']} "
                f"({player['team']}) "
                f"- Limited historical minutes"
            )



def print_player_rankings(rankings, team_map, limit=10):
    """A public shortlist, explicitly labelled as an uncalibrated heuristic."""
    table = Table(title="Player shortlist (heuristic score, NOT expected points)")
    for heading in ("Player", "Team", "Price", "Score", "Score/£m", "Why"):
        table.add_column(heading)
    eligible = [p for p in rankings if p["availability"] == 1 and p["score"] > 0]
    for player in eligible[:limit]:
        # API strings are literal text, not Rich markup.
        from rich.text import Text
        table.add_row(
            Text(player["player"]), Text(team_map.get(player["team_id"], "Unknown")),
            f"£{player['cost']/10:.1f}", f"{player['score']:.2f}",
            str(player["value_score"]), Text(player["reason"]),
        )
    console.print(table)



def print_lineup(lineup):
    from rich.text import Text
    table = Table(title=f"Suggested XI ({lineup['formation']}) - heuristic, review before acting")
    for label in ("Role", "Player", "Next-GW score"):
        table.add_column(label)
    for player in lineup["xi"]:
        role = "C" if player["player_id"] == lineup["captain"]["player_id"] else "VC" if player["player_id"] == lineup["vice_captain"]["player_id"] else "XI"
        table.add_row(role, Text(player["player"]), str(player["next_score"]))
    table.add_row("Bench GK", Text(lineup["bench_goalkeeper"]["player"]), str(lineup["bench_goalkeeper"]["next_score"]))
    for index, player in enumerate(lineup["bench_outfield"], 1):
        table.add_row(f"Bench {index}", Text(player["player"]), str(player["next_score"]))
    console.print(table)
    for warning in lineup["warnings"]:
        console.print(warning, markup=False, style="yellow")



def print_transfer_options(report):
    from rich.text import Text
    console.print(report["note"], markup=False)
    if not report["options"]:
        return
    table = Table(title="Single-transfer alternatives (not a combined plan)")
    for heading in ("Out", "In", "Heuristic gain", "Bank after", "Why"):
        table.add_column(heading)
    for option in report["options"]:
        table.add_row(Text(option["out"]), Text(option["in"]), str(option["gain"]),
                      f"£{option['bank_after']/10:.1f}", Text(option["reason"]))
    console.print(table)



def print_price_changes(report):
    from rich.text import Text
    if report["since"] is None:
        console.print("Price baseline saved. Run again later to compare; no prediction made.", markup=False)
        return
    table = Table(title=f"Observed price changes since {report['since']} (not predictions)")
    for heading in ("Player", "Old price", "New price", "Change"):
        table.add_column(heading)
    for change in report["changes"]:
        table.add_row(Text(change["player"]), f"£{change['old_cost']/10:.1f}",
                      f"£{change['new_cost']/10:.1f}", f"{change['change']/10:+.1f}")
    console.print(table)
