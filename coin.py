from Methods import ConfigLoader
import random

class Coin:
    def __init__(self, name, index, start_date, color=None):
        self.name = name
        self.prices = [[], []]
        self.index = index
        self.color = color if color else "#{:06x}".format(random.randint(0, 0xFFFFFF))  # 지정된 색깔이 없을 경우 랜덤 색상 지정
        self.delisted = False  # 상장폐지 여부를 가리키는 변수
        self.set_start_price(start_date)
        self.price_modifier = 1.0  # 이벤트에 의한 가격 변동

    def set_start_price(self, start_date):
        # 시작 날짜를 MainWindow의 DateSystem에서 불러옴
        config_loader = ConfigLoader('config.ini')
        start_coin_price = [int(price) for price in config_loader.get_setting('Init', 'StartCoinPrice').split('|')]
        self.prices[0].append(start_date)
        self.prices[1].append(random.randint(start_coin_price[0], start_coin_price[1]))

    def price_change(self, date):
        if not self.delisted:  # 상장폐지가 되지 않은 경우에만 가격 변동
            coin_price_coverage = [int(price) for price in ConfigLoader('config.ini').get_setting('Init', 'CoinPriceCoverage').split('|')]
            new_price = self.prices[1][-1] + random.randint(coin_price_coverage[0], coin_price_coverage[1])
            new_price *= self.price_modifier  # 이벤트에 의한 가격 변동 적용
            
            if new_price <= 0:  # 가격이 0 이하로 내려가면 상장폐지 처리
                new_price = 0
                self.delisted = True

            self.prices[0].append(date)
            self.prices[1].append(new_price)
        else:
            # 상장폐지된 경우, 가격 0을 유지
            self.prices[0].append(date)
            self.prices[1].append(0)
        
        self.price_modifier = 1.0  # 이벤트에 의한 가격 변동 초기화

    def apply_price_modifier(self, modifier):
        self.price_modifier *= modifier
