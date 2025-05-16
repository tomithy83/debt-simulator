import unittest
from strategies import snowball_strategy
import pandas as pd

class TestStrategies(unittest.TestCase):
    def test_snowball_strategy_basic(self):
        debts = pd.DataFrame([
            {"Remaining": 1000, "Rate": 5, "PaidOff": False},
            {"Remaining": 500, "Rate": 10, "PaidOff": False}
        ])
        plan = [0] * len(debts)
        extra = 200

        allocation = snowball_strategy(debts, plan, extra)
        self.assertEqual(sum(allocation), extra)
        self.assertTrue(all(i >= 0 for i in allocation))

if __name__ == '__main__':
    unittest.main()
