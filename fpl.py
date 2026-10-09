from price_tracking import track_prices
from display import print_price_changes
import json
from pathlib import Path
from fpl_api import get_picks
import argparse
from decimal import Decimal, InvalidOperation
from transfers import transfer_options
from display import print_transfer_options


def parse_bank(value):
    try:
        amount = Decimal(value) * 10
        if not amount.is_finite() or amount < 0 or amount != amount.to_integral_value():
            raise ValueError
        return int(amount)
    except (InvalidOperation, ValueError):
        raise argparse.ArgumentTypeError("Bank must be non-negative £m in 0.1 increments, e.g. 1.5.")


from squad_strategy import squad_rankings, choose_lineup
from display import print_lineup
from player_analysis import score_players
from display import print_player_rankings
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
    build_squad_dataset,
)

from analysis import (
    calculate_all_fixture_scores,
    add_fixture_scores_to_players,
    add_player_eligibility,
    analyze_squad,
)

from display import (
    console,
    print_fixture_score_ranking,
    print_gameweek_info,
    print_manager_info,
    print_my_team,
    print_squad_analysis,
)


# ============================================================
# CONFIGURATION
# ============================================================

MANAGER_ID = 6829404

NUMBER_OF_GAMEWEEKS = 5


# ============================================================
# GAMEWEEK STATUS
# ============================================================

def get_gameweek_status(
    bootstrap
):
    """
    Find the current and next Gameweek.

    Returns:

        current_gameweek
        next_gameweek
    """

    events = bootstrap[
        "events"
    ]


    current_gameweek = next(

        (
            event

            for event in events

            if event.get(
                "is_current"
            )
        ),

        None
    )


    next_gameweek = next(

        (
            event

            for event in events

            if event.get(
                "is_next"
            )
        ),

        None
    )


    return (
        current_gameweek,
        next_gameweek
    )


# ============================================================
# MAIN
# ============================================================

def main(argv=None):
    parser = argparse.ArgumentParser(description="Read-only FPL analytics and squad suggestions")
    parser.add_argument("--bank", type=parse_bank, help="Confirmed current bank in £m")
    parser.add_argument("--free-transfers", type=int, choices=range(6), help="Confirmed remaining free transfers")
    parser.add_argument("--entry", type=int, default=MANAGER_ID)
    parser.add_argument("--current", action="store_true", help="Require authenticated current squad (no silent fallback)")
    parser.add_argument("--market-only", action="store_true", help="Only public fixture/player rankings")
    parser.add_argument("--offline", type=Path, help="Directory with bootstrap.json, fixtures.json, manager.json and squad.json")
    parser.add_argument("--snapshot", type=Path, help="Compare/save local observed price baseline")
    args = parser.parse_args(argv)
    if args.entry < 1:
        parser.error("Entry must be positive.")
    def load(name, fetch):
        if args.offline:
            return json.loads((args.offline / (name + ".json")).read_text())
        return fetch()



    # ========================================================
    # HEADER
    # ========================================================

    console.print()

    console.print(
        "=" * 60
    )

    console.print(
        "[bold]FPL AGENT[/bold]"
    )

    console.print(
        "=" * 60
    )


    # ========================================================
    # 1. LOAD FPL DATA
    # ========================================================

    console.print()

    console.print(
        "[bold]Loading FPL data...[/bold]"
    )


    bootstrap = load("bootstrap", get_bootstrap)


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
    # 4. PLAYER ELIGIBILITY
    # ========================================================

    player_dataset = add_player_eligibility(

        player_dataset
    )


    # ========================================================
    # 5. LOAD FIXTURES
    # ========================================================

    console.print()

    console.print(
        "[bold]Loading fixtures...[/bold]"
    )


    fixtures = load("fixtures", get_fixtures)


    console.print(
        f"[green]✓ {len(fixtures)} "
        f"fixtures loaded[/green]"
    )


    # ========================================================
    # 6. BUILD FIXTURE DATASET
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
    # 8. FIXTURE ANALYSIS
    # ========================================================

    player_rankings = []

    if next_gameweek:

        team_fixture_scores = (
            calculate_all_fixture_scores(

                fixture_dataset=fixture_dataset,

                teams=teams,

                start_gameweek=(
                    next_gameweek["id"]
                ),

                number_of_gameweeks=(
                    NUMBER_OF_GAMEWEEKS
                )
            )
        )


        player_rankings = score_players(
            players, fixture_dataset, next_gameweek["id"], NUMBER_OF_GAMEWEEKS
        )
        print_player_rankings(player_rankings, team_map)

        print_fixture_score_ranking(

            team_fixture_scores,

            number_of_gameweeks=(
                NUMBER_OF_GAMEWEEKS
            )
        )


        # ----------------------------------------------------
        # Add Fixture Score to every player
        # ----------------------------------------------------

        player_dataset = (
            add_fixture_scores_to_players(

                player_dataset=player_dataset,

                team_fixture_scores=(
                    team_fixture_scores
                )
            )
        )


    else:

        console.print()

        console.print(
            "[yellow]"
            "No upcoming Gameweek available."
            "[/yellow]"
        )


    # ========================================================
    # 9. LOAD MANAGER
    # ========================================================

    console.print()

    console.print(
        "[bold]Loading manager...[/bold]"
    )


    if args.snapshot:
        print_price_changes(track_prices(players, args.snapshot))

    if args.market_only:
        return

    try:

        manager = load("manager", lambda: get_manager(args.entry))


        console.print(
            "[green]✓ Manager data loaded[/green]"
        )


        print_manager_info(
            manager
        )


    except (RuntimeError, OSError, ValueError) as error:

        console.print(
            "[red]"
            "Could not load manager information."
            "[/red]"
        )


        console.print(
            str(error)
        )


        return 1


    # ========================================================
    # 10. LOAD CURRENT SQUAD
    # ========================================================

    console.print()

    console.print(
        "[bold]Loading current squad...[/bold]"
    )


    try:

        if args.offline:
            my_team = load("squad", None)
            console.print("Offline squad: freshness unverified. Review before acting.", markup=False)
        elif args.current:
            my_team = get_my_team(args.entry)
            console.print("Authenticated current squad", markup=False)
        else:
            event = manager.get("current_event")
            if not event:
                console.print("No published picks yet. Use --current if your squad is set.", markup=False)
                return
            my_team = get_picks(args.entry, event)
            console.print(f"PUBLIC GW{event} DEADLINE PICKS, NOT CURRENT SQUAD. Transfers since that deadline are invisible.", markup=False, style="yellow")


        console.print(
            "[green]✓ Current squad loaded[/green]"
        )


    except (RuntimeError, OSError, ValueError) as error:

        console.print()

        console.print(
            "[red]"
            "Could not load current squad."
            "[/red]"
        )


        console.print(
            str(error)
        )


        return 1


    # ========================================================
    # 11. DISPLAY CURRENT SQUAD
    # ========================================================

    if player_rankings:
        try:
            ranked_squad = squad_rankings(my_team.get("picks", []), player_rankings)
            print_lineup(choose_lineup(ranked_squad))
            print_transfer_options(transfer_options(
                ranked_squad, player_rankings,
                bank=args.bank, free_transfers=args.free_transfers,
            ))
        except ValueError as error:
            console.print(f"Could not suggest a legal lineup: {error}", markup=False)

    print_my_team(

        my_team,

        player_map,

        team_map
    )


    # ========================================================
    # 12. BUILD SQUAD DATASET
    # ========================================================

    squad_dataset = build_squad_dataset(

        my_team,

        player_dataset
    )


    # ========================================================
    # 13. ANALYZE SQUAD
    # ========================================================

    squad_analysis = analyze_squad(

        squad_dataset
    )


    # ========================================================
    # 14. DISPLAY SQUAD ANALYSIS
    # ========================================================

    print_squad_analysis(

        squad_dataset,

        squad_analysis
    )


    # ========================================================
    # COMPLETE
    # ========================================================

    console.print()

    console.print(
        "=" * 60
    )

    console.print(
        "[bold green]"
        "FPL ANALYSIS COMPLETE"
        "[/bold green]"
    )

    console.print(
        "=" * 60
    )

    console.print()


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    import sys
    try:
        sys.exit(main() or 0)
    except (RuntimeError, OSError, ValueError, KeyError) as error:
        print(f"Error: {error}", file=sys.stderr)
        sys.exit(1)
