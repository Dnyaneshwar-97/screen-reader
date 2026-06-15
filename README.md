# Accessible Ebook Reader

A free, web-based accessible ebook reader built with Python and Streamlit. Designed for visually impaired students to consume XHTML, EPUB, and PDF textbook content through text-to-speech, keyboard navigation, and high-contrast UI.

## Features

- **File upload** — XHTML, EPUB, and PDF support
- **Text-to-speech** — Google TTS with adjustable speed (0.5x–2.0x)
- **Chapter navigation** — Sidebar chapter list with progress tracking
- **High-contrast themes** — Default Light, Dark Mode, High Contrast, Sepia
- **Font size control** — 12px to 36px
- **Sentence highlighting** — Highlights the sentence currently being read aloud
- **Bookmarks** — Save and resume reading position per book
- **Reading modes** — Sentence-by-sentence or paragraph-by-paragraph
- **Heading navigation** — Sidebar heading list for quick jumps
- **OpenDyslexic font** — Dyslexia-friendly font toggle
- **Sample books** — Bundled demo content for instant testing
- **WCAG 2.1 AA** — Accessible UI with skip links, focus indicators, ARIA

## Quick Start

```bash
# Clone the repository
git clone https://github.com/your-username/screen-reader.git
cd screen-reader

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate   # Linux/Mac
# venv\Scripts\activate    # Windows

# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run app.py
```

Open http://localhost:8501 in your browser.

## Project Structure

```
├── app.py                  # Main entry point
├── pages/
│   ├── 1_Reader.py         # Reading experience
│   ├── 2_Library.py        # Browse/upload books
│   └── 3_Settings.py       # Accessibility preferences
├── utils/
│   ├── parser.py           # XHTML/EPUB/PDF parser
│   ├── tts_engine.py       # Text-to-speech engine
│   ├── navigator.py        # Content navigation
│   ├── theme.py            # High-contrast themes
│   └── accessibility.py    # Keyboard shortcuts, ARIA
├── assets/sample_books/      # Demo XHTML files
├── config/settings.py        # App constants
└── tests/                    # Unit tests
```

## Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `Space` | Play / Pause |
| `Escape` | Stop |
| `→` / `←` | Next / Previous section |
| `H` / `Shift+H` | Next / Previous heading |
| `+` / `-` | Font size up / down |
| `T` | Cycle theme |
| `1-9` | Jump to chapter |

## Deployment

### Streamlit Community Cloud (Recommended)

1. Push code to a public GitHub repository
2. Go to https://share.streamlit.io
3. Sign in with GitHub, select repo, branch, and `app.py`
4. Click Deploy

### HuggingFace Spaces

1. Create a new Space at https://huggingface.co/spaces
2. Select "Streamlit" as the SDK
3. Push code or link your GitHub repo

## Testing

```bash
pytest tests/ -v
```

## License

MIT License — see [LICENSE](LICENSE).
