# -*- coding: utf-8 -*-

from nm.funclib.ncfunclib import trans_msg_to_msgchain

from ncatbot.core.client import BotClient

async def post_json_msg_group(bot: BotClient, group_id: int, json_msg: list[dict]) -> None:
    """
    發送一條json格式的群消息
    Args:
        bot: BotClient實例
        group_id: 群號
        json_msg: json格式的消息
    """
    msg_chain = trans_msg_to_msgchain(json_msg)
    await bot.api.post_group_msg(group_id=group_id, rtf=msg_chain)

