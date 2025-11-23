from fastapi import APIRouter
from fastapi.params import Depends
from fastapi.security import OAuth2PasswordRequestForm

from api.Person_User import persona_users
from api.UserApi import create_user
from api.loginApi import login
from models.model import User, User_Pydantic_In

app_user_router = APIRouter(prefix="/user", tags=["user"])
@app_user_router.post("/create")
async def creat_user_route(u:User_Pydantic_In):
    result=await create_user(u)
    return result

@app_user_router.post("/login")
async def login_user_route(user:OAuth2PasswordRequestForm=Depends()):
    result=await login(user)
    return result

@app_user_router.post("/get_persona/{_id}")
async def get_persona_route(_id:str):
    result=await persona_users(_id)
    return result