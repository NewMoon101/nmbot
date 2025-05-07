# -*- coding: utf-8 -*-

import re
import os
import sys
import time
import random
import signal
import asyncio

def sleep_random(min: int, max: int) -> None:
    time.sleep(random.randrange(min, max))

async def sleep_random_async(min: int, max: int) -> None:
    await asyncio.sleep(random.randrange(min, max))

def restart_program():
    """重启当前进程"""
    python = sys.executable  # 获取当前 Python 解释器路径
    os.execvp(python, [python] + sys.argv)  # 重新启动脚本

def stop_program():
    """結束當前進程"""
    # sys.exit(0)
    os.kill(os.getpid(), signal.SIGINT)

def print_value_and_type(object0: object):
    print(object0)
    print(type(object0))

def parse_command_order(command_str: str) -> tuple[dict[str, list], dict[str, list]]:
    pattern = r'\S+'
    matches = re.findall(pattern, command_str)
    command = ""
    options_values = []
    for match in matches:
        if command == "":
            command = match
        else:
            options_values.append(match)
    pair_dict = {}
    if options_values == []:
        return ({command:[]}, pair_dict)
    else:
        if options_values[0][0] != "-":
                command_pair_list = [options_values[0]]
                for j in range(1, len(options_values)):
                    if options_values[j][0] == "-":
                        break
                    else:
                        command_pair_list.append(options_values[j])
        else:
            command_pair_list = []
        for i in range(len(options_values)):
            if options_values[i][0] == "-": # 這是一個option
                if i == len(options_values) - 1: # 這是最後一個option, 後面沒有參數了
                    pair_dict[options_values[i]] = []
                elif options_values[i + 1][0] == "-": # 下一個也是option
                    pair_dict[options_values[i]] = []
                else: # 下一個不是options
                    option_pair_list = [options_values[i + 1]]
                    for k in range(i + 2, len(options_values)):
                        if options_values[k][0] == "-":
                            break
                        else:
                            option_pair_list.append(options_values[k])
                    pair_dict[options_values[i]] = option_pair_list
    return {command: command_pair_list}, pair_dict