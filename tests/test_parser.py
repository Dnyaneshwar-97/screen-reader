"""Unit tests for content parser."""

from pathlib import Path

import pytest

from utils.parser import (
    Book,
    Chapter,
    ContentNode,
    load_sample_books,
    parse_upload,
    parse_xhtml,
)

SAMPLE_DIR = Path(__file__).resolve().parent.parent / "assets" / "sample_books"

SAMPLE_XHTML = """<?xml version="1.0" encoding="UTF-8"?>
<html><body>
<h1>Test Chapter</h1>
<p>First paragraph.</p>
<h2>Section</h2>
<p>Second paragraph.</p>
<ul><li>Item one</li><li>Item two</li></ul>
<table><tr><th>Col</th></tr><tr><td>Data</td></tr></table>
<img src="test.png" alt="A test image"/>
</body></html>"""


class TestParseXhtml:
    def test_parses_headings(self):
        chapter = parse_xhtml(SAMPLE_XHTML)
        headings = [n for n in chapter.nodes if n.type == "heading"]
        assert len(headings) == 2
        assert headings[0].level == 1
        assert headings[0].text == "Test Chapter"

    def test_parses_paragraphs(self):
        chapter = parse_xhtml(SAMPLE_XHTML)
        paragraphs = [n for n in chapter.nodes if n.type == "paragraph"]
        assert len(paragraphs) >= 2

    def test_parses_lists(self):
        chapter = parse_xhtml(SAMPLE_XHTML)
        lists = [n for n in chapter.nodes if n.type == "list"]
        assert len(lists) == 1
        assert len(lists[0].children) == 2

    def test_parses_tables(self):
        chapter = parse_xhtml(SAMPLE_XHTML)
        tables = [n for n in chapter.nodes if n.type == "table"]
        assert len(tables) == 1
        assert len(tables[0].children) >= 1

    def test_parses_images(self):
        chapter = parse_xhtml(SAMPLE_XHTML)
        images = [n for n in chapter.nodes if n.type == "image"]
        assert len(images) == 1
        assert images[0].alt_text == "A test image"

    def test_empty_content(self):
        chapter = parse_xhtml("<html><body></body></html>")
        assert isinstance(chapter, Chapter)
        assert chapter.nodes == [] or all(n.text for n in chapter.nodes)


class TestParseUpload:
    def test_parse_xhtml_upload(self):
        book = parse_upload(SAMPLE_XHTML.encode(), "test.xhtml")
        assert isinstance(book, Book)
        assert len(book.chapters) == 1
        assert len(book.chapters[0].nodes) > 0

    def test_unsupported_format(self):
        with pytest.raises(ValueError, match="Unsupported"):
            parse_upload(b"data", "file.docx")


class TestSampleBooks:
    def test_load_sample_books(self):
        books = load_sample_books(SAMPLE_DIR)
        assert len(books) >= 2
        for name, book in books.items():
            assert isinstance(book, Book)
            assert len(book.chapters) >= 1

    def test_science_chapter_content(self):
        path = SAMPLE_DIR / "sample_science_chapter1.xhtml"
        if not path.exists():
            pytest.skip("Sample file not found")
        book = parse_upload(path.read_bytes(), path.name)
        texts = [n.text for ch in book.chapters for n in ch.nodes]
        assert any("Science" in t for t in texts)
