import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QLabel, QLineEdit, QHBoxLayout, QComboBox, QProgressBar, QDockWidget, QTextEdit
from PyQt5.QtCore import QTimer, Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.pyplot import rcParams
from models import GraphSystem, PlayerSystem, EventSystem
from utils import ConfigLoader

class MainWindowUI:
    def setup_ui(self, MainWindow, GS, config_loader):
        MainWindow.setWindowTitle('Crypto Simulator')
        MainWindow.setGeometry(100, 100, 1000, 800)

        self.main_widget = QWidget(MainWindow)
        MainWindow.setCentralWidget(self.main_widget)
        layout = QVBoxLayout(self.main_widget)

        self.event_label = QLabel("", MainWindow)
        self.event_label.setFixedHeight(50)
        self.event_label.setStyleSheet("background-color: yellow; font-size: 16px; qproperty-alignment: AlignCenter;")
        self.event_label.setGeometry(0, -50, MainWindow.width(), 50)

        canvas_layout = QHBoxLayout()
        self.canvas = FigureCanvas(GS.figure)
        canvas_layout.addWidget(self.canvas)

        right_panel = QVBoxLayout()

        self.portfolio_label = QLabel(f"{config_loader.get_setting('Labels', 'PortfolioLabel')}:\n{config_loader.get_setting('Labels', 'CashLabel')}: 0")
        self.portfolio_label.setStyleSheet("background-color: white; padding: 10px;")
        right_panel.addWidget(self.portfolio_label)

        coin_control_layout = QVBoxLayout()
        self.coin_selector = QComboBox()
        self.coin_selector.currentIndexChanged.connect(MainWindow.update_coin_info)
        coin_control_layout.addWidget(self.coin_selector)

        self.current_price_label = QLabel(f"{config_loader.get_setting('Labels', 'CurrentPriceLabel')}: 0")
        coin_control_layout.addWidget(self.current_price_label)

        self.quantity_input = QLineEdit()
        self.quantity_input.setPlaceholderText(config_loader.get_setting('Labels', 'QuantityPlaceholder'))
        self.quantity_input.textChanged.connect(MainWindow.update_coin_info)
        coin_control_layout.addWidget(self.quantity_input)

        self.total_cost_label = QLabel(f"{config_loader.get_setting('Labels', 'TotalCostLabel')}: 0")
        coin_control_layout.addWidget(self.total_cost_label)

        self.buy_button = QPushButton(config_loader.get_setting('Labels', 'BuyButton'))
        self.buy_button.clicked.connect(MainWindow.buy_coin)
        coin_control_layout.addWidget(self.buy_button)

        self.sell_button = QPushButton(config_loader.get_setting('Labels', 'SellButton'))
        self.sell_button.clicked.connect(MainWindow.sell_coin)
        coin_control_layout.addWidget(self.sell_button)

        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximum(100)
        coin_control_layout.addWidget(self.progress_bar)

        right_panel.addLayout(coin_control_layout)
        canvas_layout.addLayout(right_panel)

        layout.addLayout(canvas_layout)

        news_layout = QVBoxLayout()
        news_title = QLabel("최신 뉴스")
        news_title.setStyleSheet("font-size: 18px; font-weight: bold;")
        news_layout.addWidget(news_title)

        self.news_feed = QTextEdit()
        self.news_feed.setReadOnly(True)
        news_layout.addWidget(self.news_feed)

        layout.addLayout(news_layout)

        self.debug_dock = QDockWidget("Debug Info", MainWindow)
        self.debug_text_edit = QTextEdit()
        self.debug_text_edit.setReadOnly(True)
        self.debug_dock.setWidget(self.debug_text_edit)
        MainWindow.addDockWidget(Qt.RightDockWidgetArea, self.debug_dock)
        MainWindow.update_debug_info()

class MainWindow(QMainWindow, MainWindowUI):
    def __init__(self):
        super().__init__()
        self.config_loader = ConfigLoader('config.ini')
        self.GS = GraphSystem()
        self.PS = PlayerSystem()
        self.ES = EventSystem(self.GS, self.PS, self.config_loader)
        self.setup_ui(self, self.GS, self.config_loader)

        self.day_interval = int(self.config_loader.get_setting('Simulation', 'DayInterval'))
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_progress)
        self.timer.start(self.day_interval // 4)
        self.progress_step = self.day_interval // 4
        self.current_progress = 0

        QTimer.singleShot(0, self.notify_next_step)

    def update_progress(self):
        self.current_progress += 1
        self.progress_bar.setValue(self.current_progress * 25)

        if self.current_progress >= 4:
            self.notify_next_step()
            self.current_progress = 0

    def notify_next_step(self):
        self.GS.next_step()
        self.ES.check_for_event(self)
        self.canvas.draw()
        self.update_portfolio()
        self.update_coin_info()
        self.update_debug_info()

    def make_coin(self, name, color=None):
        self.GS.add_new_coin(name, color)
        self.coin_selector.addItem(name)

    def buy_coin(self):
        coin_name = self.coin_selector.currentText()
        quantity = int(self.quantity_input.text())
        price = self.GS.coins[self.coin_selector.currentIndex()].prices[1][-1]
        if self.PS.buy_coin(coin_name, quantity, price):
            self.update_portfolio()
            self.update_debug_info()

    def sell_coin(self):
        coin_name = self.coin_selector.currentText()
        quantity = int(self.quantity_input.text())
        price = self.GS.coins[self.coin_selector.currentIndex()].prices[1][-1]
        if self.PS.sell_coin(coin_name, quantity, price):
            self.update_portfolio()
            self.update_debug_info()

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

    def display_event_message(self, title, message, duration):
        news_item = f"{message}"
        self.news_feed.append(news_item)

    def update_debug_info(self):
        debug_info = "DateSystem:\n"
        debug_info += f"  Current Date: {self.GS.DS.get_cur_date_str()}\n"
        
        debug_info += "\nPlayerSystem:\n"
        debug_info += f"  Cash: {self.PS.cash}\n"
        debug_info += "  Portfolio:\n"
        for coin, quantity in self.PS.portfolio.items():
            debug_info += f"    {coin}: {quantity}\n"
        
        debug_info += "\nGraphSystem:\n"
        debug_info += f"  Coins:\n"
        for coin in self.GS.coins:
            debug_info += f"    {coin.name}: {coin.prices[1][-1]}\n"
        
        debug_info += "\nEventSystem:\n"
        debug_info += f"  Day Counter: {self.ES.day_counter}\n"
        
        self.debug_text_edit.setText(debug_info)

if __name__ == '__main__':
    rcParams['font.family'] = 'Malgun Gothic'
    rcParams['axes.unicode_minus'] = False

    app = QApplication(sys.argv)
    window = MainWindow()

    window.make_coin("BTC", "blue")
    window.make_coin("ETH", "#FF5733")
    window.setGeometry(100, 100, 1000, 800)
    window.show()

    sys.exit(app.exec_())