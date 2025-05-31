# -*- coding: utf-8 -*-

from pathlib import Path
from peewee import SqliteDatabase, Model, IntegerField, TextField, BlobField, AutoField, ForeignKeyField

from nm.funclib.funclib import time_time
from nm.funclib.ncfunclib import get_msg_img_num, get_msg_hash, get_msg_image

from ncatbot.core.message import GroupMessage

msg_db_path : str = str(Path(".", "data", "msg.db")) # 這裏的路徑不知放在哪裏, 暫時先寫在這裏吧, 以後可能放進config

def create_msg_db():
    msg_db.connect()
    msg_db.create_tables([SavedMsg, MsgImg])

msg_db = SqliteDatabase(msg_db_path) # 對於這個庫, 期望之後加入檢測大小自動存檔之前消息的功能

class MsgModel(Model):

    class Meta:
        database = msg_db

class SavedMsg(MsgModel):

    class Meta: # type: ignore # 這裏會報錯, 無視即可
        table_name = "saved_msg"

    id = AutoField()
    data_scrape_time = IntegerField()
    self_id = IntegerField()
    user_id = IntegerField()
    time = IntegerField()
    message_id = IntegerField()
    message_seq = IntegerField()
    real_id = IntegerField()
    message_type = TextField()
    sender_user_id = IntegerField()
    sender_nickname = TextField()
    sender_card = TextField()
    sender_role = TextField()
    raw_message = TextField()
    sub_type = TextField()
    message = TextField()
    message_format = TextField()
    post_type = TextField()
    group_id = IntegerField()
    img_num = IntegerField()
    hash_ = BlobField(unique=True)

class MsgImg(MsgModel):

    class Meta: # type: ignore
        table_name = "msg_img"

    id = AutoField() # 自增主鍵
    data_scrape_time = IntegerField()
    msg_db_id = ForeignKeyField(SavedMsg, field="id", backref="msg_img") # 對應消息的外鍵
    order_index = IntegerField() # 在消息中的順序
    file_path = TextField() # api返回的, 在本地的路徑
    file_name = TextField(unique=True) # 圖像名, 唯一, 可用來調用api
    # hash_ = BlobField(unique=True) 因爲有file_name所以這兒取hash沒必要

# 測試之後發現napcat提供的api可以把圖像保存到本地, 十分方便, 因而捨棄下面的函數(直接將二進制文件儲存進數據庫的方式)
# def insert_msg_img(msg_db_id: int, order_index: int, img_name: str, img_data: bytes, hash_: bytes) -> int:
#     msg_img0 = MsgImg.create(data_scrape_time = int(time_time()), msg_db_id = msg_db_id, order_index = order_index, img_name = img_name, img_data = img_data, hash_ = hash_)
#     return msg_img0.id
def insert_msg_img(msg_db_id: int, order_index: int, file_path: str, file_name: str) -> int:
    msg_img0 = MsgImg.create(data_scrape_time = time_time(), msg_db_id=msg_db_id, order_index=order_index, file_path=file_path, file_name=file_name)
    return msg_img0.id

def insert_saved_msg(self_id: int, user_id: int, time: int, message_id: int, message_seq: int, real_id: int, message_type: str, sender_user_id: int, sender_nickname: str, sender_card: str, sender_role: str, raw_message: str, sub_type: str, message: str, message_format: str, post_type: str, group_id: int, img_num: int, hash_: bytes) -> int:
    saved_msg0 = SavedMsg.create(data_scrape_time = time_time(), self_id = self_id, user_id = user_id, time = time, message_id = message_id, message_seq = message_seq, real_id = real_id, message_type = message_type, sender_user_id = sender_user_id, sender_nickname = sender_nickname, sender_card = sender_card, sender_role = sender_role, raw_message = raw_message, sub_type = sub_type, message = message, message_format = message_format, post_type = post_type, group_id = group_id, img_num = img_num, hash_ = hash_)
    return saved_msg0.id

async def save_msg(msg: GroupMessage) -> None:
    """
    保存一條**群**消息
    Args:
        msg: 要保存的消息
    """
    img_num = get_msg_img_num(msg)
    hash_ = get_msg_hash(msg)
    insert_saved_msg(self_id=msg.self_id, user_id=msg.user_id, time=msg.time, message_id=msg.message_id, message_seq=msg.message_seq, real_id=msg.real_id, message_type=msg.message_type, sender_user_id=msg.sender.user_id, sender_nickname=msg.sender.nickname, sender_card=msg.sender.card, sender_role="null_temp", raw_message=msg.raw_message, sub_type=msg.sub_type, message=msg.message, message_format=msg.message_format, post_type=msg.post_type, group_id=msg.group_id, img_num=img_num, hash_=hash_) # TODO: sender_role不是在收到消息時能獲得的, 而是使用get_group_member_list之類的函數獲取的, 因爲這個字段並不重要, 暫時未增加此功能
    #下面是圖像處理
    img_array = get_msg_image(msg)
    for i in img_array:
        pass #TODO:
