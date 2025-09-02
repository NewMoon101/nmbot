# -*- coding: utf-8 -*-

import time
import asyncio
import datetime

from pathlib import Path
from peewee import SqliteDatabase, Model, IntegerField, AutoField, Proxy
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from nm.funclib.funclib import text_to_png
from nm.core.config import ConfigNm
from nm.core.info import get_group_list, get_group_info

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
    self_msg_record_db.create_tables([SelfMsgRecord])
    return self_msg_record_db

class SelfRecord(Model):

    class Meta:
        database = self_msg_record_db_proxy

class SelfMsgRecord(SelfRecord):

    class Meta: # type: ignore
        table_name = "record"

    group_id = IntegerField(primary_key=True)
    time = IntegerField()

async def init_self_msg_record_db(bot: BotClient, self_msg_record_db: SqliteDatabase):
    # 首次創建, 以及添加新群時可使用
    group_list = await get_group_list(bot)
    group_list = [x["group_id"] for x in group_list]
    group_data = [{"group_id": int(i), "time": 0} for i in group_list]
    with self_msg_record_db.atomic():
        SelfMsgRecord.insert_many(group_data).on_conflict("ignore").execute()

async def delete_inexistent_group_self_db(bot: BotClient):
    group_list = await get_group_list(bot)
    group_list = [x["group_id"] for x in group_list]
    ids = [row.group_id for row in SelfMsgRecord.select(SelfMsgRecord.group_id)]
    diff = list(set(ids) - set(group_list))
    SelfMsgRecord.delete().where(SelfMsgRecord.group_id.in_(diff)).execute()

async def update_self_msg_record_db_cron(bot: BotClient, config_nm: ConfigNm, self_msg_record_db: SqliteDatabase, logger):
    await init_self_msg_record_db(bot, self_msg_record_db)
    await delete_inexistent_group_self_db(bot)
    logger.info(f"(bot:{config_nm.selfid}) 已更新bot發言記錄數據庫")

async def schedule_statistic_self(bot: BotClient, config_nm: ConfigNm, self_msg_record_db: SqliteDatabase, logger):
    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        update_self_msg_record_db_cron,
        "interval",
        hours=12,
        args=[bot, config_nm, self_msg_record_db, logger],
        id="update_self_msg_record_db",
        next_run_time=datetime.datetime.now() + datetime.timedelta(seconds=10)
    )
    scheduler.start()
    try:
        await asyncio.Event().wait()
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
        logger.info(f"(bot:{config_nm.selfid}) stop")

def insert_self_msg_record(msg: GroupMessage):
    msg_record_data = {
        "group_id": msg.group_id,
        "time": msg.time
    }
    SelfMsgRecord.insert(msg_record_data).on_conflict_replace().execute()

def update_self_msg_record(bot: BotClient, msg: GroupMessage, config_nm: ConfigNm, logger):
    if str(msg.user_id) == config_nm.selfid:
        insert_self_msg_record(msg)
        logger.debug(f"(bot:{config_nm.selfid}) 更新了bot消息記錄數據庫")

async def report_self_msg_record(bot: BotClient, msg: GroupMessage, config_nm:ConfigNm, logger):
    data:list[SelfMsgRecord] = list(SelfMsgRecord.select())
    data.sort(key= lambda group_time: group_time.time) # type: ignore
    time_now = int(time.time())
    text = ""
    for group_time in data:
        group_text = ""
        gorup_info = get_group_info(group_time.group_id) # type: ignore
        group_name = gorup_info.group_name # type: ignore
        if group_time.time == 0:
            time_text = "从未\n"
        else:
            time_delta = datetime.timedelta(time_now - group_time.time) # type: ignore # 未校验 
            hms = str(time_delta)
            time_text = hms + "\n"
        group_text = f"{group_name}({group_time.group_id}): {time_text}"
        text += group_text
    img_path = Path(config_nm.cache_path) / "self_msg_record.png"
    font_path = Path("src", "font", "SourceHanSansCN-Bold.otf")
    text_to_png(text=text, out_path=str(img_path), font_path=str(font_path), font_size=20)
    await bot.api.post_group_msg(group_id=msg.group_id, image=str(img_path))
    logger.info(f"(bot:{config_nm.selfid}) 上报了多久未发言")



def statistic(bot: BotClient, msg: GroupMessage, config_nm: ConfigNm, logger):
    insert_msg_record(msg)
    update_self_msg_record(bot, msg, config_nm, logger)