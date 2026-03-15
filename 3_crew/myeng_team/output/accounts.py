class Account:
    """
    A class to represent a user account in a trading simulation platform.
    """

    def __init__(self, user_id: str, initial_deposit: float):
        """
        Initializes the account with a unique user ID and an initial deposit.

        Args:
            user_id (str): Unique identifier for the account holder.
            initial_deposit (float): Initial deposit amount for the account.
        """
        self.user_id = user_id
        self.balance = initial_deposit
        self.portfolio = {}  # {symbol: quantity}
        self.transactions = []  # List of transaction records

    def deposit(self, amount: float) -> None:
        """
        Deposits funds into the user's account.

        Args:
            amount (float): Amount to deposit.
        """
        if amount <= 0:
            raise ValueError("Deposit amount must be greater than zero.")
        self.balance += amount
        self.transactions.append(f'Deposited: ${amount}')

    def withdraw(self, amount: float) -> None:
        """
        Withdraws funds from the user's account.

        Args:
            amount (float): Amount to withdraw.
        """
        if amount <= 0:
            raise ValueError("Withdrawal amount must be greater than zero.")
        if amount > self.balance:
            raise ValueError("Insufficient funds for this withdrawal.")
        self.balance -= amount
        self.transactions.append(f'Withdrew: ${amount}')

    def buy_shares(self, symbol: str, quantity: int) -> None:
        """
        Records the purchase of shares by the user.

        Args:
            symbol (str): The stock symbol for the shares.
            quantity (int): Amount of shares to buy.
        """
        price = get_share_price(symbol)
        total_cost = price * quantity
        if total_cost > self.balance:
            raise ValueError("Not enough funds to buy these shares.")
        
        self.balance -= total_cost
        if symbol in self.portfolio:
            self.portfolio[symbol] += quantity
        else:
            self.portfolio[symbol] = quantity
        self.transactions.append(f'Bought: {quantity} shares of {symbol} at ${price} each')

    def sell_shares(self, symbol: str, quantity: int) -> None:
        """
        Records the sale of shares by the user.

        Args:
            symbol (str): The stock symbol for the shares.
            quantity (int): Amount of shares to sell.
        """
        if symbol not in self.portfolio or self.portfolio[symbol] < quantity:
            raise ValueError("Not enough shares to sell.")
        
        price = get_share_price(symbol)
        total_income = price * quantity
        self.balance += total_income
        self.portfolio[symbol] -= quantity
        
        if self.portfolio[symbol] == 0:
            del self.portfolio[symbol]
        
        self.transactions.append(f'Sold: {quantity} shares of {symbol} at ${price} each')

    def total_portfolio_value(self) -> float:
        """
        Calculates the total value of the user's portfolio.

        Returns:
            float: Total value of the user's shares in the portfolio.
        """
        total_value = self.balance
        for symbol, quantity in self.portfolio.items():
            total_value += get_share_price(symbol) * quantity
        return total_value

    def profit_or_loss(self) -> float:
        """
        Calculates the profit or loss from the initial deposit.

        Returns:
            float: Profit or loss amount.
        """
        return self.total_portfolio_value() - self.balance

    def report_holdings(self) -> dict:
        """
        Reports the current holdings of the user.

        Returns:
            dict: A dictionary of the user's portfolio holdings.
        """
        return self.portfolio

    def report_profit_or_loss(self) -> float:
        """
        Reports the current profit or loss.

        Returns:
            float: Current profit or loss amount.
        """
        return self.profit_or_loss()

    def list_transactions(self) -> list:
        """
        Lists all transactions made by the user.

        Returns:
            list: List of transaction records.
        """
        return self.transactions


def get_share_price(symbol: str) -> float:
    """
    Gets the current price of a share based on the stock symbol.

    Args:
        symbol (str): The stock symbol (AAPL, TSLA, GOOGL).

    Returns:
        float: The price of the share.
    """
    prices = {
        'AAPL': 150.00,
        'TSLA': 700.00,
        'GOOGL': 2800.00
    }
    return prices.get(symbol, 0)  # Returning 0 for any unrecognized symbol.