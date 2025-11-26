from __future__ import annotations

from pathlib import Path
from typing import Optional

from fastapi import UploadFile

from app.config import Settings


class LocalStorage:
    """File-system backed storage for uploads and generated transcripts."""

    def __init__(self, upload_dir: str, output_dir: str) -> None:
        self.upload_dir = Path(upload_dir)
        self.output_dir = Path(output_dir)
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    async def save_upload(self, file: UploadFile, filename: str) -> Path:
        destination = self.upload_dir / filename
        destination.parent.mkdir(parents=True, exist_ok=True)
        with destination.open("wb") as buffer:
            while True:
                chunk = await file.read(1024 * 1024)
                if not chunk:
                    break
                buffer.write(chunk)
        await file.seek(0)
        return destination

    def write_output(self, filename: str, payload: str) -> Path:
        path = self.output_dir / filename
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(payload, encoding="utf-8")
        return path

    def build_download_url(self, filename: str, settings: Settings) -> str:
        return f"{settings.api_prefix}/download/{filename}"

    def resolve_output_path(self, filename: str) -> Path:
        return self.output_dir / filename

    def delete_file(self, file_path: Optional[Path]) -> None:
        if file_path is None:
            return
        try:
            Path(file_path).unlink(missing_ok=True)
        except AttributeError:
            # Python<3.8 compatibility fallback
            if Path(file_path).exists():
                Path(file_path).unlink()
