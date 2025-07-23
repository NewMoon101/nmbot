# -*- coding: utf-8 -*-

from nm.core.config import ConfigNm
from nm.funclib.ncfunclib import get_msg_at, get_msg_type, get_msg_reply
from nm.core.info import get_group_info, get_user_info

from ncatbot.core.client import BotClient
from ncatbot.core.message import GroupMessage, PrivateMessage
from ncatbot.core.notice import NoticeMessage

async def report_ated(msg: GroupMessage, bot:BotClient, config_nm: ConfigNm, report_group_id: int, logger, is_report_at_all=False):
    flag_at_all = False
    if is_report_at_all:
        if "all" in get_msg_at(msg):
            flag_at_all = True
    if config_nm.selfid in get_msg_at(msg) or flag_at_all:
        logger.info(msg)
        group_info = get_group_info(msg.group_id)
        if group_info is None:
            logger.error(f"群组信息获取失败: {msg.group_id}")
            return
        info_reply = f"群消息:\n来自群>{group_info.group_name}({group_info.group_id})<\n用户>{msg.sender.nickname}({msg.user_id})<"
        await bot.api.post_group_msg(group_id=report_group_id, text=info_reply)
        await bot.api.forward_group_single_msg(group_id=report_group_id, message_id=msg.message_id)

async def report_msg_private(msg: PrivateMessage, bot: BotClient, config_nm: ConfigNm, report_group_id: int, logger):
    info_reply = f"私聊消息:\n来自>{msg.sender.nickname}({msg.user_id})<"
    await bot.api.post_group_msg(group_id=report_group_id, text=info_reply)
    await bot.api.forward_group_single_msg(group_id=report_group_id, message_id=msg.message_id)

async def report_poke(msg: NoticeMessage, bot: BotClient, config_nm: ConfigNm, report_group_id: int, logger):
    if msg["notice_type"] == "notify": #type: ignore
        if msg["sub_type"] == "poke": # type: ignore
            if config_nm.selfid == str(msg["target_id"]): #notice类未被解析, 目前是dict, 见ncatbot的issue https://github.com/liyihao1110/ncatbot/issues/171 #type: ignore
                msg = NoticeMessage(msg)  #type: ignore
                info_reply = f"戳一戳:\n"
                if msg.group_id:
                    group_info = get_group_info(msg.group_id)
                    if group_info is None:
                        logger.error(f"群组信息获取失败: {msg.group_id}")
                        pass
                    else:
                        info_reply += f"来自群>{group_info.group_name}({msg.group_id})<\n"
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

async def report_red_pocket(msg: GroupMessage, bot: BotClient, config_nm: ConfigNm, report_group_id: int, logger): # 因完全无法解析红包相关内容, 以下所有判定方式均是猜测
    if msg.raw_message == "" and msg.message == [] and msg.message_format == "array" and msg.post_type == "message":
        group_info = get_group_info(msg.group_id)
        if group_info is None:
            logger.error(f"群组信息获取失败: {msg.group_id}")
            return
        info_reply = f"无内容的群消息:\n来自>{group_info.group_name}({msg.group_id})<"
        await bot.api.post_group_msg(group_id=report_group_id, text=info_reply)

async def report_replied(msg: GroupMessage, bot: BotClient, config_nm: ConfigNm, report_group_id: int, logger):
    if "reply" in get_msg_type(msg):
        msg_id = get_msg_reply(msg)
        try:
            replied_msg_data: dict = await bot.api.get_msg(message_id=msg_id)
            replied_user_id: int = replied_msg_data.get("user_id", 0)
        except Exception as e:
            logger.info(e)
        else:
            if config_nm.selfid == str(replied_user_id):
                info_reply = f"回复:\n"
                logger.info(msg)
                group_info = get_group_info(msg.group_id)
                if group_info is None:
                    logger.error(f"群组信息获取失败: {msg.group_id}")
                    return
                info_reply += f"来自群>{group_info.group_name}({msg.group_id})<\n用户>{msg.sender.nickname}({msg.user_id})<"
                await bot.api.post_group_msg(group_id=report_group_id, text=info_reply)
                await bot.api.forward_group_single_msg(group_id=report_group_id, message_id=msg.message_id)