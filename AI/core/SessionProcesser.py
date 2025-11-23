import asyncio
import datetime

from AIModel.ArkModel import get_ark_model
from AIModel.DouBaoFlask import DouBaoFlash
from models.model import Session, DialogueHistory
from core.logger import emotion_logger


class SessionProcessor:
    def __init__(self, session_id, device, user, persona_id):
        self.device = device
        self.user = user
        self.user_id = user['user_id']
        self.persona_id = persona_id
        # 实现用户id+人设id的session命名规则：user_id_persona_id
        self.session_id = f"{self.user_id}_{self.persona_id}"

    async def create_session(self):
        emotion_logger.info(f"创建会话 - 用户ID: {self.user_id}, 人设ID: {self.persona_id}")
        # 1. 优先查询：同一用户+人设+设备的活跃会话（核心复用逻辑）
        existing_session = await Session.filter(
            user_id=self.user_id,
            current_persona_id=self.persona_id,
            is_active=True
        ).first()

        if existing_session:
            # 2. 复用已有会话：更新最后活跃时间和设备信息
            emotion_logger.debug(f"复用已有会话 - 会话ID: {existing_session.session_id}")
            session = existing_session
            session.last_activity = datetime.datetime.now()
            session.connection_info = self.device
            # 关键：把前端传的新ID，替换成后端已有的有效ID（避免前端ID不一致）
            self.session_id = existing_session.session_id
            await session.save()
            emotion_logger.debug(f"会话信息更新完成 - 设备: {self.device}")
        else:
            # 3. 没有活跃会话：用前端传的固定ID新建（此时前端ID已唯一，不会重复）
            emotion_logger.debug(f"创建新会话 - 会话ID: {self.session_id}")
            session = await Session.create(
                session_id=self.session_id,
                user_id=self.user_id,
                is_active=True,
                last_activity=datetime.datetime.now(),
                current_persona_id=self.persona_id,
                connection_info=self.device,
                session_name=f"与{self.persona_id}的对话"
            )
            emotion_logger.info(f"新会话创建成功 - 会话ID: {self.session_id}")
        asyncio.create_task(self.get_dialogue_history_summary())
        return session

    async def get_dialogue_history_summary(self):
            emotion_logger.debug(f"获取对话历史摘要 - 会话ID: {self.session_id}")
            ark_model = DouBaoFlash()
            try:
                # 先查该会话的前3条用户消息
                dh = await DialogueHistory.filter(session_id=self.session_id).offset(0).limit(3).all()
                if len(dh) < 3:
                    emotion_logger.debug(f"对话消息不足3条，跳过摘要生成")
                    return  # 不够3条，不总结

                # 构造总结指令
                user_messages_str = "; ".join([d.user_message for d in dh])
                msg = [
                    {
                        "role": "user",
                        "content": f"总结以下对话，总字数控制在10字以内：{user_messages_str}"
                    }
                ]

                # 更新会话名
                s = await Session.get_or_none(session_id=self.session_id, user_id=self.user_id)
                if s and s.session_name == "默认会话":
                    result = await ark_model.get_session_summary(message=msg) # 调用模型
                    print(result)
                    print(2)
                    if not result:
                        return
                    s.session_name = result[:10]  # 强制截断，避免超字数
                    await s.save()
                    emotion_logger.info(f"会话名称已更新 - 新名称: {s.session_name}")

            except Exception as e:
                emotion_logger.error(f"生成会话总结失败：{e}")
                return