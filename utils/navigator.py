"""Content navigation for chapters, headings, and paragraphs."""

from __future__ import annotations

from dataclasses import dataclass

from utils.parser import Book, Chapter, ContentNode
from utils.tts_engine import split_raw_sentences


@dataclass
class ReadingPosition:
    chapter_index: int = 0
    node_index: int = 0
    sentence_index: int = 0


class Navigator:
    """Navigate structured book content by chapter, heading, and paragraph."""

    def __init__(self, book: Book) -> None:
        self.book = book
        self.position = ReadingPosition()

    @property
    def current_chapter(self) -> Chapter | None:
        if not self.book.chapters:
            return None
        idx = min(self.position.chapter_index, len(self.book.chapters) - 1)
        return self.book.chapters[idx]

    @property
    def current_node(self) -> ContentNode | None:
        chapter = self.current_chapter
        if not chapter or not chapter.nodes:
            return None
        idx = min(self.position.node_index, len(chapter.nodes) - 1)
        return chapter.nodes[idx]

    @property
    def current_text(self) -> str:
        node = self.current_node
        return node.text if node else ""

    def go_to_chapter(self, index: int) -> bool:
        if 0 <= index < len(self.book.chapters):
            self.position.chapter_index = index
            self.position.node_index = 0
            self.position.sentence_index = 0
            return True
        return False

    def next_node(self) -> bool:
        chapter = self.current_chapter
        if not chapter:
            return False
        if self.position.node_index < len(chapter.nodes) - 1:
            self.position.node_index += 1
            self.position.sentence_index = 0
            return True
        if self.position.chapter_index < len(self.book.chapters) - 1:
            self.position.chapter_index += 1
            self.position.node_index = 0
            self.position.sentence_index = 0
            return True
        return False

    def previous_node(self) -> bool:
        if self.position.node_index > 0:
            self.position.node_index -= 1
            self.position.sentence_index = 0
            return True
        if self.position.chapter_index > 0:
            self.position.chapter_index -= 1
            chapter = self.current_chapter
            if chapter and chapter.nodes:
                self.position.node_index = len(chapter.nodes) - 1
            else:
                self.position.node_index = 0
            self.position.sentence_index = 0
            return True
        return False

    def next_heading(self) -> bool:
        chapter = self.current_chapter
        if not chapter:
            return False
        start = self.position.node_index + 1
        for i in range(start, len(chapter.nodes)):
            if chapter.nodes[i].type == "heading":
                self.position.node_index = i
                self.position.sentence_index = 0
                return True
        return self._advance_to_next_chapter_heading()

    def previous_heading(self) -> bool:
        chapter = self.current_chapter
        if not chapter:
            return False
        for i in range(self.position.node_index - 1, -1, -1):
            if chapter.nodes[i].type == "heading":
                self.position.node_index = i
                self.position.sentence_index = 0
                return True
        return self._retreat_to_previous_chapter_heading()

    def _advance_to_next_chapter_heading(self) -> bool:
        for ci in range(self.position.chapter_index + 1, len(self.book.chapters)):
            chapter = self.book.chapters[ci]
            for ni, node in enumerate(chapter.nodes):
                if node.type == "heading":
                    self.position.chapter_index = ci
                    self.position.node_index = ni
                    self.position.sentence_index = 0
                    return True
        return False

    def _retreat_to_previous_chapter_heading(self) -> bool:
        for ci in range(self.position.chapter_index - 1, -1, -1):
            chapter = self.book.chapters[ci]
            for ni in range(len(chapter.nodes) - 1, -1, -1):
                if chapter.nodes[ni].type == "heading":
                    self.position.chapter_index = ci
                    self.position.node_index = ni
                    self.position.sentence_index = 0
                    return True
        return False

    def progress_in_chapter(self) -> float:
        chapter = self.current_chapter
        if not chapter or not chapter.nodes:
            return 0.0
        return (self.position.node_index + 1) / len(chapter.nodes)

    def progress_in_book(self) -> float:
        total_nodes = sum(len(c.nodes) for c in self.book.chapters)
        if total_nodes == 0:
            return 0.0
        passed = 0
        for ci, chapter in enumerate(self.book.chapters):
            if ci < self.position.chapter_index:
                passed += len(chapter.nodes)
            elif ci == self.position.chapter_index:
                passed += self.position.node_index + 1
                break
        return passed / total_nodes

    @property
    def current_sentences(self) -> list[str]:
        return split_raw_sentences(self.current_text)

    @property
    def current_sentence(self) -> str:
        sentences = self.current_sentences
        if not sentences:
            return self.current_text
        idx = min(self.position.sentence_index, len(sentences) - 1)
        return sentences[idx]

    def next_sentence(self) -> bool:
        sentences = self.current_sentences
        if not sentences:
            return self.next_node()
        if self.position.sentence_index < len(sentences) - 1:
            self.position.sentence_index += 1
            return True
        if self.next_node():
            self.position.sentence_index = 0
            return True
        return False

    def previous_sentence(self) -> bool:
        if self.position.sentence_index > 0:
            self.position.sentence_index -= 1
            return True
        if self.previous_node():
            sentences = self.current_sentences
            self.position.sentence_index = max(0, len(sentences) - 1)
            return True
        return False

    def headings_in_chapter(self, chapter_index: int | None = None) -> list[tuple[int, ContentNode]]:
        """Return (node_index, heading) pairs for a chapter."""
        ci = chapter_index if chapter_index is not None else self.position.chapter_index
        if ci < 0 or ci >= len(self.book.chapters):
            return []
        return [
            (i, node)
            for i, node in enumerate(self.book.chapters[ci].nodes)
            if node.type == "heading"
        ]

    def go_to_node(self, chapter_index: int, node_index: int) -> bool:
        if 0 <= chapter_index < len(self.book.chapters):
            chapter = self.book.chapters[chapter_index]
            if 0 <= node_index < len(chapter.nodes):
                self.position.chapter_index = chapter_index
                self.position.node_index = node_index
                self.position.sentence_index = 0
                return True
        return False

    def progress_label(self) -> str:
        chapter = self.current_chapter
        if not chapter or not chapter.nodes:
            return "0%"
        book_pct = int(self.progress_in_book() * 100)
        chapter_pct = int(self.progress_in_chapter() * 100)
        return f"Book {book_pct}% · Chapter {chapter_pct}% · Section {self.position.node_index + 1}/{len(chapter.nodes)}"

    def chapter_titles(self) -> list[str]:
        return [c.title for c in self.book.chapters]

    def readable_nodes(self) -> list[tuple[int, ContentNode]]:
        """Return (global_index, node) pairs for sidebar navigation."""
        result: list[tuple[int, ContentNode]] = []
        for ci, chapter in enumerate(self.book.chapters):
            for ni, node in enumerate(chapter.nodes):
                if node.type in {"heading", "paragraph", "list", "table", "image"}:
                    result.append((ci * 10000 + ni, node))
        return result
