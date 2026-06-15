"""Unit tests for navigation logic."""

import pytest

from utils.navigator import Navigator, ReadingPosition
from utils.parser import Book, Chapter, ContentNode


def _make_book() -> Book:
    ch1 = Chapter(
        title="Chapter 1",
        nodes=[
            ContentNode(type="heading", level=1, text="Intro", html="<h1>Intro</h1>"),
            ContentNode(type="paragraph", level=0, text="Para 1. Another sentence.", html="<p>Para 1. Another sentence.</p>"),
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
        assert self.nav.current_text == "Para 1. Another sentence."

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

    def test_current_sentences(self):
        self.nav.position.node_index = 1
        sentences = self.nav.current_sentences
        assert len(sentences) >= 2

    def test_next_sentence(self):
        self.nav.position.node_index = 1
        self.nav.position.sentence_index = 0
        assert self.nav.next_sentence()
        assert self.nav.position.sentence_index == 1

    def test_previous_sentence(self):
        self.nav.position.node_index = 1
        self.nav.position.sentence_index = 1
        assert self.nav.previous_sentence()
        assert self.nav.position.sentence_index == 0

    def test_headings_in_chapter(self):
        headings = self.nav.headings_in_chapter()
        assert len(headings) == 2
        assert headings[0][1].text == "Intro"

    def test_go_to_node(self):
        assert self.nav.go_to_node(0, 1)
        assert self.nav.position.node_index == 1

    def test_progress_label(self):
        label = self.nav.progress_label()
        assert "Book" in label
        assert "Chapter" in label

    def test_current_words(self):
        self.nav.position.node_index = 1
        words = self.nav.current_words
        assert len(words) >= 3

    def test_next_word(self):
        self.nav.position.node_index = 1
        assert self.nav.next_word()
        assert self.nav.position.word_index == 1

    def test_tts_text_image(self):
        image = ContentNode(type="image", level=0, text="Diagram", html="<img>", alt_text="A diagram of cells")
        self.nav.book.chapters[0].nodes.append(image)
        self.nav.go_to_node(0, len(self.nav.book.chapters[0].nodes) - 1)
        assert "diagram" in self.nav.tts_text.lower()

    def test_chapter_tts_text(self):
        text = self.nav.chapter_tts_text(0)
        assert "Intro" in text
        assert "Para 1" in text
