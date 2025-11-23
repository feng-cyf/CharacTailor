from fastapi import Depends
from fastapi.security import OAuth2PasswordRequestForm

from Helper.Jwt import create_token
from models.model import User


async def login(from_data):
    user=await User.get_or_none(user_id=from_data.username)
    if not user:
        return {"code": 401, "message": "Invalid username or password"}
    if user.pwd!=from_data.password:
        return {"code": 401, "message": "Invalid username or password"}
    token= create_token({"user_id":user.user_id,"username":user.username})
    return {"code": 200,"token":token,"token_type":"bearer"}