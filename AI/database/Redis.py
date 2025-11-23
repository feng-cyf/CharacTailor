import asyncio
import redis.asyncio as redis
from typing import Optional, Dict
from threading import Lock

_redis_pool_dict: Dict[int, redis.ConnectionPool] = {}

_pool_lock = Lock()

DEFAULT_REDIS_CONFIG = {
    "host": "127.0.0.1",
    "port": 6379,
    "password": "",
    "decode_responses": True,
    "max_connections": 10,
    "socket_timeout": 5.0,
}


async def get_redis_client(
        db: int,
        host: Optional[str] = None,
        port: Optional[int] = None,
        password: Optional[str] = None,
        decode_responses: Optional[bool] = None,
        max_connections: Optional[int] = None,
        socket_timeout: Optional[float] = None,
) -> redis.Redis:
    if not isinstance(db, int):
        raise TypeError("db 必须是整数类型")

    # 使用锁来确保在并发环境下，每个 db 只创建一个连接池
    with _pool_lock:
        # 检查连接池是否已存在
        if db not in _redis_pool_dict:
            # 合并默认配置和传入参数
            config = DEFAULT_REDIS_CONFIG.copy()
            if host is not None:
                config["host"] = host
            if port is not None:
                config["port"] = port
            if password is not None:
                config["password"] = password
            if decode_responses is not None:
                config["decode_responses"] = decode_responses
            if max_connections is not None:
                config["max_connections"] = max_connections
            if socket_timeout is not None:
                config["socket_timeout"] = socket_timeout

            # 创建新的连接池
            new_pool = redis.ConnectionPool(**config,db=db)
            _redis_pool_dict[db] = new_pool

    return redis.Redis(connection_pool=_redis_pool_dict[db])