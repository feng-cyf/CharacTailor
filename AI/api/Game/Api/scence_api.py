import asyncio
import json
import logging
from typing import Optional, Dict, Any

from AIModel.DeepSeek import DeepSeek
from AIModel.DouBaoLite import DouBaoLite
from core.RedisProcess import generate_and_save_summary, add_history_message, get_summary

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def get_message(scene, token):
    """
    处理用户消息，生成回复

    Args:
        scene: 场景对象，包含场景信息和用户消息
        token: 用户令牌，包含用户ID等信息

    Returns:
        dict: 包含状态码、消息和数据的字典
    """
    try:
        # 提取必要的信息
        user_msg = scene.userMessage
        scene_id = scene.sceneId
        name = scene.name
        description = scene.description
        background = getattr(scene, 'background', '')  # 场景背景信息
        character_setting = getattr(scene, 'character_setting', '')  # 人设信息

        user_id = token.get("user_id")
        username = token.get("username", "未知用户")

        if user_id is None:
            raise ValueError("用户不存在")

        # 获取用户记忆
        summary = await get_summary(session_id=scene_id, user_id=user_id)
        memory_included = bool(summary)

        # 始终包含场景信息（强制使用）
        include_scene = True
        scene_info = f"场景ID: {scene_id}, 名称: {name}, 描述: {description}, 背景: {background}"

        # 根据场景类型决定是否生成选项（例如：对话场景可能需要选项，查询场景可能不需要）
        include_options = any(keyword in description.lower() for keyword in
                              ['选择', '对话', '交互', '菜单', '选项'])

        # 构建系统提示词
        system_prompt = f"""
        场景助手，严格输出JSON对象，无任何额外字符。

        【角色设定】
        {character_setting}

        【场景信息】
        {scene_info}

        【用户信息】
        用户: {username}({user_id})
        用户记忆: {summary.strip() if summary else '无'}

        【当前对话】
        用户消息: {user_msg.strip()}

        【输出要求】
        你必须根据以下信息生成回复：
        1. 严格遵循角色设定（人设）
        2. 充分利用场景信息和背景
        3. 考虑用户的历史记忆（如果有）
        4. 保持对话的连贯性和逻辑性

        【输出JSON结构】
        {{
          "type": "text",
          "data": {{
            "user_message": "{user_msg.strip().replace('"', '\\"')}",
            "reply": "基于人设、场景、背景和用户记忆生成的自然语言回复(非空)",
            "options": [{{"id":"1","text":"..."}},...]或 "",
            "scene_included": {str(include_scene).lower()},
            "memory_included": {str(memory_included).lower()},
            "options_included": {str(include_options).lower()}
          }}
        }}

        【规则】
        - "reply"必须非空，并且必须体现人设特点
        - "options"为选项数组（2-5个选项）或空字符串
        - 如果"options_included"为true，"options"必须是有效数组
        - 如果"options_included"为false，"options"必须是""
        - 严格JSON语法：使用双引号，布尔值为小写，无多余逗号
        - 回复必须自然、连贯，符合当前场景和角色设定
        """
        print(system_prompt)
        # 调用AI模型
        ds = DouBaoLite()
        loop=asyncio.get_running_loop()
        response =await loop.run_in_executor(
            None,
            ds.get_message,
            *[user_msg,system_prompt,500]
        )
        logger.info(f"AI response: {response}")

        # 解析响应
        data = json.loads(response)

        # 验证响应结构
        if not isinstance(data, dict) or 'data' not in data:
            raise ValueError("响应格式不正确")

        # 保存对话历史
        message = {"user": user_msg, "ass": data['data']['reply']}
        await add_history_message(session_id=scene_id, user_id=user_id, msg=message)

        # 异步生成摘要
        asyncio.create_task(
            generate_and_save_summary(
                session_id=scene_id,
                user_id=user_id,
                desc=description
            )
        )

        return {
            "statusCode": 200,
            "message": "获取成功",
            "data": response
        }

    except json.JSONDecodeError as e:
        logger.error(f"JSON解析错误: {e}")
        return {"statusCode": 500, "message": "响应格式错误", "error": str(e)}
    except ValueError as e:
        logger.error(f"值错误: {e}")
        return {"statusCode": 400, "message": str(e)}
    except Exception as e:
        logger.error(f"未知错误: {e}", exc_info=True)
        return {"statusCode": 500, "message": "服务器内部错误", "error": str(e)}


# 如果DeepSeek没有异步方法，可以使用这个包装器
class DeepSeekAsyncWrapper:
    def __init__(self, deepseek_instance):
        self.deepseek = deepseek_instance

    async def get_message_async(self, *args, **kwargs):
        # 在 executor 中运行同步方法
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(
            None,
            self.deepseek.get_message,
            *args,
            **kwargs
        )


# 使用示例
async def main():
    # 假设这些是测试数据
    class MockScene:
        def __init__(self):
            self.userMessage = "你好"
            self.sceneId = "scene_123"
            self.name = "测试场景"
            self.description = "这是一个测试场景，需要生成选项"
            self.background = "这是场景的详细背景信息"
            self.character_setting = "你是一个友好的助手，总是乐于助人"

    scene = MockScene()
    token = {"user_id": "user_456", "username": "测试用户"}

    result = await get_message(scene, token)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    asyncio.run(main())