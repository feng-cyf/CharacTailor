from fastapi import APIRouter, UploadFile, File, HTTPException, Path,Body
from fastapi.params import Depends
from pydantic import BaseModel

from api.fileApi import FileType
from api.fileApi import uploaded_files

app_file=APIRouter(prefix="/file", tags=["file"])
class AudioTextRequest(BaseModel):
    text: str  # 明确 text 是字符串类型
def get_file_type_enum(file_type_str: str = Path(...)) -> FileType:
    try:
        normalized = file_type_str.strip().lower()
        alias = {"images": "image", "videos": "video"}
        normalized = alias.get(normalized, normalized)
        return FileType(normalized)
    except KeyError:
        # 如果找不到对应的枚举成员，抛出 HTTP 400 错误
        allowed_types = [ft.value for ft in FileType]
        raise HTTPException(
            status_code=400,
            detail=f"无效的文件类型: '{file_type_str}'。允许的类型为: {allowed_types}"
        )
@app_file.post("/upload/{file_type}")
async def save_image_route(file_type,file: UploadFile = File(...),):
    file_type=get_file_type_enum(file_type)
    result=await uploaded_files.upload_file(file_type=file_type, file=file)
    return result
@app_file.post("/upload/audio/{file_type}/{session_id}")
async def save_audio_route(file_type,session_id,request: AudioTextRequest):
    file_type=get_file_type_enum(file_type)
    result=await uploaded_files.upload_audio(file_type=file_type,text=request.text,session_id=session_id)
    return result
@app_file.get("/UploadedFiles/{file_type}/{filename}")
async def get_uploaded_file_route(filename:str,file_type):
    file_type=get_file_type_enum(file_type)
    result=uploaded_files.get_file_path(filename=filename,file_type=file_type)
    return result