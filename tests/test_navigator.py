"""Unit tests for navigation logic."""

import pytest

from utils.navigator import Navigator, ReadingPosition
from utils.parser import Book, Chapter, ContentNode


def _make_book() -> Book:
    ch1 = Chapter(
        title="Chapter 1",
        nodes=[
            ContentNode(type="heading", level=1, text="Intro", html="<h1>Intro</h1>"),
            ContentNode(type="paragraph", level=0, text="Para 1", html="<p>Para 1</p>"),
            ContentNode(type="heading", level=2, text="Section A", html="<h2>Section A</h2>"),
            ContentNode(type="paragraph", level=0, text="Para 2", html="<p>Para 2</p>"),
        ],
    )
    ch2 = Chapter(
        title="Chapter 2",
        nodes=[
            ContentNode(type="heading", level=1, text="Chapter Two", html="<h1>Chapter Two</h1>"),
            ContentNode(type="paragraph", level=0, text="Para 3", html="<p>Para 3</p>"),
        ],
    )
    return Book(title="Test Book", chapters=[ch1, ch2])


class TestNavigator:
    def setup_method(self):
        self.nav = Navigator(_make_book())

    def test_initial_position(self):
        assert self.nav.position.chapter_index == 0
        assert self.nav.position.node_index == 0
        assert self.nav.current_text == "Intro"

    def test_next_node(self):
        assert self.nav.next_node()
        assert self.nav.current_text == "Para 1"

    def test_previous_node(self):
        self.nav.next_node()
        assert self.nav.previous_node()
        assert self.nav.current_text == "Intro"

    def test_next_heading(self):
        assert self.nav.next_heading()
        assert self.nav.current_node.type == "heading"
        assert self.nav.current_text == "Section A"

    def test_previous_heading(self):
        self.nav.go_to_chapter(0)
        self.nav.position.node_index = 3
        assert self.nav.previous_heading()
        assert self.nav.current_text == "Section A"

    def test_go_to_chapter(self):
        assert self.nav.go_to_chapter(1)
        assert self.nav.position.chapter_index == 1
        assert self.nav.current_text == "Chapter Two"

    def test_invalid_chapter(self):
        assert not self.nav.go_to_chapter(99)

    def test_cross_chapter_next(self):
        self.nav.position.node_index = 3
        assert self.nav.next_node()
        assert self.nav.position.chapter_index == 1

    def test_progress_in_chapter(self):
        progress = self.nav.progress_in_chapter()
        assert 0.0 < progress <= 1.0

    def test_progress_in_book(self):
        progress = self.nav.progress_in_book()
        assert 0.0 < progress <= 1.0

    def test_chapter_titles(self):
        titles = self.nav.chapter_titles()
        assert titles == ["Chapter 1", "Chapter 2"]

    def test_next_node_end_of_book(self):
        self.nav.go_to_chapter(1)
        self.nav.position.node_index = 1
        assert not self.nav.next_node()
