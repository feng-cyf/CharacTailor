from fastapi import APIRouter

from route.GameRoute.ComokuRoute import app_gomoku
from route.GameRoute.sceneRoute import app_scene

app_game=APIRouter(prefix="/game", tags=["game"])
app_game.include_router(app_gomoku)
app_game.include_router(app_scene)