"""Text-to-speech engine using gTTS with optional speed adjustment."""

from __future__ import annotations

import base64
import io
import re
from dataclasses import dataclass

from gtts import gTTS

from config.settings import TTS_CHUNK_MAX_CHARS, TTS_LANGUAGE

SENTENCE_SPLIT = re.compile(r"(?<=[.!?])\s+")


@dataclass
class AudioChunk:
    index: int
    text: str
    audio_bytes: bytes
    mime_type: str = "audio/mpeg"


def split_raw_sentences(text: str) -> list[str]:
    """Split text into individual sentences without chunk merging."""
    text = text.strip()
    if not text:
        return []
    parts = SENTENCE_SPLIT.split(text)
    return [p.strip() for p in parts if p.strip()] or [text]


def split_into_sentences(text: str) -> list[str]:
    """Split text into sentence-level chunks for responsive playback."""
    sentences = split_raw_sentences(text)
    if not sentences:
        return []
    chunks: list[str] = []
    buffer = ""
    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue
        if len(buffer) + len(sentence) + 1 <= TTS_CHUNK_MAX_CHARS:
            buffer = f"{buffer} {sentence}".strip()
        else:
            if buffer:
                chunks.append(buffer)
            buffer = sentence
    if buffer:
        chunks.append(buffer)
    return chunks if chunks else [text]


def generate_speech(
    text: str,
    language: str = TTS_LANGUAGE,
    slow: bool = False,
) -> bytes:
    """Generate MP3 audio bytes from text using gTTS."""
    if not text.strip():
        return b""
    tts = gTTS(text=text, lang=language, slow=slow)
    buffer = io.BytesIO()
    tts.write_to_fp(buffer)
    return buffer.getvalue()


def adjust_speed(audio_bytes: bytes, speed: float) -> bytes:
    """
    Adjust playback speed using pydub.
    Speed 1.0 = normal, 0.5 = slower, 2.0 = faster.
    """
    if not audio_bytes or speed == 1.0:
        return audio_bytes
    try:
        from pydub import AudioSegment
    except ImportError:
        return audio_bytes

    try:
        segment = AudioSegment.from_mp3(io.BytesIO(audio_bytes))
    except (OSError, FileNotFoundError):
        return audio_bytes
    if speed <= 0:
        return audio_bytes

    # Change frame rate to adjust speed (simpler than time-stretch)
    adjusted = segment._spawn(
        segment.raw_data,
        overrides={"frame_rate": int(segment.frame_rate * speed)},
    )
    adjusted = adjusted.set_frame_rate(segment.frame_rate)
    out = io.BytesIO()
    adjusted.export(out, format="mp3")
    return out.getvalue()


def generate_chunks(
    text: str,
    language: str = TTS_LANGUAGE,
    speed: float = 1.0,
) -> list[AudioChunk]:
    """Generate audio chunks for each sentence group."""
    sentences = split_into_sentences(text)
    slow = speed < 0.85
    effective_speed = speed if not slow else 1.0
    chunks: list[AudioChunk] = []
    for index, sentence in enumerate(sentences):
        audio = generate_speech(sentence, language=language, slow=slow)
        if effective_speed != 1.0:
            audio = adjust_speed(audio, effective_speed)
        if audio:
            chunks.append(AudioChunk(index=index, text=sentence, audio_bytes=audio))
    return chunks


def audio_to_base64(audio_bytes: bytes) -> str:
    """Encode audio bytes as base64 for HTML embedding."""
    return base64.b64encode(audio_bytes).decode("utf-8")


def audio_player_html(audio_bytes: bytes, autoplay: bool = True) -> str:
    """Return an HTML audio element with base64-encoded MP3."""
    if not audio_bytes:
        return ""
    b64 = audio_to_base64(audio_bytes)
    autoplay_attr = "autoplay" if autoplay else ""
    return (
        f'<audio id="tts-player" controls {autoplay_attr} '
        f'style="width:100%;" aria-label="Text-to-speech playback">'
        f'<source src="data:audio/mpeg;base64,{b64}" type="audio/mpeg">'
        f"Your browser does not support audio playback."
        f"</audio>"
    )
