import os
from configparser import ConfigParser


class ConfigUtil:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ConfigUtil, cls).__new__(cls)
            cls._instance._initialize_config()
        return cls._instance

    def _initialize_config(self):
        self.config = ConfigParser()
        self.config.read('config.ini')
        self.profile = os.getenv("APP_PROFILE", "DEFAULT")

    def get_config(self, name, default=None, fallback=None):
        return self.config[self.profile].get(name, default, fallback=fallback) if fallback else self.config[self.profile].get(name, default)