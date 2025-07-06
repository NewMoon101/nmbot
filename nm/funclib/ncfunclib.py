# -*- coding: utf-8 -*-

from nm.funclib.funclib import del_whitespace, get_hash256

from ncatbot.core.message import GroupMessage, PrivateMessage
from ncatbot.core.client import BotClient
from ncatbot.core import (MessageChain, Text, Reply, At, AtAll, Dice, Face, Image, Json, Music, CustomMusic, Record, Rps, Video, File)

def get_msg_img_num(msg: GroupMessage) -> int:
    """
    獲取一條**群**消息中的圖像數量
    Args:
        msg: 一條群消息
    Returns:
        數量
    """
    num = 0
    for i in msg.message:
        if i["type"] == "image":
            num += 1
        else:
            continue
    return num

def get_msg_hash(msg: GroupMessage | PrivateMessage) -> bytes:
    """
    獲取一條消息的sha256值  
    進行hash的內容爲消息中的所有文字內容除去空白字符(re中的\\s+)之後的字符以utf-8編碼
    Args:
        msg: 一條消息
    Returns:
        二進制sha256數據
    """
    msg_raw_text = get_msg_text(msg)
    msg_text = del_whitespace(msg_raw_text)
    msg_sha256 = get_hash256(msg_text.encode("utf-8"))
    return msg_sha256

def get_msg_text(msg: GroupMessage | PrivateMessage) -> str:
    """
    獲取一條消息中所有類型爲"text"的消息段, 已拼接
    Args:
        msg: 消息
    Returns:
        字符串
    """
    str0 = ""
    for i in msg.message:
        if i["type"] == "text":
            str0 += i["data"]["text"]
    return str0

def get_msg_image(msg: GroupMessage | PrivateMessage) -> list:
    """
    獲取一條消息中的"image"消息段
    Args:
        msg: 消息
    Returns:
        image消息段的列表
    """
    message_arry = []
    for i in msg.message:
        if i["type"] == "image":
            message_arry += i
    return message_arry

def trans_msg_to_msgchain(msg_arrays: list[dict]) -> MessageChain:
    """
    將一條msg_arrays轉換爲MessageChain對象
    Args:
        msg: 消息
    Returns:
        MessageChain對象
    """
    message_chain = MessageChain()
    for i in msg_arrays:
        if i["type"] == "text":
            message_chain += (Text(i["data"]["text"]))
        elif i["type"] == "image":
            message_chain += (Image(i["data"]["file"]))
        elif i["type"] == "reply":
            message_chain += (Reply(i["data"]["id"]))
        elif i["type"] == "at":
            message_chain += (At(i["data"]["qq"]))
        elif i["type"] == "at_all":
            message_chain += (AtAll())
        elif i["type"] == "dice":
            message_chain += (Dice(i["data"]["result"]))
        elif i["type"] == "face":
            message_chain += (Face(i["data"]["id"]))
        # elif i["type"] == "json":
        #     message_chain += (Json(i["data"]["content"]))  
        #暫時不支持json music custom_music record video file消息段
        elif i["type"] == "rps":
            message_chain += (Rps(i["data"]["result"]))
        elif i["type"] == "image":
            message_chain += (Image(i["data"]["file"])) # TODO: 圖像可能無法獲取, 以後應當在這裏加一個檢查機制
    return message_chain

async def post_msg_arrays_group(bot: BotClient, group_id: int, msg_arrays: list[dict]) -> None:
    """
    發送一條msg_arrays的群消息
    Args:
        bot: BotClient實例
        group_id: 群號
        msg_arrays: 消息數組
    """
    msg_chain = trans_msg_to_msgchain(msg_arrays)
    await bot.api.post_group_msg(group_id=group_id, rtf=msg_chain)
