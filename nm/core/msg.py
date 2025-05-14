# -*- coding: utf-8 -*-

import sqlite3
from pathlib import Path

def creat_msg_db():
    try:
        msg_db_path : str = str(Path(".", "data", "msg.db"))
        table_name = "msg"
        creat_table_sql : str = f"""
            CREATE TABLE IF NOT EXISTS {table_name} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data_scrape_time INTEGER,
            self_id INTEGER,
            user_id INTEGER,
            time INTEGER,
            message_id INTEGER,
            message_seq INTEGER,
            real_id INTEGER,
            message_type TEXT,
            sender_user_id INTEGER,
            sender_nickname TEXT,
            sender_card TEXT,
            sender_role TEXT,
            raw_message TEXT,
            sub_type TEXT,
            message TEXT,
            message_format TEXT,
            post_type TEXT,
            group_id INTEGER,
            img_num INTEGER,
            hash BLOB UNIQUE
            );
            """
        # message_id 在不同賬戶中不互通, 不方便使用, 因而使用hash值作爲唯一約束
        # hash的計算邏輯見函數
        # img_num 在構造消息時應當進行檢驗, 和msg_img中能查詢到的數量是否相符
        conn = sqlite3.connect(msg_db_path)
        cursor = conn.cursor()
        cursor.execute(creat_table_sql)
        conn.commit()
        cursor.close()
        conn.close()
        table_name_1 = "msg_img"
        creat_table_sql : str = f"""
            CREATE TABLE IF NOT EXISTS {table_name_1} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data_scrape_time INTEGER,
            msg_db_id INTEGER,
            order_index INTEGER,
            img_name TEXT,
            img_data BLOB,
            hash BLOB UNIQUE,
            FOREIGN KEY (msg_db_id) REFERENCES {table_name}(id)
            );
            """
        # msg_db_id 作爲外鍵
        # order 當一條消息中的圖像數量大於一個的時候確定插入順序
        conn = sqlite3.connect(msg_db_path)
        cursor = conn.cursor()
        cursor.execute(creat_table_sql)
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"{e}")
        return 1 # 未知錯誤
    else:
        return 0 # 正常完成
