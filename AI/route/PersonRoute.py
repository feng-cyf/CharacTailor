from fastapi import APIRouter, Depends
from pydantic import BaseModel

from Helper.Jwt import get_current_user
from api.PersonApi import create_person,get_person,update_person,delete_person
from models.model import Persona,Persona_Pydantic_In

app_persona_router = APIRouter(prefix="/persona", tags=["persona"])

class DeviceInfo(BaseModel):
    device_id: str
    device_type: str
    browser: str
    user_agent: str

class SessionInfo(BaseModel):
    session_id: str
    device: DeviceInfo

class CreatePersonaRequest(BaseModel):
    persona: Persona_Pydantic_In
    session: SessionInfo

@app_persona_router.post("/create")
async def create_persona_route(request: CreatePersonaRequest, token=Depends(get_current_user)):
    result = await create_person(request.persona, token, request.session)
    return result
@app_persona_router.get("/get_persona/{id}")
async def get_persona_route(id: str):
    result=await get_person(id)
    return result
@app_persona_router.post("/update_person")
async def update_person_route(persona: Persona_Pydantic_In):
    result=await update_person(persona)
    return result
@app_persona_router.post("/delete_person")
async def delete_person_route(id: str):
    result=await delete_person(id)
    return result