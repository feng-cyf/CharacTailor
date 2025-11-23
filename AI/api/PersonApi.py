from fastapi import APIRouter
from tortoise.exceptions import IntegrityError
from tortoise.transactions import in_transaction

from core.SessionProcesser import SessionProcessor
from core.dialogHistoryProcessor import DialogHistoryProcessor
from models.model import Persona_Pydantic_In, Persona, User, UserPersonaMapping
from api.Person_User import persona_users


async def create_person(p: Persona_Pydantic_In, user, session=None):
    try:
        user_id = user['user_id']
        u = await User.get_or_none(user_id=user_id)
        if not u:
            return {"code": 404, "message": f"用户 {user_id} 不存在"}

        # 1. 先校验：当前 persona_id 是否已存在（全局唯一，主键约束）
        existing_persona = await Persona.get_or_none(persona_id=p.persona_id)
        if existing_persona:
            return {"code": 400, "message": f"人设ID {p.persona_id} 已被占用，请更换其他ID"}

        # 2. 再校验：该用户是否已关联过这个人设（中间表唯一约束）
        existing_mapping = await UserPersonaMapping.get_or_none(
            user_id=user_id,
            persona_id=p.persona_id
        )
        if existing_mapping:
            return {"code": 400, "message": f"你已关联过该人设，无需重复创建"}

        async with in_transaction():
            # 3. 创建人设（此时persona_id全局唯一，无冲突）
            # 使用dict()而不是dict(exclude_unset=True)，确保空对象字段也能保存
            persona_data = p.dict()
            # 确保speech_characteristics和emotional_bias即使为空也会被保存
            if 'speech_characteristics' not in persona_data or persona_data['speech_characteristics'] is None:
                persona_data['speech_characteristics'] = {}
            if 'emotional_bias' not in persona_data or persona_data['emotional_bias'] is None:
                persona_data['emotional_bias'] = {}
            persona = await Persona.create(**persona_data)
            print(persona_data)
            # 4. 关联用户和人设（中间表插入记录，而非update）
            await persona.user.add(u)

            # 5. 取消该用户的旧默认人设（正确过滤中间表记录）
            await UserPersonaMapping.filter(
                user_id=user_id,
                is_default=True
            ).update(is_default=False)

            # 6. 设新创建的人设为默认（直接更新刚插入的中间表记录）
            await UserPersonaMapping.filter(
                user_id=user_id,
                persona_id=persona.persona_id
            ).update(is_default=True)
            
            # 7. 创建或更新关联session（无论是否有前端session信息都执行）
            # 构建设备信息字典，如果没有session对象则使用默认值
            device_info = {
                'device_id': session.device.device_id if session and hasattr(session, 'device') and hasattr(session.device, 'device_id') else 'unknown',
                'device_type': session.device.device_type if session and hasattr(session, 'device') and hasattr(session.device, 'device_type') else 'unknown',
                'browser': session.device.browser if session and hasattr(session, 'device') and hasattr(session.device, 'browser') else 'unknown',
                'user_agent': session.device.user_agent if session and hasattr(session, 'device') and hasattr(session.device, 'user_agent') else 'unknown'
            }
            # 创建会话处理器，session_id将在内部自动按照 user_id_persona_id 格式生成
            sp = SessionProcessor(
                session_id='',  # 这个值会在SessionProcessor内部被覆盖
                user=user, 
                persona_id=persona.persona_id,
                device=device_info
            )
            # 创建或更新会话
            await sp.create_session()
        
        # 直接使用用户id+人设id格式返回session_id，确保一致性
        session_id = f"{user_id}_{persona.persona_id}"
        return {"code": 200, "message": "人设创建并关联成功", "persona_id": persona.persona_id, "session_id": session_id}

    except IntegrityError as e:
        # 捕获主键冲突或中间表唯一约束冲突（兜底）
        if "Duplicate entry" in str(e) and "persona_id" in str(e):
            return {"code": 400, "message": f"人设ID {p.persona_id} 已存在"}
        elif "Duplicate entry" in str(e) and "user_id" in str(e) and "persona_id" in str(e):
            return {"code": 400, "message": "你已关联过该人设"}
        else:
            return {"code": 400, "message": f"创建冲突：{str(e)}"}
    # except Exception as e:
    #     # 其他错误（如字段缺失、类型错误）
    #     return {"code": 500, "message": f"创建失败：{str(e)}"}


async def get_person(_id:str):
    p=await Persona.get_or_none(persona_id=_id)
    if p is None:
        return {"code": 404, "message": "Not Found"}
    return {"code":200,"message":"获取成功","data":p}

async def update_person(p:Persona_Pydantic_In):
    persona=await Persona.get_or_none(persona_id=p.persona_id)
    if persona is None:
        return {"code": 404, "message": "Not Found"}
    for k,v in p.dict(exclude_unset=True).items():
        if hasattr(persona,k):
            setattr(persona,k,v)
    await persona.save()
    return {"code":200,"message":"Updated"}

async def delete_person(_id:str):
    p=await Persona.get_or_none(persona_id=_id)
    if p is None:
        return {"code": 404, "message": "Not Found"}
    await Persona.delete(p)
    return {"code":200,"message":"Deleted"}