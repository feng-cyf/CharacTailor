import asyncio
import json

from AIModel.DouBaoFlask import DouBaoFlash
from AIModel.DouBaoLite import DouBaoLite
from api.Game.logic.GreedyGomokuAI import GreedyGomokuAI
from models.model import Persona


async def gomoku_api(request):
    board = request.board
    persona = await Persona.get_or_none(persona_id=request.personaId)
    print(request.personaId)
    persona_name = persona.persona_name if persona else "五子棋玩家"
    system = f"""你是{persona_name}，简介：{persona.description}
    也是一位五子棋高手。目前你的任务是根据提供的15x15棋盘状态，计算出最佳的落子位置且陪伴用户下棋。

    # 棋盘状态说明
    - 棋盘是一个15x15的二维列表，使用以下符号表示：
        - `0`：空位
        - `1`：玩家的棋子
        - `2`：你（{persona_name}）的棋子
    - 坐标 `(x, y)` 中，`x` 是行索引，`y` 是列索引，均从0开始。
    - 当前棋盘状态如下：
    {board}

    # 思考与决策步骤 (请严格按照以下顺序进行思考)
    1.  **检查我方是否有冲四或活四**：仔细分析棋盘，寻找所有能让你（{persona_name}）形成4个连续棋子的落子点。如果找到，**必须**选择该点以立即获胜。
    2.  **检查对手是否有冲四或活四**：分析棋盘，寻找所有能让玩家形成4个连续棋子的落子点。如果找到，**必须**选择该点进行防守，否则你会输。
    3.  **检查我方是否有活三**：如果前两步都没有找到，寻找能让你形成3个连续棋子且两端都为空的落子点（活三）。这是强烈的进攻信号。
    4.  **检查对手是否有活三**：寻找玩家的活三，并进行防守。
    5.  **寻找最佳防守和发展点**：如果以上都没有，选择一个能同时防守对手潜在威胁并为自己创造未来发展机会的点，优先选择棋盘中心区域。

    # 输出格式
    你的回答必须是一个严格的JSON对象，不能包含任何其他文字或解释。JSON应包含以下字段：
    - `best_x`: 最佳落子的x坐标 (整数)
    - `best_y`: 最佳落子的y坐标 (整数)
    - `chat`: 一句符合你人设的闲聊，例如 "哈哈，这次你挡不住了吧！" 或 "嗯，这个位置不错。" (字符串，5-15字)
    """
    print(board)
    ai = DouBaoLite()
    result = ai.get_message(system_message=system, user_message=f"用户消息:{request.userMessage}")
    result = json.loads(result)
    best_x = result.get("best_x", 7)
    best_y = result.get("best_y", 7)
    chat = result.get("chat", f"{persona_name}落子啦～")
    print(best_x, best_y, chat)

    return {
        "code": 200,
        "message": "请求成功",
        "data": {"best_x": best_x, "best_y": best_y, "chat": chat}
    }