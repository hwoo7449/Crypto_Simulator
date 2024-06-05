from Methods import ConfigLoader
from coin import Coin
from date import DateSystem
import matplotlib.pyplot as plt

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
        self.annotations = []  # 가격 주석을 저장할 리스트
        
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
            annotation.remove()  # 이전 주석 제거
        self.annotations.clear()
        
        for coin in self.coins:
            if len(coin.prices[0]) > self.max_points:
                coin.prices[0] = coin.prices[0][-self.max_points:]
                coin.prices[1] = coin.prices[1][-self.max_points:]
            
            self.axe.plot(coin.prices[0], coin.prices[1], label=coin.name, color=coin.color)
            
            # 최신 가격을 그래프에 주석으로 추가
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
