# Speech-to-Text Web Application API Specification

## 1. Purpose

Define the HTTP contract between the FastAPI backend and the React frontend for uploading audio, tracking transcription progress, and inference the transcript.

1. Uploading audio files
2. Running speech-to-text transcription
3. Displaying real-time processing status & elapsed time
4. Providing downloadable TXT or SRT output

## 2. Scope & Assumptions

- Backend stack: FastAPI + Python (Faster-Whisper for inference).
- Frontend stack: React + Tailwind (SPA) communicating over REST
- Job execution: Synchronous inference (processing → completed)
- Storage: temporary output folder /tmp/transcripts/
- No database & no job history — each transcription is independent

## 3. Identifiers & Formats

- `transcription_id`: A unique ID (transcription_id) returned immediately when processing begins
- Timestamp: ISO 8601 UTC string (e.g., `2025-11-26T09:15:22Z`).
- Duration: seconds (float) produced from Whisper metadata.
- Output Filename Format:
  Generated from original filename + timestamp: `<original_stem>_<timestamp>.<ext>`.
  Example:meeting_20251126T091522Z.txt

## 4. Data Models

### 4.1 AudioUploadRequest

```
multipart/form-data

| Field  | Type   | Required | Description                  |
| ------ | ------ | -------- | ---------------------------- |
| `file` | File   | Yes      | Audio file (mp3 / wav / m4a) |
| `mode` | String | Yes      | `"txt"` or `"srt"`           |

```

### 4.2 TranscriptionStatusResource

Returned by /api/status/{transcription_id}.

```
{
  "transcription_id": "7abcf1e3-fd3b-4f83-8c1b-2c41d9abf9e2",
  "status": "processing" | "completed" | "failed",
  "created_at": "2025-11-26T09:15:22Z",
  "updated_at": "2025-11-26T09:16:40Z",
  "input_filename": "meeting.mp3",
  "duration_seconds": 12.48,
  "output_type": "srt",
  "download_url": "/api/download/meeting_20251126T091522Z.srt",
  "error": null
}
```

## 5. Endpoint Catalog

| Method   | Path                             | Description                        |
| -------- | -------------------------------- | ---------------------------------- |
| **POST** | `/api/transcribe`                | Upload audio → start transcription |
| **GET**  | `/api/status/{transcription_id}` | Check current processing status    |
| **GET**  | `/api/download/{filename}`       | Download generated TXT/SRT         |

# **6. Endpoint Details**

---

# **6.1 POST /api/transcribe**

### Description

Accept audio file → begin transcription synchronously.
Returns a transcription_id immediately

### Request

`multipart/form-data`

- `file`: required
- `mode`: `"txt"` or `"srt"`

---

### Response (202 Accepted)

Backend begins processing and gives client an ID to poll:

```
{
  "transcription_id": "7abcf1e3-fd3b-4f83-8c1b-2c41d9abf9e2",
  "status": "processing",
  "started_at": "2025-11-26T09:15:22Z",
  "output_type": "srt",
  "input_filename": "meeting.mp3"
}
```

---

### Validation Errors

#### 400 invalid mode

`{"error": "Mode must be 'txt' or 'srt'."}`

#### 415 wrong file format

`{"error": "Unsupported audio format."}`

---

# **6.2 GET /api/status/{transcription_id}`**

### Description

Frontend polls this endpoint every 1–2 seconds to show:

- processing spinner
- elapsed time counter
- whether transcription is ready for download

### Response (Processing)

```{
  "transcription_id": "7abcf1e3-fd3b-4f83-8c1b-2c41d9abf9e2",
  "status": "processing",
  "created_at": "2025-11-26T09:15:22Z",
  "updated_at": "2025-11-26T09:15:31Z",
  "duration_seconds": 9.12
}
```

### Response (Completed)

```
{
  "transcription_id": "7abcf1e3-fd3b-4f83-8c1b-2c41d9abf9e2",
  "status": "completed",
  "duration_seconds": 14.72,
  "output_type": "txt",
  "download_url": "/api/download/meeting_20251126T091522Z.txt"
}
```

### Error (Not Found)

`{"error": "Invalid transcription ID."}`

---

# **6.3 GET /api/download/{filename}`**

### Description

Return generated transcript/subtitle file (TXT or SRT).

| Type | MIME                   |
| ---- | ---------------------- |
| TXT  | `text/plain`           |
| SRT  | `application/x-subrip` |

---

# **7. File Output Specification**

### Directory

`/tmp/transcripts/`

### Filename Format

`<original_stem>_<timestamp>.<ext>`

Example:

`thedetail_20251126T091522Z.srt`

### Extensions

- `.txt`
- `.srt`

### Lifetime

Files are temporary.  
They may be cleaned automatically by OS or by optional cleanup cron.

---

# **8. Inference Model Specification**

- Model: **Whisper Medium** via Faster-Whisper
- Device selection:
  - `cuda` if available
  - fallback to CPU automatically
- Loaded **once** at application start
- Inference is synchronous

---

# **9. Error Codes**

| Error Code             | HTTP | Meaning                    |
| ---------------------- | ---- | -------------------------- |
| `UNSUPPORTED_FORMAT`   | 415  | Only mp3/wav/m4a allowed   |
| `INVALID_MODE`         | 400  | Mode must be txt or srt    |
| `TRANSCRIPTION_FAILED` | 500  | Whisper model error        |
| `FILE_NOT_FOUND`       | 404  | Download or status invalid |

---

# **10. Security**

- CORS enabled
- Sanitized filename
- HTTPS recommended
- Temporary folder isolation (/tmp/transcripts/)
