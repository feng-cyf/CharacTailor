import os
from datetime import datetime
from typing import Optional, List, Dict
from dotenv import load_dotenv
from cozepy import Coze as CozeSDK, TokenAuth, Message, ChatEventType, MessageRole, MessageContentType, MessageType
from cozepy.exception import CozeAPIError

# 数据库模型导入（按你的实际路径调整）
# from models import EmotionalHistory, GridEmotionalHistory

# 加载环境变量（完全按你的源码）
load_dotenv(r"D:\GridFriend\AI\apiKey.env")
COZE_API_KEY = os.getenv("Coze_Api")
if not COZE_API_KEY:
    raise ValueError("❌ 环境变量 Coze_Api 未配置")


class Coze:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Coze, cls).__new__(cls)
        return cls._instance

    def __init__(self, api_key=None, base_url: str = "https://api.coze.cn"):
        if hasattr(self, "initialized"):
            return
        # 完全按你的源码初始化 SDK
        if not api_key:
            api_key = COZE_API_KEY
        self.coze_sdk = CozeSDK(
            auth=TokenAuth(token=api_key),
            base_url=base_url
        )
        self.bot_id = "7571425324266127394"
        self.initialized = True

    def convert_to_number_if_possible(self,value_str):
        """
        尝试将一个字符串转换为整数或浮点数。
        如果转换失败，则返回原始字符串。
        """
        # 去除首尾空白
        s = value_str.strip()

        # 空字符串直接返回
        if not s:
            return s

        # 尝试转换为整数
        try:
            return int(s)
        except ValueError:
            # 整数转换失败，尝试转换为浮点数
            try:
                return float(s)
            except ValueError:
                # 浮点数转换也失败，返回原始字符串
                return s

    def _build_messages(
            self,
            user_msg: str,
            persona: str,
            history_msg: Optional[List[Dict]] = None,
    ) -> List[Message]:
        """基于整体对话氛围分析情绪，采用滑窗形式整合上下文"""
        history_msg = history_msg or []
        messages = []

        # 提示词强调整体氛围分析，明确采用滑窗形式整合上下文
        prompt = f"""
        你是{persona}，请严格遵循以下规则：
        1. 结合**整体对话氛围**（包括所有历史消息和当前消息，采用滑窗形式整合上下文）分析双方情绪
        2. 情绪强度评分标准：以5分为中间线（中性）
           - 正面情绪：5分以上，越强烈分值越高（最高10分）
           - 负面情绪：5分以下，越强烈分值越低（最低0分）
           - 中性情绪：5分左右（4.5-5.5）
        3. 必须用===作为分界线包裹两行数据，格式如下：
        第1行（用户）：emotion_label|emotion_strength(0-10,1位小数)|emotion_confidence(0-1,3位小数)|emotion_trend(上升/下降/平稳)|trend_confidence(0-1,3位小数)|user_intent|intent_confidence(0-1,3位小数)
        第2行（你）：emotion_label|emotion_strength(0-10,1位小数)|emotion_confidence(0-1,3位小数)|emotion_trend(上升/下降/平稳)|trend_confidence(0-1,3位小数)|your_intent|intent_confidence(0-1,3位小数)
        示例1（正面互动）：
        ===
        开心|8.5|0.985|上升|0.920|分享|0.950
        激动|8.0|0.970|上升|0.900|回应|0.960
        ===
        示例2（负面互动）：
        ===
        生气|2.0|0.930|上升|0.880|抱怨|0.940
        委屈|3.5|0.910|上升|0.850|解释|0.920
        ===
        示例3（中性互动）：
        ===
        平静|5.0|0.900|平稳|0.870|询问|0.930
        平淡|5.2|0.890|平稳|0.860|回答|0.910
        ===
        4. 严格遵守格式，不添加任何额外内容，即使情绪不明显也要生成合理数据
        """.strip()
        messages.append(Message(
            role=MessageRole.ASSISTANT,
            content=prompt,
            type=MessageType.QUESTION,
            content_type=MessageContentType.TEXT,
        ))

        # 历史对话保留完整上下文（滑窗基础）
        for msg in history_msg:
            content = msg["content"]
            if msg["role"] == "user":
                messages.append(Message(
                    role=MessageRole.USER,
                    content=content,
                    type=MessageType.QUESTION,
                    content_type=MessageContentType.TEXT,
                ))
            elif msg["role"] == "assistant":
                messages.append(Message(
                    role=MessageRole.ASSISTANT,
                    content=content,
                    type=MessageType.ANSWER,
                    content_type=MessageContentType.TEXT,
                ))

        # 当前用户消息
        messages.append(Message(
            role=MessageRole.USER,
            content=user_msg,
            type=MessageType.QUESTION,
            content_type=MessageContentType.TEXT,
        ))

        return messages

    def _parse_data(self, full_content: str) -> Dict[str, Dict]:
        """极简解析，只按分隔符提取"""
        if "===" not in full_content:
            raise ValueError(f"无===分隔符，回复：{full_content[:50]}")
        data_block = full_content.split("===")[1].strip()
        lines = [line.strip() for line in data_block.split("\n") if line.strip()]
        if len(lines) < 2:
            raise ValueError(f"数据不足2行")

        user_parts = lines[0].split("|")
        gf_parts = lines[1].split("|")
        if len(user_parts) != 7 or len(gf_parts) != 7:
            raise ValueError(f"字段错误")

        return {
            "user": dict(zip(
                ["emotion_label", "emotion_strength", "emotion_confidence",
                 "emotion_trend", "trend_confidence", "user_intent", "intent_confidence"],
                [self.convert_to_number_if_possible(p) for p in user_parts]
            )),
            "gf": dict(zip(
                ["emotion_label", "emotion_strength", "emotion_confidence",
                 "emotion_trend", "trend_confidence", "user_intent", "intent_confidence"],
                [self.convert_to_number_if_possible(p) for p in gf_parts]
            ))
        }

    def get_emotion(self, persona,user_id: int, session_id: int, user_msg: str, history_msg=None):
        """核心方法：调用+解析+入库（按你的模型）"""
        messages = self._build_messages(user_msg=user_msg, history_msg=history_msg,persona=persona)
        full_content = ""
        print(messages)
        # 按你的源码用 stream 调用
        try:
            for event in self.coze_sdk.chat.stream(
                    bot_id=self.bot_id,
                    user_id=str(user_id),
                    additional_messages=messages
            ):
                if event.event == ChatEventType.CONVERSATION_MESSAGE_DELTA:
                    full_content += event.message.content
                    print(event.message.content, end="")
            print()
        except CozeAPIError as e:
            raise RuntimeError(f"Coze调用失败：{e}")

        # 解析数据
        data = self._parse_data(full_content)
        user_emotion = data["user"]
        gf_emotion = data["gf"]
        return {"user_emotion": user_emotion, "gf_emotion": gf_emotion}


# 测试（按你的源码风格）
if __name__ == "__main__":
    coze = Coze(api_key=COZE_API_KEY)
    try:
        result = coze.get_emotion(
            persona="你是一名活泼可爱的女友，很喜欢粘着用户",
            user_id=1,
            session_id=2,
            user_msg="你怎么又忘了我们的纪念日？我等了你一晚上...",
            history_msg=[
                {"role": "user", "content": "后天是我们的周年纪念日，记得吗？"},
                {"role": "assistant", "content": "当然记得啦，到时候给你惊喜～"}
            ]
        )
        print(f"\n✅ 成功：{result}")
    except Exception as e:
        print(f"\n❌ 失败：{str(e)}")