# -*- coding: utf-8 -*-

import json
from pathlib import Path

from ncatbot.core.client import BotClient
from ncatbot.core.message import GroupMessage

from nm.core.config import ConfigNm
from nm.funclib.funclib import sleep_random_async
from nm.funclib.ncfunclib import get_msg_reply

class PromoteConfig:

    def init_promote_config(self, config_nm: ConfigNm, logger):
        if self.config_path.is_file():
            logger.debug(f"(bot:{config_nm.selfid}) 宣发配置文件已存在")
        else:
            logger.info(f"(bot:{config_nm.selfid}) 宣发配置文件不存在")
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
            with open(self.config_path, mode="w", encoding="utf-8") as f:
                json.dump(default_promote_config, f, ensure_ascii=False, indent=4)
            logger.info(f"(bot:{config_nm.selfid}) 已成功初始化配置文件")

    def load_data(self, config_nm: ConfigNm, logger):
        with open(self.config_path, 'r', encoding='utf-8') as f:
            data: dict = json.load(f)
            self.promote_time_min: int = data.get("promote_time_min", 20)
            self.promote_time_max: int = data.get("promote_time_max", 100) # 或許需要在這裏添加測試, 以防止不符合random.randint()的數據
            self.activetag: str = data.get("activetag", "default")
            self.tag: dict[str, dict] = data.get("tag", {})

    def __init__(self, config_nm: ConfigNm, logger):
        self.config_path = Path(".", "data", f"qq{config_nm.selfid}", "promote_config.json")
        self.init_promote_config(config_nm, logger)
        self.load_data(config_nm, logger)

    def update_config_file(self, config_nm: ConfigNm, logger):
        new_data = {}
        new_data.update({"promote_time_min": self.promote_time_min})
        new_data.update({"promote_time_max": self.promote_time_max})
        new_data.update({"activetag": self.activetag})
        new_data.update({"tag": self.tag})
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(new_data, f, ensure_ascii=False, indent=4)
        logger.info(f"(bot:{config_nm.selfid}) 已更新宣发配置文件")

    def show_config(self):
        return (self.promote_time_min, self.promote_time_max, self.activetag, self.get_tag_list(), self.get_activetag())

    def get_tag_list(self):
        return list(self.tag.keys())

    def add_tag(self, tag_name: str, config_nm: ConfigNm, logger):
        tag_list = self.get_tag_list()
        if tag_name in tag_list:
            # 已存在
            logger.info(f"(bot:{config_nm.selfid}) 该tag已存在{tag_name}")
            return
        else:
            self.tag.update({tag_name: {"mode": "white", "list": []}})
            self.update_config_file(config_nm, logger)

    def del_tag(self, tag_name: str, config_nm: ConfigNm, logger):
        tag_list = self.get_tag_list()
        if tag_name in tag_list:
            # 已存在
            self.tag.pop(tag_name)
            self.update_config_file(config_nm, logger)
        else:
            # 不存在
            logger.info(f"(bot:{config_nm.selfid}) 该tag不存在{tag_name}")
            return

    def get_activetag(self):
        return self.tag[self.activetag]

    def change_activetag_mode(self, config_nm: ConfigNm, logger):
        activetag = self.get_activetag()
        tag_mode = activetag["mode"]
        if tag_mode == "white":
            tag_mode = "black"
            self.update_config_file(config_nm, logger)
        elif tag_mode == "black":
            tag_mode = "white"
            self.update_config_file(config_nm, logger)

    def change_activetag_mode_to(self, mode: str, config_nm: ConfigNm, logger):
        activetag = self.get_activetag()
        tag_mode = activetag["mode"]
        if mode in ["white", "black"]:
            tag_mode = mode

    def change_activetag(self, tag_name: str, config_nm: ConfigNm, logger):
        tag_list = self.get_tag_list()
        if tag_name in tag_list:
            self.activetag = tag_name
            self.update_config_file(config_nm, logger)
        else:
            logger.info(f"(bot:{config_nm.selfid}) 无此tag")

    def get_active_tag_group_list(self) -> list[int]:
        activetag = self.get_activetag()
        return activetag["list"]

    def add_group_to_activetag(self, group_list: list[int], config_nm: ConfigNm, logger):
        pre_group_list = self.get_active_tag_group_list()
        new_group_list = list(set(pre_group_list).union(set(group_list)))
        pre_group_list = new_group_list
        self.update_config_file(config_nm, logger)

    def del_group_from_activetag(self, group_list: list[int], config_nm: ConfigNm, logger):
        pre_group_list = self.get_active_tag_group_list()
        new_group_list = list(set(pre_group_list) - (set(group_list)))
        pre_group_list = new_group_list
        self.update_config_file(config_nm, logger)

async def get_group_id_list(bot: BotClient) -> list[int]:
    data: dict = await bot.api.get_group_list(no_cache=True)
    group_id_list: list[int] = []
    for i in data["data"]:
        group_id_list.append(i["group_id"])
    return group_id_list

async def show_promote_config(bot: BotClient, msg: GroupMessage, config_nm: ConfigNm, logger):
    promote_config: PromoteConfig = config_nm.promote_config  # type: ignore
    promote_time_min, promote_time_max, activetag_name, tag_list, activetag = promote_config.show_config()
    info = f"最小宣发时间:{promote_time_min}\n最大宣发时间:{promote_time_max}\ntag列表:{" ".join(tag_list)}\n活跃tag:\nname:{activetag_name}\nmode:{activetag["mode"]}\ngroup_list:{" ".join([str(i) for i in activetag["list"]])}"
    await bot.api.post_group_msg(group_id=msg.group_id, text=info)

async def add_tag(bot: BotClient, msg: GroupMessage, tag_name: str, config_nm: ConfigNm, logger):
    """添加tag"""
    promote_config: PromoteConfig = config_nm.promote_config  # type: ignore
    promote_config.add_tag(tag_name, config_nm, logger)
    await bot.api.post_group_msg(group_id=msg.group_id, text=f"已添加tag: {tag_name}")

async def del_tag(bot: BotClient, msg: GroupMessage, tag_name: str, config_nm: ConfigNm, logger):
    """删除tag"""
    promote_config: PromoteConfig = config_nm.promote_config  # type: ignore
    promote_config.del_tag(tag_name, config_nm, logger)
    await bot.api.post_group_msg(group_id=msg.group_id, text=f"已删除tag: {tag_name}")
    
async def change_mode(bot: BotClient, msg: GroupMessage, config_nm: ConfigNm, logger):
    """切换tag模式"""
    promote_config: PromoteConfig = config_nm.promote_config  # type: ignore
    promote_config.change_activetag_mode(config_nm, logger)
    await bot.api.post_group_msg(group_id=msg.group_id, text=f"已切换tag模式为: {promote_config.get_activetag()['mode']}")

async def change_mode_to(bot: BotClient, msg: GroupMessage, mode: str, config_nm: ConfigNm, logger):
    """切换tag模式到指定模式"""
    promote_config: PromoteConfig = config_nm.promote_config  # type: ignore
    promote_config.change_activetag_mode_to(mode, config_nm, logger)
    await bot.api.post_group_msg(group_id=msg.group_id, text=f"已切换tag模式为: {promote_config.get_activetag()['mode']}")
    
async def change_tag(bot: BotClient, msg: GroupMessage, tag_name: str, config_nm: ConfigNm, logger):
    """切换活跃tag"""
    promote_config: PromoteConfig = config_nm.promote_config  # type: ignore
    promote_config.change_activetag(tag_name, config_nm, logger)
    await bot.api.post_group_msg(group_id=msg.group_id, text=f"已切换活跃tag为: {tag_name}")
    
async def add_group(bot: BotClient, msg: GroupMessage, group_list: list[str], config_nm: ConfigNm, logger):
    """添加群组到活跃tag"""
    group_list_int = [int(i) for i in group_list]
    promote_config: PromoteConfig = config_nm.promote_config  # type: ignore
    promote_config.add_group_to_activetag(group_list_int, config_nm, logger)
    await bot.api.post_group_msg(group_id=msg.group_id, text=f"已添加群组到活跃tag: {' '.join([str(i) for i in group_list])}")
    
async def del_group(bot: BotClient, msg: GroupMessage, group_list: list[str], config_nm: ConfigNm, logger):
    """从活跃tag中删除群组"""
    group_list_int = [int(i) for i in group_list]
    promote_config: PromoteConfig = config_nm.promote_config  # type: ignore
    promote_config.del_group_from_activetag(group_list_int, config_nm, logger)
    await bot.api.post_group_msg(group_id=msg.group_id, text=f"已从活跃tag中删除群组: {' '.join([str(i) for i in group_list])}")

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
        logger.info(f"(bot:{config_nm.selfid}) 未知情況")
    return group_list

async def promote_t(bot: BotClient, msg: GroupMessage, config_nm: ConfigNm, logger) -> None:
    """
    傳統: 引用後宣發
    """
    promote_post_group_id: int = msg.group_id
    await bot.api.post_group_msg(group_id=promote_post_group_id, text="将宣发一条消息")
    logger.info(f"(bot:{config_nm.selfid}) 将宣发消息, msg_id:{msg.message[0]['data']['id']}")
    promote_msg_id = get_msg_reply(msg)
    group_list = await get_promote_group_list(bot, config_nm, logger)
    promote_config: PromoteConfig = config_nm.promote_config # type: ignore
    for group_id in group_list:
        await sleep_random_async(promote_config.promote_time_min, promote_config.promote_time_max)
        await bot.api.forward_group_single_msg(message_id=promote_msg_id, group_id=group_id)
        logger.info(f"(bot:{config_nm.selfid}) 已宣發至群{group_id}")
    await bot.api.post_group_msg(group_id=promote_post_group_id, text="宣发成功", reply=promote_msg_id)