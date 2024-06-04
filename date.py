from Methods import ConfigLoader
import datetime

class DateSystem:
    def __init__(self):
        # ConfigLoader 인스턴스를 생성하여 설정 파일을 불러옴
        self.config_loader = ConfigLoader('config.ini')
        # 설정 파일에서 시작 날짜를 불러와 datetime 객체로 변환
        self.start_date = datetime.datetime.strptime(self.config_loader.get_setting('Init', 'StartDate'), "%Y-%m-%d")
        self.date = self.start_date
        
    def get_cur_date_str(self):
        # 현재 날짜를 문자열로 반환
        return self.date.strftime("%Y-%m-%d")
    
    def go_next_date(self):
        # 현재 날짜를 하루 증가시킴
        self.date += datetime.timedelta(days=1)
