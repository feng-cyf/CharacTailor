import asyncio
import json
import re
import threading
import uuid
import io
import os
import tempfile

import aiomysql
import anyio
import numpy as np
from enum import Enum
from pathlib import Path
from typing import Dict, Any

import cv2
import requests
from fastapi import UploadFile, HTTPException
from starlette.responses import FileResponse

from AIModel.TenCent import TenCent
from database.raw_mysql import get_raw_pool

load_dotenv("./database.env")
class FileType(Enum):
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"

FILE_TYPE_CONFIGS: Dict[FileType, Dict[str, Any]] = {
    FileType.IMAGE: {
        "upload_dir": Path("./UploadedFiles/image"),
        "max_size_bytes": 10 * 1024 * 1024,  # 10MB
        "allowed_extensions": {".jpg", ".jpeg", ".png", ".gif"},
        "route_prefix": "image"
    },
    FileType.VIDEO: {
        "upload_dir": Path("./UploadedFiles/video"),
        "max_size_bytes": 100 * 1024 * 1024,  # 100MB
        "allowed_extensions": {".mp4"},
        "route_prefix": "video"
    },
    FileType.AUDIO: {
        "upload_dir": Path("./UploadedFiles/audio"),
        "max_size_bytes": 50 * 1024 * 1024,
        "allowed_extensions": {".mp3"},
        "route_prefix": "audio"
    }
}

for config in FILE_TYPE_CONFIGS.values():
    config["upload_dir"].mkdir(parents=True, exist_ok=True)

class UploadedFiles:
    def __init__(self):
        self.base_url = "http://localhost:8000"
        self.PASSWORD = "AICHATGETFILE"
        self.UPLOAD_URL = os.getenv("cloud_url")
        self.FRAME_QUALITY = 90
        self.SECONDS_PER_FRAME = 1.0  # 每秒1帧
        self.LAYOUT = "horizontal"

    def upload_file_cloud(self, file, file_type: str):
        data = {"password": self.PASSWORD, "file_type": file_type}
        files = {"file": file}
        try:
            res = requests.post(
                self.UPLOAD_URL,
                data=data,
                files=files,
                timeout=60,
                proxies={"http": None, "https": None}
            )
            res.raise_for_status()
            result = res.json()
            if result.get("code") != 200:
                raise HTTPException(status_code=400, detail=f"云上传失败：{result.get('message')}")
            return result
        except requests.exceptions.RequestException as e:
            raise HTTPException(status_code=503, detail=f"云存储连接失败：{str(e)}")
        except json.JSONDecodeError:
            raise HTTPException(status_code=500, detail="云存储响应格式错误")

    def get_file_path(self, file_type: FileType, filename: str):
        config = FILE_TYPE_CONFIGS.get(file_type)
        if not config:
            raise HTTPException(status_code=404, detail="文件不存在")

        file_path = config["upload_dir"] / filename
        if not file_path.exists() or not file_path.is_file():
            raise HTTPException(status_code=404, detail="文件不存在")

        if not str(file_path.resolve()).startswith(str(config["upload_dir"].resolve())):
            raise HTTPException(status_code=403, detail="访问被拒绝")

        return FileResponse(path=file_path)

    def _stitch_frames(self, frames: list[np.ndarray]) -> io.BytesIO:
        if not frames:
            raise HTTPException(status_code=500, detail="未提取到有效帧")
        frame_size = (frames[0].shape[1], frames[0].shape[0])
        resized_frames = [cv2.resize(f, frame_size) for f in frames]
        stitched = np.hstack(resized_frames) if self.LAYOUT == "horizontal" else np.vstack(resized_frames)
        is_success, buffer = cv2.imencode(".jpg", stitched, [cv2.IMWRITE_JPEG_QUALITY, self.FRAME_QUALITY])
        if not is_success:
            raise HTTPException(status_code=500, detail="拼图编码失败")
        return io.BytesIO(buffer.tobytes())

    async def _video_to_puzzle(self, video_bytes: bytes) -> tuple[io.BytesIO, str]:
        with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as temp_file:
            temp_file.write(video_bytes)
            temp_file_path = temp_file.name

        try:
            cap = cv2.VideoCapture(temp_file_path)
            if not cap.isOpened():
                raise ValueError("无法打开视频")

            fps = cap.get(cv2.CAP_PROP_FPS) or 30
            frame_interval = max(1, int(fps * self.SECONDS_PER_FRAME))
            frames = []
            frame_count = 0

            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break
                if frame_count % frame_interval == 0:
                    frames.append(frame)
                frame_count += 1
            cap.release()

            puzzle_stream = self._stitch_frames(frames)
            puzzle_filename = f"puzzle_{uuid.uuid4()}.jpg"
            return puzzle_stream, puzzle_filename
        finally:
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)

    # ==================== 核心方法 ====================
    async def upload_file(self, file_type: FileType, file: UploadFile):
        config = FILE_TYPE_CONFIGS.get(file_type)
        if not config:
            raise HTTPException(status_code=400, detail="不支持的文件类型")

        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in config["allowed_extensions"]:
            allowed = ", ".join(config["allowed_extensions"])
            raise HTTPException(status_code=400, detail=f"不支持的格式：{file_ext}，允许：{allowed}")

        contents = await file.read()
        file_size = len(contents)
        if file_size > config["max_size_bytes"]:
            max_size = config["max_size_bytes"] / (1024 * 1024)
            raise HTTPException(status_code=400, detail=f"文件过大，最大允许 {max_size} MB")

        await file.seek(0)

        file_name = f"{uuid.uuid4()}{file_ext}"
        file_path = config["upload_dir"] / file_name
        with open(file_path, "wb") as f:
            f.write(contents)

        # ---------------------- 唯一修改：视频云上传换成拼图 ----------------------
        if file_type == FileType.VIDEO:
            puzzle_stream, puzzle_filename = await self._video_to_puzzle(contents)
            puzzle_stream.seek(0)
            # 云上传拼图（res 接收拼图的上传结果）
            res = self.upload_file_cloud(
                file_type=FileType.IMAGE.value,
                file=(puzzle_filename, puzzle_stream, "image/jpeg")
            )
            # 本地保存拼图（可选，不影响原始视频）
            puzzle_local_path = FILE_TYPE_CONFIGS[FileType.IMAGE]["upload_dir"] / puzzle_filename
            with open(puzzle_local_path, "wb") as f:
                f.write(puzzle_stream.getvalue())
        else:
            # 图片文件：保持原始逻辑
            res = self.upload_file_cloud(
                file_type=file_type.value,
                file=(file_name, contents, file.content_type)
            )

        return {
            "code": 200,
            "message": "上传成功",
            "data": {
                "local_url": f"{self.base_url}/file/UploadedFiles/{config['route_prefix']}/{file_name}",  # 原始视频本地URL
                "cloud_url": res["data"]["url"],  # 拼图的云URL（给API用）
                "file_name": file_name,  # 原始视频文件名
                "file_size": file_size,  # 原始视频文件大小
            }
        }
    async def upload_audio(self,text,file_type:FileType,session_id:str):
        pattern = r'[^\u4e00-\u9fff\s，。！？；：""''（）【】《》、]'
        text_sub = re.sub(pattern, "", text)
        config = FILE_TYPE_CONFIGS.get(file_type)
        if not config:
            raise HTTPException(status_code=404,detail="该文件类型不存在")
        file_name=f"{str(uuid.uuid4())}.mp3"
        file_path: str = config["upload_dir"] / file_name
        file_size=TenCent(text=text_sub,path=file_path).simple_tts()
        audio_url=f"{self.base_url}/file/UploadedFiles/{config['route_prefix']}/{file_name}"

        asyncio.create_task(
           self._async_db_operation(session_id=session_id,text=text,audio_url=audio_url)
        )

        return {
            "code": 200,
            "message":"上传成功",
            "data":{
                "local_url": audio_url,
                "file_name":file_name,
                "file_size":file_size,
            }
        }

    # 这是一个异步函数，包含所有数据库操作
    async def _async_db_operation(self, session_id: str, text: str, audio_url: str):
        def clean_text(text: str) -> str:
            if not text:
                return ""
            return re.sub(r'[^\u4e00-\u9fff_a-zA-Z0-9]', '', text)

        cleaned_input_text = clean_text(text)
        if not cleaned_input_text:
            print(f"⚠️ 清洗后用于匹配的文本为空，无法进行匹配。")
            return
        try:
            db = get_raw_pool()

            sql_select = """
                SELECT dialogue_id, bot_response 
                FROM dialogue_history 
                WHERE session_id = %s 
                ORDER BY created_at DESC
            """
            async with db.acquire() as conn:
                async with conn.cursor() as cur:
                    await cur.execute(sql_select, (session_id,))
                    all_dialogues = await cur.fetchall()

            if not all_dialogues:
                print(f"⚠️ 在 session_id '{session_id}' 下未找到任何对话记录。")
                return

            matched_dialogue_id = None
            for dialogue_id, bot_response in all_dialogues:
                cleaned_db_text = clean_text(bot_response)
                if cleaned_input_text in cleaned_db_text:
                    matched_dialogue_id = dialogue_id
                    break

            if matched_dialogue_id:
                sql_update = """
                    UPDATE dialogue_history 
                    SET bot_audio_url = %s 
                    WHERE dialogue_id = %s
                """
                async with db.acquire() as conn:
                    async with conn.cursor() as cur:
                        await cur.execute(sql_update, (audio_url, matched_dialogue_id))
                        await conn.commit()
                print(f"✅ 成功为对话ID {matched_dialogue_id} 更新音频URL。")
            else:
                print(f"❌ 未找到匹配的对话记录。清洗后的输入文本：'{cleaned_input_text[:50]}...'")

        except Exception as e:
            print(f"❌ 在执行原始 SQL 操作时发生错误: {str(e)}")
        # finally:
        #     await db.close()
uploaded_files = UploadedFiles()
