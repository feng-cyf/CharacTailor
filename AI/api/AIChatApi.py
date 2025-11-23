from fastapi import WebSocket, Depends, WebSocketDisconnect
from typing import Optional

from tortoise.transactions import in_transaction

from AIModel.Coze import Coze
from core.EmotionInteractionAnalyzer import EmotionInteractionAnalyzer
from core.MemoriesProcess import MemoriesProcess
from core.SessionProcesser import SessionProcessor
from core.StarInteractionManager import StarProbabilityManager
from core.dialogHistoryProcessor import DialogHistoryProcessor
from core.EmotionalHistoryProcess import EmotionalHistoryProcess, GridEmotionalHistoryProcess
from core.logger import chat_api_logger, emotion_logger, emotion_analyzer_logger
from models.model import Persona, DialogueHistory, Session
# 导入模型管理器
from AIModel.Ollama import model_manager
from AIModel.ArkModel import get_ark_model

coze=Coze()
async def chat_with_ai(
    web_socket: WebSocket,
    persona_id: str,
    user,
    device,
    session_id,
    use_cloud_model: bool = False ,

):
    # 1. 验证用户（JWT 验证失败直接关闭连接）
    if not user:
        return
    user_id=user['user_id']
    # 2. 建立 WebSocket 连接
    await web_socket.accept()
    chat_api_logger.info(f"用户 {user_id} 已连接，使用人设：{persona_id}")

    try:
        while True:
            # 3. 接收前端消息（格式：{"message": "用户输入"}）
            data = await web_socket.receive_json()
            user_message = data.get("message", "") #用户信息
            user_message_type = data.get("user_message_type", "") #用户信息类型
            user_file_local_url = data.get("user_file_local_url", None) #本地存储
            user_file_cloud_url = data.get("user_file_cloud_url", None) #api调用
            print(user_message_type)
            if not user_message:
                await web_socket.send_json({
                    "code": 400,
                    "message": "消息内容不能为空"
                })
                continue

            # 4. 获取人设配置
            persona = await Persona.get_or_none(persona_id=persona_id)
            print(persona_id)
            if not persona:
                chat_api_logger.warning(f"人设 {persona_id} 不存在")
                await web_socket.send_json({
                    "code": 404,
                    "message": f"人设 {persona_id} 不存在"
                })
                continue

            # 5. 获取对话历史
            dialogs_context = await DialogHistoryProcessor.get_dialog(session_id=session_id, user_id=user_id)
            predictor_mag=await DialogHistoryProcessor.get_recent_user_dialogs(session_id=session_id, user_id=user_id)
            # 6. 格式化对话历史为字符串形式
            formatted_history = ""
            if dialogs_context:
                # 确保formatted_history是字符串类型
                formatted_history = "\n".join([f"{msg['role']}: {msg['content']}" for msg in dialogs_context])
            
            # 7. 进行情感分析
            # 构建包含文件信息的完整消息内容
            full_user_message = user_message
            if user_file_cloud_url:
                if user_message_type == "image":
                    full_user_message = f"用户上传了图片: {user_file_cloud_url}\n用户描述: {user_message}"
                elif user_message_type == "video":
                    full_user_message = f"用户上传了视频: {user_file_cloud_url}\n用户描述: {user_message}"
            
            chat_api_logger.info(f"对用户 {user_id} 的消息进行情感分析: {full_user_message}")
            chat_api_logger.info(f"使用对话历史进行上下文分析，历史长度: {len(dialogs_context) if dialogs_context else 0}")
            analysis=coze.get_emotion(user_id=user_id,session_id=session_id,persona=f"{persona.persona_name},{persona.description}",
                                              history_msg=predictor_mag,user_msg=full_user_message)
            emotion_analysis,grid_emotion_analysis=analysis['user_emotion'],analysis['gf_emotion']
            chat_api_logger.info(f"情感分析完成 - 完整结果: {emotion_analysis}")
            chat_api_logger.info(f"情绪处理上下文: {dialogs_context}")

            # 7. 获取情感分析结果（修正字段映射）
            emotion = {
                "emotion_label": emotion_analysis["emotion_label"],
                "confidence": emotion_analysis["emotion_confidence"],
                "emotion_weight": emotion_analysis["emotion_strength"],
                "secondary_label": None,
                "secondary_confidence": 0.0
            }

            # 修正1：StarProbabilityManager 调用参数（用真实变量，不硬编码）
            manager = StarProbabilityManager()
            probabilities = await manager.get_final_probabilities(
                session_id=session_id,  # 复用当前会话ID
                user_id=user_id,  # 复用当前用户ID
                persona_key=persona_id  # 复用当前选择的人设ID
            )

            memery=MemoriesProcess(user_id=user_id)
            user_memery=await memery.get_memory()
            trend, confidence, _ = await EmotionInteractionAnalyzer.calculate_emotion_trend(session_id, user_id)

            # 构建包含文件信息的用户消息描述
            user_message_description = user_message
            if user_file_cloud_url:
                if user_message_type == "image":
                    user_message_description = f"用户上传了图片（URL: {user_file_cloud_url}）并描述：{user_message}"
                elif user_message_type == "video":
                    user_message_description = f"用户上传了视频（URL: {user_file_cloud_url}）并描述：{user_message}"
            
            # 最终极简提示词（无任何多余描述，直接传递核心信息）
            system_prompt = f"""你是「{persona.persona_name}」，与用户「{user["username"]}」（ID：{user_id}）对话。
            人设：{persona.description}，语气：{persona.tone}，语言特征：{persona.speech_characteristics}
            场景：{persona.functional_scene}，情感倾向：{persona.emotional_bias}
            用户记忆:{user_memery}
            实时情绪：{emotion['emotion_label']}（置信度：{emotion['confidence']}，强度：{emotion['emotion_weight']}）
            情绪趋势：{trend}（置信度：{confidence}），趋势优先
            行为概率：{probabilities}，按概率调整行为风格
            互动规则：情绪上升则共情轻松，下降则温柔安慰，平稳则自然互动
            用户消息：{user_message_description}
            上下文：{formatted_history}
            仅输出回复，无其他内容。""".strip()
            # 9. 拼接Session
            session_pro=SessionProcessor(device=device,user=user,persona_id=persona_id,session_id=session_id)
            response=None
            # 10. 根据标志位选择使用本地模型或云端模型
            if use_cloud_model:
                # 使用火山引擎Ark云端模型
                ark_model = get_ark_model()
                if user_message_type == "text":
                    response= await ark_model.generate_text_via_websocket(
                        websocket=web_socket,
                        user_message=user_message,
                        system_prompt=system_prompt,
                        session_id=session_id,
                    )
                elif user_message_type == "image" or user_message_type=="video":
                    response= await ark_model.analyze_image_via_websocket(
                        user_message=user_message,websocket=web_socket,session_id=session_id,
                        image_url=user_file_cloud_url,system_prompt=system_prompt)
            else:
                # 使用本地Ollama模型
                if user_message_type == "image" and user_file_cloud_url:
                    # 本地模型处理图片：在用户消息中添加图片描述
                    enhanced_user_message = f"用户上传了图片（URL: {user_file_cloud_url}）并描述：{user_message}"
                    response= await model_manager.generate_via_websocket(
                        websocket=web_socket,
                        user_message=enhanced_user_message,
                        system_prompt=system_prompt,
                        session_id=session_id,
                    )
                elif user_message_type == "video" and user_file_cloud_url:
                    # 本地模型处理视频：在用户消息中添加视频描述
                    enhanced_user_message = f"用户上传了视频（URL: {user_file_cloud_url}）并描述：{user_message}"
                    response= await model_manager.generate_via_websocket(
                        websocket=web_socket,
                        user_message=enhanced_user_message,
                        system_prompt=system_prompt,
                        session_id=session_id,
                    )
                else:
                    # 普通文本处理
                    response= await model_manager.generate_via_websocket(
                        websocket=web_socket,
                        user_message=user_message,
                        system_prompt=system_prompt,
                        session_id=session_id,
                    )

            # 保存对话历史
            dialog_history = DialogHistoryProcessor(
                user_id=user_id,
                persona_id=persona_id,
                session_id=session_id,
                bot_response=response,
                user_message=user_message,
                emotional_feedback=round(emotion["emotion_weight"], 2),
                emotion_type=emotion["emotion_label"],
                confidence=emotion["confidence"],
                user_file_url=user_file_local_url,
                user_message_type=user_message_type,
                bot_response_type="text",  # 默认为文本类型
                bot_file_url=None
            )
            # 保存情感历史记录（修正同步/异步）
            emotional_processor = EmotionalHistoryProcess(
                user_id=user_id,
                session_id=session_id,
                scene="chat",
                emotion_source="system"
            )
            emotional_processor.from_predict_result(emotion_analysis)
            grid_emotion_processor = GridEmotionalHistoryProcess(session_id=session_id,user_id=user_id)
            grid_emotion_processor.from_predict_result(grid_emotion_analysis)
            async with in_transaction():
                await session_pro.create_session()
                await dialog_history.creat_dialog()
                await emotional_processor.create_emotional_history()
                await grid_emotion_processor.create_emotional_history()
    except WebSocketDisconnect:
        chat_api_logger.info(f"用户 {user_id} 断开连接")
    # except Exception as e:
    #     chat_api_logger.error(f"服务异常: {str(e)}", exc_info=True)
    #     await web_socket.send_json({
    #         "code": 500,
    #         "message": f"服务异常：{str(e)}"
    #     })
    #     await web_socket.close()