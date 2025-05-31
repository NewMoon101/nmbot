# -*- coding: utf-8 -*-

from nm.funclib.funclib import del_whitespace, get_hash256

from ncatbot.core.message import GroupMessage, PrivateMessage

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