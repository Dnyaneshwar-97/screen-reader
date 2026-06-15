"""Core reading experience with TTS, navigation, and content display."""

from __future__ import annotations

import streamlit as st

from config.settings import READING_MODES
from utils.accessibility import (
    announce_message,
    inject_keyboard_shortcuts,
    inject_reader_layout_css,
    inject_skip_link,
    render_content_html,
    render_image_html,
    render_sentences_html,
    render_words_html,
)
from utils.bookmarks import delete_bookmark, has_bookmark, restore_bookmark, save_bookmark
from utils.navigator import Navigator
from utils.parser import Book
from utils.preferences import save_preferences_to_url
from utils.table_reader import format_table_html
from utils.theme import apply_theme, init_theme_state
from utils.tts_engine import audio_player_html, export_text_as_mp3, generate_speech

init_theme_state()
apply_theme()
inject_skip_link()
inject_keyboard_shortcuts()
inject_reader_layout_css()


def _init_reader_state() -> None:
    defaults = {
        "tts_playing": False,
        "tts_audio": None,
        "tts_cache_key": None,
        "current_book_name": None,
        "export_audio": None,
        "continuous_reading": True,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value
    if "reading_mode" not in st.session_state:
        st.session_state.reading_mode = "sentence"


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


def _navigate_prev(nav: Navigator) -> None:
    mode = st.session_state.reading_mode
    if mode == "word":
        nav.previous_word()
    elif mode == "sentence":
        nav.previous_sentence()
    elif nav.current_node and nav.current_node.type == "table":
        if nav.position.table_row_index > 0:
            nav.position.table_row_index -= 1
        else:
            nav.previous_node()
    else:
        nav.previous_node()


def _navigate_next(nav: Navigator) -> bool:
    """Advance to next unit. Returns False if at end of book."""
    mode = st.session_state.reading_mode
    if mode == "word":
        return nav.next_word()
    if mode == "sentence":
        return nav.next_sentence()
    if nav.current_node and nav.current_node.type == "table":
        if nav.next_table_row():
            return True
        return nav.next_node()
    return nav.next_node()


def _render_sidebar(nav: Navigator, book_name: str) -> None:
    with st.sidebar:
        st.caption(nav.progress_label())
        st.progress(nav.progress_in_book(), text="Book")
        st.progress(nav.progress_in_chapter(), text="Chapter")

        with st.expander("Chapters", expanded=True):
            for i, title in enumerate(nav.chapter_titles()):
                is_current = i == nav.position.chapter_index
                label = f"{'▶ ' if is_current else ''}{i + 1}. {title[:40]}"
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

        headings = nav.headings_in_chapter()
        if headings:
            with st.expander("Headings", expanded=False):
                for node_idx, heading in headings:
                    indent = "  " * max(0, heading.level - 1)
                    is_active = node_idx == nav.position.node_index
                    prefix = "▸ " if is_active else ""
                    label = f"{prefix}{indent}{heading.text[:50]}"
                    if st.button(
                        label,
                        key=f"heading_{nav.position.chapter_index}_{node_idx}",
                        use_container_width=True,
                    ):
                        nav.go_to_node(nav.position.chapter_index, node_idx)
                        _reset_tts()
                        st.rerun()

        with st.expander("Bookmark & Export", expanded=False):
            if has_bookmark(book_name):
                from utils.bookmarks import get_bookmark
                bookmark = get_bookmark(book_name)
                if bookmark:
                    st.caption(f'"{bookmark.node_preview}"')
                c1, c2 = st.columns(2)
                with c1:
                    if st.button("Resume", key="resume_bookmark", use_container_width=True):
                        if restore_bookmark(nav, book_name):
                            _reset_tts()
                            st.rerun()
                with c2:
                    if st.button("Delete", key="delete_bookmark", use_container_width=True):
                        delete_bookmark(book_name)
                        st.rerun()
            if st.button("Save bookmark", key="save_bookmark", use_container_width=True):
                save_bookmark(nav, book_name)
                st.rerun()

            chapter_text = nav.chapter_tts_text()
            if chapter_text and st.button("Generate MP3", use_container_width=True):
                with st.spinner("Generating..."):
                    st.session_state.export_audio = export_text_as_mp3(
                        chapter_text,
                        language=st.session_state.get("tts_language", "en"),
                        tld=st.session_state.get("tts_tld", "com"),
                        speed=st.session_state.get("speech_speed", 1.0),
                    )
            if st.session_state.get("export_audio"):
                chapter = nav.current_chapter
                fname = f"{chapter.title if chapter else 'chapter'}.mp3".replace(" ", "_")
                st.download_button(
                    "Download MP3",
                    data=st.session_state.export_audio,
                    file_name=fname,
                    mime="audio/mpeg",
                    use_container_width=True,
                )


def _render_compact_toolbar(nav: Navigator, reading_mode: str, node) -> None:
    """Single compact row of playback controls."""
    st.markdown('<div class="reader-toolbar-marker"></div>', unsafe_allow_html=True)

    t1, t2, t3, t4, t5, t6, t7, t8 = st.columns([0.5, 0.5, 0.5, 0.5, 0.5, 1.5, 1.2, 1.2])

    with t1:
        if st.button("▶", key="play_btn", help="btn-play-pause", use_container_width=True):
            st.session_state.tts_playing = True
    with t2:
        if st.button("⏸", key="pause_btn", use_container_width=True):
            st.session_state.tts_playing = False
    with t3:
        if st.button("⏹", key="stop_btn", help="btn-stop", use_container_width=True):
            _reset_tts()
    with t4:
        if st.button("⬅", key="prev_btn", help="btn-prev", use_container_width=True):
            _navigate_prev(nav)
            _reset_tts()
            st.rerun()
    with t5:
        if st.button("➡", key="next_btn", help="btn-next", use_container_width=True):
            _navigate_next(nav)
            _reset_tts()
            st.rerun()
    with t6:
        st.session_state.speech_speed = st.slider(
            "Speed",
            min_value=0.5,
            max_value=2.0,
            value=st.session_state.get("speech_speed", 1.0),
            step=0.1,
            key="reader_speed",
            label_visibility="collapsed",
        )
    with t7:
        mode = st.selectbox(
            "Mode",
            options=READING_MODES,
            format_func=lambda m: {"sentence": "Sentence", "paragraph": "Para", "word": "Word"}.get(m, m),
            index=READING_MODES.index(st.session_state.reading_mode),
            key="reading_mode_select",
            label_visibility="collapsed",
        )
        st.session_state.reading_mode = mode
    with t8:
        st.session_state.continuous_reading = st.checkbox(
            "Continuous",
            value=st.session_state.get("continuous_reading", True),
            help="Auto-advance to next section when speech finishes",
        )

    # Hidden buttons for keyboard shortcuts and auto-advance
    h1, h2, h3, h4, h5, h6 = st.columns(6)
    with h1:
        if st.button("H+", key="next_h_btn", help="btn-next-heading"):
            nav.next_heading()
            _reset_tts()
            st.rerun()
    with h2:
        if st.button("H-", key="prev_h_btn", help="btn-prev-heading"):
            nav.previous_heading()
            _reset_tts()
            st.rerun()
    with h3:
        if st.button("A+", key="sc_font_inc", help="btn-font-increase"):
            st.session_state.font_size = min(36, st.session_state.font_size + 2)
            save_preferences_to_url()
            st.rerun()
    with h4:
        if st.button("A-", key="sc_font_dec", help="btn-font-decrease"):
            st.session_state.font_size = max(12, st.session_state.font_size - 2)
            save_preferences_to_url()
            st.rerun()
    with h5:
        if st.button("T", key="sc_theme", help="btn-cycle-theme"):
            from utils.theme import cycle_theme
            st.session_state.theme = cycle_theme(st.session_state.theme)
            save_preferences_to_url()
            st.rerun()
    with h6:
        if st.button("adv", key="auto_advance", help="btn-auto-advance"):
            if st.session_state.get("continuous_reading", True):
                if _navigate_next(nav):
                    st.session_state.tts_playing = True
                    st.session_state.tts_cache_key = None
                    st.rerun()
                else:
                    _reset_tts()
                    announce_message("Finished reading.")


def _get_tts_text(nav: Navigator) -> str:
    mode = st.session_state.reading_mode
    node = nav.current_node
    if not node:
        return ""
    if node.type in {"image", "table"}:
        return nav.tts_text
    if mode == "word":
        return nav.current_word
    if mode == "sentence":
        return nav.current_sentence
    return nav.current_text


def _position_caption(nav: Navigator, reading_mode: str, node) -> str:
    if reading_mode == "word" and nav.current_words:
        return f"Word {nav.position.word_index + 1}/{len(nav.current_words)}"
    if reading_mode == "sentence" and nav.current_sentences:
        return f"Sentence {nav.position.sentence_index + 1}/{len(nav.current_sentences)}"
    if node.type == "table":
        rows = [r for r in node.children if r.type == "table_row"]
        return f"Row {nav.position.table_row_index + 1}/{len(rows)}"
    return ""


def _render_node_content(nav: Navigator, node, reading_mode: str) -> None:
    if node.type == "image":
        st.markdown(
            render_image_html(node.alt_text or node.text, node.alt_text),
            unsafe_allow_html=True,
        )
        return
    if node.type == "table":
        st.markdown(
            f'<div class="reader-content reader-content-main">'
            f"{format_table_html(node, nav.position.table_row_index)}</div>",
            unsafe_allow_html=True,
        )
        return
    if reading_mode == "word":
        st.markdown(
            render_words_html(nav.current_words, nav.position.word_index),
            unsafe_allow_html=True,
        )
    elif reading_mode == "sentence":
        st.markdown(
            render_sentences_html(
                nav.current_sentences, nav.position.sentence_index, node.type
            ),
            unsafe_allow_html=True,
        )
    else:
        highlighted = st.session_state.get("tts_playing", False)
        st.markdown(
            render_content_html(node.html, highlighted=highlighted),
            unsafe_allow_html=True,
        )


def _play_tts(nav: Navigator, reading_mode: str) -> None:
    tts_text = _get_tts_text(nav)
    if not st.session_state.get("tts_playing", False) or not tts_text:
        return

    cache_key = (
        f"tts_{nav.position.chapter_index}_{nav.position.node_index}_"
        f"{nav.position.sentence_index}_{nav.position.word_index}_"
        f"{nav.position.table_row_index}_{reading_mode}_"
        f"{st.session_state.get('tts_language')}_{st.session_state.get('tts_tld')}"
    )
    if st.session_state.get("tts_cache_key") != cache_key:
        with st.spinner("Preparing speech..."):
            from utils.tts_engine import adjust_speed
            audio = generate_speech(
                tts_text,
                language=st.session_state.get("tts_language", "en"),
                tld=st.session_state.get("tts_tld", "com"),
                slow=st.session_state.speech_speed < 0.85,
            )
            speed = st.session_state.get("speech_speed", 1.0)
            if speed != 1.0 and speed >= 0.85:
                audio = adjust_speed(audio, speed)
            if audio:
                st.session_state.tts_audio = audio
                st.session_state.tts_cache_key = cache_key
            else:
                st.session_state.tts_playing = False
                st.warning("Could not generate speech.")

    audio = st.session_state.get("tts_audio")
    if audio:
        continuous = st.session_state.get("continuous_reading", True)
        st.markdown(
            audio_player_html(audio, autoplay=True, continuous=continuous),
            unsafe_allow_html=True,
        )


def main() -> None:
    _init_reader_state()

    book = _ensure_book_loaded()
    if book is None:
        return

    nav = _ensure_navigator(book)
    _render_sidebar(nav, _book_name())

    chapter = nav.current_chapter
    node = nav.current_node
    if not chapter or not node:
        st.error("This book has no readable content.")
        return

    reading_mode = st.session_state.reading_mode
    pos = _position_caption(nav, reading_mode, node)
    st.markdown(
        f'<p class="reader-page-header"><strong>{book.title}</strong> · '
        f"{chapter.title}"
        f'{f" · {pos}" if pos else ""}</p>',
        unsafe_allow_html=True,
    )

    _render_compact_toolbar(nav, reading_mode, node)

    st.markdown('<div id="reader-main-content"></div>', unsafe_allow_html=True)
    _render_node_content(nav, node, reading_mode)
    _play_tts(nav, reading_mode)


if __name__ == "__main__":
    main()
