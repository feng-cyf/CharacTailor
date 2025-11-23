from fastapi import APIRouter,WebSocket
from fastapi.params import Depends

from Helper.Jwt import get_current_user_from_ws
from api.AIChatApi import chat_with_ai

app_AIChatRouter = APIRouter(prefix="/AIChat", tags=["AIChat"])
@app_AIChatRouter.websocket("/ws/{persona_id}")
async def websocket_endpoint(websocket: WebSocket, persona_id: str,user=Depends(get_current_user_from_ws)):
    # 从查询参数中获取use_cloud_model标志，默认为False
    use_cloud_model = websocket.query_params.get("use_cloud_model", "false").lower() == "true"
    device_id = websocket.query_params.get("device_id") #设备Id,例如本地电脑或者手机型号
    device_type = websocket.query_params.get("device_type") #设备类型:iPad，phone，pc
    device={"device_id": device_id, "device_type": device_type}
    session_id = websocket.query_params.get("session_id","")
    if session_id == "":
        raise {"code":400,"msg":"session_id不能为空"}
    await chat_with_ai(web_socket=websocket, persona_id=persona_id, user=user,
                       use_cloud_model=use_cloud_model,device=device,session_id=session_id)