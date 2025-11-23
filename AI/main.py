import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core import Expection
from core.Expection import ExceptionHandler
from database.mysql import register_mysql
from database.raw_mysql import init_raw_pool
from route.AIChatRoute import app_AIChatRouter
from route.GameAllRoute import app_game
from route.PersonRoute import app_persona_router
from route.UserRoute import app_user_router
from route.diaolgRoutw import app_dialog_router
from route.fileRoute import app_file

app = FastAPI()

# 配置CORS中间件，允许前端跨域访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173","http://localhost:5174"],  # 允许的前端地址
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有HTTP方法
    allow_headers=["*"],  # 允许所有HTTP头
)

ExceptionHandler.register(app)
register_mysql(app)
@app.on_event("startup")
async def startup():
    await init_raw_pool()
app.include_router(app_persona_router)
app.include_router(app_user_router)
app.include_router(app_AIChatRouter)
app.include_router(app_file)
app.include_router(app_game)
app.include_router(app_dialog_router)
if __name__ == '__main__':
    uvicorn.run(app, host="127.0.0.1", port=8000)