import argparse
import unittest
from unittest.mock import patch

import fpl


class FinancialArgumentTests(unittest.TestCase):
    def test_bank_uses_exact_integer_tenths(self):
        self.assertEqual(fpl.parse_bank("1.5"), 15)
        self.assertEqual(fpl.parse_bank("0"), 0)
        self.assertEqual(fpl.parse_bank("1.10"), 11)

    def test_bad_bank_values_rejected(self):
        for value in ("-1", "1.01", "NaN", "Infinity", "text"):
            with self.subTest(value=value):
                with self.assertRaises(argparse.ArgumentTypeError):
                    fpl.parse_bank(value)

    def test_help_does_not_call_api(self):
        with patch.object(fpl, "get_bootstrap") as bootstrap:
            with self.assertRaises(SystemExit) as exit:
                fpl.main(["--help"])
            self.assertEqual(exit.exception.code, 0)
            bootstrap.assert_not_called()


if __name__ == "__main__":
    unittest.main()


class PublicCLITests(unittest.TestCase):
    def setUp(self):
        import contextlib
        import io

        self.output = io.StringIO()
        self.redirect = contextlib.redirect_stdout(self.output)
        self.redirect.__enter__()

    def tearDown(self):
        self.redirect.__exit__(None, None, None)

    def test_market_only_never_fetches_manager_or_private_squad(self):
        bootstrap = {"elements": [], "teams": [], "events": []}
        with patch.object(fpl, "get_bootstrap", return_value=bootstrap), patch.object(
            fpl, "get_fixtures", return_value=[]
        ), patch.object(fpl, "get_manager") as manager, patch.object(
            fpl, "get_my_team"
        ) as private:
            fpl.main(["--market-only"])
            manager.assert_not_called()
            private.assert_not_called()

    def test_public_mode_uses_last_published_event_not_next_event(self):
        bootstrap = {"elements": [], "teams": [], "events": []}
        with patch.object(fpl, "get_bootstrap", return_value=bootstrap), patch.object(
            fpl, "get_fixtures", return_value=[]
        ), patch.object(
            fpl, "get_manager", return_value={"current_event": 5}
        ), patch.object(
            fpl, "get_picks", side_effect=RuntimeError("stop after picks")
        ) as picks, patch.object(
            fpl, "get_my_team"
        ) as private, patch.object(
            fpl, "print_manager_info"
        ):
            self.assertEqual(fpl.main(["--entry", "123"]), 1)
            picks.assert_called_once_with(123, 5)
            private.assert_not_called()

    def test_current_mode_never_falls_back_to_public_picks(self):
        bootstrap = {"elements": [], "teams": [], "events": []}
        with patch.object(fpl, "get_bootstrap", return_value=bootstrap), patch.object(
            fpl, "get_fixtures", return_value=[]
        ), patch.object(
            fpl, "get_manager", return_value={"current_event": 5}
        ), patch.object(
            fpl, "get_my_team", side_effect=RuntimeError("invalid token")
        ) as private, patch.object(
            fpl, "get_picks"
        ) as picks, patch.object(
            fpl, "print_manager_info"
        ):
            self.assertEqual(fpl.main(["--entry", "123", "--current"]), 1)
            private.assert_called_once_with(123)
            picks.assert_not_called()
