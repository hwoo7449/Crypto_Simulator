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
    def __init__(self, name, index, color=None):
        self.name = name
        self.prices = [[], []]
        self.index = index
        self.color = color if color else "#{:06x}".format(random.randint(0, 0xFFFFFF))  # 지정된 색깔이 없을 경우 랜덤 색상 지정
        self.delisted = False  # 상장폐지 여부를 가리키는 변수
        self.set_start_price()
        
    def set_start_price(self):
        config_loader = ConfigLoader('config.ini')
        start_coin_price = [int(price) for price in config_loader.get_setting('Init', 'StartCoinPrice').split('|')]
        start_date = config_loader.get_setting('Init', 'StartDate')
        self.prices[0].append(start_date)
        self.prices[1].append(random.randint(start_coin_price[0], start_coin_price[1]))

    def price_change(self, date):
        if not self.delisted:  # 상장폐지가 되지 않은 경우에만 가격 변동
            coin_price_coverage = [int(price) for price in ConfigLoader('config.ini').get_setting('Init', 'CoinPriceCoverage').split('|')]
            new_price = self.prices[1][-1] + random.randint(coin_price_coverage[0], coin_price_coverage[1])
            
            if new_price <= 0:  # 가격이 0 이하로 내려가면 상장폐지 처리
                new_price = 0
                self.delisted = True

            self.prices[0].append(date)
            self.prices[1].append(new_price)
        else:
            # 상장폐지된 경우, 가격 0을 유지
            self.prices[0].append(date)
            self.prices[1].append(0)
        
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
        self.initial_date_passed = False  # 초기 날짜를 지나기 전 상태를 추적
        self.annotations = []  # 가격 주석을 저장할 리스트
        
    def add_new_coin(self, name, color=None):
        coin = Coin(name, len(self.coins), color)
        self.coins.append(coin)
        
    def next_step(self):
        self.axe.clear()
        self.axe.set_xlabel(ConfigLoader('config.ini').get_setting('Graph', 'xlabel'))
        self.axe.set_ylabel(ConfigLoader('config.ini').get_setting('Graph', 'ylabel'))
        self.axe.set_title(ConfigLoader('config.ini').get_setting('Graph', 'title'))
        
        for annotation in self.annotations:
            annotation.remove()  # 이전 주석 제거
        self.annotations.clear()
        
        for coin in self.coins:
            if self.initial_date_passed:  # 초기 날짜를 지난 경우에만 가격을 변경
                coin.price_change(self.DS.get_cur_date_str())
            
            if len(coin.prices[0]) > self.max_points:
                coin.prices[0] = coin.prices[0][-self.max_points:]
                coin.prices[1] = coin.prices[1][-self.max_points:]
            
            self.axe.plot(coin.prices[0], coin.prices[1], label=coin.name, color=coin.color)
            
            # 최신 가격을 그래프에 주석으로 추가
            latest_price = coin.prices[1][-1]
            latest_date = coin.prices[0][-1]
            annotation = self.axe.annotate(f'{latest_price}', xy=(latest_date, latest_price),
                                           xytext=(0, -10), textcoords='offset points', ha='center', color=coin.color)
            self.annotations.append(annotation)
        
        self.DS.go_next_date()
        self.axe.legend(loc='best')  # 범례를 빈곳으로 자동 배치
        self.figure.autofmt_xdate()
        self.initial_date_passed = True  # 초기 날짜를 지났음을 표시
        
class DateSystem:
    def __init__(self):
        self.config_loader = ConfigLoader('config.ini')
        self.start_date = datetime.datetime.strptime(self.config_loader.get_setting('Init', 'StartDate'), "%Y-%m-%d")
        self.date = self.start_date
        
    def get_cur_date_str(self):
        return self.date.strftime("%Y-%m-%d")
    
    def go_next_date(self):
        self.date += datetime.timedelta(days=1)

        
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
        
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.config_loader = ConfigLoader('config.ini')
        self.GS = GraphSystem()
        self.PS = PlayerSystem()
        self.initUI()
        
        self.day_interval = int(self.config_loader.get_setting('Simulation', 'DayInterval'))
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

    def make_coin(self, name, color=None):
        self.GS.add_new_coin(name, color)
        self.coin_selector.addItem(name)

    def buy_coin(self):
        coin_name = self.coin_selector.currentText()
        quantity = int(self.quantity_input.text())
        price = self.GS.coins[self.coin_selector.currentIndex()].prices[1][-1]
        if self.PS.buy_coin(coin_name, quantity, price):
            self.update_portfolio()
    
    def sell_coin(self):
        coin_name = self.coin_selector.currentText()
        quantity = int(self.quantity_input.text())
        price = self.GS.coins[self.coin_selector.currentIndex()].prices[1][-1]
        if self.PS.sell_coin(coin_name, quantity, price):
            self.update_portfolio()

    def update_portfolio(self):
        portfolio_str = '\n'.join([f"{coin}: {quantity}" for coin, quantity in self.PS.portfolio.items()])
        self.portfolio_label.setText(f"{self.config_loader.get_setting('Labels', 'PortfolioLabel')}:\n{portfolio_str}\n{self.config_loader.get_setting('Labels', 'CashLabel')}: {self.PS.cash}")

    def update_coin_info(self):
        coin_name = self.coin_selector.currentText()
        if coin_name:
            price = self.GS.coins[self.coin_selector.currentIndex()].prices[1][-1]
            self.current_price_label.setText(f"{self.config_loader.get_setting('Labels', 'CurrentPriceLabel')}: {price}")
            quantity = int(self.quantity_input.text()) if self.quantity_input.text() else 0
            total_cost = price * quantity
            self.total_cost_label.setText(f"{self.config_loader.get_setting('Labels', 'TotalCostLabel')}: {total_cost}")

    def initUI(self):
        self.setWindowTitle('Crypto Simulator')
        
        self.main_widget = QWidget(self)
        self.setCentralWidget(self.main_widget)
        layout = QHBoxLayout(self.main_widget)

        self.canvas = FigureCanvas(self.GS.figure)
        layout.addWidget(self.canvas)
        
        right_panel = QVBoxLayout()

        self.portfolio_label = QLabel(f"{self.config_loader.get_setting('Labels', 'PortfolioLabel')}:\n{self.config_loader.get_setting('Labels', 'CashLabel')}: 0")
        self.portfolio_label.setStyleSheet("background-color: white; padding: 10px;")
        right_panel.addWidget(self.portfolio_label)

        coin_control_layout = QVBoxLayout()
        self.coin_selector = QComboBox()
        self.coin_selector.currentIndexChanged.connect(self.update_coin_info)
        coin_control_layout.addWidget(self.coin_selector)

        self.current_price_label = QLabel(f"{self.config_loader.get_setting('Labels', 'CurrentPriceLabel')}: 0")
        coin_control_layout.addWidget(self.current_price_label)

        self.quantity_input = QLineEdit()
        self.quantity_input.setPlaceholderText(self.config_loader.get_setting('Labels', 'QuantityPlaceholder'))
        self.quantity_input.textChanged.connect(self.update_coin_info)
        coin_control_layout.addWidget(self.quantity_input)

        self.total_cost_label = QLabel(f"{self.config_loader.get_setting('Labels', 'TotalCostLabel')}: 0")
        coin_control_layout.addWidget(self.total_cost_label)

        self.buy_button = QPushButton(self.config_loader.get_setting('Labels', 'BuyButton'))
        self.buy_button.clicked.connect(self.buy_coin)
        coin_control_layout.addWidget(self.buy_button)

        self.sell_button = QPushButton(self.config_loader.get_setting('Labels', 'SellButton'))
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
    window.make_coin("BTC", "blue")  # CSS 색상 이름 사용
    window.make_coin("ETH", "#FF5733") # 16진수 색상 코드 사용
    window.setGeometry(100, 100, 800, 600)
    window.show()
    
    # 애플리케이션 실행 종료
    sys.exit(app.exec_())