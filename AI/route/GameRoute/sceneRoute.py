from fastapi import APIRouter, Depends
from pydantic import BaseModel

from Helper.Jwt import get_current_user
from api.Game.Api.scence_api import get_message

app_scene=APIRouter(prefix="/scene", tags=["scene"])
class ScenePar(BaseModel):
    sceneId:int
    userMessage:str
    name:str
    description:str
@app_scene.post("")
async def scene_message(scene: ScenePar,token=Depends(get_current_user)):
    result=await get_message(scene,token)
    return result