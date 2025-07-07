# -*- coding: utf-8 -*-

import yaml

from ncatbot.utils.config import config as nc_config

class ConfigNm:

    class DatabaseConfig:
        def __init__(self, db_config: dict):
            self.host = db_config.get("host", "localhost")
            self.port = db_config.get("port", 5432)
            self.user = db_config.get("user", "nmbot")
            self.password = db_config.get("password", "123456")
            self.database = db_config.get("database", "nmbot")

    def __init__(self, path: str):
        with open(path, mode="r", encoding="utf-8") as config_file:
            config: dict = yaml.safe_load(config_file)
            self.nc_conf = nc_config
            self.master: list[int] = config.get("master", [])
            self.selfid = nc_config.bt_uin
            self.db = self.DatabaseConfig(config.get("db", {}))