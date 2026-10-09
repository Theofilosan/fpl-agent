import json
import tempfile
import unittest
from pathlib import Path

from price_tracking import track_prices


class PriceTrackingTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / "cache" / "prices.json"
        self.players = [{"id": 1, "web_name": "Example", "now_cost": 50}]

    def test_first_run_is_baseline_not_a_prediction(self):
        report = track_prices(self.players, self.path)
        self.assertIsNone(report["since"])
        self.assertEqual(report["changes"], [])
        self.assertEqual(json.loads(self.path.read_text())["prices"], {"1": 50})

    def test_rise_and_fall_are_observed_in_integer_tenths(self):
        track_prices(self.players, self.path)
        self.players[0]["now_cost"] = 51
        self.assertEqual(
            track_prices(self.players, self.path)["changes"][0]["change"], 1
        )
        self.players[0]["now_cost"] = 49
        self.assertEqual(
            track_prices(self.players, self.path)["changes"][0]["change"], -2
        )

    def test_unchanged_price_is_quiet(self):
        track_prices(self.players, self.path)
        self.assertEqual(track_prices(self.players, self.path)["changes"], [])

    def test_new_player_has_no_invented_previous_price(self):
        track_prices(self.players, self.path)
        self.players.append({"id": 2, "web_name": "New", "now_cost": 45})
        self.assertEqual(track_prices(self.players, self.path)["changes"], [])

    def test_invalid_previous_json_is_not_overwritten(self):
        self.path.parent.mkdir(parents=True)
        self.path.write_text("invalid")
        with self.assertRaises(ValueError):
            track_prices(self.players, self.path)
        self.assertEqual(self.path.read_text(), "invalid")


if __name__ == "__main__":
    unittest.main()
