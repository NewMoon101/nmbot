# -*- coding: utf-8 -*-

import shlex
from argparse import ArgumentError

from peewee import SqliteDatabase

from nm.core.config import ConfigNm
from nm.core.info import update_group_info
from nm.funclib.funclib import get_sysinfo, NoExitArgumentParser
from nm.funclib.ncfunclib import get_msg_text, get_msg_at, get_msg_type
from nm.utils.promote import promote_t, show_promote_config, add_tag, del_tag, change_mode, change_mode_to, change_tag, add_group, del_group, change_promote_wait_time
from nm.utils.master import reply_friend_and_group_num

from ncatbot.core import BotClient
from ncatbot.core.message import GroupMessage

help_text = """nmbot 帮助
help 唤出此列表
sysinfo 查看cpu和内存使用情况
update 更新数据库
    -m 指定模块
        group_info qq群数据
显示 显示某些数据
    群友数 群数和好友数
宣发 宣发一条消息
    [reply] 需要在回复一条消息的情况下
显示宣发 显示宣发配置
宣发时间 修改宣发等待时间
    [time1] [time2] 接收两个正整数, 前者为最小值, 后者为最大值
添加标签 添加群标签
    [tag_name]
删除标签 使用方法同上
切换模式 切换当前正在使用的标签的黑白模式
添加群 在当前正在使用的标签中添加群
    [group_id] 接收大于1个qq群id, 以空格( )分割
删除群 使用方法同上

以上命令只有机主可以使用
如果消息中含有@, 只有只@了一个bot的会被该bot执行
""" # TODO: 编写帮助列表

async def command(bot: BotClient, msg: GroupMessage, config_nm: ConfigNm, logger, group_info_db: SqliteDatabase) -> None:
    """全部聊天內命令入口
    Args:
        bot (BotClient): BotClient實例
        msg (GroupMessage): 群消息實例
        config_nm (ConfigNm): 配置實例
        logger: 日志實例
    """
    # master 命令
    if int(msg.user_id) in config_nm.master:
        parser = NoExitArgumentParser(description="NcatBot Command Parser", exit_on_error=False)
        parser.add_argument("command", type=str, help="要執行的命令")
        if not get_msg_text(msg).strip(): # 如果消息文本為空，則不執行任何命令; 且防止parser解析出錯導致的sysexit
            return None
        try:
            tokens = shlex.split(get_msg_text(msg).strip())
            args = parser.parse_args(tokens)
        except Exception as e:
            return
        else:
            if len(get_msg_at(msg)) == 0 or (config_nm.selfid in get_msg_at(msg) and (len(get_msg_at(msg)) == 1)): # 如果沒被@, 直接執行; 如果被@了, 只有只@了bot纔能執行
                if args.command == "sysinfo":
                    sysinfo = get_sysinfo()
                    logger.info(f"(bot:{config_nm.selfid}) 系統信息: {sysinfo}")
                    await bot.api.post_group_msg(group_id=msg.group_id, text=f"cpu: {sysinfo['cpu_usage']}\nmemory: {sysinfo['memory_usage']}")
                    return
                elif args.command == "help":
                    await bot.api.post_group_msg(group_id=msg.group_id, text=help_text)
                    return
                elif args.command == "update":
                    parser.add_argument("-m", "--module", type=str, help="要更新的模塊")
                    args = parser.parse_args(shlex.split(get_msg_text(msg)))
                    if args.module:
                        if args.module == "group_info":
                            await update_group_info(bot, group_info_db, logger)
                            await bot.api.post_group_msg(group_id=msg.group_id, text="已更新")
                            return
                        return
                    return
                elif args.command == "显示":
                    parser.add_argument("thing", type=str, help="要显示的东西")
                    args = parser.parse_args(shlex.split(get_msg_text(msg)))
                    if args.thing:
                        if args.thing == "群友数":
                            await reply_friend_and_group_num(msg, bot, config_nm, logger)
                            return
                elif args.command == "宣发":
                    if config_nm.function_open.promote == True:
                        if not "reply" in get_msg_type(msg):
                            logger.warning(f"(bot:{config_nm.selfid}) 消息{msg.message_id}不含reply消息段, 无法宣发")
                            return
                        else:
                            await promote_t(bot, msg, config_nm, logger)
                            return
                elif args.command == "显示宣发":
                    if config_nm.function_open.promote == True:
                        await show_promote_config(bot, msg, config_nm, logger)
                        logger.info(f"(bot:{config_nm.selfid}) 显示宣发配置")
                        return
                elif args.command == "宣发时间":
                    if config_nm.function_open.promote == True:
                        parser.add_argument("time", type=int, nargs="+", help="宣发等待时间")
                        args = parser.parse_args(shlex.split(get_msg_text(msg)))
                        if args.time:
                            if len(args.time) == 1:
                                await change_promote_wait_time(bot, msg, args.time[0], args.time[0], config_nm, logger)
                            elif len(args.time) >= 2 :
                                await change_promote_wait_time(bot, msg, args.time[0], args.time[1], config_nm, logger)
                        return
                elif args.command == "添加标签":
                    if config_nm.function_open.promote == True:
                        parser.add_argument("tag", type=str, help="要添加的tag")
                        args = parser.parse_args(shlex.split(get_msg_text(msg)))
                        if args.tag:
                            await add_tag(bot, msg, args.tag, config_nm, logger)
                            return
                elif args.command == "删除标签":
                    if config_nm.function_open.promote == True:
                        parser.add_argument("tag", type=str, help="要删除的tag")
                        args = parser.parse_args(shlex.split(get_msg_text(msg)))
                        if args.tag:
                            await del_tag(bot, msg, args.tag, config_nm, logger)
                            return
                elif args.command == "切换标签":
                    if config_nm.function_open.promote == True:
                        parser.add_argument("tag", type=str, help="要修改的tag")
                        args = parser.parse_args(shlex.split(get_msg_text(msg)))
                        await change_tag(bot, msg,  args.tag, config_nm, logger)
                        return
                elif args.command == "切换模式":
                    if config_nm.function_open.promote == True:
                        parser.add_argument("-m", "--mode", type=str, help="要修改的模式", choices=["white", "black"])
                        try:
                            args = parser.parse_args(shlex.split(get_msg_text(msg)))
                        except ArgumentError:
                            logger.warning(f"(bot:{config_nm.selfid}) 切换模式命令参数错误")
                            await bot.api.post_group_msg(group_id=msg.group_id, text="参数错误，请检查命令格式")
                            return
                        if args.mode:
                            await change_mode_to(bot, msg, args.mode, config_nm, logger)
                        else:
                            await change_mode(bot, msg, config_nm, logger)
                            return
                elif args.command == "添加群":
                    if config_nm.function_open.promote == True:
                        parser.add_argument("group_id", type=int, nargs="+", help="要添加的群ID")
                        args = parser.parse_args(shlex.split(get_msg_text(msg)))
                        if args.group_id:
                            await add_group(bot, msg, args.group_id, config_nm, logger)
                            return
                elif args.command == "删除群":
                    if config_nm.function_open.promote == True:
                        parser.add_argument("group_id", type=int, nargs="+", help="要删除的群ID")
                        args = parser.parse_args(shlex.split(get_msg_text(msg)))
                        if args.group_id:
                            await del_group(bot, msg, args.group_id, config_nm, logger)
                            return
            else:
                pass