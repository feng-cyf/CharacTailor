import datetime
import os
import uuid

from dotenv import load_dotenv
from fastapi import HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from starlette import status
from starlette.websockets import WebSocket

import jwt
import dotenv
load_dotenv(r"D:\GridFriend\AI\apiKey.env")


SCRET_KEY=os.environ.get("SCRET_KEY")
ALGORITHM = "HS256"
sc=OAuth2PasswordBearer(tokenUrl="/user/login")
def create_token(data: dict, expire_delta: datetime.timedelta = None):  # 修改参数名
    to_encode = data.copy()
    now = datetime.datetime.utcnow()
    if expire_delta is None:
        exp = now + datetime.timedelta(days=3)
    else:
        exp = now + expire_delta  # 使用修改后的参数名
    to_encode.update({
        "exp": exp,
        "nbf": now
    })
    token = jwt.encode(to_encode, SCRET_KEY, algorithm=ALGORITHM)
    return token
def decode_token(token:str) -> dict:
    return jwt.decode(token, SCRET_KEY, algorithms=[ALGORITHM])

def get_current_user(token=Depends(sc)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="令牌无效或已过期",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_token(token)
        user=payload.get("user_id")
        if not user:
            raise credentials_exception
        return payload
    except Exception as e:
        raise credentials_exception

async def get_current_user_from_ws(web_socket:WebSocket):

    token=web_socket.query_params.get("token")
    if not token:
        await web_socket.close(code=status.WS_1008_POLICY_VIOLATION)
        return None
    try:
        payload=get_current_user(token)
        username=payload.get("username")
        user_id=payload.get("user_id")
        if not user_id:
            await web_socket.close(code=status.WS_1008_POLICY_VIOLATION)
            return None
        return {"username":username,"user_id":user_id}
    except Exception as e:
        print(e)
        await web_socket.close(code=status.WS_1008_POLICY_VIOLATION)
        return None