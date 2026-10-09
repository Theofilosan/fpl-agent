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
