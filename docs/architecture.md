# Speech-to-Text Web Application Architecture

## 1. Objectives

- Translate the approved API specification into an implementable FastAPI backend and React frontend.
- Keep the MVP synchronous and file-system-based while leaving seams for future background workers, persistent storage, and authentication.
- Ensure each layer (API, service, storage, inference) is independently testable.

## 2. High-Level System Overview

```
React SPA (upload UI, progress polling)
        ↓ REST/HTTPS
FastAPI Application (app/)
  - Routers: HTTP endpoints
  - Schemas: request/response validation
  - Services: transcription orchestration
  - Storage: audio + outputs on disk
  - Model Manager: Faster-Whisper singleton
        ↓
Local File System (/tmp/uploads/, /tmp/transcripts/)
```

## 3. Backend Module Layout

```
app/
├── main.py                # FastAPI app factory, CORS, router registration
├── config.py              # Settings (file limits, model size, paths)
├── schemas.py             # Pydantic models matching API spec
├── routers/
│   └── transcription.py   # /api/transcribe, /api/status, /api/download
├── services/
│   ├── transcriber.py     # Business logic for transcription
│   └── job_store.py       # In-memory job tracking abstraction
├── storage/
│   └── local.py           # Audio + output file persistence helpers
├── inference/
│   └── whisper_runner.py  # Faster-Whisper loading & execution
└── utils/
    └── filenames.py       # Sanitization and naming helpers
```

- Each layer depends only on the layer below (router → schema/service → storage/inference).
- `config.py` exposes `Settings` via `pydantic_settings` for easy override in tests.

## 4. Request Lifecycle

1. **POST /api/transcribe**
   - Router validates multipart payload (`mode`, allowed extensions, size limit).
   - `storage.local.save_upload()` streams file to `audio/`.
   - `services.transcriber.transcribe_sync()`
     - Creates `job` entry in `job_store` with status `processing`.
     - Calls `inference.whisper_runner.run()` with saved file, requested format.
     - Writes transcript to `/tmp/transcripts/` via storage layer.
     - Updates job status to `completed` or `failed` + error payload.
   - Returns `202` with DTO per spec.
2. **GET /api/status/{id}`**
   - Router queries `job_store.get(id)`; returns DTO or 404.
3. **GET /api/download/{filename}`**
   - Router resolves sanitized filename to `/tmp/transcripts/`; streams file if job finished and file exists.

## 5. Job Tracking Strategy

MVP: A simple in-memory dictionary keyed by transcription_id storing:

- status
- timestamps
- original filename
- generated output filename

It is not persistent and is cleared when the server restarts.

## 6. Storage Strategy

- **Uploads**: `/tmp/uploads/` (or similar)
- **Outputs**: `/tmp/transcripts/`
- Sanitize filenames and generate deterministic `<stem>_<timestamp>` names to avoid collisions.

## 7. Inference Layer

- `whisper_runner.py` loads Faster-Whisper model at startup using model size from settings.
- Provides `run(audio_path, mode, language=None)` returning transcript text/SRT plus metadata (duration, detected language).
- Automatically selects `cuda` if available, else CPU.

## 8. Configuration & Environment

- Use `.env` or environment variables for:
  - `MODEL_SIZE` (default `medium`).
  - `MAX_UPLOAD_MB` (default 200).
  - `OUTPUT_DIR`, `UPLOAD_DIR`.
  - `ALLOWED_ORIGINS` for CORS.
- Provide `config.Settings` to centralize defaults and allow overrides in unit tests.

## 9. Error Handling & Logging

- Map internal exceptions to API error codes defined in `docs/api-specification.md`.
- Use structured logging (job_id, filename, model, duration) via `logging` module.
- Capture inference stack traces for debugging while returning sanitized messages to clients.

## 10. Testing Strategy

- **Unit tests**
  - Schemas: validation rules for `mode`, file metadata.
  - Services: mock `whisper_runner` to verify job transitions.
  - Storage utils: filename sanitizer, cleanup logic.
- **Integration tests**
  - Use FastAPI `TestClient` to upload small audio sample and assert lifecycle.
- **Contract tests**
  - Ensure responses stay aligned with API spec (status codes, fields).

## 11. Frontend Integration Notes

- React app calls `POST /api/transcribe`, then polls `GET /api/status/{id}` until `completed` or `failed`.
- Download button links to `/api/download/{filename}` when status completes.
- Provide friendly messages for error codes (INVALID_MODE, UNSUPPORTED_FORMAT, TRANSCRIPTION_FAILED).

## 12. Future Enhancements

- Replace in-memory job store with Redis for multi-worker deployments.
- Introduce background processing queue (Celery/RQ/FastAPI BackgroundTasks) for long audios.
- Persist job history in SQLite/Postgres, enabling `/api/jobs` listing.
- Add authentication and per-user quotas when required.
