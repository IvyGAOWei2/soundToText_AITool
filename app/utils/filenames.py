from __future__ import annotations

import re
from datetime import datetime, timezone
from pathlib import Path

from app.schemas import OutputMode

INVALID_CHARS = re.compile(r"[^A-Za-z0-9._-]")


def sanitize_stem(value: str) -> str:
    stem = Path(value).stem or "audio"
    sanitized = INVALID_CHARS.sub("_", stem)
    return sanitized.strip("._") or "audio"


def build_upload_filename(job_id: str, suffix: str) -> str:
    suffix = suffix if suffix else ".wav"
    return f"{job_id}{suffix}"


def build_output_filename(original_name: str, mode: OutputMode) -> str:
    safe_stem = sanitize_stem(original_name)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return f"{safe_stem}_{timestamp}.{mode.value}"


def format_timestamp(seconds: float) -> str:
    milliseconds = int((seconds - int(seconds)) * 1000)
    total_seconds = int(seconds)
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    secs = total_seconds % 60
    return f"{hours:02}:{minutes:02}:{secs:02},{milliseconds:03}"
