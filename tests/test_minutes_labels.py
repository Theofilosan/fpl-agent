import unittest

from analysis import add_player_eligibility, classify_player_eligibility


class MinutesLabelsTests(unittest.TestCase):
    def test_full_minutes_early_season_are_established(self):
        self.assertEqual(classify_player_eligibility(450, 450), "Established")

    def test_relative_samples(self):
        self.assertEqual(classify_player_eligibility(90, 450), "Limited")
        self.assertEqual(classify_player_eligibility(180, 450), "Rotation")
        self.assertEqual(classify_player_eligibility(360, 450), "Regular")

    def test_no_history_is_limited_not_invented(self):
        self.assertEqual(classify_player_eligibility(450), "Limited")

    def test_completed_team_fixtures_only_and_ratio_clamp(self):
        players = [{"team_id": 1, "minutes": 180}, {"team_id": 2, "minutes": 90}]
        fixtures = [{"team_id": 1, "finished": True, "gameweek": 1},
                    {"team_id": 1, "finished": False, "gameweek": 2},
                    {"team_id": 1, "finished": True, "gameweek": 3}]
        result = add_player_eligibility(players, fixtures, 3)
        self.assertEqual(result[0]["minutes_ratio"], 1)
        self.assertEqual(result[0]["eligibility"], "Established")
        self.assertEqual(result[1]["minutes_ratio"], 0)
        self.assertEqual(result[1]["eligibility"], "Limited")


if __name__ == "__main__":
    unittest.main()
