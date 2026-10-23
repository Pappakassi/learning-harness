"""Offline narration for manim-voiceover.

Default engine: Kokoro (natural-sounding, offline). Fallback: Piper.

Environment variables:
  CSVIDEO_TTS          "kokoro" (default) or "piper"
  CSVIDEO_KOKORO_VOICE Kokoro voice name, default "af_heart"
                       (others: am_michael, bf_emma, am_fenrir, ...)
  CSVIDEO_SPEED        speaking speed, default 1.0
  CSVIDEO_VOICE        path to a Piper .onnx voice (only for CSVIDEO_TTS=piper)

Model files live in voices/ inside the skill folder (setup.sh downloads them).
"""
from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

from manim_voiceover.services.base import SpeechService, initialize_speech_service

SKILL_DIR = Path(__file__).resolve().parent.parent
VOICES = SKILL_DIR / "voices"
KOKORO_MODEL = VOICES / "kokoro-v1.0.onnx"
KOKORO_VOICES = VOICES / "voices-v1.0.bin"
PIPER_DEFAULT = VOICES / "en-us-lessac-medium.onnx"


def make_speech_service() -> SpeechService:
    engine = os.environ.get("CSVIDEO_TTS", "kokoro").lower()
    if engine == "piper":
        return PiperService()
    return KokoroService()


def make_gnome_service() -> SpeechService:
    """Hr. Schiffel's voice: a deep Kokoro voice pitched up into a small, gruff gnome.
    CSVIDEO_GNOME_VOICE (default bm_george), CSVIDEO_GNOME_PITCH in cents (default 380),
    CSVIDEO_GNOME_SPEED (default 1.08)."""
    return KokoroService(voice=os.environ.get("CSVIDEO_GNOME_VOICE", "bm_george"),
                         speed=float(os.environ.get("CSVIDEO_GNOME_SPEED", 1.08)),
                         pitch_cents=int(os.environ.get("CSVIDEO_GNOME_PITCH", 380)))


class KokoroService(SpeechService):
    """Kokoro TTS via kokoro-onnx. Runs locally, no network needed."""

    _engine = None  # loaded once per process

    def __init__(self, voice: str | None = None, speed: float | None = None, pitch_cents: int = 0, **kwargs):
        for p in (KOKORO_MODEL, KOKORO_VOICES):
            if not p.exists():
                raise FileNotFoundError(f"Kokoro file missing: {p}. Run setup.sh.")
        self.voice = voice or os.environ.get("CSVIDEO_KOKORO_VOICE", "af_heart")
        self.speed = float(speed or os.environ.get("CSVIDEO_SPEED", 1.0))
        self.pitch_cents = pitch_cents
        initialize_speech_service(self, kwargs)

    @classmethod
    def _get_engine(cls):
        if cls._engine is None:
            from kokoro_onnx import Kokoro
            cls._engine = Kokoro(str(KOKORO_MODEL), str(KOKORO_VOICES))
        return cls._engine

    def generate_from_text(self, text, cache_dir=None, path=None, **kwargs):
        import soundfile as sf
        cache_dir = cache_dir or self.cache_dir
        input_data = {"input_text": text, "service": "kokoro",
                      "voice": self.voice, "speed": self.speed}
        if self.pitch_cents:
            input_data["pitch"] = self.pitch_cents
        cached = self.get_cached_result(input_data, cache_dir)
        if cached is not None:
            return cached
        audio, sr = self._get_engine().create(text, voice=self.voice, speed=self.speed,
                                              lang="en-us")
        audio_path = path or (self.get_audio_basename(input_data) + ".wav")
        out = Path(cache_dir) / audio_path
        sf.write(str(out), audio, sr)
        if self.pitch_cents:  # pitch up without changing tempo (sox), plus a little brightness
            tmp = out.with_suffix(".tmp.wav")
            subprocess.run(["sox", str(out), str(tmp), "pitch", str(self.pitch_cents), "treble", "3"], check=True)
            tmp.replace(out)
        return {"input_text": text, "input_data": input_data,
                "original_audio": str(audio_path)}


def _piper_cmd() -> list[str]:
    exe = Path(sys.executable).parent / "piper"
    if exe.exists():
        return [str(exe)]
    found = shutil.which("piper")
    return [found] if found else [sys.executable, "-m", "piper"]


class PiperService(SpeechService):
    """Piper TTS (more robotic, but tiny and fast)."""

    def __init__(self, model: str | os.PathLike | None = None,
                 length_scale: float = 1.05, sentence_silence: float = 0.25, **kwargs):
        self.model = str(model or os.environ.get("CSVIDEO_VOICE") or PIPER_DEFAULT)
        if not Path(self.model).exists():
            raise FileNotFoundError(f"Piper voice not found at {self.model}.")
        self.length_scale = length_scale
        self.sentence_silence = sentence_silence
        initialize_speech_service(self, kwargs)

    def generate_from_text(self, text, cache_dir=None, path=None, **kwargs):
        cache_dir = cache_dir or self.cache_dir
        input_data = {"input_text": text, "service": "piper",
                      "model": Path(self.model).name, "length_scale": self.length_scale}
        cached = self.get_cached_result(input_data, cache_dir)
        if cached is not None:
            return cached
        audio_path = path or (self.get_audio_basename(input_data) + ".wav")
        subprocess.run(
            _piper_cmd() + ["-m", self.model, "-f", str(Path(cache_dir) / audio_path),
                            "--length-scale", str(self.length_scale),
                            "--sentence-silence", str(self.sentence_silence)],
            input=text.encode("utf-8"), check=True,
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return {"input_text": text, "input_data": input_data,
                "original_audio": str(audio_path)}
