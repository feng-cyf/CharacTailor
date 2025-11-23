import os

from dotenv import load_dotenv
from volcenginesdkarkruntime import Ark
from volcenginesdkarkruntime.types.chat import completion_create_params
from volcenginesdkarkruntime.types.chat.completion_create_params import Thinking

load_dotenv(r"D:\GridFriend\AI\apiKey.env")
api_key = os.getenv("API_KEY")
class DouBaoLite:
    _instance=None
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(DouBaoLite, cls).__new__(cls)
        return cls._instance
    def __init__(self,key=None):
        if hasattr(self,"init"):
            return
        if not key:
            self.api_key = api_key
        else:
            self.api_key = key
        self.client=Ark(api_key=self.api_key,
                        base_url="https://ark.cn-beijing.volces.com/api/v3")
        self.model="doubao-seed-1-6-lite-251015"
        # self.model="deepseek-v3-1-250821"
        self.init=True
    def get_message(self,user_message,system_message=None,max_token=300,
                    thinking={"type": "disabled"},temperature=1):
        message=[]
        if system_message:
            message.append({"role":"system","content":system_message})
        message.append({"role":"user","content":user_message})
        response = self.client.chat.completions.create(
            model=self.model,
            messages=message,
            max_tokens=max_token,  # 精简输出，减少生成时间
            temperature=temperature,  # 降低随机性，减少犹豫
            stream=False,  # 关闭流式，一次性输出
            thinking=thinking
        )
        return response.choices[0].message.content

if __name__=="__main__":
    doubao=DouBaoLite()
    print(doubao.get_message("你是用户的小女友","过来亲亲我"))
