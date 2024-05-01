import configparser
import random

class ConfigLoader:
    def __init__(self, config_file):
        self.config = configparser.ConfigParser()
        self.config.read(config_file, encoding='utf-8')

    def get_setting(self, section, option):
        return self.config.get(section, option)

# Usage example
# config_file = '/path/to/config.ini'
# loader = ConfigLoader(config_file)
# setting = loader.get_setting('section_name', 'option_name')
# print(setting)