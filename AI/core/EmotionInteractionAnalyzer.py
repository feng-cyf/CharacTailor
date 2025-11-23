import numpy as np

from models.model import EmotionalHistory


class EmotionInteractionAnalyzer:
    @classmethod
    async def calculate_emotion_trend(cls, session_id: str, user_id: int, window_size: int = 15, alpha: float = 0.4):
        """
        根据最近 window_size 次情绪记录计算趋势和加权平均
        """
        records = await EmotionalHistory.filter(
            user_id=user_id, session_id=session_id,
        ).order_by("-created_at").limit(window_size).all()

        if len(records) < 2:
            return "平稳", 0.0, 5.0  # 平均情绪值默认中性

        records = list(reversed(records))
        strengths = np.array([r.emotion_strength for r in records])
        confidences = np.array([r.emotion_confidence for r in records])

        # 加权 EMA 平滑
        weighted_strength = strengths * confidences
        ema = [weighted_strength[0]]
        for s in weighted_strength[1:]:
            ema.append(alpha * s + (1 - alpha) * ema[-1])
        ema = np.array(ema)

        # 趋势判断
        delta = ema[-1] - ema[0]
        std_dev = np.std(ema)
        # 结合波动决定平稳阈值
        if abs(delta) < max(0.3, std_dev / 2):
            trend = "平稳"
        elif delta > 0:
            trend = "上升"
        else:
            trend = "下降"

        # 趋势置信度：波动越大，置信度越低
        confidence = min(1.0, abs(delta) / (np.max(ema) - np.min(ema) + 1e-5))

        # 平均情绪强度（加权平均）
        avg_strength = np.average(strengths, weights=confidences)

        return trend, confidence, avg_strength
