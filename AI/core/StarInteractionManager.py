import json
from typing import Dict, Optional
from core.EmotionInteractionAnalyzer import EmotionInteractionAnalyzer  # 假设你的类在这个路径


# 核心封装类（仅计算概率，不生成回复，直接调用你的分析类）
class StarProbabilityManager:
    def __init__(self, config_path: str = r"D:\GridFriend\AI\PersonaRule.json"):
        self.config_path = config_path
        self.persona_config: Optional[Dict] = None

    # 1. 加载角色配置
    def _load_config(self, persona_key: str) -> None:
        """加载指定角色的JSON配置"""
        if self.persona_config:
            return  # 避免重复加载

        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                configs = json.load(f)

            if isinstance(configs, list):
                for config in configs:
                    if config.get("persona_key") == persona_key:
                        self.persona_config = config
                        break
            else:
                self.persona_config = configs if configs.get("persona_key") == persona_key else None

            if not self.persona_config:
                raise ValueError(f"未找到 persona_key: {persona_key} 的配置")
        except FileNotFoundError:
            raise FileNotFoundError(f"配置文件 {self.config_path} 不存在")

    # 2. 核心方法：计算最终行为概率（供API使用）
    async def get_final_probabilities(
            self,
            session_id: str,
            user_id: int,
            persona_key: str
    ) -> Dict[str, float]:
        """
        对外暴露的唯一核心方法
        输入：session_id, user_id, persona_key
        输出：最终行为概率字典（供API参考）
        """
        # 加载配置
        self._load_config(persona_key)

        # ------------------------------
        # 直接调用你已经封装好的类！
        # ------------------------------
        trend, _, avg_strength = await EmotionInteractionAnalyzer.calculate_emotion_trend(session_id, user_id)

        # 根据返回的趋势和平均强度计算最终概率
        behavior_probs = self.persona_config["behavior_probabilities"]
        trend_modifiers = self.persona_config["trend_modifiers"]

        # 选择基础概率组
        if avg_strength < 4.0:
            base_probs = behavior_probs["negative"]
        elif avg_strength < 6.0:
            base_probs = behavior_probs["neutral"]
        else:
            base_probs = behavior_probs["positive"]

        # 应用趋势修正
        modifiers = trend_modifiers.get(trend, trend_modifiers["stable"])

        # 计算最终概率并限制在 [0.0, 1.0] 范围内
        final_probs = {}
        for behavior, prob in base_probs.items():
            modified_prob = prob + modifiers.get(behavior, 0.0)
            final_probs[behavior] = max(0.0, min(1.0, modified_prob))

        # 合并随机事件概率
        final_probs.update(self.persona_config.get("random_event_probabilities", {}))

        # 概率归一化（确保总和为1）
        total_prob = sum(final_probs.values())
        if total_prob > 0:
            final_probs = {k: v / total_prob for k, v in final_probs.items()}

        return final_probs