# -*- coding: utf-8 -*-

from pathlib import Path
from peewee import SqliteDatabase, Model, IntegerField, AutoField, Proxy

from nm.core.config import ConfigNm

from ncatbot.core.message import GroupMessage

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

def statistic(msg: GroupMessage):
    insert_msg_record(msg)