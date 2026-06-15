"""High-contrast themes and font sizing for accessibility."""

from __future__ import annotations

import streamlit as st

from config.settings import DEFAULT_FONT_SIZE, DEFAULT_THEME, THEMES

THEME_STYLES: dict[str, dict[str, str]] = {
    "default_light": {
        "background": "#ffffff",
        "text": "#1a1a1a",
        "accent": "#4a90d9",
        "secondary_bg": "#f0f2f6",
        "highlight": "#fff3cd",
    },
    "dark_mode": {
        "background": "#1a1a2e",
        "text": "#eeeeee",
        "accent": "#6cb4ee",
        "secondary_bg": "#16213e",
        "highlight": "#2d4a6f",
    },
    "high_contrast": {
        "background": "#000000",
        "text": "#ffff00",
        "accent": "#ffffff",
        "secondary_bg": "#1a1a1a",
        "highlight": "#333300",
    },
    "sepia": {
        "background": "#f4ecd8",
        "text": "#3e2723",
        "accent": "#8d6e63",
        "secondary_bg": "#e8dcc8",
        "highlight": "#fff8e1",
    },
}

THEME_LABELS = {
    "default_light": "Default Light",
    "dark_mode": "Dark Mode",
    "high_contrast": "High Contrast",
    "sepia": "Sepia",
}


def get_theme_css(theme_name: str, font_size: int, use_dyslexic_font: bool = False) -> str:
    """Generate CSS for the selected theme and font size."""
    theme = THEME_STYLES.get(theme_name, THEME_STYLES[DEFAULT_THEME])
    font_family = (
        "'OpenDyslexic', 'Comic Sans MS', sans-serif"
        if use_dyslexic_font
        else "system-ui, -apple-system, 'Segoe UI', Roboto, sans-serif"
    )
    return f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Atkinson+Hyperlegible&display=swap');

    :root {{
        --reader-bg: {theme["background"]};
        --reader-text: {theme["text"]};
        --reader-accent: {theme["accent"]};
        --reader-secondary: {theme["secondary_bg"]};
        --reader-highlight: {theme["highlight"]};
        --reader-font-size: {font_size}px;
    }}

    .stApp {{
        background-color: var(--reader-bg) !important;
        color: var(--reader-text) !important;
    }}

    .stApp [data-testid="stSidebar"] {{
        background-color: var(--reader-secondary) !important;
    }}

    .reader-content {{
        font-family: {font_family};
        font-size: var(--reader-font-size) !important;
        line-height: 1.8;
        color: var(--reader-text);
        background-color: var(--reader-bg);
        padding: 1.5rem;
        border-radius: 8px;
        max-width: 800px;
        margin: 0 auto;
    }}

    .reader-content h1, .reader-content h2, .reader-content h3,
    .reader-content h4, .reader-content h5, .reader-content h6 {{
        color: var(--reader-accent);
        margin-top: 1.5em;
        margin-bottom: 0.5em;
        font-weight: 700;
    }}

    .reader-content p {{
        margin-bottom: 1em;
    }}

    .reader-highlight {{
        background-color: var(--reader-highlight) !important;
        padding: 2px 4px;
        border-radius: 3px;
        outline: 2px solid var(--reader-accent);
    }}

    .skip-link {{
        position: absolute;
        top: -40px;
        left: 0;
        background: var(--reader-accent);
        color: var(--reader-bg);
        padding: 8px 16px;
        z-index: 10000;
        text-decoration: none;
        font-weight: bold;
    }}

    .skip-link:focus {{
        top: 0;
    }}

    button:focus, a:focus, input:focus, select:focus, textarea:focus,
    [tabindex]:focus {{
        outline: 3px solid var(--reader-accent) !important;
        outline-offset: 2px !important;
    }}

    .stProgress > div > div {{
        background-color: var(--reader-accent) !important;
    }}
    </style>
    """


def apply_theme(theme_name: str | None = None, font_size: int | None = None) -> None:
    """Apply theme CSS to the current Streamlit page."""
    theme = theme_name or st.session_state.get("theme", DEFAULT_THEME)
    size = font_size or st.session_state.get("font_size", DEFAULT_FONT_SIZE)
    dyslexic = st.session_state.get("use_dyslexic_font", False)
    st.markdown(get_theme_css(theme, size, dyslexic), unsafe_allow_html=True)


def cycle_theme(current: str) -> str:
    """Return the next theme in the rotation."""
    try:
        idx = THEMES.index(current)
        return THEMES[(idx + 1) % len(THEMES)]
    except ValueError:
        return DEFAULT_THEME


def init_theme_state() -> None:
    """Initialize theme-related session state defaults."""
    defaults = {
        "theme": DEFAULT_THEME,
        "font_size": DEFAULT_FONT_SIZE,
        "use_dyslexic_font": False,
        "speech_speed": 1.0,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value
