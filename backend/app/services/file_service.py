"""
파일 서비스 — 이미지 업로드/삭제/URL 생성.
메뉴 이미지를 로컬 파일 시스템에 저장합니다.

저장 구조:
  uploads/stores/{store_id}/menus/{uuid}_{filename}.{ext}
"""

import os
import uuid

from fastapi import UploadFile

from app.config import get_settings
from app.domain.menu_domain import MenuDomain

settings = get_settings()


class FileService:
    """이미지 파일 관리 서비스"""

    def __init__(self):
        self.menu_domain = MenuDomain()

    async def upload_image(self, file: UploadFile, store_id: uuid.UUID) -> str:
        """이미지 파일 저장. 저장된 파일 경로를 반환."""
        content = await file.read()

        # 유효성 검증
        validation = self.menu_domain.validate_image_file(
            content_type=file.content_type or "",
            size=len(content),
        )
        if not validation.valid:
            raise ValueError(validation.message)

        # 저장 디렉토리 생성
        store_dir = os.path.join(
            settings.UPLOAD_DIR, "stores", str(store_id), "menus"
        )
        os.makedirs(store_dir, exist_ok=True)

        # 고유 파일명 생성
        ext = os.path.splitext(file.filename or "image.jpg")[1]
        unique_name = f"{uuid.uuid4()}{ext}"
        file_path = os.path.join(store_dir, unique_name)

        # 파일 저장
        with open(file_path, "wb") as f:
            f.write(content)

        return file_path

    async def delete_image(self, file_path: str) -> bool:
        """이미지 파일 삭제"""
        if file_path and os.path.exists(file_path):
            os.remove(file_path)
            return True
        return False

    @staticmethod
    def get_image_url(file_path: str | None) -> str | None:
        """이미지 서빙 URL 생성"""
        if not file_path:
            return None
        return f"/{file_path.replace(os.sep, '/')}"
