from fastapi import APIRouter
from pydantic import BaseModel

from api.Game.Api.gomoku_api import gomoku_api

app_gomoku=APIRouter(prefix="/gomoku")
class Gomoku(BaseModel):
    board: list[list[int]]
    personaId:str
    userMessage:str|None=None
    x:int|None=None
    y:int|None=None
    color:int|None=None
@app_gomoku.post("/")
async def gomoku_post(gomoku: Gomoku):
    result=await gomoku_api(gomoku)
    return result