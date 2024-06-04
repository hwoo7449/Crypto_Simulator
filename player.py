from Methods import ConfigLoader

class PlayerSystem:
    def __init__(self):
        self.config_loader = ConfigLoader('config.ini')
        self.initial_funds = int(float(self.config_loader.get_setting('Player', 'InitialFunds')))
        self.cash = self.initial_funds
        self.portfolio = {}  # {coin_name: quantity}
    
    def buy_coin(self, coin_name, quantity, price):
        if price <= 0:
            return False
        
        cost = int(quantity * price)
        if self.cash >= cost:
            self.cash -= cost
            if coin_name in self.portfolio:
                self.portfolio[coin_name] += int(quantity)
            else:
                self.portfolio[coin_name] = int(quantity)
            return True
        else:
            return False
    
    def sell_coin(self, coin_name, quantity, price):
        if coin_name in self.portfolio and self.portfolio[coin_name] >= quantity:
            self.portfolio[coin_name] -= int(quantity)
            self.cash += int(quantity * price)
            if self.portfolio[coin_name] == 0:
                del self.portfolio[coin_name]
            return True
        else:
            return False
    
    def get_portfolio_value(self, coin_prices):
        total_value = self.cash
        for coin_name, quantity in self.portfolio.items():
            total_value += quantity * coin_prices[coin_name]
        return total_value