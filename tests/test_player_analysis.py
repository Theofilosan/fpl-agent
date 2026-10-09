import unittest

from player_analysis import availability, score_players


def player(**overrides):
    return dict(
        {
            "id": 1,
            "web_name": "Example",
            "team": 1,
            "element_type": 3,
            "now_cost": 50,
            "minutes": 450,
            "form": "6",
            "points_per_game": "6",
            "status": "a",
            "chance_of_playing_next_round": None,
        },
        **overrides
    )


def fixture(event, *, team=1, finished=False, difficulty=3):
    return {
        "team_id": team,
        "gameweek": event,
        "finished": finished,
        "difficulty": difficulty,
        "kickoff_time": None,
    }


class PlayerScoringTests(unittest.TestCase):
    def setUp(self):
        self.past = [fixture(gw, finished=True) for gw in range(1, 6)]

    def score(self, raw=None, future=None, horizon=1):
        return score_players([raw or player()], self.past + (future or []), 6, horizon)[
            0
        ]

    def test_regular_player_at_season_start_is_not_called_rotation(self):
        p = self.score(future=[fixture(6)])
        self.assertEqual(p["minutes_share"], 1)
        self.assertEqual(p["score"], 6)

    def test_blank_is_zero(self):
        self.assertEqual(self.score()["next_score"], 0)

    def test_double_counts_both_fixtures(self):
        self.assertEqual(self.score(future=[fixture(6), fixture(6)])["next_score"], 12)

    def test_horizon_counts_blank_gameweeks(self):
        self.assertEqual(self.score(future=[fixture(6)], horizon=2)["score"], 3)

    def test_finished_fixture_is_not_scored_again(self):
        self.assertEqual(self.score(future=[fixture(6, finished=True)])["score"], 0)

    def test_next_week_and_horizon_are_separate(self):
        p = self.score(future=[fixture(7)], horizon=2)
        self.assertEqual(p["next_score"], 0)
        self.assertGreater(p["score"], 0)

    def test_small_sample_is_damped(self):
        self.assertLess(self.score(player(minutes=90), [fixture(6)])["score"], 6)

    def test_no_history_is_not_invented(self):
        p = score_players([player()], [fixture(1)], 1, 1)[0]
        self.assertEqual(p["score"], 0)

    def test_unknown_doubt_is_not_fully_fit(self):
        self.assertEqual(availability(player(status="d")), 0.75)

    def test_injury_and_probability(self):
        self.assertEqual(availability(player(status="i")), 0)
        self.assertEqual(availability(player(chance_of_playing_next_round=50)), 0.5)

    def test_removed_and_unselectable_players(self):
        self.assertEqual(availability(player(removed=True)), 0)
        self.assertEqual(availability(player(can_select=False)), 0)

    def test_invalid_horizon(self):
        with self.assertRaises(ValueError):
            self.score(horizon=0)


if __name__ == "__main__":
    unittest.main()
