import os
import json
from typing import Optional
from redis.asyncio import Redis
from watchfiles import awatch

from AIModel.CozeScence import CozeScene
from database.Redis import get_redis_client
from pathlib import Path
import logging
# 配置路径（使用 Path 更安全，支持跨平台）
MESSAGE_DIR = Path(r"D:\GridFriend\AI\message\historyMessage")
SUMMARY_DIR = Path(r"D:\GridFriend\AI\message\summary")

# 确保目录存在（mkdir -p 效果，避免竞争异常）
MESSAGE_DIR.mkdir(parents=True, exist_ok=True)
SUMMARY_DIR.mkdir(parents=True, exist_ok=True)
async def get_pool():
    redis = await get_redis_client(db=4, host="127.0.0.1", port=6379)
    return redis


async def add_history_message(msg: dict, session_id: int,user_id:str) -> None:
    """
    添加对话消息到 Redis 队列，超过5条则将最旧消息持久化到文件

    :param user_id:
    :param msg: 对话消息（建议是 JSON 字符串，包含发送者、内容、时间戳等）
    :param session_id: 会话唯一标识
    """
    # 统一键名为复数，语义更清晰
    redis = await get_pool()
    chat_key = f"chat:session:{session_id}:{user_id}:messages"

    # 1. 获取当前队列长度
    current_len = await redis.llen(chat_key)
    msg = json.dumps(msg,ensure_ascii=False)
    # 2. 超过5条，持久化最旧消息（队尾元素，因为用 lpush 入队，队尾是最旧的）
    if current_len >= 5:
        # rpop 弹出队尾（最旧消息），lpop 弹出队头（最新消息），这里逻辑是保留最近5条，所以删最旧的
        oldest_msg = await redis.rpop(chat_key)
        if oldest_msg:
            # 每个会话一个文件，避免覆盖，用 session_id 命名
            history_file = MESSAGE_DIR / f"{session_id}.txt"
            # 写入时添加换行符，方便后续读取
            with history_file.open("a", encoding="utf-8") as f:
                f.write(f"{oldest_msg}\n")

    # 3. 将新消息加入队头（lpush 保证队头是最新消息）
    await redis.lpush(chat_key, msg)

async def generate_and_save_summary(session_id: int,user_id:str,desc:str) -> Optional[str]:
    """
    从最近5条对话生成总结，存储到 Redis 总结队列，超过10条则持久化最旧总结

    :param desc:
    :param user_id:
    :param session_id: 会话唯一标识
    :return: 生成的总结文本，失败返回 None
    """
    redis = await get_pool()
    chat_key = f"chat:session:{session_id}:{user_id}:messages"
    summary_key = f"chat:session:{session_id}:{user_id}:summary"

    try:
        recent_messages = await redis.lrange(chat_key, 0, 4)
        recent_messages.insert(0, f"当前场景信息:{desc}")
        if not recent_messages:
            return None

        messages = json.dumps([json.loads(msg) for msg in recent_messages[1:]], ensure_ascii=False)
        coze = CozeScene()
        summary = coze.get_message(messages)
        if not summary:
            return None
        current_summary_len = await redis.llen(summary_key)
        if current_summary_len >= 10:
            oldest_summary = await redis.rpop(summary_key)
            if oldest_summary:
                summary_file = SUMMARY_DIR / f"{session_id}.txt"
                with summary_file.open("a", encoding="utf-8") as f:
                    f.write(f"{oldest_summary}\n")

        await redis.lpush(summary_key, summary)
    except Exception as e:
        print(f"生成或保存总结失败：{str(e)}")
        return None
async def get_summary(session_id: int, user_id: str) -> Optional[str]:
    """
    获取会话的最新总结

    :param session_id: 会话唯一标识
    :param user_id: 用户唯一标识
    :return: 最新总结文本，无总结返回None
    """
    if not all([session_id, user_id]):
        logging.error("缺少必要参数：session_id/user_id不能为空")
        return None

    try:
        redis = await get_pool()
        summary_key = f"chat:session:{session_id}:{user_id}:summary"

        # 取队头（索引0）的最新总结（lrange返回列表，提取第一个元素）
        latest_summary_list = await redis.lrange(summary_key, 0, 0)
        if not latest_summary_list:
            logging.warning(f"会话{session_id}没有缓存的总结")
            return None

        # 解码并返回最新总结
        latest_summary = latest_summary_list[0]
        logging.debug(f"获取会话{session_id}的最新总结：{latest_summary[:50]}...")
        return latest_summary

    except Exception as e:
        logging.error(f"获取总结失败：{str(e)}", exc_info=True)
        return None