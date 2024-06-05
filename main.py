import sys
from PyQt5.QtWidgets import QApplication, QMainWindow
from Methods import ConfigLoader
from graph import GraphSystem
from player import PlayerSystem
from event import EventSystem
from ui_mainwindow import MainWindowUI
from PyQt5.QtCore import QTimer
from matplotlib.pyplot import rcParams


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

        QTimer.singleShot(0, self.notify_next_step)  # UI 초기화 후 첫 번째 스텝 실행

    def update_progress(self):
        self.current_progress += 1
        self.progress_bar.setValue(self.current_progress * 25)

        if self.current_progress >= 4:
            self.notify_next_step()
            self.current_progress = 0

    def notify_next_step(self):
        self.GS.next_step()  # 날짜 업데이트
        self.ES.check_for_event(self)  # 이벤트 체크
        self.canvas.draw()    # 그래프 업데이트
        self.update_portfolio()  # 포트폴리오 업데이트
        self.update_coin_info()  # 코인 정보 업데이트
        self.update_debug_info()  # 디버그 정보 업데이트

    def make_coin(self, name, color=None):
        self.GS.add_new_coin(name, color)
        self.coin_selector.addItem(name)

    def buy_coin(self):
        coin_name = self.coin_selector.currentText()
        quantity = int(self.quantity_input.text())
        price = self.GS.coins[self.coin_selector.currentIndex()].prices[1][-1]
        if self.PS.buy_coin(coin_name, quantity, price):
            self.update_portfolio()
            self.update_debug_info()  # 디버그 정보 업데이트

    def sell_coin(self):
        coin_name = self.coin_selector.currentText()
        quantity = int(self.quantity_input.text())
        price = self.GS.coins[self.coin_selector.currentIndex()].prices[1][-1]
        if self.PS.sell_coin(coin_name, quantity, price):
            self.update_portfolio()
            self.update_debug_info()  # 디버그 정보 업데이트

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
    # matplotlib 폰트 설정
    rcParams['font.family'] = 'Malgun Gothic'
    rcParams['axes.unicode_minus'] = False

    # 애플리케이션 실행
    app = QApplication(sys.argv)
    window = MainWindow()

    # 디버그용 코인 추가
    window.make_coin("BTC", "blue")  # CSS 색상 이름 사용
    window.make_coin("ETH", "#FF5733") # 16진수 색상 코드 사용
    window.setGeometry(100, 100, 1000, 800)
    window.show()

    # 애플리케이션 실행 종료
    sys.exit(app.exec_())
