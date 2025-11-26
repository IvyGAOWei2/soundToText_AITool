from __future__ import annotations

import importlib.util
from dataclasses import dataclass
from typing import List

from faster_whisper import WhisperModel  # type: ignore[import-not-found]


@dataclass
class Segment:
    start: float
    end: float
    text: str


@dataclass
class TranscriptionResult:
    segments: List[Segment]
    language: str
    language_probability: float
    duration_seconds: float


class WhisperRunner:
    """Thin wrapper around Faster-Whisper for reuse across requests."""

    def __init__(self, model_size: str) -> None:
        self.device = self._resolve_device()
        compute_type = "int8_float16" if self.device == "cuda" else "float32"
        self.model = WhisperModel(model_size, device=self.device, compute_type=compute_type)

    def run(self, audio_path: str) -> TranscriptionResult:
        segments, info = self.model.transcribe(audio_path, beam_size=5)
        data = [Segment(start=s.start, end=s.end, text=s.text.strip()) for s in segments]
        duration = getattr(info, "duration", data[-1].end if data else 0.0)
        return TranscriptionResult(
            segments=data,
            language=info.language,
            language_probability=getattr(info, "language_probability", 0.0),
            duration_seconds=duration,
        )

    @staticmethod
    def _resolve_device() -> str:
        spec = importlib.util.find_spec("torch")
        if spec is not None:
            try:
                import torch  # type: ignore[import-not-found]

                if torch.cuda.is_available():
                    return "cuda"
            except Exception:  # pragma: no cover - torch optional
                return "cuda"
        return "cpu"

    @staticmethod
    def _compute_type(device: str) -> str:
        return "int8_float16" if device == "cuda" else "float32"
