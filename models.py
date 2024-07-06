import random
import datetime
import matplotlib.pyplot as plt
from utils import ConfigLoader

class Coin:
    def __init__(self, name, index, start_date, color=None):
        self.name = name
        self.prices = [[], []]
        self.index = index
        self.color = color if color else "#{:06x}".format(random.randint(0, 0xFFFFFF))
        self.delisted = False
        self.set_start_price(start_date)
        self.price_modifier = 1.0
        self.first_appearance = True

    def set_start_price(self, start_date):
        config_loader = ConfigLoader('config.ini')
        start_coin_price = [int(price) for price in config_loader.get_setting('Init', 'StartCoinPrice').split('|')]
        self.prices[0].append(start_date)
        self.prices[1].append(random.randint(start_coin_price[0], start_coin_price[1]))

    def price_change(self, date):
        if self.first_appearance:
            self.first_appearance = False
            self.prices[0].append(date)
            self.prices[1].append(self.prices[1][-1])
            return

        if not self.delisted:
            coin_price_coverage = [int(price) for price in ConfigLoader('config.ini').get_setting('Init', 'CoinPriceCoverage').split('|')]
            new_price = self.prices[1][-1] + random.randint(coin_price_coverage[0], coin_price_coverage[1])
            new_price *= self.price_modifier
            
            if new_price <= 0:
                new_price = 0
                self.delisted = True

            self.prices[0].append(date)
            self.prices[1].append(new_price)
        else:
            self.prices[0].append(date)
            self.prices[1].append(0)
        
        self.price_modifier = 1.0

    def apply_price_modifier(self, modifier):
        self.price_modifier *= modifier

class DateSystem:
    def __init__(self):
        self.config_loader = ConfigLoader('config.ini')
        self.start_date = datetime.datetime.strptime(self.config_loader.get_setting('Init', 'StartDate'), "%Y-%m-%d")
        self.date = self.start_date
        
    def get_cur_date_str(self):
        return self.date.strftime("%Y-%m-%d")
    
    def go_next_date(self):
        self.date += datetime.timedelta(days=1)

class GraphSystem:
    def __init__(self):
        super().__init__()
        plt.style.use(['seaborn-v0_8-notebook'])
        
        self.figure = plt.figure()
        self.DS = DateSystem()
        self.coins = []
        self.axe = self.figure.add_subplot(111)
        self.axe.set_xlabel(ConfigLoader('config.ini').get_setting('Graph', 'xlabel'))
        self.axe.set_ylabel(ConfigLoader('config.ini').get_setting('Graph', 'ylabel'))
        self.axe.set_title(ConfigLoader('config.ini').get_setting('Graph', 'title'))
        self.max_points = int(ConfigLoader('config.ini').get_setting('Graph', 'max_points'))
        self.annotations = []
        
    def add_new_coin(self, name, color=None):
        start_date = self.DS.get_cur_date_str()
        coin = Coin(name, len(self.coins), start_date, color)
        self.coins.append(coin)
        
    def draw_coins(self):
        self.axe.clear()
        self.axe.set_xlabel(ConfigLoader('config.ini').get_setting('Graph', 'xlabel'))
        self.axe.set_ylabel(ConfigLoader('config.ini').get_setting('Graph', 'ylabel'))
        self.axe.set_title(ConfigLoader('config.ini').get_setting('Graph', 'title'))
        
        for annotation in self.annotations:
            annotation.remove()
        self.annotations.clear()
        
        for coin in self.coins:
            if len(coin.prices[0]) > self.max_points:
                coin.prices[0] = coin.prices[0][-self.max_points:]
                coin.prices[1] = coin.prices[1][-self.max_points:]
            
            self.axe.plot(coin.prices[0], coin.prices[1], label=coin.name, color=coin.color)
            
            latest_price = coin.prices[1][-1]
            latest_date = coin.prices[0][-1]
            annotation = self.axe.annotate(f'{latest_price}', xy=(latest_date, latest_price), xytext=(0, -10), textcoords='offset points', ha='center', color=coin.color)
            self.annotations.append(annotation)
        
        self.axe.legend(loc='best')
        self.figure.autofmt_xdate()
        self.initial_date_passed = True

    def next_step(self):
        for coin in self.coins:
            coin.price_change(self.DS.get_cur_date_str())
        
        self.DS.go_next_date()
        self.draw_coins()

class PlayerSystem:
    def __init__(self):
        self.config_loader = ConfigLoader('config.ini')
        self.initial_funds = int(float(self.config_loader.get_setting('Player', 'InitialFunds')))
        self.cash = self.initial_funds
        self.portfolio = {}

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

class Event:
    def execute(self, GS, PS, parent):
        raise NotImplementedError("Subclasses should implement this method")

    def show_message(self, parent, title, message):
        parent.display_event_message(title, message, int(parent.config_loader.get_setting('Events', 'EventDisplayDuration')))

class NewCoinEvent(Event):
    def execute(self, GS, PS, parent):
        coin_name = f"Coin{len(GS.coins) + 1}"
        GS.add_new_coin(coin_name)
        self.show_message(parent, "새로운 코인", f"새로운 코인 {coin_name}이(가) 상장되었습니다!")

class SuddenRiseEvent(Event):
    def execute(self, GS, PS, parent):
        if not GS.coins:
            return
        coin = random.choice(GS.coins)
        if not coin.delisted:
            coin.apply_price_modifier(1.5)
            self.show_message(parent, "급등", f"코인 {coin.name}이(가) 갑자기 50% 상승했습니다!")

class SuddenFallEvent(Event):
    def execute(self, GS, PS, parent):
        if not GS.coins:
            return
        coin = random.choice(GS.coins)
        if not coin.delisted:
            coin.apply_price_modifier(0.5)
            self.show_message(parent, "급락", f"코인 {coin.name}이(가) 갑자기 50% 하락했습니다!")

class DelistEvent(Event):
    def execute(self, GS, PS, parent):
        if not GS.coins:
            return
        coin = random.choice(GS.coins)
        if not coin.delisted:
            coin.delisted = True
            coin.prices[1][-1] = 0
            self.show_message(parent, "상장 폐지", f"코인 {coin.name}이(가) 상장 폐지되었습니다!")

class EventSystem:
    def __init__(self, GS, PS, config_loader):
        self.GS = GS
        self.PS = PS
        self.config_loader = config_loader
        self.event_interval = int(config_loader.get_setting('Events', 'EventInterval'))
        self.events = []
        self.day_counter = 0
        self.load_events()

    def load_events(self):
        self.add_event(NewCoinEvent(), float(self.config_loader.get_setting('Events', 'NewCoinProbability')))
        self.add_event(SuddenRiseEvent(), float(self.config_loader.get_setting('Events', 'SuddenRiseProbability')))
        self.add_event(SuddenFallEvent(), float(self.config_loader.get_setting('Events', 'SuddenFallProbability')))
        self.add_event(DelistEvent(), float(self.config_loader.get_setting('Events', 'DelistProbability')))

    def add_event(self, event, probability):
        self.events.append((event, probability))

    def check_for_event(self, parent):
        self.day_counter += 1
        if self.day_counter % self.event_interval == 0:
            event = self.select_event()
            if event:
                event.execute(self.GS, self.PS, parent)

    def select_event(self):
        total = sum(prob for _, prob in self.events)
        r = random.uniform(0, total)
        upto = 0
        for event, prob in self.events:
            if upto + prob >= r:
                return event
            upto += prob
        return None

