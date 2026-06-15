"""Unit tests for URL preference persistence."""

from unittest.mock import MagicMock, patch

import pytest

from utils.preferences import _coerce_pref, init_preferences, load_preferences_from_url


class TestPreferences:
    def test_coerce_theme(self):
        assert _coerce_pref("theme", "dark_mode") == "dark_mode"
        assert _coerce_pref("theme", "invalid") is None

    def test_coerce_font_size(self):
        assert _coerce_pref("font_size", "24") == 24
        assert _coerce_pref("font_size", "99") == 36

    def test_coerce_language(self):
        assert _coerce_pref("tts_language", "hi") == "hi"
        assert _coerce_pref("tts_language", "xx") is None

    def test_coerce_reading_mode(self):
        assert _coerce_pref("reading_mode", "word") == "word"

    def test_load_from_url(self):
        session = {}
        mock_params = MagicMock()
        mock_params.__contains__ = lambda self, k: k in {"theme", "tts_language"}
        mock_params.__getitem__ = lambda self, k: {"theme": "sepia", "tts_language": "hi"}[k]

        with patch("utils.preferences.st") as mock_st:
            mock_st.session_state = session
            mock_st.query_params = mock_params
            load_preferences_from_url()
            assert session["theme"] == "sepia"
            assert session["tts_language"] == "hi"

    def test_init_preferences(self):
        session = {}
        mock_params = {}

        class Params(dict):
            def __contains__(self, key):
                return False

        with patch("utils.preferences.st") as mock_st:
            mock_st.session_state = session
            mock_st.query_params = Params()
            init_preferences()
            assert session["theme"] == "default_light"
            assert session["tts_language"] == "en"
