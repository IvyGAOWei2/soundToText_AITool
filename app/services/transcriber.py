from __future__ import annotations

import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from fastapi import HTTPException, UploadFile, status

from app.config import Settings
from app.schemas import OutputMode, TranscriptionAcceptedResponse, TranscriptionStatusResponse
from app.services.job_store import JobRecord, JobStore
from app.storage.local import LocalStorage
from app.inference.whisper_runner import TranscriptionResult, WhisperRunner
from app.utils import filenames


class TranscriberService:
    """Coordinates uploads, inference, and artifact generation."""

    def __init__(
        self,
        *,
        settings: Settings,
        job_store: JobStore,
        storage: LocalStorage,
        runner: WhisperRunner,
    ) -> None:
        self.settings = settings
        self.job_store = job_store
        self.storage = storage
        self.runner = runner

    async def transcribe(self, upload: UploadFile, mode: OutputMode) -> TranscriptionAcceptedResponse:
        job_id = str(uuid.uuid4())
        safe_stem = filenames.sanitize_stem(upload.filename or "audio")
        source_suffix = Path(upload.filename or "audio.mp3").suffix
        upload_name = filenames.build_upload_filename(job_id, source_suffix)
        upload_path = await self.storage.save_upload(upload, upload_name)

        job = JobRecord(
            transcription_id=job_id,
            status="processing",
            input_filename=upload.filename or upload_name,
            output_type=mode,
        )
        self.job_store.create(job)

        try:
            result = self.runner.run(str(upload_path))
            output_filename = filenames.build_output_filename(upload.filename or "audio", mode)
            if mode is OutputMode.txt:
                payload = self._segments_to_text(result)
            else:
                payload = self._segments_to_srt(result)
            output_path = self.storage.write_output(output_filename, payload)
            download_url = self.storage.build_download_url(output_filename, self.settings)
            self.job_store.update(
                job_id,
                status="completed",
                duration_seconds=result.duration_seconds,
                output_filename=output_filename,
                download_url=download_url,
            )
            return TranscriptionAcceptedResponse(
                transcription_id=job_id,
                status="processing",
                started_at=job.created_at,
                output_type=mode,
                input_filename=job.input_filename,
            )
        except Exception as exc:  # pylint: disable=broad-except
            self.job_store.update(job_id, status="failed", error=str(exc))
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="TRANSCRIPTION_FAILED") from exc
        finally:
            self.storage.delete_file(upload_path)

    def get_status(self, transcription_id: str) -> TranscriptionStatusResponse:
        job = self.job_store.get(transcription_id)
        if not job:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid transcription ID.")
        return TranscriptionStatusResponse(
            transcription_id=job.transcription_id,
            status=job.status,
            created_at=job.created_at,
            updated_at=job.updated_at,
            duration_seconds=job.duration_seconds,
            output_type=job.output_type,
            download_url=job.download_url,
            error=job.error,
        )

    def ensure_job_ready(self, transcription_id: str) -> JobRecord:
        job = self.job_store.get(transcription_id)
        if not job:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid transcription ID.")
        if job.status != "completed":
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Transcription not ready.")
        return job

    def resolve_output_path(self, output_filename: str) -> Path:
        return self.storage.resolve_output_path(output_filename)

    def ensure_file_available(self, filename: str) -> JobRecord:
        job = self.job_store.find_by_output_filename(filename)
        if not job:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")
        if job.status != "completed":
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Transcription not ready")
        return job

    @staticmethod
    def _segments_to_text(result: TranscriptionResult) -> str:
        lines = [f"[{seg.start:.2f} - {seg.end:.2f}] {seg.text}" for seg in result.segments]
        return "\n".join(lines)

    @staticmethod
    def _segments_to_srt(result: TranscriptionResult) -> str:
        rows = []
        for idx, seg in enumerate(result.segments, start=1):
            rows.append(str(idx))
            rows.append(f"{filenames.format_timestamp(seg.start)} --> {filenames.format_timestamp(seg.end)}")
            rows.append(seg.text)
            rows.append("")
        return "\n".join(rows)
