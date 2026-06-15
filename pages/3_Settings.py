"""Accessibility preferences: themes, font size, and speech settings."""

import streamlit as st

from config.settings import (
    MAX_FONT_SIZE,
    MAX_SPEECH_SPEED,
    MIN_FONT_SIZE,
    MIN_SPEECH_SPEED,
    THEMES,
)
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
        "Use dyslexia-friendly font",
        value=st.session_state.get("use_dyslexic_font", False),
        help="Uses OpenDyslexic-style font for easier reading.",
    )
    st.session_state.use_dyslexic_font = use_dyslexic

    if st.button("Cycle Theme (T)"):
        st.session_state.theme = cycle_theme(st.session_state.theme)
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

    st.markdown("---")
    st.subheader("Theme Preview")

    apply_theme(st.session_state.theme, st.session_state.font_size)

    st.markdown(
        f"""
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
| `1-9` | Jump to chapter |
        """
    )


if __name__ == "__main__":
    main()
