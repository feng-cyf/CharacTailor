import requests
from typing import Dict, Optional
from fastapi import WebSocket

class ModelManager:
    # 类级别的单例实例，确保模型只初始化一次
    _instance = None

    def __new__(cls, model_name: str = "qwen3:8b", base_url: str = "http://localhost:11434"):
        if not cls._instance:
            cls._instance = super().__new__(cls)
            # 初始化模型配置
            cls._instance.model_name = model_name
            cls._instance.base_url = base_url
            cls._instance.chat_endpoint = f"{base_url}/api/chat"
            # 验证模型是否可用（启动时检查）
            cls._instance._check_model_available()
        return cls._instance

    def _check_model_available(self):
        """启动时检查模型是否能正常连接"""
        try:
            response = requests.post(
                self.chat_endpoint,
                json={"model": self.model_name, "messages": [{"role": "user", "content": "hello"}]},
                timeout=10
            )
            if response.status_code != 200:
                raise Exception(f"模型 {self.model_name} 不可用，状态码：{response.status_code}")
            print(f"模型 {self.model_name} 初始化成功，可正常调用")
        except Exception as e:
            print(f"模型初始化失败：{str(e)}，请确保已用 `ollama run {self.model_name}` 启动服务")

    def switch_model(self, new_model: str):
        """切换模型（动态切换，无需重启）"""
        self.model_name = new_model
        self._check_model_available()  # 切换后验证新模型

    async def generate_via_websocket(self, websocket: WebSocket, user_message: str, system_prompt: str,session_id:str):
        """通过 WebSocket 实时返回模型回复（非流式）"""
        try:
            # 发送开始生成的消息
            await websocket.send_json({
                "code": 200,
                "message": "开始生成回复",
                "type": "start"
            })
            
            # 调用 Ollama 模型
            response = requests.post(
                self.chat_endpoint,
                json={
                    "model": self.model_name,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_message}
                    ],
                    "stream": False
                },
                timeout=30
            )
            response.raise_for_status()
            
            # 处理响应内容
            bot_response = ""
            try:
                json_response = response.json()
                if "message" in json_response and "content" in json_response["message"]:
                    content = json_response["message"]["content"]
                    # 尝试提取需要的内容部分（如果有</think>分隔符）
                    if "</think>" in content:
                        parts = content.split("</think>")
                        if len(parts) > 1:
                            bot_response = parts[1]
                        else:
                            bot_response = content
                    else:
                        bot_response = content
                else:
                    bot_response = "未生成有效内容"
            except Exception as parse_error:
                bot_response = f"处理响应数据出错: {str(parse_error)}"
            
            # 通过 WebSocket 把完整结果发回前端，使用与ArkModel一致的格式
            await websocket.send_json({
                "code": 200,
                "message": bot_response,
                "type": "end",
                "session_id": session_id
            })
            return bot_response

        except Exception as e:
            # 错误信息也通过 WebSocket 返回，使用标准格式
            await websocket.send_json({
                "code": 500,
                "message": f"本地模型服务异常: {str(e)}",
                "type": "error"
            })


# 全局初始化模型（启动时执行一次，后续直接复用）
model_manager = ModelManager(model_name="qwen3:8b")  # 默认用 qwen3:8b