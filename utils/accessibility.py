"""Accessibility helpers: skip links, ARIA, and keyboard shortcut injection."""

from __future__ import annotations

import html

import streamlit as st


def inject_skip_link() -> None:
    """Inject a skip-to-content link for keyboard users."""
    st.markdown(
        '<a href="#reader-main-content" class="skip-link">Skip to content</a>',
        unsafe_allow_html=True,
    )


def inject_keyboard_shortcuts() -> None:
    """
    Inject JavaScript for keyboard shortcuts.
    Buttons use data-shortcut attributes for reliable triggering.
    """
    st.markdown(
        """
        <script>
        (function() {
            if (window.__readerShortcutsInstalled) return;
            window.__readerShortcutsInstalled = true;

            document.addEventListener('keydown', function(e) {
                if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA'
                    || e.target.isContentEditable) return;

                const SHORTCUTS = {
                    ' ': 'btn-play-pause',
                    'Escape': 'btn-stop',
                    'ArrowRight': 'btn-next',
                    'ArrowLeft': 'btn-prev',
                    'h': 'btn-next-heading',
                    't': 'btn-cycle-theme',
                    'T': 'btn-cycle-theme',
                    '+': 'btn-font-increase',
                    '=': 'btn-font-increase',
                    '-': 'btn-font-decrease',
                    'b': 'btn-bookmark',
                    'B': 'btn-bookmark',
                };

                let helpId = SHORTCUTS[e.key];
                if (e.shiftKey && e.key === 'H') helpId = 'btn-prev-heading';

                if (helpId) {
                    const btn = [...document.querySelectorAll('button')]
                        .find(b => b.getAttribute('title') === helpId);
                    if (btn) { e.preventDefault(); btn.click(); return; }
                }

                if (e.key >= '1' && e.key <= '9') {
                    const chapterBtn = [...document.querySelectorAll('button')]
                        .find(b => b.getAttribute('title') === 'chapter-' + e.key);
                    if (chapterBtn) { e.preventDefault(); chapterBtn.click(); }
                }
            });
        })();
        </script>
        """,
        unsafe_allow_html=True,
    )


def render_sentences_html(
    sentences: list[str],
    active_index: int,
    node_type: str = "paragraph",
) -> str:
    """Render sentences with the active sentence highlighted for TTS sync."""
    if not sentences:
        return '<p class="reader-empty">No content.</p>'

    parts: list[str] = []
    for i, sentence in enumerate(sentences):
        escaped = html.escape(sentence)
        if i == active_index:
            parts.append(
                f'<span class="reader-sentence-highlight" aria-current="true">'
                f"{escaped}</span>"
            )
        else:
            parts.append(f"<span>{escaped}</span>")

    tag = "h2" if node_type == "heading" else "p"
    inner = " ".join(parts)
    return f'<div class="reader-content reader-content-main" role="article" aria-live="polite"><{tag}>{inner}</{tag}></div>'


def render_content_html(html_content: str, highlighted: bool = False) -> str:
    """Wrap content HTML with accessibility attributes."""
    css_class = "reader-content reader-content-main"
    if highlighted:
        css_class += " reader-highlight"
    return (
        f'<div class="{css_class}" role="article" aria-live="polite">'
        f"{html_content}</div>"
    )


def render_words_html(words: list[str], active_index: int) -> str:
    """Render words with the active word highlighted for learning mode."""
    if not words:
        return '<p class="reader-empty">No content.</p>'
    parts: list[str] = []
    for i, word in enumerate(words):
        escaped = html.escape(word)
        if i == active_index:
            parts.append(
                f'<span class="reader-word-highlight" aria-current="true">{escaped}</span>'
            )
        else:
            parts.append(f"<span>{escaped}</span>")
    inner = " ".join(parts)
    return f'<div class="reader-content reader-content-main" role="article" aria-live="polite"><p>{inner}</p></div>'


def render_image_html(alt_text: str, src_hint: str = "") -> str:
    """Render image placeholder with alt text for screen readers."""
    safe_alt = html.escape(alt_text or "Image with no description")
    caption = html.escape(src_hint) if src_hint else ""
    extra = f"<small>{caption}</small>" if caption else ""
    return (
        f'<figure class="reader-image" role="img" aria-label="{safe_alt}">'
        f'<div class="reader-image-placeholder" aria-hidden="true">🖼️</div>'
        f'<figcaption><strong>Image:</strong> {safe_alt}</figcaption>'
        f"{extra}</figure>"
    )


def inject_reader_layout_css() -> None:
    """Compact toolbar and maximize content reading area."""
    st.markdown(
        """
        <style>
        /* Hide auto-advance and keyboard-only helper buttons */
        button[title="btn-auto-advance"],
        button[title="btn-next-heading"],
        button[title="btn-prev-heading"],
        button[title="btn-font-increase"],
        button[title="btn-font-decrease"],
        button[title="btn-cycle-theme"],
        div[data-testid="stAudio"] { display: none !important; }

        .reader-content-main {
            min-height: 65vh;
            max-width: 100% !important;
            width: 100%;
            padding: 2rem 2.5rem !important;
            margin: 0 !important;
            box-sizing: border-box;
        }

        .reader-page-header {
            font-size: 0.95rem;
            color: var(--reader-text);
            opacity: 0.85;
            margin-bottom: 0.25rem;
        }

        /* Compact toolbar buttons */
        div[data-testid="column"] .stButton > button {
            padding: 0.2rem 0.4rem !important;
            min-height: 2rem !important;
            font-size: 0.85rem !important;
        }

        .reader-toolbar-marker + div[data-testid="stVerticalBlock"] {
            padding: 0.25rem 0 !important;
        }

        #tts-player {
            position: absolute !important;
            left: -9999px !important;
            width: 1px !important;
            height: 1px !important;
        }

        [data-testid="stExpander"] details summary {
            padding: 0.35rem 0.5rem !important;
            font-size: 0.9rem !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def announce_message(message: str) -> None:
    """Render an aria-live region for screen reader announcements."""
    safe = html.escape(message)
    st.markdown(
        f'<div role="status" aria-live="assertive" aria-atomic="true" '
        f'style="position:absolute;left:-9999px;">{safe}</div>',
        unsafe_allow_html=True,
    )
