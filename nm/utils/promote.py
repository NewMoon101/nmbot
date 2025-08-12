# -*- coding: utf-8 -*-

import json
from pathlib import Path

from ncatbot.core.client import BotClient
from ncatbot.core.message import GroupMessage

from nm.core.config import ConfigNm
from nm.funclib.funclib import sleep_random_async
from nm.funclib.ncfunclib import get_msg_reply

def init_promote_config(config_nm: ConfigNm, logger):
    config_path = Path(".", "data", f"qq{config_nm.selfid}", "promote_config.json")
    if config_path.is_file():
        logger.debug("宣发配置文件已存在")
    else:
        logger.info("宣发配置文件不存在")
        # 硬编码 默认宣发配置文件
        default_promote_config = {
            "promote_time_min": 20,
            "promote_time_max": 100,
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
            self.promote_time_min: int = data.get("promote_time_min", 20)
            self.promote_time_max: int = data.get("promote_time_max", 100) # 或許需要在這裏添加測試, 以防止不符合random.randint()的數據
            self.activetag = data.get("activetag", "default")
            self.tag: dict[str, dict] = data.get("tag", {})

async def get_group_id_list(bot: BotClient) -> list[int]:
    data: dict = await bot.api.get_group_list(no_cache=True)
    group_id_list: list[int] = []
    for i in data["data"]:
        group_id_list.append(i["group_id"])
    return group_id_list

async def get_promote_group_list(bot: BotClient, config_nm: ConfigNm, logger):
    all_group_id_list = await get_group_id_list(bot)
    promote_config: PromoteConfig = config_nm.promote_config # type: ignore
    mode = promote_config.tag[promote_config.activetag]["mode"]
    tag_group_id_list: list[int] = promote_config.tag[promote_config.activetag]["list"]
    group_list: list[int] = []
    if mode == "white":
        group_list = tag_group_id_list
    elif mode == "black":
        group_list = list(set(all_group_id_list) - set(tag_group_id_list))
    else:
        logger.info("未知情況")
    return group_list

async def promote_t(bot: BotClient, msg: GroupMessage, config_nm: ConfigNm, logger) -> None:
    """
    傳統: 引用後宣發
    """
    promote_post_group_id: int = msg.group_id
    await bot.api.post_group_msg(group_id=promote_post_group_id, text="将宣发一条消息")
    logger.info(f"将宣发消息, msg_id:{msg.message[0]['data']['id']}")
    promote_msg_id = get_msg_reply(msg)
    group_list = await get_promote_group_list(bot, config_nm, logger)
    promote_config: PromoteConfig = config_nm.promote_config # type: ignore
    for group_id in group_list:
        await sleep_random_async(promote_config.promote_time_min, promote_config.promote_time_max)
        await bot.api.forward_group_single_msg(message_id=promote_msg_id, group_id=group_id)
        logger.info(f"已宣發至群{group_id}")
    await bot.api.post_group_msg(group_id=promote_post_group_id, text="宣发成功", reply=promote_msg_id)