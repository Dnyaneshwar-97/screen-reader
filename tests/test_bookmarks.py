"""Unit tests for bookmark management."""

from unittest.mock import MagicMock, patch

import pytest

from utils.bookmarks import Bookmark, delete_bookmark, get_bookmark, has_bookmark, restore_bookmark, save_bookmark
from utils.navigator import Navigator
from utils.parser import Book, Chapter, ContentNode


def _make_book() -> Book:
    ch = Chapter(
        title="Chapter 1",
        nodes=[
            ContentNode(type="heading", level=1, text="Intro", html="<h1>Intro</h1>"),
            ContentNode(type="paragraph", level=0, text="First para. Second sentence.", html="<p>First para. Second sentence.</p>"),
        ],
    )
    return Book(title="Test Book", chapters=[ch])


class TestBookmarks:
    @pytest.fixture
    def mock_session(self):
        session = {}
        with patch("utils.bookmarks.st") as mock_st:
            mock_st.session_state = session
            yield session

    def test_save_and_get_bookmark(self, mock_session):
        nav = Navigator(_make_book())
        nav.position.node_index = 1
        nav.position.sentence_index = 1
        bookmark = save_bookmark(nav, "test.xhtml")
        assert isinstance(bookmark, Bookmark)
        assert bookmark.book_name == "test.xhtml"
        assert bookmark.node_index == 1
        assert bookmark.sentence_index == 1
        assert has_bookmark("test.xhtml")
        assert get_bookmark("test.xhtml").chapter_title == "Chapter 1"

    def test_restore_bookmark(self, mock_session):
        nav = Navigator(_make_book())
        nav.position.node_index = 1
        save_bookmark(nav, "book.epub")
        nav.position.node_index = 0
        assert restore_bookmark(nav, "book.epub")
        assert nav.position.node_index == 1

    def test_delete_bookmark(self, mock_session):
        nav = Navigator(_make_book())
        save_bookmark(nav, "book.epub")
        delete_bookmark("book.epub")
        assert not has_bookmark("book.epub")

    def test_restore_missing_bookmark(self, mock_session):
        nav = Navigator(_make_book())
        assert not restore_bookmark(nav, "missing.epub")
