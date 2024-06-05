from PyQt5.QtWidgets import QVBoxLayout, QWidget, QPushButton, QLabel, QLineEdit, QHBoxLayout, QComboBox, QProgressBar, QDockWidget, QTextEdit
from PyQt5.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.pyplot import rcParams

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

        # 뉴스 피드 추가
        news_layout = QVBoxLayout()
        news_title = QLabel("최신 뉴스")
        news_title.setStyleSheet("font-size: 18px; font-weight: bold;")
        news_layout.addWidget(news_title)

        self.news_feed = QTextEdit()
        self.news_feed.setReadOnly(True)
        news_layout.addWidget(self.news_feed)

        layout.addLayout(news_layout)

        # 디버그 창 추가
        self.debug_dock = QDockWidget("Debug Info", MainWindow)
        self.debug_text_edit = QTextEdit()
        self.debug_text_edit.setReadOnly(True)
        self.debug_dock.setWidget(self.debug_text_edit)
        MainWindow.addDockWidget(Qt.RightDockWidgetArea, self.debug_dock)
        MainWindow.update_debug_info()  # 초기 디버그 정보 업데이트
