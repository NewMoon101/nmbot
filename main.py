# -*- coding: utf-8 -*-

import argparse

from pathlib import Path # 引入Path类是为了适配不同系统的路径分隔符不同(windows\linux/)
from peewee import SqliteDatabase

from nm.core.config import ConfigNm
from nm.core.msg import create_msg_db, msg_db_proxy  # 导入创建消息数据库的函数
from nm.core.info import create_group_info_db, group_info_db_proxy  # 导入创建群组信息数据库的函数
from nm.command import command  # 导入命令处理函数

from ncatbot.utils.config import config
from ncatbot.core.client import BotClient
from ncatbot.core.message import GroupMessage, PrivateMessage
from ncatbot.utils.logger import get_log

parser = argparse.ArgumentParser(description="NcatBot Bot Client")
parser.add_argument("-c", "--config", type=str, default="config.yaml", help="Path to the configuration file", required=False)
args = parser.parse_args()
if args.config:
    config_yaml_path = str(Path(args.config))  # 将路径转换为字符串
else:
    config_yaml_path = str(Path("config.yaml"))
config.load_config(config_yaml_path) # 从文件加载配置, 一定版本后的ncatbot会自动完成这一步
config_nm = ConfigNm(config_yaml_path)  # 创建ConfigNm实例

msg_db = create_msg_db(config_nm) # TODO:對於這個庫, 期望之後加入檢測大小自動存檔之前消息的功能
gorup_info_db = create_group_info_db(config_nm)  # 创建群组信息数据库

bot = BotClient() # 创建BotClient
logger = get_log() # 创建logger

@bot.group_event()
async def on_group_message(msg: GroupMessage):
    await command(bot, msg, config_nm, logger, gorup_info_db)  # 调用命令处理函数

@bot.private_event()
async def on_private_message(msg: PrivateMessage):
    logger.info(msg)

if __name__ == "__main__":
    bot.run()