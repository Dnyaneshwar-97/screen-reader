"""Accessibility helpers: skip links, ARIA, and keyboard shortcut injection."""

from __future__ import annotations

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
    Uses Streamlit custom events to trigger button clicks.
    """
    st.markdown(
        """
        <script>
        (function() {
            if (window.__readerShortcutsInstalled) return;
            window.__readerShortcutsInstalled = true;

            const SHORTCUTS = {
                ' ': 'btn-play-pause',
                'Escape': 'btn-stop',
                'ArrowRight': 'btn-next',
                'ArrowLeft': 'btn-prev',
                'h': 'btn-next-heading',
                'H': 'btn-prev-heading',
                '+': 'btn-font-increase',
                '=': 'btn-font-increase',
                '-': 'btn-font-decrease',
                't': 'btn-cycle-theme',
                'T': 'btn-cycle-theme',
            };

            document.addEventListener('keydown', function(e) {
                if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA'
                    || e.target.isContentEditable) return;

                const btnId = SHORTCUTS[e.key];
                if (!btnId) {
                    if (e.key >= '1' && e.key <= '9') {
                        const chapterBtn = document.querySelector(
                            '[data-testid="stSidebar"] button[data-chapter="' + e.key + '"]'
                        );
                        if (chapterBtn) { e.preventDefault(); chapterBtn.click(); }
                    }
                    return;
                }

                const btn = document.getElementById(btnId)
                    || document.querySelector('[data-shortcut="' + e.key + '"]');
                if (btn) {
                    e.preventDefault();
                    btn.click();
                }
            });
        })();
        </script>
        """,
        unsafe_allow_html=True,
    )


def render_content_html(html: str, highlighted: bool = False) -> str:
    """Wrap content HTML with accessibility attributes."""
    css_class = "reader-content"
    if highlighted:
        css_class += " reader-highlight"
    return f'<div class="{css_class}" role="article" aria-live="polite">{html}</div>'


def announce_message(message: str) -> None:
    """Render an aria-live region for screen reader announcements."""
    st.markdown(
        f'<div role="status" aria-live="assertive" aria-atomic="true" '
        f'style="position:absolute;left:-9999px;">{message}</div>',
        unsafe_allow_html=True,
    )
