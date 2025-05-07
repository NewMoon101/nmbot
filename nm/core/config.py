# -*- coding: utf-8 -*-

import json
from pathlib import Path

from ncatbot.utils.config import config as nc_config

config_json_path = str(Path("config.json"))

class ConfigNm:

    def __init__(self):
        with open(config_json_path, mode="r", encoding="utf-8") as config_file:
            config: dict = json.load(config_file)
            self.master: list[int] = config.get("master", [])
            self.userid = nc_config.bt_uin

config_nm = ConfigNm()