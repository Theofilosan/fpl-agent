"""Explainable player rankings. Scores are heuristic units, not expected points."""

from data import get_team_fixtures


def availability(player):
    if not player.get("can_select", True) or player.get("removed", False):
        return 0.0
    if player.get("status") in {"i", "s", "u", "n"}:
        return 0.0
    chance = player.get("chance_of_playing_next_round")
    if chance is not None:
        return max(0, min(100, chance)) / 100
    return 0.75 if player.get("status") == "d" else 1.0


def fixture_weight(fixture):
    difficulty = fixture.get("difficulty")
    return (6 - difficulty) / 3 if difficulty in range(1, 6) else 1.0


def score_players(players, fixtures, gameweek, horizon=5):
    """Blend form/PPG with fixture count, historical minutes and availability.

    A blank counts zero, a double counts twice. Minutes are scaled against
    completed team matches, rather than a fixed full-season maximum.
    """
    if not 1 <= horizon <= 38 or not 1 <= gameweek <= 38:
        raise ValueError("Gameweek and horizon must be in the range 1-38.")
    result = []
    for raw in players:
        upcoming = [
            f
            for f in get_team_fixtures(fixtures, raw["team"], gameweek, horizon)
            if not f.get("finished", False)
        ]
        played = sum(
            f["team_id"] == raw["team"]
            and f.get("finished", False)
            and f["gameweek"] < gameweek
            for f in fixtures
        )
        minutes = float(raw.get("minutes", 0) or 0)
        share = min(1, minutes / (90 * played)) if played else 0
        confidence = min(1, minutes / 450)
        form = float(raw.get("form", 0) or 0)
        ppg = float(raw.get("points_per_game", 0) or 0)
        quality = (0.6 * form + 0.4 * ppg) * share * confidence * availability(raw)
        score = quality * sum(map(fixture_weight, upcoming)) / horizon
        next_score = quality * sum(
            fixture_weight(f) for f in upcoming if f["gameweek"] == gameweek
        )
        result.append(
            {
                "player_id": raw["id"],
                "player": raw["web_name"],
                "team_id": raw["team"],
                "position_id": raw["element_type"],
                "cost": raw["now_cost"],
                "score": round(score, 3),
                "next_score": round(next_score, 3),
                "value_score": (
                    round(score / (raw["now_cost"] / 10), 3) if raw["now_cost"] else 0
                ),
                "availability": availability(raw),
                "minutes_share": round(share, 3),
                "fixtures": upcoming,
                "news": raw.get("news", ""),
                "reason": f"form {form:.1f}; PPG {ppg:.1f}; minutes {share:.0%}; availability {availability(raw):.0%}; {len(upcoming)} fixtures/{horizon} GWs",
            }
        )
    return sorted(result, key=lambda p: (p["score"], p["player_id"]), reverse=True)
