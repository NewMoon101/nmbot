# -*- coding: utf-8 -*-

from ncatbot.core.client import BotClient
from ncatbot.core.message import GroupMessage

from nm.core.config import ConfigNm
from nm.funclib.ncfunclib import get_msg_at
from nm.core.info import get_group_info

async def report_ated(msg: GroupMessage, bot:BotClient, config_nm: ConfigNm, logger):
    post_group_id = config_nm.promote_group[0]
    if config_nm.selfid in get_msg_at(msg):
        logger.info(msg)
        group_info = get_group_info(msg.group_id)
        if group_info is None:
            logger.error(f"群组信息获取失败: {msg.group_id}")
            return
        info_reply = f"群消息: 来自>{group_info.group_name}({group_info.group_id})<, 用户>{msg.sender.nickname}({msg.user_id})<"
        await bot.api.post_group_msg(group_id=post_group_id, text=info_reply)
        await bot.api.forward_group_single_msg(group_id=post_group_id, message_id=msg.message_id)