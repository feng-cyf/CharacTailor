# database/raw_mysql.py
import contextvars
import threading

import aiomysql
import os

from dotenv import load_dotenv

POOL = None
load_dotenv("D:\GridFriend\AI\database.env")
async def init_raw_pool():
    global POOL
    POOL = await aiomysql.create_pool(
        host=os.getenv("DB_HOST", "127.0.0.1"),
        port=int(os.getenv("DB_PORT", "3306")),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("Mysql_Pwd"),
        db=os.getenv("db"),
        charset="utf8mb4",
        autocommit=True,
        minsize=1,
        maxsize=10,
    )

async def close_raw_pool():
    if POOL:
        POOL.close()
        await POOL.wait_closed()

def get_raw_pool():
    return POOL