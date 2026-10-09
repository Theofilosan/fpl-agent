"""Legal next-gameweek XI, bench and captain choices from heuristic rankings."""

from collections import Counter
from itertools import combinations


def squad_rankings(picks, rankings):
    ids = [p["element"] for p in picks]
    if len(ids) != 15 or len(set(ids)) != 15:
        raise ValueError("Squad must contain 15 distinct players.")
    lookup = {p["player_id"]: p for p in rankings}
    if any(pid not in lookup for pid in ids):
        raise ValueError("Squad contains players absent from the current dataset.")
    squad = [
        dict(lookup[p["element"]], selling_price=p.get("selling_price")) for p in picks
    ]
    if Counter(p["position_id"] for p in squad) != {1: 2, 2: 5, 3: 5, 4: 3}:
        raise ValueError("Squad must have 2 GK, 5 DEF, 5 MID and 3 FWD.")
    if max(Counter(p["team_id"] for p in squad).values()) > 3:
        raise ValueError("Squad exceeds the three-player club limit.")
    return squad


def choose_lineup(squad):
    # Validate even when called independently of squad_rankings.
    squad = squad_rankings(
        [
            {"element": p["player_id"], "selling_price": p.get("selling_price")}
            for p in squad
        ],
        squad,
    )
    keepers = sorted(
        (p for p in squad if p["position_id"] == 1),
        key=lambda p: p["next_score"],
        reverse=True,
    )
    outfield = [p for p in squad if p["position_id"] != 1]
    legal = []
    for group in combinations(outfield, 10):
        count = Counter(p["position_id"] for p in group)
        if 3 <= count[2] <= 5 and 2 <= count[3] <= 5 and 1 <= count[4] <= 3:
            legal.append(group)
    best = max(legal, key=lambda group: sum(p["next_score"] for p in group))
    xi = [keepers[0], *best]
    selected = {p["player_id"] for p in xi}
    bench = sorted(
        (p for p in outfield if p["player_id"] not in selected),
        key=lambda p: p["next_score"],
        reverse=True,
    )
    captain_pool = sorted(xi, key=lambda p: p["next_score"], reverse=True)
    fit = [p for p in captain_pool if p["availability"] == 1 and p["next_score"] > 0]
    # A forced risky XI must not silently give armband priority to an injury doubt.
    captain_pool = fit + [p for p in captain_pool if p not in fit]
    counts = Counter(p["position_id"] for p in best)
    return {
        "xi": sorted(xi, key=lambda p: (p["position_id"], -p["next_score"])),
        "bench_goalkeeper": keepers[1],
        "bench_outfield": bench,
        "captain": captain_pool[0],
        "vice_captain": captain_pool[1],
        "formation": f"{counts[2]}-{counts[3]}-{counts[4]}",
        "warnings": [
            f"{p['player']}: availability {p['availability']:.0%}; {p['news']}"
            for p in xi
            if p["availability"] < 1
        ]
        + (
            ["No fully fit, non-blank captain candidate. Review manually."]
            if not fit
            else []
        ),
    }
