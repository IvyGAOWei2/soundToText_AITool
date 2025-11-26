from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from threading import Lock
from typing import Dict, Optional

from app.schemas import OutputMode


@dataclass
class JobRecord:
    transcription_id: str
    status: str
    input_filename: str
    output_type: OutputMode
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    duration_seconds: Optional[float] = None
    output_filename: Optional[str] = None
    download_url: Optional[str] = None
    error: Optional[str] = None

    def touch(self) -> None:
        self.updated_at = datetime.now(timezone.utc)


class JobStore:
    """Thread-safe in-memory registry for transcription jobs."""

    def __init__(self) -> None:
        self._jobs: Dict[str, JobRecord] = {}
        self._lock = Lock()

    def create(self, job: JobRecord) -> JobRecord:
        with self._lock:
            self._jobs[job.transcription_id] = job
        return job

    def get(self, transcription_id: str) -> Optional[JobRecord]:
        return self._jobs.get(transcription_id)

    def update(
        self,
        transcription_id: str,
        *,
        status: Optional[str] = None,
        duration_seconds: Optional[float] = None,
        output_filename: Optional[str] = None,
        download_url: Optional[str] = None,
        error: Optional[str] = None,
    ) -> Optional[JobRecord]:
        with self._lock:
            job = self._jobs.get(transcription_id)
            if not job:
                return None
            if status:
                job.status = status
            if duration_seconds is not None:
                job.duration_seconds = duration_seconds
            if output_filename is not None:
                job.output_filename = output_filename
            if download_url is not None:
                job.download_url = download_url
            if error is not None:
                job.error = error
            job.touch()
            return job

    def delete(self, transcription_id: str) -> None:
        with self._lock:
            self._jobs.pop(transcription_id, None)

    def find_by_output_filename(self, filename: str) -> Optional[JobRecord]:
        with self._lock:
            for job in self._jobs.values():
                if job.output_filename == filename:
                    return job
        return None
