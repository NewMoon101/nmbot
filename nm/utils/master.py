# -*- coding: utf-8 -*-

from nm.core.config import ConfigNm
from nm.funclib.ncfunclib import get_msg_at
from nm.core.info import get_group_info, get_user_info

from ncatbot.core.client import BotClient
from ncatbot.core.message import GroupMessage, PrivateMessage
from ncatbot.core.notice import NoticeMessage

async def report_ated(msg: GroupMessage, bot:BotClient, config_nm: ConfigNm, report_group_id: int, logger):
    if config_nm.selfid in get_msg_at(msg):
        logger.info(msg)
        group_info = get_group_info(msg.group_id)
        if group_info is None:
            logger.error(f"群组信息获取失败: {msg.group_id}")
            return
        info_reply = f"群消息:\n来自>{group_info.group_name}({group_info.group_id})<\n用户>{msg.sender.nickname}({msg.user_id})<"
        await bot.api.post_group_msg(group_id=report_group_id, text=info_reply)
        await bot.api.forward_group_single_msg(group_id=report_group_id, message_id=msg.message_id)

async def report_msg_private(msg: PrivateMessage, bot: BotClient, config_nm: ConfigNm, report_group_id: int, logger):
    logger.info(msg)
    info_reply = f"私聊消息:\n来自>{msg.sender.nickname}({msg.user_id})<"
    await bot.api.post_group_msg(group_id=report_group_id, text=info_reply)
    await bot.api.forward_group_single_msg(group_id=report_group_id, message_id=msg.message_id)

async def report_poke(msg: NoticeMessage, bot: BotClient, config_nm: ConfigNm, report_group_id: int, logger):
    logger.info(msg)
    info_reply = f"戳一戳:\n"
    if msg.group_id:
        group_info = get_group_info(msg.group_id)
        if group_info is None:
            logger.error(f"群组信息获取失败: {msg.group_id}")
            pass
        else:
            info_reply += "来自>{msg.group_name}({msg.group_id})<\n"
    if not msg.user_id:
        logger.error("用户ID获取失败")
        return
    user_info = await get_user_info(bot, msg.user_id)
    if user_info is None:
        logger.error(f"用户信息获取失败: {msg.user_id}")
        info_reply += f"用户>?({msg.user_id})<"
    else:
        info_reply += f"用户>{user_info.nickname}({user_info.user_id})<"
    await bot.api.post_group_msg(group_id=report_group_id, text=info_reply)

