from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.inference.whisper_runner import WhisperRunner
from app.routers import transcription
from app.services.job_store import JobStore
from app.services.transcriber import TranscriberService
from app.storage.local import LocalStorage


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title="Speech-to-Text API",
        version="0.1.0",
        description="REST API for the speech transcription web application",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_methods=["*"],
        allow_headers=["*"],
        allow_credentials=True,
    )

    app.state.settings = settings
    app.state.job_store = JobStore()
    storage = LocalStorage(settings.upload_dir, settings.output_dir)
    runner = WhisperRunner(settings.model_size)
    app.state.transcriber_service = TranscriberService(
        settings=settings,
        job_store=app.state.job_store,
        storage=storage,
        runner=runner,
    )

    app.include_router(transcription.router, prefix=settings.api_prefix, tags=["transcription"])

    return app


app = create_app()
