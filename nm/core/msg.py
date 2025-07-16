# -*- coding: utf-8 -*-

from pathlib import Path
from peewee import SqliteDatabase, Model, IntegerField, TextField, BlobField, AutoField, ForeignKeyField, Proxy

from nm.funclib.funclib import time_time
from nm.funclib.ncfunclib import get_msg_img_num, get_msg_hash, get_msg_image

from ncatbot.core.client import BotClient
from ncatbot.core.message import GroupMessage

from nm.core.config import ConfigNm

msg_db_proxy = Proxy()  # 使用Proxy来延迟数据库的创建

def create_msg_db(config_nm: ConfigNm) -> SqliteDatabase:
    db_path = Path(config_nm.db_local.path + "/msg.db")
    if not db_path.parent.exists():
        db_path.parent.mkdir(parents=True, exist_ok=True)
    msg_db = SqliteDatabase(db_path)
    msg_db.connect()
    msg_db_proxy.initialize(msg_db)
    msg_db.create_tables([SavedMsg, MsgImg])
    return msg_db

class MsgModel(Model):

    class Meta:
        database = msg_db_proxy

class SavedMsg(MsgModel):

    class Meta: # type: ignore # 這裏會報錯, 無視即可
        table_name = "saved_msg"

    id = AutoField()
    data_scrape_time = IntegerField() # 數據抓取時間
    self_id = IntegerField() # 機器人自身的ID
    user_id = IntegerField() # 發送者的ID
    time = IntegerField() # 消息發送時間
    message_id = IntegerField() # 消息ID, 這個ID是唯一的, 但不是自增的
    message_seq = IntegerField() # 消息序列號, 這個ID是唯一的, 但不是自增的
    real_id = IntegerField() 
    message_type = TextField() # 消息類型, 例如"private"或"group"
    sender_user_id = IntegerField() # 發送者的ID
    sender_nickname = TextField() # 發送者的暱稱
    sender_card = TextField() # 發送者的群暱稱
    sender_role = TextField() # 發送者的角色, 例如"owner", "admin", "member"
    raw_message = TextField() # 原始CQ碼
    sub_type = TextField() # 消息子類型 normal json等
    message = TextField() # 消息內容, 消息段格式
    message_format = TextField() # 消息格式
    post_type = TextField() # 消息發送類型
    group_id = IntegerField() # 群組ID
    img_num = IntegerField() # 圖片數量
    hash_ = BlobField(unique=True) # 消息的哈希值, 用於檢測重複消息, 這個字段是唯一的

class MsgImg(MsgModel):

    class Meta: # type: ignore
        table_name = "msg_img"

    id = AutoField() # 自增主鍵
    data_scrape_time = IntegerField() # 數據抓取時間
    msg_db_id = ForeignKeyField(SavedMsg, field="id", backref="msg_img") # 對應消息的外鍵
    order_index = IntegerField() # 在消息中的順序
    file_path = TextField() # api返回的, 在本地的路徑
    file_name = TextField(unique=True) # 圖像名, 唯一, 可用來調用api
    # hash_ = BlobField(unique=True) 因爲有file_name所以這兒取hash沒必要

# 測試之後發現napcat提供的api可以把圖像保存到本地, 十分方便, 因而捨棄直接將二進制文件儲存進數據庫的方式
def insert_msg_img(msg_db_id: int, order_index: int, file_path: str, file_name: str) -> int:
    """ 插入一條消息中的圖片到數據庫
    Args:"""
    msg_img0 = MsgImg.create(data_scrape_time = time_time(), msg_db_id=msg_db_id, order_index=order_index, file_path=file_path, file_name=file_name)
    return msg_img0.id

def insert_saved_msg(msg: GroupMessage) -> int:
    """
    插入一條消息到數據庫
    Args:
        msg: 要插入的消息內容
    Returns:
        int: 插入的消息ID
    """
    saved_msg_data = {
        "data_scrape_time": time_time(),
        "self_id": msg.self_id,
        "user_id": msg.user_id,
        "time": msg.time,
        "message_id": msg.message_id,
        "message_seq": msg.message_seq,
        "real_id": msg.real_id,
        "message_type": msg.message_type,
        "sender_user_id": msg.sender.user_id,
        "sender_nickname": msg.sender.nickname,
        "sender_card": msg.sender.card,
        "sender_role": "null_temp",  # TODO: sender_role不是在收到消息時能獲得的, 而是使用get_group_member_list之類的函數獲取的, 暫時未增加此功能
        "raw_message": msg.raw_message,
        "sub_type": msg.sub_type,
        "message": msg.message,
        "message_format": msg.message_format,
        "post_type": msg.post_type,
        "group_id": msg.group_id,
        "img_num": get_msg_img_num(msg),
        "hash_": get_msg_hash(msg)
    }
    saved_msg0 = SavedMsg.create(**saved_msg_data)
    return saved_msg0.id

async def save_img(msg_db_id: int, img_array: list, bot: BotClient) -> None:
    """ 保存一條消息中的所有圖片
    Args:
        img_array: 要保存的圖片數組
        bot: BotClient實例
    """
    i = 0
    for img in img_array:
        img_data = await bot.api.get_image(img["data"]["file"])
        insert_msg_img(msg_db_id, i, img_data["file"], img_data["file_name"])
        i += 1

async def save_msg(msg: GroupMessage, bot: BotClient) -> None:
    """
    保存一條**群**消息
    Args:
        msg: 要保存的消息
    """
    msg_db_id = insert_saved_msg(msg)
    #下面是圖像處理
    img_array = get_msg_image(msg)
    await save_img(msg_db_id, img_array, bot)

