import configparser

class ConfigLoader:
    def __init__(self, config_file):
        self.config = configparser.ConfigParser()
        self.config.read(config_file, encoding='utf-8')

    def get_setting(self, section, option):
        return self.config.get(section, option)