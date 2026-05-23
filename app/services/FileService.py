import os
import uuid

from fastapi import UploadFile


class FileService:
    @staticmethod
    async def save_file(file: UploadFile, folder: str) -> str:
        file_extension = os.path.splitext(file.filename)[1]
        file_name = f"{uuid.uuid4()}{file_extension}"
        file_path = os.path.join("static", folder, file_name)

        # Записываем файл на диск
        content = await file.read()
        with open(file_path, "wb") as f:
            f.write(content)

        # Возвращаем путь, который будет храниться в БД
        return f"/static/{folder}/{file_name}"