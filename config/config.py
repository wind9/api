import configparser
import os
import time
from redis import StrictRedis, ConnectionPool


class Config(object):

    def __init__(self, config_file='config.ini'):
        self._path = os.path.join(os.path.dirname(__file__), 'config.ini')
        if not os.path.exists(self._path):
            raise FileNotFoundError("can not find file config.ini")
        self._config = configparser.ConfigParser()
        self._config.read(self._path, encoding='utf-8')

    def get(self, section, name, strip_blank=True, strip_quote=True):
        s = self._config.get(section, name)
        if strip_blank:
            s = s.strip()
        if strip_quote:
            s = s.strip("'").strip('"')
        return s


global_config = Config()
