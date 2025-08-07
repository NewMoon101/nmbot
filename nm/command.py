# -*- coding: utf-8 -*-

import shlex
import argparse

from peewee import SqliteDatabase

from nm.core.config import ConfigNm
from nm.core.info import update_group_info
from nm.funclib.funclib import get_sysinfo, NoExitArgumentParser
from nm.funclib.ncfunclib import get_msg_text, get_msg_at, get_msg_type
from nm.utils.promote import promote_t

from ncatbot.core import BotClient
from ncatbot.core.message import GroupMessage

help_text = """
使用 help 唤出此列表

""" # TODO: 编写帮助列表

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
        parser = NoExitArgumentParser(description="NcatBot Command Parser", exit_on_error=False)
        parser.add_argument("command", type=str, help="要執行的命令")
        if not get_msg_text(msg).strip(): # 如果消息文本為空，則不執行任何命令; 且防止parser解析出錯導致的sysexit
            return None
        try:
            tokens = shlex.split(get_msg_text(msg).strip())
            args = parser.parse_args(tokens)
        except Exception as e:
            return
        else:
            if len(get_msg_at(msg)) == 0 or (config_nm.selfid in get_msg_at(msg) and (len(get_msg_at(msg)) == 1)): # 如果沒被@, 直接執行; 如果被@了, 只有只@了bot纔能執行
                if args.command == "sysinfo":
                    sysinfo = get_sysinfo()
                    logger.info(f"系統信息: {sysinfo}")
                    await bot.api.post_group_msg(group_id=msg.group_id, text=f"系統信息: {sysinfo}")
                    return
                elif args.command == "help":
                    await bot.api.post_group_msg(group_id=msg.group_id, text="可用命令: sysinfo, help")
                    return
                elif args.command == "update":
                    parser.add_argument("-m", "--module", type=str, help="要更新的模塊")
                    args = parser.parse_args(shlex.split(get_msg_text(msg)))
                    if args.module:
                        if args.module == "group_info":
                            await update_group_info(bot, group_info_db, logger)
                            return
                        return
                    return
                elif args.command == "宣发":
                    if not "reply" in get_msg_type(msg):
                        logger.warning(f"消息{msg.message_id}不含reply消息段, 无法宣发")
                        return
                    else:
                        await promote_t(bot, msg, config_nm, logger)
                        return
            else:
                pass