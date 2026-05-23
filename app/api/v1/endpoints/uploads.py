from fastapi import APIRouter, UploadFile, File, Depends
from app.services.FileService import FileService
from app.core import deps

upload_router = APIRouter()

@upload_router.post("/upload-image")
async def upload_image(
    file: UploadFile = File(...),
    current_user = Depends(deps.get_current_user)
):
    file_url = await FileService.save_file(file, "images")
    return {"url": file_url}

@upload_router.post("/upload-audio")
async def upload_audio(
    file: UploadFile = File(...),
    current_user = Depends(deps.get_current_user)
):
    file_url = await FileService.save_file(file, "audio")
    return {"url": file_url}