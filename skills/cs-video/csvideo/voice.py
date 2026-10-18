"""Offline narration with Piper TTS, plugged into manim-voiceover.

The voice model path comes from the CSVIDEO_VOICE environment variable,
or defaults to voices/en-us-lessac-medium.onnx inside the skill folder
(setup.sh downloads it).
"""
from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

from manim_voiceover.services.base import SpeechService, initialize_speech_service

SKILL_DIR = Path(__file__).resolve().parent.parent
DEFAULT_VOICE = SKILL_DIR / "voices" / "en-us-lessac-medium.onnx"


def _piper_cmd() -> list[str]:
    exe = Path(sys.executable).parent / "piper"
    if exe.exists():
        return [str(exe)]
    found = shutil.which("piper")
    if found:
        return [found]
    return [sys.executable, "-m", "piper"]


class PiperService(SpeechService):
    """Speech service that runs the Piper CLI locally (no network needed)."""

    def __init__(self, model: str | os.PathLike | None = None,
                 length_scale: float = 1.05, sentence_silence: float = 0.25,
                 **kwargs):
        self.model = str(model or os.environ.get("CSVIDEO_VOICE") or DEFAULT_VOICE)
        if not Path(self.model).exists():
            raise FileNotFoundError(
                f"Piper voice not found at {self.model}. Run setup.sh or set CSVIDEO_VOICE.")
        self.length_scale = length_scale        # >1 = slower, calmer speech
        self.sentence_silence = sentence_silence
        initialize_speech_service(self, kwargs)

    def generate_from_text(self, text, cache_dir=None, path=None, **kwargs):
        if cache_dir is None:
            cache_dir = self.cache_dir
        input_data = {
            "input_text": text,
            "service": "piper",
            "model": Path(self.model).name,
            "length_scale": self.length_scale,
        }
        cached = self.get_cached_result(input_data, cache_dir)
        if cached is not None:
            return cached

        audio_path = path or (self.get_audio_basename(input_data) + ".wav")
        out = Path(cache_dir) / audio_path
        subprocess.run(
            _piper_cmd() + ["-m", self.model, "-f", str(out),
                            "--length-scale", str(self.length_scale),
                            "--sentence-silence", str(self.sentence_silence)],
            input=text.encode("utf-8"), check=True,
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )
        return {"input_text": text, "input_data": input_data,
                "original_audio": str(audio_path)}
