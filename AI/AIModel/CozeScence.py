import os
import uuid
import json
from dotenv import load_dotenv
from cozepy import Coze as CozeSDK, TokenAuth, Message, ChatEventType, MessageRole, MessageContentType, MessageType

load_dotenv(r"D:\GridFriend\AI\apiKey.env")
api_key = os.getenv("Coze_Api")

class CozeScene:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(CozeScene, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self, key=None):
        if hasattr(self, "init"):
            return
        self.api_key = key if key else api_key
        self.bot_id = "7573634456175575074"
        self.client = CozeSDK(auth=TokenAuth(self.api_key), base_url="https://api.coze.cn")
        self.init = True  # 标记已初始化

    def get_message(self, user_message):
        print(30)
        final_answer = ""
        for event in self.client.chat.stream(
                bot_id=self.bot_id,
                user_id=str(uuid.uuid1()),
                additional_messages=[Message.build_user_question_text(user_message)]
        ):
            # 提取最终完成的 ANSWER 类型消息（这是核心总结）
            if (event.event == ChatEventType.CONVERSATION_MESSAGE_COMPLETED and
                    event.message and event.message.type == MessageType.ANSWER):
                final_answer = event.message.content.strip()
                break
        print(final_answer)
        return final_answer


def chat_summary():
    """测试对话分析（总结）功能"""
    print("=== 对话分析测试开始 ===")

    # 1. 模拟从 Redis 获取的 5 条对话记录
    mock_redis_messages = [
        '{"user": "用户A", "content": "你好，我最近在准备考研，英语阅读总错很多，怎么办？"}',
        '{"user": "助手", "content": "英语阅读错题多，核心可以从词汇、题型技巧、错题复盘三个方面改进。"}',
        '{"user": "用户A", "content": "词汇我一直在背，但做题还是有很多不认识的，而且记不住。"}',
        '{"user": "助手", "content": "可以试试场景化记忆，结合阅读语境记单词，比孤立背单词更有效，每天花10分钟复习前一天的错题词汇。"}',
        '{"user": "用户A", "content": "好的，那题型技巧方面有什么具体方法吗？比如细节题和主旨题。"}'
    ]

    # 2. 解析对话并格式化为 Coze 能理解的文本
    messages_list = [json.loads(msg) for msg in mock_redis_messages]
    chat_text = ""
    for msg in messages_list:
        chat_text += f"{msg['user']}: {msg['content']}\n"

    # 3. 调用 CozeScene 进行对话分析（添加明确的总结指令）
    coze = CozeScene()
    # 优化提示词：明确要求总结核心内容，避免歧义
    analysis_prompt = f"请总结以下对话的核心内容，要求简洁明了，不超过100字：\n{chat_text}"

    print("📤 发送对话给 Coze 分析...")
    result = coze.get_message(analysis_prompt)

    # 4. 输出结果
    print("\n✅ 对话分析结果：")
    print("-" * 50)
    print(result if result else "未获取到有效总结")
    print("-" * 50)


if __name__ == "__main__":
    chat_summary()