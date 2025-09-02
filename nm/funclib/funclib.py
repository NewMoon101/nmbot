# -*- coding: utf-8 -*-

import re
import os
import sys
import time
import random
import signal
import aiohttp
import hashlib
import asyncio
import argparse
import textwrap

import psutil
from PIL import Image, ImageDraw, ImageFont

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

async def download_img(url, retry_times: int = 3) -> bytes | None:
    for _ in range(0,retry_times):
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    return await response.read()
                else:
                    continue

def get_hash256(data: bytes) -> bytes:
    """
    获取数据的sha256值
    Args:
        data: 二进制的数据
    Returns:
        二进制数据
    """
    # TODO:數據很大时可能有性能问题
    hash256 = hashlib.sha256()
    hash256.update(data)
    return hash256.digest()

def time_time() -> int:
    return int(time.time())

def del_whitespace(s: str) -> str:
    """
    刪除字符串中的空白字符
    Args:
        s: 一個字符串
    Returns:
        一個字符串
    """
    s_ = re.sub(r"\s+", "", s)
    return s_

def func_time(func):
    def wrapper():
        start_time = time.time()
        func()
        end_time = time.time()
        print(f"運行時間: {end_time - start_time}")
    return wrapper

def get_sysinfo() -> dict[str, float]:
    """获取系统信息，包括CPU和内存使用率"""
    cpu_usage = psutil.cpu_percent(interval=1)
    memory_info = psutil.virtual_memory()
    memory_usage = memory_info.percent
    return {"cpu_usage": cpu_usage, "memory_usage": memory_usage}

class NoExitArgumentParser(argparse.ArgumentParser):
    def exit(self): # type: ignore
        pass

    def error(self, message): # type: ignore
        pass

def text_to_png(text: str,
                out_path: str,
                font_path: str | None = None,
                font_size: int = 40,
                max_width_px: int | None = None,      # 画布最大宽度，None=不限
                char_soft_wrap: int = 128,            # 字符数软阈值，仅当 max_width_px=None 时生效
                padding: int = 10,
                line_spacing: int = 10,
                bg='white',
                fg='black') -> None:
    """
    将多行文本渲染为 PNG，支持长行自动分行。
    text        : 原始字符串，可含 \n
    out_path    : 输出 PNG 文件
    font_path   : 支持中文的 TTF 路径，如 'msyh.ttc'
    max_width_px: 画布最大像素宽度；若给定，则按像素精确断行。
                  若 None，则按 char_soft_wrap 字符数粗略断行。
    char_soft_wrap: 当 max_width_px=None 时，每行最大字符数
    padding     : 四周留白
    line_spacing: 行间距（像素）
    """
    # 1) 字体
    font = ImageFont.truetype(font_path, font_size) if font_path \
           else ImageFont.load_default()

    # 2) 按行拆分
    raw_lines = text.splitlines()
    wrapped_lines = []
    dummy = Image.new('RGB', (1, 1))
    draw = ImageDraw.Draw(dummy)

    for line in raw_lines:
        if line.strip() == '':
            wrapped_lines.append('')
            continue

        # 如果给了像素宽度，用像素断行；否则按字符数软断行
        if max_width_px is not None:
            # 逐字符累加直到超宽
            words = list(line)
            current = ''
            for ch in words:
                test = current + ch
                l, t, r, b = draw.textbbox((0, 0), test, font=font)
                w, h = r - l, b - t
                if w <= max_width_px - 2*padding:
                    current = test
                else:
                    if current:
                        wrapped_lines.append(current)
                    current = ch
            if current:
                wrapped_lines.append(current)
        else:
            # 字符数软断行
            wrapped_lines.extend(textwrap.wrap(line, width=char_soft_wrap))

    # 3) 计算画布尺寸
    line_sizes = []
    for ln in wrapped_lines:
        l, t, r, b = draw.textbbox((0, 0), ln, font=font)
        line_sizes.append((r - l, b - t))
    max_w = max(w for w, _ in line_sizes) if line_sizes else 0
    total_h = sum(h for _, h in line_sizes) + line_spacing * max(0, len(line_sizes) - 1)

    img_w = max_w + 2 * padding
    img_h = total_h + 2 * padding

    # 4) 绘图
    img = Image.new('RGB', (img_w, img_h), color=bg)
    draw = ImageDraw.Draw(img)
    y = padding
    for ln, (w, h) in zip(wrapped_lines, line_sizes):
        draw.text((padding, y), ln, font=font, fill=fg)
        y += h + line_spacing

    # 5) 保存
    img.save(out_path)

# -------------------- 示例 --------------------
if __name__ == "__main__":
    long_line = "a" * 200  # 200 个 a
    chinese_long = "这" * 150
    multiline = f"第一行\n{long_line}\n{chinese_long}\n最后一行"

    text_to_png(multiline,
                out_path="multi.png",
                font_path="msyh.ttc",   # 替换为本地中文字体
                font_size=36,
                max_width_px=600,       # 画布最大 600 px，超长按像素断行
                padding=15,
                line_spacing=8)