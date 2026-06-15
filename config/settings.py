"""Application constants and default accessibility preferences."""

from pathlib import Path

APP_TITLE = "Accessible Ebook Reader"
APP_DESCRIPTION = (
    "A free, web-based accessible ebook reader for visually impaired students. "
    "Upload XHTML, EPUB, or PDF files and listen with text-to-speech."
)

BASE_DIR = Path(__file__).resolve().parent.parent
ASSETS_DIR = BASE_DIR / "assets"
SAMPLE_BOOKS_DIR = ASSETS_DIR / "sample_books"
CSS_DIR = ASSETS_DIR / "css"

SUPPORTED_EXTENSIONS = {".xhtml", ".html", ".htm", ".epub", ".pdf"}

DEFAULT_THEME = "default_light"
DEFAULT_FONT_SIZE = 18
DEFAULT_SPEECH_SPEED = 1.0
MIN_FONT_SIZE = 12
MAX_FONT_SIZE = 36
MIN_SPEECH_SPEED = 0.5
MAX_SPEECH_SPEED = 2.0

THEMES = ("default_light", "dark_mode", "high_contrast", "sepia")

TTS_LANGUAGE = "en"
TTS_TLD = "com"
TTS_CHUNK_MAX_CHARS = 500

READING_MODES = ("sentence", "paragraph", "word")

# gTTS language codes with display labels (Indian languages highlighted)
TTS_LANGUAGES: dict[str, str] = {
    "en": "English",
    "hi": "Hindi",
    "mr": "Marathi",
    "bn": "Bengali",
    "ta": "Tamil",
    "te": "Telugu",
    "gu": "Gujarati",
    "kn": "Kannada",
    "ml": "Malayalam",
    "pa": "Punjabi",
    "ur": "Urdu",
}

# gTTS top-level domain accents (voice variants)
TTS_VOICES: dict[str, str] = {
    "com": "English (US)",
    "co.uk": "English (UK)",
    "com.au": "English (Australia)",
    "co.in": "English (India) / Indian languages",
    "ca": "English (Canada)",
}

PERSISTED_PREFS = (
    "theme",
    "font_size",
    "speech_speed",
    "tts_language",
    "tts_tld",
    "use_dyslexic_font",
    "reading_mode",
)
