# -*- coding: utf-8 -*-

import json
from pathlib import Path

from ncatbot.core.client import BotClient
from ncatbot.core.message import GroupMessage

from nm.core.config import ConfigNm
from nm.funclib.ncfunclib import get_msg_at, get_msg_type
from nm.core.info import get_group_info

def init_promote_config(config_nm: ConfigNm, logger):
    config_path = Path(".", "data", f"qq{config_nm.selfid}", "promote_config.json")
    if config_path.is_file():
        logger.debug("宣发配置文件已存在")
    else:
        logger.info("宣发配置文件不存在")
        # 硬编码 默认宣发配置文件
        default_promote_config = {
            "activetag": "default",
            "tag": {
                "default": {
                "mode": "white",
                "list": []
                }
            }
        }
        with open(config_path, mode="w", encoding="utf-8") as f:
            json.dump(default_promote_config, f, ensure_ascii=False, indent=4)
        logger.info("已成功初始化配置文件")

class PromoteConfig:

    def __init__(self, config_nm: ConfigNm):
        with open(Path(".", "data", f"qq{config_nm.selfid}", "promote_config.json"), 'r', encoding='utf-8') as f:
            data: dict = json.load(f)
            self.activetag = data.get("activetag", "default")
            self.tag: dict[str, dict] = data.get("tag", {})

async def promote_t(bot: BotClient, msg: GroupMessage, config_nm: ConfigNm, logger) -> None:
    """
    傳統: 引用後宣發
    """
    if not "reply" in get_msg_type(msg):
        logger.warning("消息中沒有reply段, 無法引用")
        return
    else:
        await bot.api.post_group_msg(group_id=msg.group_id, text="将宣发一条消息")
        logger.info(f"将宣发消息, msg_id:{msg.message[0]['data']['id']}")
        # TODO: