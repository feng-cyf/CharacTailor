import uuid
from models.model import DialogueHistory
from core.logger import dialog_history_logger, emotion_logger


def count_tokens(text: str) -> int:
    chinese_chars = len([c for c in text if '\u4e00' <= c <= '\u9fff'])
    other_chars = len(text) - chinese_chars
    return int(chinese_chars * 1.3 + other_chars * 0.8)

async def generate_unique_dialog_id(prefix: str = "dialog_", length: int = 32) -> str:
    emotion_logger.debug(f"生成唯一对话ID - 前缀: {prefix}, 长度: {length}")
    max_retries = 3
    for attempt in range(max_retries):
        unique_id = f"{prefix}{uuid.uuid4().hex[:length]}"
        exists = await DialogueHistory.filter(dialogue_id=unique_id).exists()
        if not exists:
            emotion_logger.debug(f"对话ID生成成功 - {unique_id}")
            return unique_id
        emotion_logger.debug(f"对话ID已存在，第{attempt+1}次重试")
    fallback_id = f"{prefix}{uuid.uuid4().hex}"
    emotion_logger.warning(f"达到最大重试次数，使用完整UUID - {fallback_id}")
    return fallback_id


class DialogHistoryProcessor:
    def __init__(self,user_message,bot_response,user_id,emotional_feedback,emotion_type,bot_file_url,
                 persona_id,session_id,confidence,user_file_url,bot_response_type,user_message_type):
        self.emotional_feedback=emotional_feedback
        self.persona_id=persona_id
        self.session_id=session_id
        self.user_message=user_message
        self.bot_response=bot_response
        self.user_id=user_id
        self.emotion_type=emotion_type
        self.dialogue_id=None
        self.confidence=confidence
        self.user_file_url=user_file_url
        self.bot_response_type=bot_response_type
        self.bot_file_url=bot_file_url
        self.user_message_type=user_message_type
        dialog_history_logger.info("DialogHistoryProcessor 初始化完成")
    async def creat_dialog(self):
        emotion_logger.info(f"创建对话记录 - 用户ID: {self.user_id}, 会话ID: {self.session_id}")
        try:
            # 记录完整的对话内容
            emotion_logger.info(f"用户消息: {self.user_message}")
            emotion_logger.info(f"AI回复: {self.bot_response}")
            emotion_logger.debug(f"情感类型: {self.emotion_type}, 情感反馈: {self.emotional_feedback}, 置信度: {self.confidence}")
            
            self.dialogue_id=await generate_unique_dialog_id()
            emotion_logger.debug(f"创建对话 - ID: {self.dialogue_id}, 情感类型: {self.emotion_type}")

            dialog=await DialogueHistory.create(
                dialogue_id=self.dialogue_id,
                persona_id=self.persona_id,
                session_id=self.session_id,
                user_message=self.user_message,
                bot_response=self.bot_response,
                user_id=self.user_id,
                emotional_feedback=self.emotional_feedback,
                emotion_type=self.emotion_type,
                confidence=self.confidence,
                user_file_url=self.user_file_url,
                bot_response_type=self.bot_response_type,
                user_message_type=self.user_message_type,
                bot_file_url=self.bot_file_url
            )
            emotion_logger.info(f"对话记录创建成功 - 对话ID: {self.dialogue_id}")
            return dialog
        except Exception as e:
            emotion_logger.error(f"创建对话记录失败: {e}", exc_info=True)
            raise
    @classmethod
    async def get_dialog(cls, session_id, user_id, limit=15):
        emotion_logger.info(f"获取对话历史 - 用户ID: {user_id}, 会话ID: {session_id}, 限制条数: {limit}")
        try:
            dh = await DialogueHistory.filter(
                session_id=session_id,
                user_id=user_id
            ).order_by('-created_at').limit(limit).all()
            dialog_history_logger.info(f"获取到 {len(dh)} 条对话历史记录")

            context = []

            for i, d in enumerate(dh):
                user_msg = d.user_message
                ai_msg = d.bot_response

                # 关键补充：把情绪和权重加到user的content里，模型能直接读取
                user_content = f"{user_msg}（情绪：{d.emotion_type}，权重：{d.emotional_feedback}分）"
                context.append({"role": "user", "content": user_content})
                context.append({"role": "assistant", "content": ai_msg})
                dialog_history_logger.info(f"对话记录[{i}]: 用户消息={user_msg}, 情感类型={d.emotion_type}")

            # 反转上下文顺序（旧→新 → 新→旧，适配模型输入习惯）
            final_context = context[::-1]
            dialog_history_logger.info(f"对话上下文准备完成 - 上下文长度: {len(final_context)}条记录")
            return final_context
        except Exception as e:
            dialog_history_logger.error(f"获取对话历史失败: {e}", exc_info=True)
            return []

    @classmethod
    async def get_recent_user_dialogs(cls, session_id, user_id, limit=3):
        """
        获取最近3条用户对话（仅用户消息，按时间倒序排列）

        Args:
            session_id: 会话ID
            user_id: 用户ID
            limit: 限制条数，默认3条

        Returns:
            List[str]: 最近3条用户消息（最新的在前）
        """
        emotion_logger.info(f"获取最近用户对话 - 用户ID: {user_id}, 会话ID: {session_id}, 限制条数: {limit}")
        try:
            # 查询最近的对话记录（按时间倒序）
            dialogs = await DialogueHistory.filter(
                session_id=session_id,
                user_id=user_id
            ).order_by('-created_at').limit(limit).all()

            # 提取用户消息，保持时间顺序（最新的在前）
            message = []
            for d in dialogs:
                message.append({"role": "user", "content": d.user_message})
                message.append({"role": "assistant", "content": d.bot_response})
            emotion_logger.info(f"成功获取 {len(message)} 条用户对话")
            return message  # 顺序：最新的在前（符合上下文输入习惯）

        except Exception as e:
            emotion_logger.error(f"获取用户对话失败: {e}", exc_info=True)
            return []