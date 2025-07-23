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
            self.path = str(Path("data/qq" + str(selfid)))

    class FunctionOpenConfig:

        class ReportConfig:
            def __init__(self, func_open_report_config: dict):
                self.ated: bool = func_open_report_config.get("ated", False)
                self.private_msg: bool = func_open_report_config.get("private_msg", False)
                self.poke: bool = func_open_report_config.get("poke", False)
                self.red_pocket: bool = func_open_report_config.get("red_pocket", False)
                self.replied: bool = func_open_report_config.get("replied", False)

        def __init__(self, function_open_config: dict):
            self.report = self.ReportConfig(function_open_config.get("report", {}))
            self.command = function_open_config.get("command", False)

    def __init__(self, path: str):
        with open(path, mode="r", encoding="utf-8") as config_file:
            config: dict = yaml.safe_load(config_file)
            self.nc_conf = nc_config
            self.master: list[int] = config.get("master", [])
            self.selfid: str = config.get("bt_uin", "123456")
            self.devgroup: int = config.get("devgroup", 123456)
            self.function_open = self.FunctionOpenConfig(config.get("function_open", {}))
            self.is_report_at_all: bool = config.get("report_at_all", False)
            self.db = self.DatabaseConfig(config.get("db", {}))
            self.db_local = self.LocalDatabaseConfig(config.get("db-local", {}), selfid=self.selfid)
            self.promote_group: list[int] = config.get("promotegroup", [])