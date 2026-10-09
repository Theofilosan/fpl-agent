"""Independent single-transfer alternatives. Never infer bank or points gains."""

from collections import Counter

from squad_strategy import squad_rankings


def transfer_options(squad, rankings, bank=None, free_transfers=None, limit=5):
    squad = squad_rankings(
        [
            {"element": p["player_id"], "selling_price": p.get("selling_price")}
            for p in squad
        ],
        squad,
    )
    if (
        bank is None
        or free_transfers is None
        or any(p["selling_price"] is None for p in squad)
    ):
        return {
            "options": [],
            "note": "Skipped: confirm bank, remaining free transfers and all selling prices.",
        }
    if not isinstance(bank, int) or bank < 0 or free_transfers not in range(6):
        raise ValueError(
            "Bank must be non-negative integer tenths; free transfers must be 0-5."
        )
    if any(
        not isinstance(p["selling_price"], int) or p["selling_price"] < 0 for p in squad
    ):
        raise ValueError("Selling prices must be non-negative integer tenths.")
    if free_transfers == 0:
        return {
            "options": [],
            "note": "No free transfers: hold. Heuristic scores cannot justify a points hit.",
        }
    owned = {p["player_id"] for p in squad}
    counts = Counter(p["team_id"] for p in squad)
    options = []
    for sell in squad:
        for buy in rankings:
            if buy["player_id"] in owned or buy["position_id"] != sell["position_id"]:
                continue
            if buy["availability"] < 1 or not buy["fixtures"]:
                continue
            after = bank + sell["selling_price"] - buy["cost"]
            if (
                after < 0
                or counts[buy["team_id"]] - (sell["team_id"] == buy["team_id"]) >= 3
            ):
                continue
            gain = round(buy["score"] - sell["score"], 3)
            if gain > 0.5:
                options.append(
                    {
                        "out": sell["player"],
                        "in": buy["player"],
                        "out_id": sell["player_id"],
                        "in_id": buy["player_id"],
                        "gain": gain,
                        "bank_after": after,
                        "reason": buy["reason"],
                    }
                )
    return {
        "options": sorted(options, key=lambda p: p["gain"], reverse=True)[:limit],
        "note": "Independent alternatives, NOT a sequence. Gain is heuristic units, NOT expected points. Review before acting.",
    }
