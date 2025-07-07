# -*- coding: utf-8 -*-

import shlex
import argparse

from nm.core.config import ConfigNm
from nm.funclib.funclib import get_sysinfo
from nm.funclib.ncfunclib import get_msg_text

from ncatbot.core import BotClient
from ncatbot.core.message import GroupMessage, PrivateMessage

async def command(bot: BotClient, msg: GroupMessage, config_nm: ConfigNm, logger) -> None:
    """全部聊天內命令入口
    Args:
        bot (BotClient): BotClient實例
        msg (GroupMessage): 群消息實例
        config_nm (ConfigNm): 配置實例
        logger: 日志實例
    """
    # master 命令
    if int(msg.user_id) in config_nm.master:
        parser = argparse.ArgumentParser(description="NcatBot Command Parser")
        parser.add_argument("command", type=str, help="要執行的命令")
        args = parser.parse_args(shlex.split(get_msg_text(msg)))
        if args.command == "sysinfo":
            sysinfo = get_sysinfo()
            logger.info(f"系統信息: {sysinfo}")
            await bot.api.post_group_msg(group_id=msg.group_id, text=f"系統信息: {sysinfo}")