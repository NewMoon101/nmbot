# -*- coding: utf-8 -*-

import yaml

from pathlib import Path

from ncatbot.utils.config import config as nc_config

class ConfigNm:

    class DatabaseConfig:
        def __init__(self, db_config: dict):
            self.host = db_config.get("host", "localhost")
            self.port = db_config.get("port", 5432)
            self.user = db_config.get("user", "nmbot")
            self.password = db_config.get("password", "123456")
            self.database = db_config.get("database", "nmbot")

    class LocalDatabaseConfig:
        def __init__(self, db_local_config: dict, selfid: str):
            self.type = db_local_config.get("type", "sqlite")
            self.path = str(Path("data/qq" + str(selfid) + "/msg.db"))

    def __init__(self, path: str):
        with open(path, mode="r", encoding="utf-8") as config_file:
            config: dict = yaml.safe_load(config_file)
            self.nc_conf = nc_config
            self.master: list[int] = config.get("master", [])
            self.selfid: str = config.get("bt_uin", "123456")
            self.db = self.DatabaseConfig(config.get("db", {}))
            self.db_local = self.LocalDatabaseConfig(config.get("db-local", {}), selfid=self.selfid)