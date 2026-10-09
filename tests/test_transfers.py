import unittest

from tests.test_squad_strategy import squad
from transfers import transfer_options


class TransferOptionsTests(unittest.TestCase):
    def setUp(self):
        self.team = squad()
        for p in self.team:
            p.update(
                selling_price=50, cost=55, fixtures=[{}], reason="example", score=1
            )
        self.buy = dict(
            self.team[-1], player_id=100, player="Target", team_id=10, cost=60, score=5
        )

    def options(self, buy=None, bank=10, free=1):
        return transfer_options(self.team, [buy or self.buy], bank, free)["options"]

    def test_affordable_same_position_options(self):
        results = self.options()
        self.assertEqual(len(results), 3)
        self.assertTrue(all(x["out_id"] in (13, 14, 15) for x in results))
        self.assertTrue(all(x["bank_after"] == 0 for x in results))

    def test_market_price_is_not_selling_price(self):
        self.assertFalse(self.options(bank=5))

    def test_club_limit_and_same_club_replacement(self):
        blocked = dict(self.buy, team_id=2)
        self.assertFalse(self.options(blocked))
        allowed = dict(self.buy, team_id=5)
        self.assertEqual({p["out_id"] for p in self.options(allowed)}, {13, 14})

    def test_owned_target_excluded(self):
        self.assertFalse(self.options(dict(self.buy, player_id=13)))

    def test_doubt_and_blank_target_excluded(self):
        self.assertFalse(self.options(dict(self.buy, availability=0.75)))
        self.assertFalse(self.options(dict(self.buy, fixtures=[])))

    def test_missing_bank_free_transfers_or_prices_skip(self):
        self.assertFalse(self.options(bank=None))
        self.assertFalse(self.options(free=None))
        self.team[0]["selling_price"] = None
        self.assertFalse(self.options())

    def test_zero_free_transfers_recommends_hold(self):
        report = transfer_options(self.team, [self.buy], 10, 0)
        self.assertFalse(report["options"])
        self.assertIn("hold", report["note"])

    def test_insignificant_gain_is_not_suggested(self):
        self.assertFalse(self.options(dict(self.buy, score=1.5)))

    def test_invalid_financial_inputs_fail(self):
        for bank, free in [(-1, 1), (1.5, 1), (0, -1), (0, 6)]:
            with self.assertRaises(ValueError):
                self.options(bank=bank, free=free)

    def test_limit_and_no_mutation(self):
        before = [p.copy() for p in self.team]
        self.assertEqual(
            len(transfer_options(self.team, [self.buy], 10, 1, limit=1)["options"]), 1
        )
        self.assertEqual(self.team, before)


if __name__ == "__main__":
    unittest.main()
