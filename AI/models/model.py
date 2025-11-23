from tortoise import Model, fields
from tortoise.contrib.pydantic import pydantic_model_creator


# 1. 人设表（先定义，避免关联依赖）
class Persona(Model):
    persona_id = fields.CharField(pk=True, max_length=50)
    persona_name = fields.CharField(max_length=100, null=False)
    description = fields.TextField(null=True)
    tone = fields.CharField(max_length=50, default="neutral")
    speech_characteristics = fields.JSONField(null=True)
    functional_scene = fields.CharField(max_length=100, default="general")
    emotional_bias = fields.JSONField(null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    is_active = fields.BooleanField(default=True)
    deploy_type = fields.CharField(max_length=20, default="cloud")
    class Meta:
        table = "personas"
        indexes = [("functional_scene",), ("tone",)]
Persona_Pydantic_In=pydantic_model_creator(Persona,exclude=("created_at",))

# 2. 用户表
class User(Model):
    user_id = fields.CharField(pk=True, max_length=50)
    username = fields.CharField(max_length=100, null=False)
    created_at = fields.DatetimeField(auto_now_add=True)
    last_login = fields.DatetimeField(auto_now=True,null=True)
    total_interaction_count = fields.IntField(default=0)
    relationship_level = fields.IntField(default=1)
    pwd=fields.CharField(max_length=50, null=False)
    # 多对多关联人设
    personas = fields.ManyToManyField(
        "base.Persona",
        related_name="user",
        through="user_persona_mapping",
        through_fields=("persona_id","user_id")
    )

    class Meta:
        table = "user"
User_Pydantic_In=pydantic_model_creator(User, exclude=("created_at",))

# 3. 用户-人设中间表（手动指定，对应SQL）
class UserPersonaMapping(Model):
    id = fields.IntField(pk=True, autoincrement=True)
    user = fields.ForeignKeyField("base.User", on_delete=fields.CASCADE)
    persona = fields.ForeignKeyField("base.Persona", on_delete=fields.CASCADE)
    is_default = fields.BooleanField(default=False)
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "user_persona_mapping"
        indexes = [("user_id", "persona_id")]
        unique_together = (("user", "persona"),)

# 4. 会话表
class Session(Model):
    session_id = fields.CharField(pk=True, max_length=100)
    user = fields.ForeignKeyField("base.User", related_name="sessions", on_delete=fields.CASCADE)
    connection_info = fields.JSONField(null=True)
    current_persona = fields.ForeignKeyField(
        "base.Persona",
        related_name="active_sessions",
        on_delete=fields.SET_DEFAULT,
        default="default"
    )
    is_active = fields.BooleanField(default=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    parent_session_id = fields.CharField(max_length=50, null=True, default=None)
    session_name = fields.CharField(max_length=100, null=True, default="默认会话")
    last_activity = fields.DatetimeField(auto_now=True)
    emotional_context = fields.JSONField(null=True)

    class Meta:
        table = "sessions"
        indexes = [("user_id",), ("is_active",), ("current_persona_id",)]

# 5. 对话历史表
class DialogueHistory(Model):
    dialogue_id = fields.CharField(pk=True, max_length=100)
    session = fields.ForeignKeyField("base.Session", related_name="dialogues", on_delete=fields.CASCADE)
    user = fields.ForeignKeyField("base.User", related_name="dialogues", on_delete=fields.CASCADE)
    persona = fields.ForeignKeyField(
        "base.Persona",
        related_name="dialogues",
        on_delete=fields.RESTRICT
    )
    emotion_type=fields.CharField(max_length=10)
    user_message = fields.TextField(null=False)
    bot_response = fields.TextField(null=False)
    emotional_feedback = fields.FloatField(default=0.5)
    created_at = fields.DatetimeField(auto_now_add=True)
    confidence=fields.FloatField()
    user_message_type=fields.CharField(max_length=10,default="text")
    bot_response_type=fields.CharField(max_length=10,default="text")
    user_file_url=fields.CharField(null=True,max_length=100)
    bot_file_url=fields.CharField(null=True,max_length=100)
    bot_audio_url=fields.CharField(null=True,max_length=100)

    class Meta:
        table = "dialogue_history"
        indexes = [("persona_id",), ("user_id", "session_id")]

# 6. 情感历史表
class EmotionalHistory(Model):
    id = fields.IntField(pk=True, autoincrement=True)
    user = fields.ForeignKeyField("base.User", related_name="emotional_histories", on_delete=fields.CASCADE)
    session = fields.ForeignKeyField("base.Session", related_name="emotional_histories", on_delete=fields.CASCADE)

    # 核心：直接存储模型输出的情感标签（替代原有的happiness/sadness等细分字段）
    emotion_label = fields.CharField(max_length=50)  # 如“委屈”“甜蜜”“生气”
    emotion_strength = fields.FloatField()  # 0-10分，对应模型的“情感强度”
    emotion_confidence = fields.FloatField()  # 模型对情感标签的置信度（0-1）

    # 情感趋势与意图（模型输出，保留）
    emotion_trend = fields.CharField(max_length=20)  # 上升/下降/平稳
    trend_confidence = fields.FloatField()  # 趋势预测的置信度
    user_intent = fields.CharField(max_length=50)  # 求安慰/求互动等
    intent_confidence = fields.FloatField()  # 意图预测的置信度

    # 辅助信息（保留必要的场景和触发事件）
    trigger_event = fields.TextField(null=True)  # 引发情绪的事件（如具体对话内容）
    scene = fields.CharField(max_length=50, default="chat")  # 场景（聊天/任务等）
    created_at = fields.DatetimeField(auto_now_add=True)  # 情绪记录时间

    class Meta:
        table = "emotional_history"
        indexes = [("user_id", "created_at"), ("scene",)]

class GridEmotionalHistory(Model):
    id = fields.IntField(pk=True, autoincrement=True)
    user = fields.ForeignKeyField("base.User", related_name="grid_emotional_histories", on_delete=fields.CASCADE)
    session = fields.ForeignKeyField("base.Session", related_name="grid_emotional_histories", on_delete=fields.CASCADE)

    # 核心：直接存储模型输出的情感标签（替代原有的happiness/sadness等细分字段）
    emotion_label = fields.CharField(max_length=50)  # 如“委屈”“甜蜜”“生气”
    emotion_strength = fields.FloatField()  # 0-10分，对应模型的“情感强度”
    emotion_confidence = fields.FloatField()  # 模型对情感标签的置信度（0-1）

    # 情感趋势与意图（模型输出，保留）
    emotion_trend = fields.CharField(max_length=20)  # 上升/下降/平稳
    trend_confidence = fields.FloatField()  # 趋势预测的置信度
    user_intent = fields.CharField(max_length=50)  # 求安慰/求互动等
    intent_confidence = fields.FloatField()  # 意图预测的置信度

    # 辅助信息（保留必要的场景和触发事件）
    trigger_event = fields.TextField(null=True)  # 引发情绪的事件（如具体对话内容）
    scene = fields.CharField(max_length=50, default="chat")  # 场景（聊天/任务等）
    created_at = fields.DatetimeField(auto_now_add=True)  # 情绪记录时间

    class Meta:
        table = "grid_emotional_history"
        indexes = [("user_id", "created_at")]

# 7. 记忆表
class Memories(Model):
    id = fields.IntField(pk=True, autoincrement=True)
    user = fields.ForeignKeyField("base.User", related_name="memories", on_delete=fields.CASCADE)
    memory_type = fields.CharField(max_length=20, null=False)
    content = fields.TextField(null=False)
    embedding_vector = fields.BinaryField(null=True)
    importance_score = fields.FloatField(default=0.5, null=False)
    emotional_weight = fields.FloatField(default=0.5, null=False)
    created_at = fields.DatetimeField(auto_now_add=True)
    last_accessed = fields.DatetimeField(auto_now=True)
    access_count = fields.IntField(default=0)
    metadata = fields.JSONField(null=True)

    class Meta:
        table = "memories"
        indexes = [("user_id", "memory_type"), ("importance_score",)]


class GameType(Model):
    # 自增主键 ID
    id = fields.IntField(pk=True, autoincrement=True)
    # 游戏类型名称，如 "MOBA", "Card", "Strategy"
    name = fields.CharField(max_length=50, unique=True, null=False)
    # 对该游戏类型的描述
    description = fields.TextField(null=True)

    class Meta:
        table = "game_types"

# 2. 游戏定义表
class GameDefinition(Model):
    # 自增主键 ID
    id = fields.IntField(pk=True, autoincrement=True)
    # 游戏名称，如 "王者荣耀", "英雄联盟"
    name = fields.CharField(max_length=100, unique=True, null=False)
    # 外键，关联到 game_types 表
    type_id = fields.ForeignKeyField(
        "base.GameType",  # 注意："base" 是你的 app_label，请根据实际情况修改
        related_name="games",
        on_delete=fields.CASCADE
    )

    class Meta:
        table = "game_definitions"
        indexes = [("type_id",)]

# 3. 游戏会话表
class GameSession(Model):
    # 自增主键 ID
    id = fields.IntField(pk=True, autoincrement=True)
    # 游戏开始时间
    start_time = fields.DatetimeField(auto_now_add=True)
    # 游戏结束时间
    end_time = fields.DatetimeField(null=True)
    # 获胜者（可以是玩家ID或AI标识）
    winner = fields.CharField(max_length=20, null=True)
    # 失败者
    loser = fields.CharField(max_length=20, null=True)
    # 外键，关联到 game_definitions 表，表示本次玩的是哪个游戏
    game_id = fields.ForeignKeyField(
        "base.GameDefinition",  # 注意："base" 是你的 app_label，请根据实际情况修改
        related_name="sessions",
        on_delete=fields.CASCADE
    )
    # 游戏状态，如 "playing", "finished", "canceled"
    status = fields.CharField(max_length=20, default="playing", null=False)
    # 参与游戏的用户 ID
    user = fields.ForeignKeyField(
        "base.User",  # 指向 "base" 应用下的 "User" 模型
        related_name="game_sessions",  # 这是 User 模型中反向引用的名称
        on_delete=fields.CASCADE  # 当用户被删除时，关联的游戏会话也会被删除
    )

    persona = fields.ForeignKeyField(
        "base.Persona",
        related_name="game_sessions",
        on_delete=fields.CASCADE
    )

    # 游戏得分
    score = fields.IntField(default=0)
    game_config = fields.JSONField(null=True)

    class Meta:
        table = "game_sessions"
        indexes = [("user_id",), ("game_id",), ("status",)]

class Scene(Model):
    id = fields.IntField(pk=True, autoincrement=True)
    name = fields.CharField(max_length=100, unique=True, null=False)
    user = fields.ForeignKeyField("base.User", related_name="scenes", on_delete=fields.CASCADE)
    description =fields.CharField(null=True,max_length=100)
    created_at = fields.DatetimeField(auto_now_add=True)