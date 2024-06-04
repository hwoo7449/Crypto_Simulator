import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QLabel, QLineEdit, QHBoxLayout, QComboBox, QProgressBar
from PyQt5.QtCore import QTimer
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.pyplot import rcParams
import matplotlib.pyplot as plt
import random
import datetime
from Methods import ConfigLoader

class Coin:
    def __init__(self, name, index):
        self.name = name
        self.prices = [[], []]
        self.index = index
        self.set_start_price()
        
    def set_start_price(self):
        # 초기 코인 가격 설정
        start_coin_price = [int(price) for price in ConfigLoader('config.ini').get_setting('Init', 'StartCoinPrice').split('|')]
        self.prices[0].append(ConfigLoader('config.ini').get_setting('Init', 'StartDate'))
        self.prices[1].append(random.randint(start_coin_price[0], start_coin_price[1]))
    
    def price_change(self, date):
        # 코인 가격 변동
        self.prices[0].append(date)
        coin_price_coverage = [int(price) for price in ConfigLoader('config.ini').get_setting('Init', 'CoinPriceCoverage').split('|')]
        self.prices[1].append(self.prices[1][-1] + random.randint(coin_price_coverage[0], coin_price_coverage[1]))
        
class GraphSystem:
    def __init__(self):
        super().__init__()
        plt.style.use(['seaborn-v0_8-notebook'])  # 스타일 설정
        
        self.figure = plt.figure()
        self.DS = DateSystem()
        self.coins = []
        self.axe = self.figure.add_subplot(111)
        self.axe.set_xlabel(ConfigLoader('config.ini').get_setting('Graph', 'xlabel'))
        self.axe.set_ylabel(ConfigLoader('config.ini').get_setting('Graph', 'ylabel'))
        self.axe.set_title(ConfigLoader('config.ini').get_setting('Graph', 'title'))
        self.max_points = int(ConfigLoader('config.ini').get_setting('Graph', 'max_points'))
        
    def add_new_coin(self, coin: Coin):
        # 새로운 코인 추가
        self.coins.append(coin)
        
    def next_step(self):
        # 다음 단계로 넘어가면서 코인 가격 갱신
        self.axe.clear()
        self.axe.set_xlabel(ConfigLoader('config.ini').get_setting('Graph', 'xlabel'))
        self.axe.set_ylabel(ConfigLoader('config.ini').get_setting('Graph', 'ylabel'))
        self.axe.set_title(ConfigLoader('config.ini').get_setting('Graph', 'title'))

        for coin in self.coins:
            coin.price_change(self.DS.get_cur_date_str())
            
            # 최대 점의 개수를 초과하면 오래된 데이터를 제거
            if len(coin.prices[0]) > self.max_points:
                coin.prices[0] = coin.prices[0][-self.max_points:]
                coin.prices[1] = coin.prices[1][-self.max_points:]
            
            self.axe.plot(coin.prices[0], coin.prices[1], label=coin.name)
        
        # 날짜 변경
        self.DS.go_next_date()
        # 범례 추가
        self.axe.legend(loc='upper right')
        # x축 날짜 레이블 포맷팅
        self.figure.autofmt_xdate()

class DateSystem:
    def __init__(self):
        self.date = datetime.datetime.strptime(ConfigLoader('config.ini').get_setting('Init', 'StartDate'), "%Y-%m-%d")
        
    def get_cur_date_str(self):
        # 현재 날짜 문자열 반환
        return self.date.strftime("%Y-%m-%d")
    
    def go_next_date(self):
        # 다음 날짜로 이동
        self.date += datetime.timedelta(days=1)
        
class PlayerSystem:
    def __init__(self):
        self.config_loader = ConfigLoader('config.ini')
        self.initial_funds = float(self.config_loader.get_setting('Player', 'InitialFunds'))
        self.cash = self.initial_funds
        self.portfolio = {}  # {coin_name: quantity}
    
    def buy_coin(self, coin_name, quantity, price):
        cost = quantity * price
        if self.cash >= cost:
            self.cash -= cost
            if coin_name in self.portfolio:
                self.portfolio[coin_name] += quantity
            else:
                self.portfolio[coin_name] = quantity
            return True
        else:
            return False
    
    def sell_coin(self, coin_name, quantity, price):
        if coin_name in self.portfolio and self.portfolio[coin_name] >= quantity:
            self.portfolio[coin_name] -= quantity
            self.cash += quantity * price
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
        
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.GS = GraphSystem()
        self.PS = PlayerSystem()
        self.initUI()
        
        self.day_interval = int(ConfigLoader('config.ini').get_setting('Simulation', 'DayInterval'))
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_progress)
        self.timer.start(self.day_interval // 4)
        self.progress_step = self.day_interval // 4
        self.current_progress = 0
    
    def update_progress(self):
        self.current_progress += 1
        self.progress_bar.setValue(self.current_progress * 25)
        
        if self.current_progress >= 4:
            self.notify_next_step()
            self.current_progress = 0
    
    def notify_next_step(self):
        self.GS.next_step()
        self.update_portfolio()
        self.update_coin_info()
        self.canvas.draw()

    def make_coin(self, name):
        self.GS.add_new_coin(Coin(name, len(self.GS.coins)))
        self.coin_selector.addItem(name)

    def buy_coin(self):
        coin_name = self.coin_selector.currentText()
        quantity = float(self.quantity_input.text())
        price = self.GS.coins[self.coin_selector.currentIndex()].prices[1][-1]
        if self.PS.buy_coin(coin_name, quantity, price):
            self.update_portfolio()
    
    def sell_coin(self):
        coin_name = self.coin_selector.currentText()
        quantity = float(self.quantity_input.text())
        price = self.GS.coins[self.coin_selector.currentIndex()].prices[1][-1]
        if self.PS.sell_coin(coin_name, quantity, price):
            self.update_portfolio()

    def update_portfolio(self):
        portfolio_str = '\n'.join([f"{coin}: {quantity}" for coin, quantity in self.PS.portfolio.items()])
        self.portfolio_label.setText(f"Portfolio:\n{portfolio_str}\nCash: {self.PS.cash}")

    def update_coin_info(self):
        coin_name = self.coin_selector.currentText()
        if coin_name:
            price = self.GS.coins[self.coin_selector.currentIndex()].prices[1][-1]
            self.current_price_label.setText(f"Current Price: {price}")
            quantity = float(self.quantity_input.text()) if self.quantity_input.text() else 0
            total_cost = price * quantity
            self.total_cost_label.setText(f"Total Cost: {total_cost}")

    def initUI(self):
        self.setWindowTitle('Crypto Simulator')
        
        self.main_widget = QWidget(self)
        self.setCentralWidget(self.main_widget)
        layout = QHBoxLayout(self.main_widget)

        self.canvas = FigureCanvas(self.GS.figure)
        layout.addWidget(self.canvas)
        
        right_panel = QVBoxLayout()

        self.portfolio_label = QLabel("Portfolio:\nCash: 0")
        self.portfolio_label.setStyleSheet("background-color: white; padding: 10px;")
        right_panel.addWidget(self.portfolio_label)

        coin_control_layout = QVBoxLayout()
        self.coin_selector = QComboBox()
        self.coin_selector.currentIndexChanged.connect(self.update_coin_info)
        coin_control_layout.addWidget(self.coin_selector)

        self.current_price_label = QLabel("Current Price: 0")
        coin_control_layout.addWidget(self.current_price_label)

        self.quantity_input = QLineEdit()
        self.quantity_input.setPlaceholderText("Quantity")
        self.quantity_input.textChanged.connect(self.update_coin_info)
        coin_control_layout.addWidget(self.quantity_input)

        self.total_cost_label = QLabel("Total Cost: 0")
        coin_control_layout.addWidget(self.total_cost_label)

        self.buy_button = QPushButton("Buy")
        self.buy_button.clicked.connect(self.buy_coin)
        coin_control_layout.addWidget(self.buy_button)

        self.sell_button = QPushButton("Sell")
        self.sell_button.clicked.connect(self.sell_coin)
        coin_control_layout.addWidget(self.sell_button)

        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximum(100)
        coin_control_layout.addWidget(self.progress_bar)

        right_panel.addLayout(coin_control_layout)
        layout.addLayout(right_panel)

if __name__ == '__main__':
    # matplotlib 폰트 설정
    rcParams['font.family'] = 'Malgun Gothic'
    rcParams['axes.unicode_minus'] = False
    
    # 애플리케이션 실행
    app = QApplication(sys.argv)
    window = MainWindow()
    
    # 디버그용 코인 추가
    window.make_coin("BTC")
    window.make_coin("ETH")
    window.setGeometry(100, 100, 800, 600)
    window.show()
    
    # 애플리케이션 실행 종료
    sys.exit(app.exec_())