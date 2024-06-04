from Methods import ConfigLoader
import datetime

class DateSystem:
    def __init__(self):
        self.config_loader = ConfigLoader('config.ini')
        self.start_date = datetime.datetime.strptime(self.config_loader.get_setting('Init', 'StartDate'), "%Y-%m-%d")
        self.date = self.start_date
        
    def get_cur_date_str(self):
        return self.date.strftime("%Y-%m-%d")
    
    def go_next_date(self):
        self.date += datetime.timedelta(days=1)