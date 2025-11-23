from fastapi import APIRouter
from fastapi.params import Depends

from Helper.Jwt import get_current_user
from api.dialogApi import get_dialog_all

app_dialog_router = APIRouter(prefix="/dialog",tags=["dialog"])
@app_dialog_router.get("/")
async def dialog_root(session_id,persona_id,token=Depends(get_current_user)):
    result=await get_dialog_all(token=token,session_id=session_id,persona_di=persona_id)
    return result