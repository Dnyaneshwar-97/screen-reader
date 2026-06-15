"""Unit tests for TTS engine."""

from unittest.mock import MagicMock, patch

import pytest

from utils.tts_engine import (
    adjust_speed,
    audio_to_base64,
    export_text_as_mp3,
    generate_chunks,
    generate_speech,
    split_into_sentences,
    split_raw_sentences,
    split_raw_words,
)

FAKE_MP3 = b"\xff\xfb\x90\x00" + b"\x00" * 100


@pytest.fixture
def mock_gtts():
    with patch("utils.tts_engine.gTTS") as mock_cls:
        instance = MagicMock()
        instance.write_to_fp.side_effect = lambda fp: fp.write(FAKE_MP3)
        mock_cls.return_value = instance
        yield mock_cls


class TestSplitSentences:
    def test_single_sentence(self):
        result = split_into_sentences("Hello world.")
        assert result == ["Hello world."]

    def test_raw_sentences(self):
        result = split_raw_sentences("First sentence. Second sentence! Third?")
        assert len(result) == 3

    def test_raw_words(self):
        result = split_raw_words("The quick brown fox")
        assert result == ["The", "quick", "brown", "fox"]

    def test_multiple_sentences(self):
        result = split_into_sentences("First sentence. Second sentence! Third?")
        combined = " ".join(result)
        assert "First sentence." in combined
        assert "Second sentence!" in combined
        assert "Third?" in combined

    def test_empty_text(self):
        assert split_into_sentences("") == []
        assert split_into_sentences("   ") == []

    def test_long_text_chunked(self):
        long_text = "Word. " * 200
        chunks = split_into_sentences(long_text)
        for chunk in chunks:
            assert len(chunk) <= 500


class TestGenerateSpeech:
    def test_generates_audio_bytes(self, mock_gtts):
        audio = generate_speech("Hello, this is a test.")
        assert isinstance(audio, bytes)
        assert len(audio) > 0
        mock_gtts.assert_called_once()

    def test_empty_text_returns_empty(self):
        audio = generate_speech("")
        assert audio == b""


class TestAdjustSpeed:
    def test_no_change_at_1x(self, mock_gtts):
        audio = generate_speech("Speed test.")
        result = adjust_speed(audio, 1.0)
        assert result == audio

    def test_speed_up(self, mock_gtts):
        audio = generate_speech("Speed test.")
        result = adjust_speed(audio, 1.5)
        assert isinstance(result, bytes)
        assert len(result) > 0

class TestGenerateChunks:
    def test_generates_chunks(self, mock_gtts):
        chunks = generate_chunks("First sentence. Second sentence.")
        assert len(chunks) >= 1
        for chunk in chunks:
            assert chunk.text
            assert len(chunk.audio_bytes) > 0

    def test_chunk_indices(self, mock_gtts):
        chunks = generate_chunks("One. Two. Three.")
        indices = [c.index for c in chunks]
        assert indices == list(range(len(chunks)))


class TestExportAudio:
    def test_export_single_chunk(self, mock_gtts):
        audio = export_text_as_mp3("Hello world.")
        assert isinstance(audio, bytes)
        assert len(audio) > 0


class TestBase64:
    def test_audio_to_base64(self, mock_gtts):
        audio = generate_speech("Test.")
        b64 = audio_to_base64(audio)
        assert isinstance(b64, str)
        assert len(b64) > 0
