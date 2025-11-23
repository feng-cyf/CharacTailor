from models.model import User, User_Pydantic_In


async def create_user(u:User_Pydantic_In):
    try:
        user=User.get_or_none(user_id=u.user_id)
        if user:
            return {"code": 409, "message": "User already exists"}
        data=u.dict(exclude_unset=True)
        data.update({"default_persona_id":"default"})
        await User.create(**data)
        return {"code": 200, "message": "Created"}
    except Exception as e:
        return {"code": 500, "message": str(e)}

