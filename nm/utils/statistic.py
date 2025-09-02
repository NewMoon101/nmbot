# -*- coding: utf-8 -*-

from pathlib import Path
from peewee import SqliteDatabase, Model, IntegerField, AutoField, Proxy

from nm.core.config import ConfigNm

from ncatbot.core.message import GroupMessage
from ncatbot.core.client import BotClient

# 以下 用于统计消息数据
msg_statistic_db_proxy = Proxy()

def create_msg_record_db(config_nm: ConfigNm) -> SqliteDatabase:
    db_path = Path(config_nm.db_local.path + "/msg_record.db")
    if not db_path.parent.exists():
        db_path.parent.mkdir(parents=True, exist_ok=True)
    msg_record_db = SqliteDatabase(db_path)
    msg_record_db.connect()
    msg_statistic_db_proxy.initialize(msg_record_db)
    msg_record_db.create_tables([MsgRecord])
    return msg_record_db

class Record(Model):

    class Meta:
        database = msg_statistic_db_proxy

class MsgRecord(Record):

    class Meta: # type: ignore
        table_name = "msgs"

    id = AutoField()
    group_id = IntegerField()
    user_id = IntegerField()
    time = IntegerField()

def insert_msg_record(msg: GroupMessage):
    msg_record_data = {
        "group_id": msg.group_id,
        "user_id": msg.user_id,
        "time": msg.time
    }
    MsgRecord.create(**msg_record_data)

def analysis_total_msg_frequence():
    data = list(Record.select())
    pass

# 以下, 用于实现"bot多久没在某群发言了"功能
self_msg_record_db_proxy = Proxy()

def create_self_msg_record_db(config_nm: ConfigNm) -> SqliteDatabase:
    db_path = Path(config_nm.db_local.path + "/self_msg_record.db")
    if not db_path.parent.exists():
        db_path.parent.mkdir(parents=True, exist_ok=True)
    self_msg_record_db = SqliteDatabase(db_path)
    self_msg_record_db.connect()
    self_msg_record_db_proxy.initialize(self_msg_record_db)
    self_msg_record_db.create_tables([MsgRecord])
    return self_msg_record_db

class SelfRecord(Model):

    class Meta:
        database = self_msg_record_db_proxy

class SelfMsgRecord(SelfRecord):

    class Meta: # type: ignore
        table_name = "record"

    group_id = IntegerField(primary_key=True)
    time = IntegerField()

def insert_self_msg_record(msg: GroupMessage):
    msg_record_data = {
        "group_id": msg.group_id,
        "time": msg.time
    }
    SelfMsgRecord.create(**msg_record_data)

def update_self_msg_record(bot: BotClient, msg: GroupMessage, config_nm: ConfigNm, logger):
    if str(msg.user_id) == config_nm.selfid:
        insert_self_msg_record(msg)
        logger.debug(f"(bot:{config_nm.selfid}) 更新了bot消息記錄數據庫")

def statistic(bot: BotClient, msg: GroupMessage, config_nm: ConfigNm, logger):
    insert_msg_record(msg)
    update_self_msg_record(bot, msg, config_nm, logger)