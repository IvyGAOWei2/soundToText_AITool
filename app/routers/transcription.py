from __future__ import annotations

from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import FileResponse

from app.schemas import ErrorResponse, OutputMode, TranscriptionAcceptedResponse, TranscriptionStatusResponse
from app.services.transcriber import TranscriberService

router = APIRouter()


def get_service(request: Request) -> TranscriberService:
    service = getattr(request.app.state, "transcriber_service", None)
    if service is None:
        raise RuntimeError("TranscriberService is not configured on application state")
    return service


@router.post(
    "/transcribe",
    status_code=202,
    response_model=TranscriptionAcceptedResponse,
    responses={
        400: {"model": ErrorResponse},
        415: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    },
)
async def transcribe_audio(
    file: UploadFile = File(..., description="Audio file to transcribe"),
    mode: OutputMode = Form(OutputMode.txt, description="Desired output format"),
    service: TranscriberService = Depends(get_service),
) -> TranscriptionAcceptedResponse:
    return await service.transcribe(file, mode)


@router.get(
    "/status/{transcription_id}",
    response_model=TranscriptionStatusResponse,
    responses={404: {"model": ErrorResponse}},
)
def get_status(transcription_id: str, service: TranscriberService = Depends(get_service)) -> TranscriptionStatusResponse:
    return service.get_status(transcription_id)


@router.get(
    "/download/{filename}",
    responses={
        404: {"model": ErrorResponse},
        409: {"model": ErrorResponse},
    },
)
def download_transcript(filename: str, service: TranscriberService = Depends(get_service)) -> FileResponse:
    service.ensure_file_available(filename)
    path = service.resolve_output_path(filename)
    if not path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    media_type = "application/x-subrip" if filename.endswith(".srt") else "text/plain"
    return FileResponse(path, media_type=media_type, filename=filename)
