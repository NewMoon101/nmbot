# -*- coding: utf-8 -*-

import shlex
import argparse

from peewee import SqliteDatabase

from nm.core.config import ConfigNm
from nm.funclib.funclib import get_sysinfo
from nm.funclib.ncfunclib import get_msg_text, get_msg_at
from nm.core.info import update_group_info

from ncatbot.core import BotClient
from ncatbot.core.message import GroupMessage

async def command(bot: BotClient, msg: GroupMessage, config_nm: ConfigNm, logger, group_info_db: SqliteDatabase) -> None:
    """全部聊天內命令入口
    Args:
        bot (BotClient): BotClient實例
        msg (GroupMessage): 群消息實例
        config_nm (ConfigNm): 配置實例
        logger: 日志實例
    """
    # master 命令
    if int(msg.user_id) in config_nm.master:
        parser = argparse.ArgumentParser(description="NcatBot Command Parser", exit_on_error=False)
        parser.add_argument("command", type=str, help="要執行的命令")
        if not get_msg_text(msg).strip(): # 如果消息文本為空，則不執行任何命令; 且防止parser解析出錯導致的sysexit
            return None
        try:
            args = parser.parse_args(shlex.split(get_msg_text(msg).strip()))
        except Exception as e:
            return
        else:
            if len(get_msg_at(msg)) == 0 or (config_nm.selfid in get_msg_at(msg) and (len(get_msg_at(msg)) == 1)): # 如果沒被@, 直接執行; 如果被@了, 只有只@了bot纔能執行
                if args.command == "sysinfo":
                    sysinfo = get_sysinfo()
                    logger.info(f"系統信息: {sysinfo}")
                    await bot.api.post_group_msg(group_id=msg.group_id, text=f"系統信息: {sysinfo}")
                elif args.command == "help":
                    await bot.api.post_group_msg(group_id=msg.group_id, text="可用命令: sysinfo, help")
                elif args.command == "update":
                    parser.add_argument("-m", "--module", type=str, help="要更新的模塊")
                    args = parser.parse_args(shlex.split(get_msg_text(msg)))
                    if args.module:
                        if args.module == "group_info":
                            await update_group_info(bot, group_info_db, logger)
            else:
                pass