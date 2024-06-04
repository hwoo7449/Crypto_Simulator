import configparser
import random

class ConfigLoader:
    def __init__(self, config_file):
        # 설정 파일을 불러와 파싱하는 클래스
        self.config = configparser.ConfigParser()
        self.config.read(config_file, encoding='utf-8')

    def get_setting(self, section, option):
        # 설정 파일에서 특정 섹션과 옵션 값을 가져옴
        return self.config.get(section, option)