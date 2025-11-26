from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path
from typing import List

from pydantic import BaseModel, Field, validator


class Settings(BaseModel):
    """Application configuration sourced from environment variables."""

    api_prefix: str = Field(default="/api")
    upload_dir: str = Field(default="tmp/uploads")
    output_dir: str = Field(default="tmp/transcripts")
    max_upload_mb: int = Field(default=200, ge=1)
    allowed_origins: List[str] = Field(default_factory=lambda: ["*"])
    model_size: str = Field(default="medium")

    @validator("upload_dir", "output_dir", pre=True)
    def _normalize_dir(cls, value: str) -> str:
        return value.replace("\\", "/") if value else value

    @classmethod
    def from_env(cls) -> "Settings":
        return cls(
            api_prefix=os.getenv("API_PREFIX", "/api"),
            upload_dir=os.getenv("UPLOAD_DIR", "tmp/uploads"),
            output_dir=os.getenv("OUTPUT_DIR", "tmp/transcripts"),
            max_upload_mb=int(os.getenv("MAX_UPLOAD_MB", "200")),
            allowed_origins=[origin.strip() for origin in os.getenv("ALLOWED_ORIGINS", "*").split(",")],
            model_size=os.getenv("MODEL_SIZE", "medium"),
        )

    def ensure_directories(self) -> None:
        Path(self.upload_dir).mkdir(parents=True, exist_ok=True)
        Path(self.output_dir).mkdir(parents=True, exist_ok=True)


def _validate_settings(settings: Settings) -> Settings:
    settings.ensure_directories()
    return settings


@lru_cache()
def get_settings() -> Settings:
    """Return a cached Settings instance."""

    return _validate_settings(Settings.from_env())
