"""Browse sample books and upload new content."""

from __future__ import annotations

import streamlit as st

from config.settings import SAMPLE_BOOKS_DIR, SUPPORTED_EXTENSIONS
from utils.navigator import Navigator
from utils.parser import load_sample_books, parse_upload
from utils.theme import apply_theme, init_theme_state

init_theme_state()
apply_theme()


def _load_book(name: str, book) -> None:
    st.session_state.current_book = book
    st.session_state.current_book_name = name
    nav = Navigator(book)
    st.session_state.navigator = nav
    st.session_state.tts_playing = False
    st.session_state.tts_audio = None
    st.session_state.tts_cache_key = None

    from utils.bookmarks import has_bookmark, restore_bookmark
    if has_bookmark(name):
        restore_bookmark(nav, name)


def main() -> None:
    st.title("📚 Library")

    # Sample books
    st.subheader("Sample Books")
    sample_books = load_sample_books(SAMPLE_BOOKS_DIR)

    if sample_books:
        for filename, book in sample_books.items():
            col1, col2 = st.columns([3, 1])
            with col1:
                chapter_count = len(book.chapters)
                st.markdown(f"**{book.title}** — {chapter_count} chapter(s)")
                st.caption(f"File: {filename}")
            with col2:
                if st.button("Open", key=f"sample_{filename}", use_container_width=True):
                    _load_book(filename, book)
                    st.success(f"Loaded: {book.title}")
                    st.switch_page("pages/1_Reader.py")
    else:
        st.info("No sample books found in assets/sample_books/.")

    st.markdown("---")

    # File upload
    st.subheader("Upload a Book")
    st.markdown(
        f"Supported formats: {', '.join(sorted(SUPPORTED_EXTENSIONS))}"
    )

    uploaded = st.file_uploader(
        "Choose a file",
        type=[ext.lstrip(".") for ext in SUPPORTED_EXTENSIONS],
        help="Upload an XHTML, EPUB, or PDF file to read aloud.",
    )

    if uploaded is not None:
        try:
            with st.spinner("Parsing book..."):
                book = parse_upload(uploaded.read(), uploaded.name)
            st.success(f"Parsed **{book.title}** with {len(book.chapters)} chapter(s).")

            with st.expander("Preview chapters"):
                for i, chapter in enumerate(book.chapters):
                    st.markdown(f"**{i + 1}. {chapter.title}** — {len(chapter.nodes)} sections")

            if st.button("Open in Reader", type="primary"):
                _load_book(uploaded.name, book)
                st.switch_page("pages/1_Reader.py")
        except Exception as exc:
            st.error(f"Failed to parse file: {exc}")
            st.markdown(
                "Please ensure the file is a valid XHTML, EPUB, or PDF document."
            )


if __name__ == "__main__":
    main()
