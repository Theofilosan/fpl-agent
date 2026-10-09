import unittest
from collections import Counter

from squad_strategy import choose_lineup, squad_rankings


def squad():
    positions = [1] * 2 + [2] * 5 + [3] * 5 + [4] * 3
    return [
        {
            "player_id": i,
            "player": f"Player {i}",
            "position_id": pos,
            "team_id": i // 3 + 1,
            "next_score": i,
            "score": 100 - i,
            "availability": 1.0,
            "news": "",
        }
        for i, pos in enumerate(positions, 1)
    ]


class SquadStrategyTests(unittest.TestCase):
    def test_legal_formation_and_no_duplicates(self):
        result = choose_lineup(squad())
        count = Counter(p["position_id"] for p in result["xi"])
        self.assertEqual(len(result["xi"]), 11)
        self.assertEqual(count[1], 1)
        self.assertGreaterEqual(count[2], 3)
        self.assertGreaterEqual(count[3], 2)
        self.assertGreaterEqual(count[4], 1)
        all_players = (
            result["xi"] + [result["bench_goalkeeper"]] + result["bench_outfield"]
        )
        self.assertEqual(len({p["player_id"] for p in all_players}), 15)

    def test_captain_and_vice_are_distinct_starters(self):
        result = choose_lineup(squad())
        self.assertIn(result["captain"], result["xi"])
        self.assertIn(result["vice_captain"], result["xi"])
        self.assertNotEqual(result["captain"], result["vice_captain"])
        self.assertEqual(result["captain"]["player_id"], 15)

    def test_uses_next_score_not_horizon_score(self):
        team = squad()
        team[0]["score"] = 1000
        self.assertEqual(choose_lineup(team)["captain"]["player_id"], 15)

    def test_outfield_bench_sorted_and_goalkeeper_separate(self):
        result = choose_lineup(squad())
        self.assertEqual(result["bench_goalkeeper"]["position_id"], 1)
        scores = [p["next_score"] for p in result["bench_outfield"]]
        self.assertEqual(scores, sorted(scores, reverse=True))
        self.assertEqual(len(scores), 3)

    def test_forced_risky_starters_warn(self):
        team = squad()
        for p in team:
            if p["position_id"] == 2:
                p["availability"] = 0
                p["next_score"] = 0
        self.assertGreaterEqual(len(choose_lineup(team)["warnings"]), 3)

    def test_doubt_not_preferred_as_captain(self):
        team = squad()
        team[-1]["availability"] = 0.5
        self.assertNotEqual(choose_lineup(team)["captain"]["player_id"], 15)

    def test_all_blanks_warn(self):
        team = squad()
        for p in team:
            p["next_score"] = 0
        self.assertTrue(choose_lineup(team)["warnings"])

    def test_bad_size_duplicates_positions_club_limit(self):
        cases = [squad()[:-1], [squad()[0]] * 15]
        wrong_positions = squad()
        wrong_positions[0]["position_id"] = 2
        cases.append(wrong_positions)
        wrong_clubs = squad()
        for p in wrong_clubs:
            p["team_id"] = 1
        cases.append(wrong_clubs)
        for team in cases:
            with self.subTest(team=team):
                with self.assertRaises(ValueError):
                    choose_lineup(team)

    def test_missing_player_fails(self):
        with self.assertRaises(ValueError):
            squad_rankings([{"element": i} for i in range(100, 115)], squad())


if __name__ == "__main__":
    unittest.main()
