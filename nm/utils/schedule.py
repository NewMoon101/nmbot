# -*- coding: utf-8 -*-

import asyncio
import datetime

from peewee import SqliteDatabase
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from nm.core.info import update_group_info

from ncatbot.core.client import BotClient

async def schedule_main(bot: BotClient, group_info_db: SqliteDatabase, logger):
    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        update_group_info,
        'interval',
        hours=12,
        args=[bot, group_info_db, logger],
        id='update_group_info_job',
        next_run_time=datetime.datetime.now() + datetime.timedelta(seconds=10)  # 初始延迟10秒后执行
    )
    scheduler.start()
    try:
        await asyncio.Event().wait()  # Keep the scheduler running
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
        logger.info("Scheduler has been shut down.")