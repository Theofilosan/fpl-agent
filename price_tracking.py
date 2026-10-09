"""Track observed price changes between local runs, never predict changes."""

import json
from datetime import datetime, timezone
from pathlib import Path


def track_prices(players, path):
    path = Path(path)
    previous = json.loads(path.read_text()) if path.exists() else None
    current = {str(p["id"]): p["now_cost"] for p in players}
    changes = []
    if previous:
        for player in players:
            before = previous["prices"].get(str(player["id"]))
            if before is not None and before != player["now_cost"]:
                changes.append(
                    {
                        "player_id": player["id"],
                        "player": player["web_name"],
                        "old_cost": before,
                        "new_cost": player["now_cost"],
                        "change": player["now_cost"] - before,
                    }
                )
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(
        json.dumps(
            {
                "recorded_at": datetime.now(timezone.utc).isoformat(),
                "prices": current,
                "schema_version": 1,
            }
        )
    )
    temp.replace(path)
    return {"since": previous["recorded_at"] if previous else None, "changes": changes}
