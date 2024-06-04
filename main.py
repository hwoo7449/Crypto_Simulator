import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QLabel, QLineEdit, QHBoxLayout, QComboBox, QProgressBar
from PyQt5.QtCore import QTimer
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.pyplot import rcParams
from Methods import ConfigLoader
from graph import GraphSystem
from player import PlayerSystem
        
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.config_loader = ConfigLoader('config.ini')
        # GraphSystem 및 PlayerSystem 인스턴스를 생성하여 초기화
        self.GS = GraphSystem()
        self.PS = PlayerSystem()
        self.initUI()
        
        # 설정 파일에서 시뮬레이션 간격을 불러와 타이머 설정
        self.day_interval = int(self.config_loader.get_setting('Simulation', 'DayInterval'))
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_progress)
        self.timer.start(self.day_interval // 4)
        self.progress_step = self.day_interval // 4
        self.current_progress = 0
    
    def update_progress(self):
        # 진행 상태를 업데이트하고 프로그레스 바에 반영
        self.current_progress += 1
        self.progress_bar.setValue(self.current_progress * 25)
        
        if self.current_progress >= 4:
            self.notify_next_step()
            self.current_progress = 0
    
    def notify_next_step(self):
        # 다음 스텝을 진행하고 포트폴리오 및 코인 정보를 업데이트
        self.GS.next_step()
        self.update_portfolio()
        self.update_coin_info()
        self.canvas.draw()

    def make_coin(self, name, color=None):
        # 새로운 코인을 생성하고 선택 목록에 추가
        self.GS.add_new_coin(name, color)
        self.coin_selector.addItem(name)

    def buy_coin(self):
        # 코인을 구매하고 포트폴리오를 업데이트
        coin_name = self.coin_selector.currentText()
        quantity = int(self.quantity_input.text())
        price = self.GS.coins[self.coin_selector.currentIndex()].prices[1][-1]
        if self.PS.buy_coin(coin_name, quantity, price):
            self.update_portfolio()
    
    def sell_coin(self):
        # 코인을 판매하고 포트폴리오를 업데이트
        coin_name = self.coin_selector.currentText()
        quantity = int(self.quantity_input.text())
        price = self.GS.coins[self.coin_selector.currentIndex()].prices[1][-1]
        if self.PS.sell_coin(coin_name, quantity, price):
            self.update_portfolio()

    def update_portfolio(self):
        # 포트폴리오의 현황을 업데이트하여 라벨에 표시
        portfolio_str = '\n'.join([f"{coin}: {quantity}" for coin, quantity in self.PS.portfolio.items()])
        self.portfolio_label.setText(f"{self.config_loader.get_setting('Labels', 'PortfolioLabel')}:\n{portfolio_str}\n{self.config_loader.get_setting('Labels', 'CashLabel')}: {self.PS.cash}")

    def update_coin_info(self):
        # 선택된 코인의 정보를 업데이트하여 라벨에 표시
        coin_name = self.coin_selector.currentText()
        if coin_name:
            price = self.GS.coins[self.coin_selector.currentIndex()].prices[1][-1]
            self.current_price_label.setText(f"{self.config_loader.get_setting('Labels', 'CurrentPriceLabel')}: {price}")
            quantity = int(self.quantity_input.text()) if self.quantity_input.text() else 0
            total_cost = price * quantity
            self.total_cost_label.setText(f"{self.config_loader.get_setting('Labels', 'TotalCostLabel')}: {total_cost}")

    def initUI(self):
        # UI 초기화
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