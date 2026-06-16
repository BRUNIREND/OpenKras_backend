import json
import os
import uuid

import aioboto3

from app.core.config import settings
from fastapi import UploadFile


class FileService:

    @staticmethod
    async def init_bucket():
        """
        Автоматически создает бакет и делает его ПУБЛИЧНЫМ на чтение.
        Вызывается при старте FastAPI приложения.
        """
        session = aioboto3.Session()
        async with session.client(
            's3',
            endpoint_url=settings.MINIO_ENDPOINT,
            aws_access_key_id=settings.MINIO_ROOT_USER,
            aws_secret_access_key=settings.MINIO_ROOT_PASSWORD
        ) as s3:
            # 1. Проверяем и создаем бакет, если его нет
            try:
                await s3.head_bucket(Bucket=settings.MINIO_BUCKET_NAME)
            except Exception:
                await s3.create_bucket(Bucket=settings.MINIO_BUCKET_NAME)
                print(f"Бакет {settings.MINIO_BUCKET_NAME} успешно создан!")

            # 2. Формируем стандартную JSON-политику AWS S3 для публичного чтения файлов
            public_read_policy = {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Sid": "PublicReadGetObject",
                        "Effect": "Allow",
                        "Principal": "*",
                        "Action": ["s3:GetObject"],
                        "Resource": [f"arn:aws:s3:::{settings.MINIO_BUCKET_NAME}/*"]
                    }
                ]
            }

            # 3. Принудительно применяем политику к нашему бакету
            await s3.put_bucket_policy(
                Bucket=settings.MINIO_BUCKET_NAME,
                Policy=json.dumps(public_read_policy)
            )
            print(f"Политика PUBLIC READ успешно применена к бакету {settings.MINIO_BUCKET_NAME}!")

    @staticmethod
    async def save_file(file: UploadFile, folder: str) -> str:
        _, ext = os.path.splitext(file.filename)

        # Генерируем абсолютно уникальное имя для MinIO
        unique_filename = f"{uuid.uuid4()}{ext}"
        file_path = f"{folder}/{unique_filename}"
        session = aioboto3.Session()
        async with session.client(
            's3',
            endpoint_url=settings.MINIO_ENDPOINT,
            aws_access_key_id=settings.MINIO_ROOT_USER,
            aws_secret_access_key=settings.MINIO_ROOT_PASSWORD
        ) as s3:
            file_content = await file.read()
            await s3.put_object(
                Bucket=settings.MINIO_BUCKET_NAME,
                Key=file_path,
                Body=file_content,
                ContentType=file.content_type
            )
        return f"http://localhost:9000/{settings.MINIO_BUCKET_NAME}/{file_path}"

    @staticmethod
    async def delete_file(backet_name: str, object_name: str):
        session = aioboto3.Session()
        try:
            async with session.client(
                    's3',
                    endpoint_url=settings.MINIO_ENDPOINT,
                    aws_access_key_id=settings.MINIO_ROOT_USER,
                    aws_secret_access_key=settings.MINIO_ROOT_PASSWORD
            ) as s3:
                await s3.delete_object(Bucket=backet_name, Key = object_name)
        except Exception as e:
            # Логируем, но можно не падать, если файла уже нет в S3
            print(f"Ошибка удаления из MinIO: {e}")

        return "Файл удален"
