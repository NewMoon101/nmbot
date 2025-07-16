# -*- coding: utf-8 -*-

from pathlib import Path
from peewee import SqliteDatabase, Model, IntegerField, TextField, AutoField, Proxy

from nm.core.config import ConfigNm

from ncatbot.core.client import BotClient

group_info_db_proxy = Proxy()  # 使用Proxy来延迟数据库的创建

def create_group_info_db(config_nm: ConfigNm) -> SqliteDatabase:
    db_path = Path(config_nm.db_local.path + "/group_info.db")
    if not db_path.parent.exists():
        db_path.parent.mkdir(parents=True, exist_ok=True)
    group_info_db = SqliteDatabase(db_path)
    group_info_db.connect()
    group_info_db_proxy.initialize(group_info_db)
    group_info_db.create_tables([GroupInfoDb])
    return group_info_db

class GroupInfoModel(Model):

    class Meta:
        database = group_info_db_proxy

class GroupInfoDb(GroupInfoModel):

    class Meta:  # type: ignore
        table_name = "group_info"

    id = AutoField()
    group_all_shut = IntegerField(default=0)  # 群全员禁言状态, 0表示未禁言, 1表示已禁言
    group_id = IntegerField(unique=True)  # 群组ID, 唯一
    group_name = TextField()
    member_count = IntegerField(default=0)  # 群成员數量
    max_member_count = IntegerField(default=0)  # 群最大成員數量

class GroupInfo:

    def __init__(self, group_id: int, group_name: str, member_count: int, max_member_count: int, group_all_shut: int = 0):
        self.group_id = group_id
        self.group_name = group_name
        self.member_count = member_count
        self.max_member_count = max_member_count
        self.group_all_shut = group_all_shut

async def get_group_list(bot: BotClient) -> list[dict]:
    data = await bot.api.get_group_list(no_cache=True)
    return data

def save_group_info(group_list: list[dict], group_info_db: SqliteDatabase):
    with group_info_db.atomic():
        for group in group_list:
            # 如果群组已存在，则更新信息
            if GroupInfoDb.select().where(GroupInfoDb.group_id == group["id"]).exists():
                GroupInfoDb.update(
                    group_all_shut=group["group_all_shut"],
                    group_name=group["group_name"],
                    member_count=group["member_count"],
                    max_member_count=group["max_member_count"]
                ).where(GroupInfoDb.group_id == group["id"]).execute()
            else:
                GroupInfoDb.create(
                    id=group["id"],
                    group_all_shut=group["group_all_shut"],
                    group_id=group["group_id"],
                    group_name=group["group_name"],
                    member_count=group["member_count"],
                    max_member_count=group["max_member_count"]
                )

def get_group_info(group_id: int) -> GroupInfo | None:
    group_info = GroupInfoDb.select().where(GroupInfoDb.group_id == group_id).first()
    if group_info:
        return GroupInfo(
            group_id=group_info.group_id,
            group_name=group_info.group_name,
            member_count=group_info.member_count,
            max_member_count=group_info.max_member_count,
            group_all_shut=group_info.group_all_shut
        )