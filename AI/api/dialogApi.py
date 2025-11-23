from models.model import DialogueHistory


async def get_dialog_all(token,session_id,persona_di):
    dialogs = await DialogueHistory.filter(user_id=token['user_id'],
                                           session_id=session_id,persona_id=persona_di).order_by('created_at').all()
    
    # 转换为前端需要的数据格式
    result = []
    
    # 遍历所有对话记录
    for dialog in dialogs:
        # 构建用户消息，添加消息类型和文件URL
        user_msg = {
            "role": "user",
            "content": dialog.user_message,
            "user_message_type": dialog.user_message_type,
            "user_file_url": dialog.user_file_url
        }
        result.append(user_msg)
        
        # 构建AI回复，添加消息类型和文件URL
        bot_response = {
            "role": "assistant",
            "content": dialog.bot_response,
            "bot_response_type": dialog.bot_response_type,
            "bot_file_url": dialog.bot_file_url,
            "bot_audio_url":dialog.bot_audio_url
        }
        result.append(bot_response)
    
    # 包含时间信息
    times = [dialog.created_at for dialog in dialogs]
    
    #需要判断类型，然后决定是否调用文件路由加载图片
    return {"data": result, "time": times}