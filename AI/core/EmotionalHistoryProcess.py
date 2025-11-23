from typing import Optional

from core.logger import emotional_history_logger
from models.model import EmotionalHistory, GridEmotionalHistory


class EmotionalHistoryProcess:
    def __init__(self, user_id, session_id, scene="chat", emotion_source="system"):
        self.user_id = user_id
        self.session_id = session_id
        self.scene = scene
        self.emotion_source = emotion_source

        self.emotion_label = None
        self.emotion_strength = None
        self.emotion_confidence = None
        self.emotion_trend = None
        self.trend_confidence = None
        self.user_intent = None
        self.intent_confidence = None
        self.trigger_event = None

        emotional_history_logger.info(f"初始化情感历史处理器 - 用户: {user_id}, 会话: {session_id}")

    def from_predict_result(self, predict_result: dict):
        try:
            self.emotion_label = predict_result["emotion_label"]
            self.emotion_strength = predict_result["emotion_strength"]
            self.emotion_confidence = predict_result["emotion_confidence"]
            self.emotion_trend = predict_result["emotion_trend"]
            self.trend_confidence = predict_result["trend_confidence"]
            self.user_intent = predict_result["user_intent"]
            self.intent_confidence = predict_result["intent_confidence"]
            self.trigger_event = predict_result["trigger_event"]
            self.scene = predict_result.get("scene", self.scene)
            emotional_history_logger.info(f"已从模型结果填充情感数据 - 标签: {self.emotion_label}")
            return self
        except KeyError as e:
            emotional_history_logger.error(f"模型结果字段缺失: {str(e)}", exc_info=True)
            return self

    async def create_emotional_history(self) -> Optional[EmotionalHistory]:
        try:
            required_fields = ["emotion_label", "emotion_strength", "emotion_confidence"]
            if not all(getattr(self, field) is not None for field in required_fields):
                raise ValueError("情感核心字段不完整，无法创建记录")

            emotional_data = {
                "user_id": self.user_id,
                "session_id": self.session_id,
                "emotion_label": self.emotion_label,
                "emotion_strength": self.emotion_strength,
                "emotion_confidence": self.emotion_confidence,
                "emotion_trend": self.emotion_trend,
                "trend_confidence": self.trend_confidence,
                "user_intent": self.user_intent,
                "intent_confidence": self.intent_confidence,
                "trigger_event": self.trigger_event,
                "scene": self.scene,
            }

            emotional_history_logger.info(f"创建情感记录: {emotional_data}")
            emotional_history = await EmotionalHistory.create(**emotional_data)
            emotional_history_logger.info(f"情感记录创建成功 - ID: {emotional_history.id}")
            return emotional_history

        except Exception as e:
            emotional_history_logger.error(f"创建情感记录失败: {str(e)}", exc_info=True)
            return None

class GridEmotionalHistoryProcess(EmotionalHistoryProcess):

    async def create_emotional_history(self) -> Optional[GridEmotionalHistory]:
        try:
            required_fields = ["emotion_label", "emotion_strength", "emotion_confidence"]
            if not all(getattr(self, field) is not None for field in required_fields):
                raise ValueError("情感核心字段不完整，无法创建记录")

            emotional_data = {
                "user_id": self.user_id,
                "session_id": self.session_id,
                "emotion_label": self.emotion_label,
                "emotion_strength": self.emotion_strength,
                "emotion_confidence": self.emotion_confidence,
                "emotion_trend": self.emotion_trend,
                "trend_confidence": self.trend_confidence,
                "user_intent": self.user_intent,
                "intent_confidence": self.intent_confidence,
                "trigger_event": self.trigger_event,
                "scene": self.scene,
            }

            emotional_history_logger.info(f"创建情感记录: {emotional_data}")
            emotional_history = await GridEmotionalHistory.create(**emotional_data)
            emotional_history_logger.info(f"情感记录创建成功 - ID: {emotional_history.id}")
            return emotional_history

        except Exception as e:
            emotional_history_logger.error(f"创建情感记录失败: {str(e)}", exc_info=True)
            return None