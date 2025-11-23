import asyncio
import os

from dotenv import load_dotenv
from volcenginesdkarkruntime import Ark
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
import os
from dotenv import load_dotenv
from pathlib import Path


def get_key():
    env_path = Path(__file__).parent.parent / "apiKey.env"
    load_dotenv(dotenv_path=env_path)  # 用绝对路径加载
    api_key = os.getenv("API_KEY")
    if not api_key:
        raise ValueError("未在 apiKey.env 中找到 API_KEY 配置")
    return api_key

class ArkModel:
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(ArkModel, cls).__new__(cls)
        return cls._instance
    
    def __init__(self,api_key=None,model: str = None):
        # 单例模式，避免重复初始化
        if api_key is None:
            api_key = get_key()
        if not hasattr(self, 'initialized'):
            # 使用传入的配置、文件中的配置
            self.api_key = api_key or globals().get('api_key')
            self.model = model or "doubao-seed-1-6-251015"
            
            # 检查api_key是否存在
            if not self.api_key:
                logger.error("ArkModel初始化失败: API_KEY未提供")
                raise ValueError("API_KEY is required")
            
            # 使用api_key认证初始化客户端
            self.client = Ark(
                base_url="https://ark.cn-beijing.volces.com/api/v3",
                api_key=self.api_key
            )
            logger.info(f"ArkModel初始化完成，使用API_KEY认证，模型: {self.model}")
                
            self.initialized = True
    
    async def generate_text(self, user_message: str, system_prompt: str = ""):
        """生成文本回复"""
        try:
            # 构建消息列表
            messages = []
            if system_prompt:
                messages.append({
                    "role": "system",
                    "content": system_prompt
                })
            messages.append({
                "role": "user",
                "content": user_message
            })
            
            # 发送请求
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=0.5,
                    max_tokens=2000
                )
            )
            
            # 返回生成的文本
            if response.choices and len(response.choices) > 0:
                return response.choices[0].message.content
            return ""
            
        except Exception as e:
            logger.error(f"生成文本时出错: {str(e)}")
            raise
    
    async def generate_text_via_websocket(self, websocket, user_message: str, system_prompt: str = "", session_id:str=None):
        """通过WebSocket生成文本回复（流式）"""
        try:
            # 构建消息列表
            messages = []
            if system_prompt:
                messages.append({
                    "role": "system",
                    "content": system_prompt
                })
            messages.append({
                "role": "user",
                "content": user_message
            })
            
            # 发送开始生成的消息
            await websocket.send_json({
                "code": 200,
                "message": "开始生成回复",
                "type": "start"
            })
            
            # 使用流式请求
            loop = asyncio.get_event_loop()
            response_stream = await loop.run_in_executor(
                None,
                lambda: self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=0.7,
                    max_tokens=2000,
                    stream=True  # 启用流式响应
                )
            )
            # 处理流式响应并通过WebSocket发送
            full_response = ""
            for chunk in response_stream:
                if chunk.choices and len(chunk.choices) > 0:
                    delta = chunk.choices[0].delta
                    if hasattr(delta, 'content') and delta.content:
                        # 累积完整响应
                        full_response += delta.content
                        # 发送流式消息
                        await websocket.send_json({
                            "code": 200,
                            "message": delta.content,
                            "type": "stream"
                        })
                        # 控制发送速率
                        await asyncio.sleep(0.05)
            
            # 确保生成非空响应
            if not full_response:
                full_response = "我已收到您的请求，但未生成具体内容。请尝试重新提问。"
                # 如果没有生成内容，发送默认回复
                await websocket.send_json({
                    "code": 200,
                    "message": full_response,
                    "type": "stream",
                    "session_id":session_id
                })
            print(full_response)
            # 发送结束消息，包含完整响应
            await websocket.send_json({
                "code": 200,
                "message": full_response,
                "type": "end"
            })
            return full_response
        except Exception as e:
            logger.error(f"WebSocket生成文本时出错: {str(e)}")
            await websocket.send_json({
                "code": 500,
                "message": f"云端模型服务异常: {str(e)}",
                "type": "error"
            })

    async def analyze_image_via_websocket(self, websocket, user_message: str, image_url: str, system_prompt: str = "",
                                          session_id: str = None):
        """通过WebSocket分析图像并生成流式回复"""
        try:
            # 1. 构建包含图像和文本的多模态消息
            messages = []
            if system_prompt:
                messages.append({
                    "role": "system",
                    "content": system_prompt
                })
            print(image_url)

            messages.append({
                "role": "user",
                "content": [
                    {"type": "text", "text": user_message},
                    {
                        "type": "image_url",
                        "image_url": {"url": image_url}
                    }
                ]
            })

            # 2. 发送“开始生成”的通知
            await websocket.send_json({
                "code": 200,
                "message": "正在分析图片并思考回复...",
                "type": "start",
                "session_id": session_id
            })

            # 3. 使用流式请求调用多模态模型
            loop = asyncio.get_event_loop()
            response_stream = await loop.run_in_executor(
                None,
                lambda: self.client.chat.completions.create(
                    model=self.model,  # 确保使用支持图像的模型，如 gpt-4o, claude-3-sonnet 等
                    messages=messages,
                    stream=True,
                    max_tokens=2000,
                    temperature=0.7,
                    # reasoning_effort 参数通常是 Anthropic Claude 的，OpenAI 不需要
                    # 如果使用 Claude，请保留并调整
                    # reasoning_effort="medium"
                )
            )

            # 4. 处理流式响应并通过WebSocket发送
            full_response = ""
            for chunk in response_stream:
                if chunk.choices and len(chunk.choices) > 0:
                    delta = chunk.choices[0].delta
                    if hasattr(delta, 'content') and delta.content:
                        # 累积完整响应文本
                        full_response += delta.content
                        # 通过WebSocket发送当前的文本片段
                        await websocket.send_json({
                            "code": 200,
                            "message": delta.content,  # 这里是流式的文本片段
                            "type": "stream",
                            "session_id": session_id
                        })
                        # 可以适当控制发送速率，让回复更自然
                        await asyncio.sleep(0.05)

            # 5. 处理空响应的边缘情况
            if not full_response:
                full_response = "我已经看到了图片，但暂时没有想到合适的回复。可以换一张图片或者问我其他问题哦～"
                await websocket.send_json({
                    "code": 200,
                    "message": full_response,
                    "type": "stream",
                    "session_id": session_id
                })

            # 6. 发送“结束”通知，并附上完整的回复文本
            await websocket.send_json({
                "code": 200,
                "message": full_response,
                "type": "end",
                "session_id": session_id
            })
            print(full_response)

            return full_response

        except Exception as e:
            logger.error(f"WebSocket图像分析时出错: {str(e)}")
            error_message = f"分析图片时遇到了一点小问题: {str(e)}"
            await websocket.send_json({
                "code": 500,
                "message": error_message,
                "type": "error",
                "session_id": session_id
            })
            # 可以选择抛出异常，让调用方知道
            raise

    
    async def stream_response_handler(self, response_stream):
        """处理流式响应"""
        full_response = ""
        try:
            for chunk in response_stream:
                if chunk.choices and len(chunk.choices) > 0:
                    delta = chunk.choices[0].delta
                    if hasattr(delta, 'content') and delta.content:
                        full_response += delta.content
                        yield delta.content
                        await asyncio.sleep(0.05)
            
            # 确保生成非空响应
            if not full_response:
                default_response = "我已收到您的请求，但未生成具体内容。请尝试重新提问。"
                yield default_response
                full_response = default_response
                
        except Exception as e:
            logger.error(f"处理流式响应时出错: {str(e)}")
            # 发生错误时生成错误消息
            error_response = f"处理响应时发生错误: {str(e)}"
            yield error_response
            raise
        
    

def get_ark_model():
    """获取ArkModel单例"""
    return ArkModel()

# 示例使用
async def main():
    # 初始化模型
    ark = ArkModel()
    #
    # # 生成文本
    response = await ark.generate_text("你好，请介绍一下你自己")
    print(f"响应: {response}")
    #
    # 分析图像
    # image_response = await ark.analyze_image("分析这张图片", "https://example.com/image.jpg")
    # print(f"图像分析响应: {image_response}")

if __name__ == "__main__":
    asyncio.run(main())