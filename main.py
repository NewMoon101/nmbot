# -*- coding: utf-8 -*-

import asyncio
import argparse

from pathlib import Path # 引入Path类是为了适配不同系统的路径分隔符不同(windows\linux/)
from peewee import SqliteDatabase

from nm.core.config import ConfigNm
from nm.core.msg import create_msg_db # 导入创建消息数据库的函数
from nm.core.info import create_group_info_db # 导入创建群组信息数据库的函数
from nm.command import command  # 导入命令处理函数
from nm.utils.schedule import schedule_main  # 导入调度函数
from nm.utils.master import report_ated, report_msg_private, report_poke, report_red_pocket, report_replied  # 导入报告函数

from ncatbot.utils.config import config
from ncatbot.core.client import BotClient
from ncatbot.core.message import GroupMessage, PrivateMessage
from ncatbot.core.notice import NoticeMessage
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
group_info_db = create_group_info_db(config_nm)  # 创建群组信息数据库

bot = BotClient() # 创建BotClient
logger = get_log() # 创建logger

i = 0
@bot.group_event()
async def on_group_message(msg: GroupMessage):
    global i
    if i == 0:
        i += 1
        await schedule_main(bot, group_info_db, logger)
    if config_nm.function_open.report.ated:
        await report_ated(msg, bot, config_nm, config_nm.devgroup, logger, is_report_at_all=config_nm.is_report_at_all)
    if config_nm.function_open.report.replied:
        await report_replied(msg, bot, config_nm, config_nm.devgroup, logger)
    if config_nm.function_open.report.red_pocket:
        await report_red_pocket(msg, bot, config_nm, config_nm.devgroup, logger)
    if config_nm.function_open.command:
        await command(bot, msg, config_nm, logger, group_info_db)  # 调用命令处理函数

@bot.private_event()
async def on_private_message(msg: PrivateMessage):
    logger.info(msg)
    if config_nm.function_open.report.private_msg:
        await report_msg_private(msg, bot, config_nm, config_nm.devgroup, logger)

@bot.notice_event()
async def on_notice_message(msg: NoticeMessage):
    if config_nm.function_open.report.poke:
        await report_poke(msg, bot, config_nm, config_nm.devgroup, logger)

if __name__ == "__main__":
    bot.run()