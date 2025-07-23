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
    return data["data"]

def save_group_info(group_list: list[dict], group_info_db: SqliteDatabase):
    with group_info_db.atomic():
        for group in group_list:
            # 如果群组已存在，则更新信息
            if GroupInfoDb.select().where(GroupInfoDb.group_id == group["group_id"]).exists():
                GroupInfoDb.update(
                    group_all_shut=group["group_all_shut"],
                    group_name=group["group_name"],
                    member_count=group["member_count"],
                    max_member_count=group["max_member_count"]
                ).where(GroupInfoDb.group_id == group["group_id"]).execute()
            else:
                GroupInfoDb.create(
                    group_all_shut=group["group_all_shut"],
                    group_id=group["group_id"],
                    group_name=group["group_name"],
                    member_count=group["member_count"],
                    max_member_count=group["max_member_count"]
                )

async def update_group_info(bot: BotClient, group_info_db: SqliteDatabase, logger) -> None:
    """
    更新群组信息
    Args:
        bot: BotClient实例
        group_info_db: 群组信息数据库
    """
    group_list = await get_group_list(bot)
    save_group_info(group_list, group_info_db)
    logger.info("群组信息已更新")

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

class UserInfo:

    def __init__(self, user_id, uid, uin, nickname, age, qid, qqLevel, sex, long_nick, reg_time, is_vip, is_years_vip, vip_level, remark, status, login_days):
        self.user_id = user_id
        self.uid = uid
        self.uin = uin
        self.nickname = nickname
        self.age = age
        self.qid = qid
        self.qqLevel = qqLevel
        self.sex = sex
        self.long_nick = long_nick
        self.reg_time = reg_time
        self.is_vip = is_vip
        self.is_years_vip = is_years_vip
        self.vip_level = vip_level
        self.remark = remark # 备注, 无需上传至远程数据库
        self.status = status
        self.login_days = login_days

async def get_user_info(bot: BotClient, user_id: int) -> UserInfo | None:
    """
    获取用户信息
    Args:
        user_id: 用户ID
    Returns:
        UserInfo对象或None
    """
    data = await bot.api.get_stranger_info(user_id=user_id)
    data = data["data"]
    user_info = UserInfo(
        user_id=data["user_id"],
        uid=data["uid"],
        uin=data["uin"],
        nickname=data["nickname"],
        age=data["age"],
        qid=data["qid"],
        qqLevel=data["qqLevel"],
        sex=data["sex"],
        long_nick=data["long_nick"],
        reg_time=data["reg_time"],
        is_vip=data["is_vip"],
        is_years_vip=data["is_years_vip"],
        vip_level=data["vip_level"],
        remark=data["remark"],
        status=data["status"],
        login_days=data["login_days"]
    )
    return user_info