# from fastapi import WebSocket, Depends, WebSocketDisconnect
# from typing import Optional
#
# # 导入重构后的情感分析器
# from core.EmotionPredictor import EmotionPredictor
# from core.SessionProcesser import SessionProcessor
# from core.dialogHistoryProcessor import DialogHistoryProcessor
# from core.EmotionalHistoryProcess import EmotionalHistoryProcess
# from core.logger import emotion_logger
# from models.model import Persona, DialogueHistory, Session
# # 导入模型管理器
# from AIModel.Ollama import model_manager
# from AIModel.ArkModel import get_ark_model
#
# # 初始化重构后的情感分析器
# refactored_emotional_assessment = AdvancedEmotionalAssessment()
#
# async def chat_with_ai_refactored(
#     web_socket: WebSocket,
#     persona_id: str,
#     user,
#     device,
#     session_id,
#     use_cloud_model: bool = False ,
# ):
#     """
#     重构版AI聊天接口，使用重构后的情感分析器
#     """
#     # 1. 验证用户（JWT 验证失败直接关闭连接）
#     if not user:
#         return
#     user_id=user['user_id']
#     # 2. 建立 WebSocket 连接
#     await web_socket.accept()
#     emotion_logger.info(f"[重构API] 用户 {user_id} 已连接，使用人设：{persona_id}")
#
#     try:
#         while True:
#             # 3. 接收前端消息（格式：{"message": "用户输入"}）
#             data = await web_socket.receive_json()
#             user_message = data.get("message", "")
#             if not user_message:
#                 emotion_logger.warning(f"[重构API] 用户 {user_id} 发送空消息")
#                 await web_socket.send_json({
#                     "code": 400,
#                     "message": "消息内容不能为空"
#                 })
#                 continue
#             emotion_logger.info(f"[重构API] 收到用户消息 - 用户ID: {user_id}, 消息内容: {user_message}")
#
#             # 4. 获取人设配置
#             persona = await Persona.get_or_none(persona_id=persona_id)
#             if not persona:
#                 emotion_logger.warning(f"[重构API] 人设 {persona_id} 不存在")
#                 await web_socket.send_json({
#                     "code": 404,
#                     "message": f"人设 {persona_id} 不存在"
#                 })
#                 continue
#             emotion_logger.debug(f"[重构API] 成功获取人设配置: {persona.persona_name}")
#
#             # 5. 拼接提示词（结合用户信息和人设）
#             # 获取对话历史，注意这里返回的是格式化的上下文，不是原始对话对象
#             emotion_logger.debug(f"[重构API] 获取对话历史 - 会话ID: {session_id}")
#             dialogs_context=await DialogHistoryProcessor.get_dialog(session_id=session_id,user_id=user_id)
#             emotion_logger.info(f"[重构API] 对话历史上下文: {dialogs_context}")
#             formatted_history=None
#             if dialogs_context:
#                 # 将格式化的上下文转换为字符串格式
#                 formatted_history = "\n".join([f"{msg['role']}: {msg['content']}" for msg in dialogs_context])
#             system_prompt = f"""
#             你现在是「{persona.persona_name}」，正在与用户「{user["username"]}」（ID：{user_id}）对话。
#             严格遵循以下设定：
#             - 语气：{persona.tone}
#             - 语言特征：{persona.speech_characteristics}
#             - 场景：{persona.functional_scene}
#             - 情感倾向：{persona.emotional_bias}
#             - 描述：{persona.description}
#             -最近上下文：{formatted_history}
#             回复需贴合人设，自然回应「{user["username"]}」的问题。
#             """
#
#             # 6. 拼接Session
#             session_pro=SessionProcessor(device=device,user=user,persona_id=persona_id,session_id=session_id)
#             await session_pro.create_session()
#
#             # 7. 根据标志位选择使用本地模型或云端模型
#             if use_cloud_model:
#                 # 使用火山引擎Ark云端模型
#                 ark_model = get_ark_model()
#                 response= await ark_model.generate_text_via_websocket(
#                     websocket=web_socket,
#                     user_message=user_message,
#                     system_prompt=system_prompt,
#                     session_id=session_id,
#                 )
#             else:
#                 # 使用本地Ollama模型
#                 response= await model_manager.generate_via_websocket(
#                     websocket=web_socket,
#                     user_message=user_message,
#                     system_prompt=system_prompt,
#                     session_id=session_id,
#                 )
#
#             # 8. 进行情感分析（使用重构后的方法）
#             # 根据是否有session_id选择不同的分析方法
#             emotion_logger.info(f"[重构API] 开始进行情感分析 - 用户消息: {user_message}")
#             if session_id and dialogs_context is not None:
#                 # 使用上下文情感分析
#                 emotion_logger.debug(f"[重构API] 使用上下文情感分析 - 会话ID: {session_id}")
#                 emotion_analysis = await refactored_emotional_assessment.analyze_contextual_emotional_state(
#                     text=user_message,
#                     user_id=user_id,
#                     scene="chat",
#                     trigger_event="user_message",
#                     session_id=session_id,
#                     conversation_history=dialogs_context
#                 )
#             else:
#                 # 使用基础情感分析
#                 emotion_logger.debug(f"[重构API] 使用基础情感分析")
#                 emotion_analysis = await refactored_emotional_assessment.analyze_basic_emotional_state(
#                     text=user_message,
#                     user_id=user_id,
#                     scene="chat",
#                     trigger_event="user_message"
#                 )
#
#             # 记录情感分析结果
#             emotion = emotion_analysis['basic_emotion']
#             emotion_logger.info(f"[重构API] 情感分析结果 - 情感类型: {emotion['emotion_label']}, 情感权重: {emotion['emotion_weight']}, 置信度: {emotion['confidence']}")
#             emotion_logger.debug(f"[重构API] 完整情感分析数据: {emotion_analysis}")
#
#             # 9. 保存对话历史
#             dialog_history = DialogHistoryProcessor(
#                 user_id=user_id,
#                 persona_id=persona_id,
#                 session_id=session_id,
#                 bot_response=response,
#                 user_message=user_message,
#                 emotional_feedback=round(emotion['emotion_weight']/10.0,2),
#                 emotion_type=emotion['emotion_label'],
#                 confidence=emotion['confidence']
#             )
#
#             await dialog_history.creat_dialog()
#
#             # 10. 保存情感历史记录
#             # 注意：重构后的情感分析器返回的数据结构可能与之前略有不同
#             emotion_logger.info(f"[重构API] 保存情感历史记录 - 用户ID: {user_id}, 会话ID: {session_id}")
#             emotional_processor = EmotionalHistoryProcess(
#                 user_id=user_id,
#                 session_id=session_id,
#                 scene=emotion_analysis.get('scene', 'chat'),
#                 emotion_source="system"
#             )
#             await emotional_processor.from_emotion_data(emotion_analysis).create_emotional_history()
#             emotion_logger.debug(f"[重构API] 情感历史记录保存完成")
#
#     except WebSocketDisconnect:
#         emotion_logger.info(f"[重构API] 用户 {user_id} 断开连接")
#     except Exception as e:
#         emotion_logger.error(f"[重构API] 服务异常: {str(e)}")
#         await web_socket.send_json({
#             "code": 500,
#             "message": f"服务异常：{str(e)}"
#         })
#         await web_socket.close()
#
#
# # 测试函数：展示如何使用重构后的情感分析器
# async def example_usage():
#     """
#     展示如何直接使用重构后的情感分析器
#     """
#     # 初始化情感分析器
#     analyzer = refactored_emotional_assessment
#
#     # 示例文本
#     text = "今天天气真好，心情也很愉快！"
#     user_id = "example_user_001"
#     session_id = "example_session_123"
#
#     # 使用上下文感知分析
#     contextual_result = await analyzer.analyze_emotional_state(
#         text=text,
#         user_id=user_id,
#         session_id=session_id,
#         scene="chat"
#     )
#
#     print("=== 上下文感知分析结果 ===")
#     print(f"主要情感: {contextual_result['basic_emotion']['emotion_label']}")
#     print(f"情感维度: {contextual_result['emotional_dimensions']}")
#     print(f"高级指标: {contextual_result['advanced_metrics']}")
#
#     # 使用基础分析
#     basic_result = await analyzer.analyze_emotional_state(
#         text=text,
#         user_id=user_id,
#         scene="chat"
#     )
#
#     print("\n=== 基础分析结果 ===")
#     print(f"主要情感: {basic_result['basic_emotion']['emotion_label']}")
#     print(f"情感维度: {basic_result['emotional_dimensions']}")
#     print(f"高级指标: {basic_result['advanced_metrics']}")