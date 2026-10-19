"""Mandarin narration for manim-voiceover.

Default engine: Kokoro **v1.1-zh** (Mandarin-trained, 100 Chinese voices) run through
sherpa-onnx, which brings its own Chinese lexicon and number/date rules.
Fallback: Kokoro v1.0 + misaki G2P (CSVIDEO_ZH_ENGINE=kokoro10).

Natural pacing: text is split at punctuation and each piece is synthesised on its own,
then joined with short silences (comma ~0.22 s, full stop ~0.45 s), which removes the
"one long breath" feel of TTS.

Env vars:
  CSVIDEO_ZH_ENGINE   sherpa (default) | kokoro10
  CSVIDEO_ZH_SPEAKER  sherpa speaker id (default 64 = zm_015, male); 3 = zf_001 ...
  CSVIDEO_ZH_SPEED    default 0.9 (10% slower than normal)
  CSVIDEO_ZH_VOICE    voice name for kokoro10 (default zf_xiaobei)
"""
from __future__ import annotations

import os
import re
from pathlib import Path

import numpy as np
from manim_voiceover.services.base import SpeechService, initialize_speech_service

from . import lang

VOICES = Path(__file__).resolve().parents[2] / "cs-video" / "voices"
SHERPA_DIR = VOICES / "kokoro-multi-lang-v1_1"

PAUSES = {"，": 0.22, "、": 0.18, "；": 0.3, "：": 0.28, "。": 0.45, "！": 0.45, "？": 0.5,
          "…": 0.4, "—": 0.25}
SPLIT = re.compile(r"([，、；：。！？…—])")
TTS_FIX = {"〇": "零", "「": "", "」": "", "『": "", "』": "", "（": "，", "）": "，"}


def pieces(text: str):
    """[(chunk, pause_after_seconds)] split at Chinese punctuation."""
    for a, b in TTS_FIX.items():
        text = text.replace(a, b)
    parts = SPLIT.split(text)
    out = []
    for i in range(0, len(parts), 2):
        chunk = parts[i].strip()
        punct = parts[i + 1] if i + 1 < len(parts) else ""
        if chunk:
            out.append((chunk + (punct if punct in "？！" else ""), PAUSES.get(punct, 0.0)))
        elif out and punct:
            out[-1] = (out[-1][0], max(out[-1][1], PAUSES.get(punct, 0.0)))
    return out


def make_zh_service() -> SpeechService:
    engine = os.environ.get("CSVIDEO_ZH_ENGINE", "sherpa")
    if engine == "sherpa" and SHERPA_DIR.exists():
        return SherpaZhService()
    return KokoroZhService()


class SherpaZhService(SpeechService):
    _tts = None

    def __init__(self, speaker: int | None = None, speed: float | None = None, **kwargs):
        self.speaker = int(speaker if speaker is not None else os.environ.get("CSVIDEO_ZH_SPEAKER", 64))
        self.speed = float(speed or os.environ.get("CSVIDEO_ZH_SPEED", 0.9))
        initialize_speech_service(self, kwargs)

    @classmethod
    def _load(cls):
        if cls._tts is None:
            import sherpa_onnx
            d = SHERPA_DIR
            cfg = sherpa_onnx.OfflineTtsConfig(
                model=sherpa_onnx.OfflineTtsModelConfig(
                    kokoro=sherpa_onnx.OfflineTtsKokoroModelConfig(
                        model=str(d / "model.onnx"), voices=str(d / "voices.bin"),
                        tokens=str(d / "tokens.txt"), data_dir=str(d / "espeak-ng-data"),
                        dict_dir=str(d / "dict"),
                        lexicon=f"{d / 'lexicon-us-en.txt'},{d / 'lexicon-zh.txt'}"),
                    num_threads=4),
                rule_fsts=f"{d / 'phone-zh.fst'},{d / 'date-zh.fst'},{d / 'number-zh.fst'}",
                max_num_sentences=1)
            cls._tts = sherpa_onnx.OfflineTts(cfg)
        return cls._tts

    def synth(self, text: str):
        tts = self._load()
        sr, chunks = 24000, []
        for chunk, pause in pieces(lang.to_simplified(text)):
            a = tts.generate(chunk, sid=self.speaker, speed=self.speed)
            sr = a.sample_rate
            chunks.append(np.asarray(a.samples, dtype=np.float32))
            if pause:
                chunks.append(np.zeros(int(sr * pause), dtype=np.float32))
        audio = np.concatenate(chunks) if chunks else np.zeros(sr // 2, dtype=np.float32)
        return audio, sr

    def generate_from_text(self, text, cache_dir=None, path=None, **kwargs):
        import soundfile as sf
        cache_dir = cache_dir or self.cache_dir
        input_data = {"input_text": text, "service": "sherpa-kokoro-1.1", "speaker": self.speaker,
                      "speed": self.speed, "pauses": 1}
        cached = self.get_cached_result(input_data, cache_dir)
        if cached is not None:
            return cached
        audio, sr = self.synth(text)
        audio_path = path or (self.get_audio_basename(input_data) + ".wav")
        sf.write(str(Path(cache_dir) / audio_path), audio, sr)
        return {"input_text": text, "input_data": input_data, "original_audio": str(audio_path)}


class KokoroZhService(SpeechService):
    """Fallback: Kokoro v1.0 with misaki's Chinese G2P."""
    _engine = None
    _g2p = None

    def __init__(self, voice: str | None = None, speed: float | None = None, **kwargs):
        self.voice = voice or os.environ.get("CSVIDEO_ZH_VOICE", "zf_xiaobei")
        self.speed = float(speed or os.environ.get("CSVIDEO_ZH_SPEED", 1.0))
        initialize_speech_service(self, kwargs)

    @classmethod
    def _load(cls):
        if cls._engine is None:
            from kokoro_onnx import Kokoro
            from misaki import zh
            cls._engine = Kokoro(str(VOICES / "kokoro-v1.0.onnx"), str(VOICES / "voices-v1.0.bin"))
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
