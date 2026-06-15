"""Bookmark management for saving and resuming reading positions."""

from __future__ import annotations

from dataclasses import dataclass

import streamlit as st

from utils.navigator import Navigator, ReadingPosition


@dataclass
class Bookmark:
    book_name: str
    book_title: str
    chapter_index: int
    node_index: int
    sentence_index: int
    chapter_title: str
    node_preview: str
    word_index: int = 0
    table_row_index: int = 0


BOOKMARKS_KEY = "bookmarks"


def _get_bookmarks() -> dict[str, Bookmark]:
    if BOOKMARKS_KEY not in st.session_state:
        st.session_state[BOOKMARKS_KEY] = {}
    return st.session_state[BOOKMARKS_KEY]


def save_bookmark(nav: Navigator, book_name: str) -> Bookmark:
    """Save the current reading position as a bookmark."""
    chapter = nav.current_chapter
    node = nav.current_node
    bookmark = Bookmark(
        book_name=book_name,
        book_title=nav.book.title,
        chapter_index=nav.position.chapter_index,
        node_index=nav.position.node_index,
        sentence_index=nav.position.sentence_index,
        word_index=nav.position.word_index,
        table_row_index=nav.position.table_row_index,
        chapter_title=chapter.title if chapter else "",
        node_preview=(node.text[:80] + "…") if node and len(node.text) > 80 else (node.text if node else ""),
    )
    bookmarks = _get_bookmarks()
    bookmarks[book_name] = bookmark
    st.session_state[BOOKMARKS_KEY] = bookmarks
    return bookmark


def get_bookmark(book_name: str) -> Bookmark | None:
    return _get_bookmarks().get(book_name)


def has_bookmark(book_name: str) -> bool:
    return book_name in _get_bookmarks()


def restore_bookmark(nav: Navigator, book_name: str) -> bool:
    """Restore reading position from a saved bookmark."""
    bookmark = get_bookmark(book_name)
    if not bookmark:
        return False
    nav.position = ReadingPosition(
        chapter_index=bookmark.chapter_index,
        node_index=bookmark.node_index,
        sentence_index=bookmark.sentence_index,
        word_index=bookmark.word_index,
        table_row_index=bookmark.table_row_index,
    )
    return True


def delete_bookmark(book_name: str) -> None:
    bookmarks = _get_bookmarks()
    bookmarks.pop(book_name, None)
    st.session_state[BOOKMARKS_KEY] = bookmarks


def list_bookmarks() -> list[Bookmark]:
    return list(_get_bookmarks().values())
