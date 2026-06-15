"""Core reading experience with TTS, navigation, and content display."""

from __future__ import annotations

import streamlit as st

from utils.accessibility import (
    announce_message,
    inject_keyboard_shortcuts,
    inject_skip_link,
    render_content_html,
    render_sentences_html,
)
from utils.bookmarks import delete_bookmark, has_bookmark, restore_bookmark, save_bookmark
from utils.navigator import Navigator
from utils.parser import Book
from utils.theme import apply_theme, init_theme_state
from utils.tts_engine import audio_player_html, generate_speech

init_theme_state()
apply_theme()
inject_skip_link()
inject_keyboard_shortcuts()

READING_MODES = ("sentence", "paragraph")


def _init_reader_state() -> None:
    defaults = {
        "tts_playing": False,
        "tts_audio": None,
        "tts_cache_key": None,
        "reading_mode": "sentence",
        "current_book_name": None,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def _ensure_book_loaded() -> Book | None:
    if "current_book" not in st.session_state or st.session_state.current_book is None:
        st.warning("No book loaded. Please visit the **Library** page to select or upload a book.")
        if st.button("Go to Library", key="goto_library"):
            st.switch_page("pages/2_Library.py")
        return None
    return st.session_state.current_book


def _ensure_navigator(book: Book) -> Navigator:
    if "navigator" not in st.session_state or st.session_state.navigator is None:
        st.session_state.navigator = Navigator(book)
    return st.session_state.navigator


def _book_name() -> str:
    return st.session_state.get("current_book_name") or "unknown"


def _reset_tts() -> None:
    st.session_state.tts_playing = False
    st.session_state.tts_audio = None
    st.session_state.tts_cache_key = None


def _render_sidebar(nav: Navigator, book_name: str) -> None:
    with st.sidebar:
        st.header("Chapters")
        for i, title in enumerate(nav.chapter_titles()):
            is_current = i == nav.position.chapter_index
            label = f"{'▶ ' if is_current else ''}{i + 1}. {title}"
            if st.button(
                label,
                key=f"chapter_{i}",
                help=f"chapter-{i + 1}",
                use_container_width=True,
                type="primary" if is_current else "secondary",
            ):
                nav.go_to_chapter(i)
                _reset_tts()
                st.rerun()

        st.markdown("---")
        st.subheader("Headings")
        headings = nav.headings_in_chapter()
        if headings:
            for node_idx, heading in headings:
                indent = "  " * max(0, heading.level - 1)
                is_active = node_idx == nav.position.node_index
                prefix = "▸ " if is_active else ""
                if st.button(
                    f"{prefix}{indent}{heading.text}",
                    key=f"heading_{nav.position.chapter_index}_{node_idx}",
                    use_container_width=True,
                ):
                    nav.go_to_node(nav.position.chapter_index, node_idx)
                    _reset_tts()
                    st.rerun()
        else:
            st.caption("No headings in this chapter.")

        st.markdown("---")
        st.markdown(
            f'<p class="reader-progress-label">{nav.progress_label()}</p>',
            unsafe_allow_html=True,
        )
        st.progress(nav.progress_in_book(), text="Book progress")
        st.progress(nav.progress_in_chapter(), text="Chapter progress")

        st.markdown("---")
        st.subheader("Bookmark")
        if has_bookmark(book_name):
            from utils.bookmarks import get_bookmark
            bookmark = get_bookmark(book_name)
            if bookmark:
                st.caption(f"Saved: {bookmark.chapter_title}")
                st.caption(f'"{bookmark.node_preview}"')
            if st.button("Resume bookmark", key="resume_bookmark", use_container_width=True):
                if restore_bookmark(nav, book_name):
                    _reset_tts()
                    announce_message("Resumed from bookmark.")
                    st.rerun()
            if st.button("Delete bookmark", key="delete_bookmark", use_container_width=True):
                delete_bookmark(book_name)
                st.rerun()
        else:
            st.caption("No bookmark saved for this book.")
        if st.button("Save bookmark", key="save_bookmark", use_container_width=True):
            save_bookmark(nav, book_name)
            announce_message("Bookmark saved.")
            st.rerun()


def _shortcut_button(label: str, action_key: str, help_id: str) -> bool:
    return st.button(label, key=action_key, help=help_id, use_container_width=True)


def _handle_shortcuts(nav: Navigator) -> None:
    """Compact shortcut-trigger buttons (also activated via keyboard)."""
    cols = st.columns(10)
    shortcuts = [
        ("▶️", "sc_play", "btn-play-pause"),
        ("⏹️", "sc_stop", "btn-stop"),
        ("⬅️", "sc_prev", "btn-prev"),
        ("➡️", "sc_next", "btn-next"),
        ("⬆️H", "sc_prev_h", "btn-prev-heading"),
        ("H⬇️", "sc_next_h", "btn-next-heading"),
        ("A-", "sc_font_dec", "btn-font-decrease"),
        ("A+", "sc_font_inc", "btn-font-increase"),
        ("🔖", "sc_bookmark", "btn-bookmark"),
        ("T", "sc_theme", "btn-cycle-theme"),
    ]
    for col, (label, key, help_id) in zip(cols, shortcuts):
        with col:
            if _shortcut_button(label, key, help_id):
                _execute_shortcut(key, nav)


def _execute_shortcut(action_key: str, nav: Navigator) -> None:
    if action_key == "sc_play":
        st.session_state.tts_playing = not st.session_state.get("tts_playing", False)
    elif action_key == "sc_stop":
        _reset_tts()
    elif action_key == "sc_prev":
        if st.session_state.reading_mode == "sentence":
            nav.previous_sentence()
        else:
            nav.previous_node()
        _reset_tts()
        st.rerun()
    elif action_key == "sc_next":
        if st.session_state.reading_mode == "sentence":
            nav.next_sentence()
        else:
            nav.next_node()
        _reset_tts()
        st.rerun()
    elif action_key == "sc_prev_h":
        nav.previous_heading()
        _reset_tts()
        st.rerun()
    elif action_key == "sc_next_h":
        nav.next_heading()
        _reset_tts()
        st.rerun()
    elif action_key == "sc_font_dec":
        st.session_state.font_size = max(12, st.session_state.font_size - 2)
        st.rerun()
    elif action_key == "sc_font_inc":
        st.session_state.font_size = min(36, st.session_state.font_size + 2)
        st.rerun()
    elif action_key == "sc_bookmark":
        save_bookmark(nav, _book_name())
        announce_message("Bookmark saved.")
    elif action_key == "sc_theme":
        from utils.theme import cycle_theme
        st.session_state.theme = cycle_theme(st.session_state.theme)
        st.rerun()


def _get_tts_text(nav: Navigator) -> str:
    if st.session_state.reading_mode == "sentence":
        return nav.current_sentence
    return nav.current_text


def main() -> None:
    _init_reader_state()
    st.title("📖 Reader")

    book = _ensure_book_loaded()
    if book is None:
        return

    nav = _ensure_navigator(book)
    book_name = _book_name()
    _render_sidebar(nav, book_name)

    chapter = nav.current_chapter
    node = nav.current_node

    if not chapter or not node:
        st.error("This book has no readable content.")
        return

    st.subheader(book.title)
    st.caption(f"Chapter: {chapter.title}")

    mode_col, info_col = st.columns([2, 3])
    with mode_col:
        reading_mode = st.radio(
            "Reading mode",
            options=READING_MODES,
            format_func=lambda m: "Sentence-by-sentence" if m == "sentence" else "Paragraph-by-paragraph",
            index=READING_MODES.index(st.session_state.reading_mode),
            horizontal=True,
            key="reading_mode_radio",
        )
        st.session_state.reading_mode = reading_mode
    with info_col:
        sentences = nav.current_sentences
        if reading_mode == "sentence" and sentences:
            st.caption(
                f"Sentence {nav.position.sentence_index + 1} of {len(sentences)}"
            )

    ctrl1, ctrl2, ctrl3, ctrl4 = st.columns([1, 1, 1, 2])
    with ctrl1:
        if st.button("▶️ Play", key="play_btn", help="btn-play-pause", use_container_width=True):
            st.session_state.tts_playing = True
    with ctrl2:
        if st.button("⏸️ Pause", key="pause_btn", use_container_width=True):
            st.session_state.tts_playing = False
    with ctrl3:
        if st.button("⏹️ Stop", key="stop_btn", help="btn-stop", use_container_width=True):
            _reset_tts()
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

    nav1, nav2, nav3, nav4, nav5 = st.columns(5)
    with nav1:
        if st.button("⬅️ Previous", key="prev_btn", help="btn-prev", use_container_width=True):
            if reading_mode == "sentence":
                nav.previous_sentence()
            else:
                nav.previous_node()
            _reset_tts()
            st.rerun()
    with nav2:
        if st.button("➡️ Next", key="next_btn", help="btn-next", use_container_width=True):
            if reading_mode == "sentence":
                nav.next_sentence()
            else:
                nav.next_node()
            _reset_tts()
            st.rerun()
    with nav3:
        if st.button("⬆️ Prev Heading", key="prev_h_btn", help="btn-prev-heading", use_container_width=True):
            nav.previous_heading()
            _reset_tts()
            st.rerun()
    with nav4:
        if st.button("⬇️ Next Heading", key="next_h_btn", help="btn-next-heading", use_container_width=True):
            nav.next_heading()
            _reset_tts()
            st.rerun()
    with nav5:
        if st.button("⏭️ Next Sentence", key="next_sent_btn", use_container_width=True):
            nav.next_sentence()
            _reset_tts()
            st.rerun()

    _handle_shortcuts(nav)

    st.markdown('<div id="reader-main-content"></div>', unsafe_allow_html=True)

    if reading_mode == "sentence" and sentences:
        st.markdown(
            render_sentences_html(sentences, nav.position.sentence_index, node.type),
            unsafe_allow_html=True,
        )
    else:
        highlighted = st.session_state.get("tts_playing", False)
        st.markdown(
            render_content_html(node.html, highlighted=highlighted),
            unsafe_allow_html=True,
        )

    tts_text = _get_tts_text(nav)
    if st.session_state.get("tts_playing", False) and tts_text:
        cache_key = (
            f"tts_{nav.position.chapter_index}_{nav.position.node_index}_"
            f"{nav.position.sentence_index}_{reading_mode}"
        )
        if st.session_state.get("tts_cache_key") != cache_key:
            with st.spinner("Generating speech..."):
                from utils.tts_engine import adjust_speed
                audio = generate_speech(tts_text, slow=st.session_state.speech_speed < 0.85)
                speed = st.session_state.get("speech_speed", 1.0)
                if speed != 1.0 and speed >= 0.85:
                    audio = adjust_speed(audio, speed)
                if audio:
                    st.session_state.tts_audio = audio
                    st.session_state.tts_cache_key = cache_key
                    announce_message(f"Reading: {tts_text[:100]}")
                else:
                    st.session_state.tts_playing = False
                    st.warning("Could not generate speech for this content.")

        audio = st.session_state.get("tts_audio")
        if audio:
            st.audio(audio, format="audio/mp3")
            st.markdown(audio_player_html(audio, autoplay=True), unsafe_allow_html=True)


if __name__ == "__main__":
    main()
