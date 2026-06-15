"""Core reading experience with TTS, navigation, and content display."""

from __future__ import annotations

import streamlit as st

from utils.accessibility import (
    announce_message,
    inject_keyboard_shortcuts,
    inject_skip_link,
    render_content_html,
)
from utils.navigator import Navigator
from utils.parser import Book
from utils.theme import apply_theme, cycle_theme, init_theme_state
from utils.tts_engine import audio_player_html, generate_chunks

init_theme_state()
apply_theme()
inject_skip_link()
inject_keyboard_shortcuts()


def _ensure_book_loaded() -> Book | None:
    if "current_book" not in st.session_state or st.session_state.current_book is None:
        st.warning("No book loaded. Please visit the **Library** page to select or upload a book.")
        if st.button("Go to Library"):
            st.switch_page("pages/2_Library.py")
        return None
    return st.session_state.current_book


def _ensure_navigator(book: Book) -> Navigator:
    if "navigator" not in st.session_state or st.session_state.navigator is None:
        st.session_state.navigator = Navigator(book)
    return st.session_state.navigator


def _render_sidebar(nav: Navigator) -> None:
    with st.sidebar:
        st.header("Chapters")
        for i, title in enumerate(nav.chapter_titles()):
            is_current = i == nav.position.chapter_index
            label = f"{'▶ ' if is_current else ''}{i + 1}. {title}"
            if st.button(
                label,
                key=f"chapter_{i}",
                use_container_width=True,
                type="primary" if is_current else "secondary",
            ):
                nav.go_to_chapter(i)
                st.session_state.tts_playing = False
                st.rerun()

        st.markdown("---")
        st.progress(nav.progress_in_book(), text="Book progress")
        st.progress(nav.progress_in_chapter(), text="Chapter progress")


def _handle_shortcut_buttons(nav: Navigator) -> None:
    """Hidden buttons triggered by keyboard shortcuts."""
    cols = st.columns(8)
    actions = [
        ("btn-play-pause", "▶️", "play_pause"),
        ("btn-stop", "⏹️", "stop"),
        ("btn-prev", "⬅️", "prev"),
        ("btn-next", "➡️", "next"),
        ("btn-prev-heading", "⬆️H", "prev_heading"),
        ("btn-next-heading", "H⬇️", "next_heading"),
        ("btn-font-decrease", "A-", "font_dec"),
        ("btn-font-increase", "A+", "font_inc"),
    ]
    for col, (btn_id, label, action) in zip(cols, actions):
        with col:
            if st.button(label, key=action, help=btn_id):
                _execute_action(action, nav)


def _execute_action(action: str, nav: Navigator) -> None:
    if action == "play_pause":
        st.session_state.tts_playing = not st.session_state.get("tts_playing", False)
    elif action == "stop":
        st.session_state.tts_playing = False
        st.session_state.tts_audio = None
    elif action == "prev":
        nav.previous_node()
        st.session_state.tts_playing = False
    elif action == "next":
        nav.next_node()
        st.session_state.tts_playing = False
    elif action == "prev_heading":
        nav.previous_heading()
        st.session_state.tts_playing = False
    elif action == "next_heading":
        nav.next_heading()
        st.session_state.tts_playing = False
    elif action == "font_dec":
        st.session_state.font_size = max(12, st.session_state.font_size - 2)
    elif action == "font_inc":
        st.session_state.font_size = min(36, st.session_state.font_size + 2)


def main() -> None:
    st.title("📖 Reader")

    book = _ensure_book_loaded()
    if book is None:
        return

    nav = _ensure_navigator(book)
    _render_sidebar(nav)

    chapter = nav.current_chapter
    node = nav.current_node

    if not chapter or not node:
        st.error("This book has no readable content.")
        return

    st.subheader(book.title)
    st.caption(f"Chapter: {chapter.title}")

    # TTS controls
    ctrl1, ctrl2, ctrl3, ctrl4 = st.columns([1, 1, 1, 2])
    with ctrl1:
        if st.button("▶️ Play", key="play_btn", use_container_width=True):
            st.session_state.tts_playing = True
    with ctrl2:
        if st.button("⏸️ Pause", key="pause_btn", use_container_width=True):
            st.session_state.tts_playing = False
    with ctrl3:
        if st.button("⏹️ Stop", key="stop_btn", use_container_width=True):
            st.session_state.tts_playing = False
            st.session_state.tts_audio = None
    with ctrl4:
        speed = st.slider(
            "Speech speed",
            min_value=0.5,
            max_value=2.0,
            value=st.session_state.get("speech_speed", 1.0),
            step=0.1,
            key="reader_speed",
        )
        st.session_state.speech_speed = speed

    # Navigation buttons
    nav1, nav2, nav3, nav4 = st.columns(4)
    with nav1:
        if st.button("⬅️ Previous", use_container_width=True):
            nav.previous_node()
            st.session_state.tts_playing = False
            st.rerun()
    with nav2:
        if st.button("➡️ Next", use_container_width=True):
            nav.next_node()
            st.session_state.tts_playing = False
            st.rerun()
    with nav3:
        if st.button("⬆️ Prev Heading", use_container_width=True):
            nav.previous_heading()
            st.session_state.tts_playing = False
            st.rerun()
    with nav4:
        if st.button("⬇️ Next Heading", use_container_width=True):
            nav.next_heading()
            st.session_state.tts_playing = False
            st.rerun()

    _handle_shortcut_buttons(nav)

    # Content display
    st.markdown('<div id="reader-main-content"></div>', unsafe_allow_html=True)
    highlighted = st.session_state.get("tts_playing", False)
    st.markdown(
        render_content_html(node.html, highlighted=highlighted),
        unsafe_allow_html=True,
    )

    # TTS audio generation
    if st.session_state.get("tts_playing", False) and node.text:
        cache_key = f"tts_{nav.position.chapter_index}_{nav.position.node_index}"
        if st.session_state.get("tts_cache_key") != cache_key:
            with st.spinner("Generating speech..."):
                chunks = generate_chunks(
                    node.text,
                    speed=st.session_state.get("speech_speed", 1.0),
                )
                if chunks:
                    st.session_state.tts_audio = chunks[0].audio_bytes
                    st.session_state.tts_cache_key = cache_key
                    announce_message(f"Reading: {node.text[:100]}")
                else:
                    st.session_state.tts_playing = False
                    st.warning("Could not generate speech for this content.")

        audio = st.session_state.get("tts_audio")
        if audio:
            st.audio(audio, format="audio/mp3")
            st.markdown(
                audio_player_html(audio, autoplay=True),
                unsafe_allow_html=True,
            )


if __name__ == "__main__":
    main()
