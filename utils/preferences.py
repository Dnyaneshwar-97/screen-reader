"""User preference persistence via URL query parameters."""

from __future__ import annotations

import streamlit as st

from config.settings import (
    DEFAULT_FONT_SIZE,
    DEFAULT_SPEECH_SPEED,
    DEFAULT_THEME,
    PERSISTED_PREFS,
    READING_MODES,
    THEMES,
    TTS_LANGUAGE,
    TTS_TLD,
    TTS_LANGUAGES,
    TTS_VOICES,
)


def _coerce_pref(key: str, value: str):
    if key == "theme" and value in THEMES:
        return value
    if key == "font_size":
        size = int(value)
        return max(12, min(36, size))
    if key == "speech_speed":
        speed = float(value)
        return max(0.5, min(2.0, speed))
    if key == "tts_language" and value in TTS_LANGUAGES:
        return value
    if key == "tts_tld" and value in TTS_VOICES:
        return value
    if key == "use_dyslexic_font":
        return value.lower() in {"1", "true", "yes"}
    if key == "reading_mode" and value in READING_MODES:
        return value
    return None


def load_preferences_from_url() -> None:
    """Hydrate session state from URL query parameters."""
    params = st.query_params
    for key in PERSISTED_PREFS:
        if key in params:
            coerced = _coerce_pref(key, params[key])
            if coerced is not None:
                st.session_state[key] = coerced


def save_preferences_to_url() -> None:
    """Persist current preferences to URL query parameters."""
    updates: dict[str, str] = {}
    for key in PERSISTED_PREFS:
        if key in st.session_state:
            value = st.session_state[key]
            if isinstance(value, bool):
                updates[key] = "true" if value else "false"
            else:
                updates[key] = str(value)
    if updates:
        st.query_params.from_dict(updates)


def init_preferences() -> None:
    """Initialize defaults then overlay URL preferences."""
    defaults = {
        "theme": DEFAULT_THEME,
        "font_size": DEFAULT_FONT_SIZE,
        "use_dyslexic_font": False,
        "speech_speed": DEFAULT_SPEECH_SPEED,
        "tts_language": TTS_LANGUAGE,
        "tts_tld": TTS_TLD,
        "reading_mode": "sentence",
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value
    load_preferences_from_url()
