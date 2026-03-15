import unittest
from accounts import Account, get_share_price

class TestAccount(unittest.TestCase):

    def setUp(self):
        self.account = Account('user123', 1000.00)

    def test_initialization(self):
        self.assertEqual(self.account.user_id, 'user123')
        self.assertEqual(self.account.balance, 1000.00)
        self.assertEqual(self.account.portfolio, {})
        self.assertEqual(self.account.transactions, [])

    def test_deposit(self):
        self.account.deposit(300.00)
        self.assertEqual(self.account.balance, 1300.00)
        self.assertIn('Deposited: $300.0', self.account.transactions)
        
        with self.assertRaises(ValueError):
            self.account.deposit(-50.00)

    def test_withdraw(self):
        self.account.withdraw(200.00)
        self.assertEqual(self.account.balance, 800.00)
        self.assertIn('Withdrew: $200.0', self.account.transactions)
        
        with self.assertRaises(ValueError):
            self.account.withdraw(1500.00)
        
        with self.assertRaises(ValueError):
            self.account.withdraw(-50.00)

    def test_buy_shares(self):
        self.account.buy_shares('AAPL', 2)
        self.assertEqual(self.account.balance, 700.00)
        self.assertEqual(self.account.portfolio['AAPL'], 2)
        self.assertIn('Bought: 2 shares of AAPL at $150.0 each', self.account.transactions)
        
        with self.assertRaises(ValueError):
            self.account.buy_shares('AAPL', 10)

    def test_sell_shares(self):
        self.account.buy_shares('AAPL', 2)
        self.account.sell_shares('AAPL', 1)
        self.assertEqual(self.account.portfolio['AAPL'], 1)
        self.assertEqual(self.account.balance, 850.00)
        self.assertIn('Sold: 1 shares of AAPL at $150.0 each', self.account.transactions)
        
        with self.assertRaises(ValueError):
            self.account.sell_shares('AAPL', 5)

    def test_total_portfolio_value(self):
        self.account.buy_shares('AAPL', 2)
        self.account.buy_shares('TSLA', 1)
        self.assertAlmostEqual(self.account.total_portfolio_value(), 850.00 + 150.00 * 2 + 700.00, places=2)

    def test_profit_or_loss(self):
        self.assertEqual(self.account.profit_or_loss(), 0.00)
        self.account.deposit(500.00)
        self.assertEqual(self.account.profit_or_loss(), 500.00)
        self.account.buy_shares('AAPL', 2)
        self.assertGreater(self.account.profit_or_loss(), 0)

    def test_report_holdings(self):
        self.assertEqual(self.account.report_holdings(), {})
        self.account.buy_shares('AAPL', 2)
        self.assertEqual(self.account.report_holdings(), {'AAPL': 2})

    def test_report_profit_or_loss(self):
        self.assertEqual(self.account.report_profit_or_loss(), 0.00)

    def test_list_transactions(self):
        self.account.deposit(100.00)
        self.assertIn('Deposited: $100.0', self.account.list_transactions())

if __name__ == '__main__':
    unittest.main()