"""Mandarin narration with Kokoro, using misaki's Chinese G2P for correct tones.

Voice: CSVIDEO_ZH_VOICE (default zf_xiaobei; also zf_xiaoxiao, zm_yunjian, zm_yunxi ...).
Speed: CSVIDEO_SPEED (default 1.0). Text may be traditional; it is converted to
simplified for pronunciation only.
"""
from __future__ import annotations

import os
from pathlib import Path

from manim_voiceover.services.base import SpeechService, initialize_speech_service

from . import lang

CS_VOICES = Path(__file__).resolve().parents[2] / "cs-video" / "voices"


class KokoroZhService(SpeechService):
    _engine = None
    _g2p = None

    def __init__(self, voice: str | None = None, speed: float | None = None, **kwargs):
        self.voice = voice or os.environ.get("CSVIDEO_ZH_VOICE", "zf_xiaobei")
        self.speed = float(speed or os.environ.get("CSVIDEO_SPEED", 1.0))
        initialize_speech_service(self, kwargs)

    @classmethod
    def _load(cls):
        if cls._engine is None:
            from kokoro_onnx import Kokoro
            from misaki import zh
            cls._engine = Kokoro(str(CS_VOICES / "kokoro-v1.0.onnx"),
                                 str(CS_VOICES / "voices-v1.0.bin"))
            cls._g2p = zh.ZHG2P()
        return cls._engine, cls._g2p

    def generate_from_text(self, text, cache_dir=None, path=None, **kwargs):
        import soundfile as sf
        cache_dir = cache_dir or self.cache_dir
        input_data = {"input_text": text, "service": "kokoro-zh", "voice": self.voice,
                      "speed": self.speed}
        cached = self.get_cached_result(input_data, cache_dir)
        if cached is not None:
            return cached
        engine, g2p = self._load()
        r = g2p(lang.to_simplified(text))
        phonemes = r[0] if isinstance(r, tuple) else r
        audio, sr = engine.create(phonemes, voice=self.voice, speed=self.speed, is_phonemes=True)
        audio_path = path or (self.get_audio_basename(input_data) + ".wav")
        sf.write(str(Path(cache_dir) / audio_path), audio, sr)
        return {"input_text": text, "input_data": input_data, "original_audio": str(audio_path)}
