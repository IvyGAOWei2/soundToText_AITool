from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Literal, Optional

from pydantic import BaseModel, Field


class OutputMode(str, Enum):
    txt = "txt"
    srt = "srt"


class TranscriptionAcceptedResponse(BaseModel):
    transcription_id: str = Field(..., description="Unique identifier for the transcription job")
    status: Literal["processing", "completed", "failed"] = "processing"
    started_at: datetime
    output_type: OutputMode
    input_filename: str


class TranscriptionStatusResponse(BaseModel):
    transcription_id: str
    status: Literal["processing", "completed", "failed"]
    created_at: datetime
    updated_at: datetime
    duration_seconds: Optional[float] = None
    output_type: Optional[OutputMode] = None
    download_url: Optional[str] = None
    error: Optional[str] = None


class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None
