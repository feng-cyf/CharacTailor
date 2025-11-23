import pandas as pd
import random
import json
import re  # 用于文本清洗

# ====================== 核心配置（严格校验版）======================
# 1. 人设定义（6种人设，覆盖更多情感倾向）
PERSONAS = {
    "甜宠近距": {
        "称呼": ["宝贝", "亲爱的", "小笨蛋", "乖乖", "宝宝"],
        "语气词": ["呀", "呢", "啦", "哦~", "嘛"],
        "常用词": ["喜欢", "爱你", "想你", "一起", "幸福", "温暖", "抱抱"],
        "情绪倾向": {
            "甜蜜": 0.3, "撒娇": 0.2, "心动": 0.2, "开心": 0.15, "思念": 0.1,
            "委屈": 0.03, "小生气": 0.02  # 负面情绪占比低
        }
    },
    "高冷疏离": {
        "称呼": ["你", "喂", "某人"],
        "语气词": ["。", "？", "…", "哦"],
        "常用词": ["随便", "无所谓", "知道了", "不用", "还好", "就这样"],
        "情绪倾向": {
            "中性": 0.4, "小生气": 0.2, "疲惫": 0.15, "冷淡": 0.1, "烦躁": 0.08,
            "甜蜜": 0.02, "思念": 0.03  # 极少正向情绪
        }
    },
    "傲娇口是心非": {
        "称呼": ["笨蛋", "傻瓜", "蠢货", "你"],
        "语气词": ["哼", "呀", "呢", "哦", "切"],
        "常用词": ["才不要", "才没有", "明明是", "你管我", "烦死了", "谁在乎"],
        "情绪倾向": {
            "小生气": 0.25, "傲娇": 0.2, "委屈": 0.15, "甜蜜": 0.1, "口是心非": 0.1,
            "开心": 0.08, "中性": 0.12  # 核心情绪明确
        }
    },
    "温柔体贴": {
        "称呼": ["亲爱的", "宝贝", "你"],
        "语气词": ["呀", "呢", "哦", "啊"],
        "常用词": ["关心", "担心", "照顾", "一起", "慢慢来", "别太累", "安心"],
        "情绪倾向": {
            "甜蜜": 0.25, "温柔": 0.2, "开心": 0.15, "思念": 0.15, "关心": 0.1,
            "委屈": 0.05, "中性": 0.1  # 以正向关怀为主
        }
    },
    "活泼开朗": {
        "称呼": ["宝贝", "亲爱的", "小伙伴", "你"],
        "语气词": ["呀", "呢", "啦", "哇", "哦"],
        "常用词": ["开心", "太棒了", "一起玩", "好耶", "惊喜", "有趣", "期待"],
        "情绪倾向": {
            "开心": 0.3, "惊喜": 0.2, "甜蜜": 0.15, "活泼": 0.15, "撒娇": 0.1,
            "中性": 0.08, "小生气": 0.02  # 高积极情绪
        }
    },
    "理性稳重": {  # 新增人设，补充中性/冷静情绪
        "称呼": ["你", "朋友", "同事"],
        "语气词": ["。", "的", "吧", "哦"],
        "常用词": ["分析", "计划", "靠谱", "稳", "放心", "没问题"],
        "情绪倾向": {
            "中性": 0.3, "安心": 0.2, "期待": 0.15, "关心": 0.1, "疲惫": 0.1,
            "小生气": 0.05, "解脱": 0.05, "崇拜": 0.05  # 新增细分情绪
        }
    }
}

# 2. 25种情感标签（覆盖全场景，无冗余）
EMOTIONS = [
    # 基础情绪
    "甜蜜", "撒娇", "委屈", "小生气", "心动", "思念", "中性",
    # 扩展情绪
    "开心", "难过", "疲惫", "惊喜", "温柔", "关心", "冷淡",
    "烦躁", "傲娇", "口是心非", "活泼", "焦虑", "失望",
    # 新增细分情绪（提升颗粒度）
    "安心", "期待", "崇拜", "害羞", "解脱"
]

# 3. 情感强度范围（严格0-10分，区间合理）
EMOTION_STRENGTH = {
    "甜蜜": (7.0, 9.5), "撒娇": (6.0, 8.5), "委屈": (4.0, 7.0), "小生气": (5.0, 8.0),
    "心动": (7.5, 9.8), "思念": (6.5, 9.0), "中性": (3.0, 6.0),
    "开心": (7.0, 10.0), "难过": (2.0, 5.5), "疲惫": (2.5, 5.0), "惊喜": (8.0, 10.0),
    "温柔": (6.0, 8.5), "关心": (5.5, 8.0), "冷淡": (2.0, 4.5), "烦躁": (4.5, 7.5),
    "傲娇": (5.0, 8.0), "口是心非": (4.0, 7.0), "活泼": (6.5, 9.0), "焦虑": (3.5, 6.5),
    "失望": (3.0, 6.0), "安心": (6.0, 8.0), "期待": (7.0, 9.0),
    "崇拜": (8.0, 10.0), "害羞": (5.0, 7.5), "解脱": (6.5, 9.0)
}

# 4. 情感触发词（与情绪强绑定，避免语义混乱）
EMOTION_KEYWORDS = {
    "甜蜜": ["幸福", "开心", "一起", "喜欢", "爱你", "温暖", "抱抱"],
    "撒娇": ["抱抱", "亲亲", "嘛", "求你", "要嘛", "陪我"],
    "委屈": ["没人管", "被忽略", "难过", "冤枉", "不开心", "没人懂"],
    "小生气": ["烦", "生气", "不理你", "过分", "忘了", "讨厌"],
    "心动": ["脸红", "心跳", "紧张", "可爱", "偷偷", "靠近"],
    "思念": ["想你", "想念", "回忆", "见面", "视频", "一起的日子"],
    "中性": ["今天", "天气", "吃饭", "工作", "怎么样", "还好"],
    "开心": ["太好了", "真棒", "开心", "兴奋", "惊喜", "超棒"],
    "难过": ["伤心", "难过", "哭", "失望", "倒霉", "不顺利"],
    "疲惫": ["好累", "疲惫", "想睡觉", "没力气", "忙死了", "熬夜"],
    "惊喜": ["惊喜", "没想到", "突然", "太棒了", "礼物", "意外"],
    "温柔": ["温柔", "体贴", "关心", "照顾", "慢慢来", "别担心"],
    "关心": ["担心你", "照顾好自己", "别太累", "注意安全", "多喝水"],
    "冷淡": ["随便", "无所谓", "不用", "还好", "随便你", "都行"],
    "烦躁": ["烦躁", "烦死人", "别烦我", "乱糟糟", "讨厌这样"],
    "傲娇": ["才不要", "才没有", "明明是", "你管我", "才不稀罕"],
    "口是心非": ["嘴上说不要", "其实很想要", "假装不在乎", "心里很在意"],
    "活泼": ["活泼", "好动", "一起玩", "好耶", "有趣", "开心果"],
    "焦虑": ["焦虑", "担心", "怕来不及", "紧张", "不安"],
    "失望": ["失望", "没想到", "落空", "不抱希望", "遗憾"],
    "安心": ["踏实", "放心", "安稳", "有你在", "不怕"],
    "期待": ["等不及", "好想", "盼望", "马上", "准备好"],
    "崇拜": ["厉害", "佩服", "太强了", "偶像", "好棒"],
    "害羞": ["脸红", "不好意思", "偷偷", "不敢看", "害羞"],
    "解脱": ["终于", "轻松了", "放下了", "没事了", "解脱"]
}

# 5. 趋势和意图（全量覆盖，无遗漏）
TRENDS = ["上升", "下降", "平稳", "波动"]
INTENTS = [
    "求互动", "求关注", "求安慰", "求见面", "表达不满",
    "表达", "撒娇调侃", "求回应", "关心对方", "分享日常"
]

# 6. 10种场景模板（逻辑严谨，语义通顺）
SCENARIOS = {
    "日常聊天": [
        ["今天{persona_kw}了一件事，想跟你说说", "中性"],
        ["什么事呀？说来听听～", "求互动"],
        ["就是{emotion_kw}，感觉好{emotion}呀", "{emotion}"]
    ],
    "工作吐槽": [
        ["今天工作{emotion_kw}，累得不行", "疲惫"],
        ["怎么了？是不是又加班了？", "关心对方"],
        ["是啊，老板{emotion_kw}，好{emotion}啊", "小生气/烦躁"]
    ],
    "约会计划": [
        ["周末我们去{emotion_kw}吧？", "甜蜜/开心"],
        ["好啊，我正好想去{emotion_kw}", "开心"],
        ["那我{emotion_kw}，给你个惊喜～", "惊喜"]
    ],
    "异地思念": [
        ["{persona_kw}，我好想你啊", "思念"],
        ["我也是，{emotion_kw}才能见面", "思念/委屈"],
        ["再等等，{emotion_kw}就去看你", "甜蜜/期待"]
    ],
    "日常分享": [
        ["今天做了{emotion_kw}，味道超赞", "开心"],
        ["真的吗？下次做给我吃呀", "求互动"],
        ["好呀，{persona_kw}一起吃", "甜蜜"]
    ],
    "节日祝福": [  # 新增
        ["{persona_kw}，节日快乐呀～", "开心/甜蜜"],
        ["谢谢～ 你今天{emotion_kw}吗？", "关心对方"],
        ["超开心的！收到你的祝福更{emotion}了～", "惊喜/开心"]
    ],
    "美食讨论": [  # 新增
        ["发现一家超赞的{emotion_kw}店！", "惊喜"],
        ["真的吗？在哪里呀？{persona_kw}", "求互动"],
        ["在{emotion_kw}附近，下次带你去～", "甜蜜/开心"]
    ],
    "天气闲聊": [  # 新增
        ["今天天气{emotion_kw}，好适合出门～", "开心"],
        ["是啊，不过据说下午要{emotion_kw}", "中性/担心"],
        ["那我们{emotion_kw}，别被雨淋到～", "关心/温柔"]
    ],
    "兴趣分享": [  # 新增
        ["我最近迷上了{emotion_kw}，超有趣！", "活泼/开心"],
        ["哦？是{persona_kw}吗？我也想试试～", "求互动"],
        ["好啊，下次教你，保证你会{emotion}～", "开心/惊喜"]
    ],
    "睡前聊天": [  # 新增
        ["今天好累呀，{emotion_kw}想睡觉了", "疲惫"],
        ["早点休息吧，{persona_kw}做个好梦～", "温柔/关心"],
        ["嗯，有你这句话睡得更{emotion}～", "甜蜜/安心"]
    ]
}

# 7. 生成配置（适合付费训练的规模）
TOTAL_SAMPLES = 50000  # 原始样本数（生成后约15万轮次样本）
OUTPUT_FILE = "final_emotion_dataset.csv"  # 输出文件名
MAX_CONTEXT_LEN = 3  # 三轮对话（保证上下文连贯性）


# ====================== 工具函数（严格校验版）======================
def get_persona_emotion(persona_name):
    """根据人设获取情绪（严格校验情绪合法性）"""
    persona = PERSONAS[persona_name]
    emotions = list(persona["情绪倾向"].keys())
    weights = list(persona["情绪倾向"].values())
    # 双重校验：确保情绪在EMOTIONS列表中
    emotion = random.choices(emotions, weights=weights, k=1)[0]
    assert emotion in EMOTIONS, f"非法情绪：{emotion}（人设：{persona_name}）"
    return emotion


def get_trend(prev_emotion, curr_emotion):
    """计算情绪趋势（严格处理边界情况）"""
    if curr_emotion == "中性":
        return "平稳"
    # 校验情绪强度配置
    assert prev_emotion in EMOTION_STRENGTH, f"情绪强度未配置：{prev_emotion}"
    assert curr_emotion in EMOTION_STRENGTH, f"情绪强度未配置：{curr_emotion}"
    # 计算均值
    prev_mean = (EMOTION_STRENGTH[prev_emotion][0] + EMOTION_STRENGTH[prev_emotion][1]) / 2
    curr_mean = (EMOTION_STRENGTH[curr_emotion][0] + EMOTION_STRENGTH[curr_emotion][1]) / 2
    # 判断趋势
    if curr_mean - prev_mean > 1.5:
        return "上升"
    elif prev_mean - curr_mean > 1.5:
        return "下降"
    else:
        return random.choice(["平稳", "波动"])


def clean_text(text):
    """清洗文本，避免重复/语病"""
    # 去除连续重复的语气词（如"呀呀"→"呀"）
    text = re.sub(r'([呀呢啦哦～嘛。？…哼切])\1+', r'\1', text)
    # 去除多余空格
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def generate_dialogue(persona_name, scenario_key):
    """生成三轮对话（全流程校验）"""
    persona = PERSONAS[persona_name]
    scenario = SCENARIOS[scenario_key]
    dialogue = []

    for i in range(MAX_CONTEXT_LEN):
        # 1. 确定当前情绪（严格校验）
        if i == 0:
            emotion_label = get_persona_emotion(persona_name)
        else:
            prev_emotion = dialogue[i-1]["emotion"]
            emotion_label = get_persona_emotion(persona_name) if random.random() < 0.3 else prev_emotion
        assert emotion_label in EMOTIONS, f"无效情绪标签：{emotion_label}"

        # 2. 填充模板
        text_template, _ = scenario[i]
        # 处理占位符（确保关键词存在）
        persona_kw = random.choice(persona["常用词"]) if "{persona_kw}" in text_template else ""
        emotion_kw = random.choice(EMOTION_KEYWORDS[emotion_label]) if "{emotion_kw}" in text_template else ""
        # 替换模板（严格使用情绪标签）
        text = text_template.format(
            persona_kw=persona_kw,
            emotion_kw=emotion_kw,
            emotion=emotion_label
        )

        # 3. 优化文本（添加称呼+清洗）
        if i > 0 and random.random() < 0.3:  # 非首轮随机加称呼
            text = f"{random.choice(persona['称呼'])}, {text}"
        text += random.choice(persona["语气词"]) if random.random() < 0.5 else ""
        text = clean_text(text)  # 清洗重复/语病

        # 4. 确定意图（严格映射）
        if emotion_label in ["甜蜜", "开心", "惊喜", "活泼", "期待"]:
            user_intent = random.choice(["求互动", "分享日常"])
        elif emotion_label in ["委屈", "难过", "疲惫", "焦虑", "害羞"]:
            user_intent = random.choice(["求安慰", "求关注"])
        elif emotion_label in ["小生气", "烦躁", "失望", "傲娇"]:
            user_intent = random.choice(["表达不满", "求回应"])
        elif emotion_label in ["思念", "温柔", "关心", "安心"]:
            user_intent = random.choice(["求见面", "关心对方"])
        elif emotion_label in ["崇拜", "解脱", "口是心非"]:
            user_intent = "表达"
        else:  # 中性
            user_intent = "表达"
        assert user_intent in INTENTS, f"无效意图：{user_intent}"

        # 5. 存入对话（带完整字段）
        dialogue.append({
            "text": text,
            "emotion": emotion_label,
            "intent": user_intent,
            "persona": persona_name
        })

    return dialogue


# ====================== 主生成逻辑（容错+校验）======================
def generate_dataset():
    print(f"开始生成 {TOTAL_SAMPLES} 条带人设的情感对话数据（严格校验版）...")
    data = []

    # 按人设和场景均衡分配样本
    personas = list(PERSONAS.keys())
    scenarios = list(SCENARIOS.keys())
    total_groups = len(personas) * len(scenarios)
    samples_per_group = TOTAL_SAMPLES // total_groups
    remaining = TOTAL_SAMPLES % total_groups  # 分配剩余样本

    for persona in personas:
        for scenario in scenarios:
            # 计算当前分组的样本数
            group_samples = samples_per_group + (1 if remaining > 0 else 0)
            remaining -= 1 if remaining > 0 else 0

            for _ in range(group_samples):
                # 生成对话（带异常捕获）
                try:
                    dialogue = generate_dialogue(persona, scenario)
                except Exception as e:
                    print(f"生成对话失败（{persona}-{scenario}）：{e}")
                    continue  # 跳过错误样本

                # 拆解为轮次数据
                for i in range(MAX_CONTEXT_LEN):
                    curr = dialogue[i]
                    # 构建上下文
                    context = [turn["text"] for turn in dialogue[:i]]
                    trigger_event = f"上下文: {' [SEP] '.join(context)} | 当前文本: {curr['text']}"

                    # 计算情绪强度
                    strength_min, strength_max = EMOTION_STRENGTH[curr["emotion"]]
                    emotion_strength = round(random.uniform(strength_min, strength_max), 1)

                    # 计算趋势
                    emotion_trend = "平稳" if i == 0 else get_trend(dialogue[i-1]["emotion"], curr["emotion"])

                    # 组装数据行（严格匹配模型字段）
                    row = {
                        "trigger_event": trigger_event,
                        "emotion_label": curr["emotion"],
                        "emotion_strength": emotion_strength,
                        "emotion_confidence": round(random.uniform(0.7, 0.99), 3),
                        "emotion_trend": emotion_trend,
                        "trend_confidence": round(random.uniform(0.6, 0.95), 3),
                        "user_intent": curr["intent"],
                        "intent_confidence": round(random.uniform(0.6, 0.95), 3),
                        "scene": scenario,
                        "persona": persona
                    }
                    data.append(row)

    # 最终校验：确保无重复/异常数据
    df = pd.DataFrame(data).drop_duplicates()
    # 打乱顺序
    df = df.sample(frac=1, random_state=42).reset_index(drop=True)
    # 保存
    df.to_csv(OUTPUT_FILE, index=False, encoding="utf-8-sig")

    # 输出数据分布（验证均衡性）
    print(f"\n数据生成完成！已保存至 {OUTPUT_FILE}，实际样本数：{len(df)}")
    print("\n=== 关键分布校验 ===")
    print("1. 情绪标签分布（前10）：")
    print(df["emotion_label"].value_counts().head(10))
    print("\n2. 意图分布：")
    print(df["user_intent"].value_counts())
    print("\n3. 场景分布：")
    print(df["scene"].value_counts())
    print("\n4. 人设分布：")
    print(df["persona"].value_counts())


if __name__ == "__main__":
    generate_dataset()