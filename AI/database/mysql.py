import os

from fastapi import FastAPI
from flask.cli import load_dotenv
from tortoise import Tortoise
from tortoise.contrib.fastapi import register_tortoise
load_dotenv(r"D:\GridFriend\AI\database.env")

TORTOISE_ORM = {
    "connections": {
        "default": {
            "engine": "tortoise.backends.mysql",
            "credentials": {
                "host": "127.0.0.1",
                "port": 3306,
                "user": "root",
                "password": os.getenv("Mysql_Pwd"),
                "database": os.getenv("db"),
                "charset": "utf8mb4",
                "connect_timeout": 10,
            }
        }
    },
    "apps": {
        "base": {
            "models": [
                "models.model",
                "aerich.models"
            ],
            "default_connection": "default",
        }
    },
    "use_tz": False,
    "timezone": "Asia/Shanghai"
}
def register_mysql(app: FastAPI):
    register_tortoise(
        app,
        config=TORTOISE_ORM,
        generate_schemas=False,  # 第一次可以 True，之后 False
        add_exception_handlers=True  # 自动把 ORM 异常转成 500
    )

async def db_init():
    """初始化数据库连接"""
    await Tortoise.init(
        config=TORTOISE_ORM
    )
