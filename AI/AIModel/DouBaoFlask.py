import asyncio
import os
from pathlib import Path

from dotenv import load_dotenv
from volcenginesdkarkruntime import Ark


def get_key():
    """加载 API Key，处理文件不存在/Key 为空的情况"""
    env_path = Path(__file__).parent.parent / "apiKey.env"
    if not env_path.exists():
        raise FileNotFoundError(f"API Key 文件不存在：{env_path}")

    load_dotenv(dotenv_path=env_path)
    api_key = os.getenv("API_KEY")
    if not api_key:
        raise ValueError("apiKey.env 中未配置 API_KEY")
    return api_key


class DouBaoFlash:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(DouBaoFlash, cls).__new__(cls)
        return cls._instance

    def __init__(self, api_key=None):
        """初始化客户端，确保仅初始化一次"""
        if hasattr(self, "initialized"):
            return  # 避免重复初始化

        if api_key is None:
            api_key = get_key()

        self.model = "doubao-seed-1-6-flash-250828"
        self.client = Ark(
            base_url="https://ark.cn-beijing.volces.com/api/v3",
            api_key=api_key
        )
        self.initialized = True

    async def get_session_summary(self, message):
        try:
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda : self.client.chat.completions.create(
                    model=self.model,
                    messages=message,
                    max_tokens=200,
                    temperature=0.7
                )
            )
            if response.choices and len(response.choices) > 0:
                return response.choices[0].message.content
            return ""
        except Exception as e:
            print(e)
            return ""
    def get_message(self,user_message,system_message=None):
        message=[]
        if system_message:
            message.append({"role":"system","content":system_message})
        message.append({"role":"user","content":user_message})
        response = self.client.chat.completions.create(
            model=self.model,
            messages=message,
            max_tokens=50,  # 精简输出，减少生成时间
            temperature=0.1,  # 降低随机性，减少犹豫
            stream=False,  # 关闭流式，一次性输出
            # thinking={"type": "disabled"}
        )
        return response.choices[0].message.content

# ------------------- 测试代码 -------------------
async def doubao_flash():
    # 初始化实例
    doubao = DouBaoFlash()

    # 构造消息（符合 OpenAI 格式）
    messages = [
        {"role": "user", "content": "请简要介绍一下自己,你是那个版本的"}
    ]

    # 调用异步方法，获取结果（包含响应码）
    result = await doubao.get_session_summary(messages)
    print(result)

if __name__ == "__main__":
    # 运行异步测试
    asyncio.run(doubao_flash())