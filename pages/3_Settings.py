"""Accessibility preferences: themes, font size, speech, and language settings."""

import streamlit as st

from config.settings import (
    MAX_FONT_SIZE,
    MAX_SPEECH_SPEED,
    MIN_FONT_SIZE,
    MIN_SPEECH_SPEED,
    READING_MODES,
    THEMES,
    TTS_LANGUAGES,
    TTS_VOICES,
)
from utils.preferences import save_preferences_to_url
from utils.theme import THEME_LABELS, apply_theme, cycle_theme, init_theme_state

init_theme_state()
apply_theme()


def main() -> None:
    st.title("⚙️ Settings")

    st.subheader("Visual Preferences")

    theme = st.selectbox(
        "Theme",
        options=THEMES,
        index=THEMES.index(st.session_state.get("theme", "default_light")),
        format_func=lambda t: THEME_LABELS.get(t, t),
        help="Choose a high-contrast theme for better readability.",
    )
    st.session_state.theme = theme

    font_size = st.slider(
        "Font size",
        min_value=MIN_FONT_SIZE,
        max_value=MAX_FONT_SIZE,
        value=st.session_state.get("font_size", 18),
        step=2,
        help="Adjust text size from 12px to 36px.",
    )
    st.session_state.font_size = font_size

    use_dyslexic = st.checkbox(
        "Use dyslexia-friendly font (OpenDyslexic)",
        value=st.session_state.get("use_dyslexic_font", False),
        help="Uses OpenDyslexic font for easier reading.",
    )
    st.session_state.use_dyslexic_font = use_dyslexic

    if st.button("Cycle Theme (T)"):
        st.session_state.theme = cycle_theme(st.session_state.theme)
        save_preferences_to_url()
        st.rerun()

    st.markdown("---")
    st.subheader("Speech Preferences")

    speech_speed = st.slider(
        "Default speech speed",
        min_value=MIN_SPEECH_SPEED,
        max_value=MAX_SPEECH_SPEED,
        value=st.session_state.get("speech_speed", 1.0),
        step=0.1,
        help="Controls text-to-speech playback speed (0.5x to 2.0x).",
    )
    st.session_state.speech_speed = speech_speed

    language = st.selectbox(
        "TTS language",
        options=list(TTS_LANGUAGES.keys()),
        index=list(TTS_LANGUAGES.keys()).index(st.session_state.get("tts_language", "en")),
        format_func=lambda code: TTS_LANGUAGES[code],
        help="Select language for text-to-speech (Hindi, Marathi, and more).",
    )
    st.session_state.tts_language = language

    voice = st.selectbox(
        "Voice / accent",
        options=list(TTS_VOICES.keys()),
        index=list(TTS_VOICES.keys()).index(st.session_state.get("tts_tld", "com")),
        format_func=lambda tld: TTS_VOICES[tld],
        help="Choose voice accent variant. Use 'co.in' for Indian languages.",
    )
    st.session_state.tts_tld = voice

    reading_mode = st.selectbox(
        "Default reading mode",
        options=READING_MODES,
        index=READING_MODES.index(st.session_state.get("reading_mode", "sentence")),
        format_func=lambda m: {
            "sentence": "Sentence-by-sentence",
            "paragraph": "Paragraph-by-paragraph",
            "word": "Word-by-word (learning)",
        }.get(m, m),
    )
    st.session_state.reading_mode = reading_mode

    if st.button("Save preferences to URL", type="primary"):
        save_preferences_to_url()
        st.success("Preferences saved to URL. Bookmark this page to keep your settings.")

    st.markdown("---")
    st.subheader("Theme Preview")

    apply_theme(st.session_state.theme, st.session_state.font_size)

    st.markdown(
        """
        <div class="reader-content">
            <h2>Sample Heading</h2>
            <p>This is a preview of how text will appear with your current settings.
            The quick brown fox jumps over the lazy dog.</p>
            <p><strong>High contrast</strong> and <em>readable fonts</em> help
            visually impaired students consume educational content.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("---")
    st.subheader("Keyboard Shortcuts Reference")
    st.markdown(
        """
| Key | Action |
|-----|--------|
| `Space` | Play / Pause TTS |
| `Escape` | Stop TTS |
| `→` | Next section |
| `←` | Previous section |
| `H` | Next heading |
| `Shift+H` | Previous heading |
| `+` / `-` | Font size up / down |
| `T` | Cycle theme |
| `B` | Save bookmark |
| `1-9` | Jump to chapter |
        """
    )


if __name__ == "__main__":
    main()
