"""XHTML, EPUB, and PDF content parser producing a unified content model."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from io import BytesIO
from pathlib import Path
from typing import BinaryIO

import fitz
from bs4 import BeautifulSoup, NavigableString, Tag
from ebooklib import epub

HEADING_TAGS = {"h1", "h2", "h3", "h4", "h5", "h6"}
BLOCK_TAGS = {"p", "div", "blockquote", "pre", "li", "td", "th", "figcaption"}
SKIP_TAGS = {"script", "style", "noscript", "meta", "link"}


@dataclass
class ContentNode:
    type: str
    level: int
    text: str
    html: str
    children: list[ContentNode] = field(default_factory=list)
    alt_text: str = ""


@dataclass
class Chapter:
    title: str
    nodes: list[ContentNode]


@dataclass
class Book:
    title: str
    chapters: list[Chapter]


def _clean_text(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def _heading_level(tag_name: str) -> int:
    if tag_name in HEADING_TAGS:
        return int(tag_name[1])
    return 0


def _node_from_tag(tag: Tag) -> ContentNode | None:
    name = tag.name.lower() if tag.name else ""

    if name in SKIP_TAGS:
        return None

    if name in HEADING_TAGS:
        text = _clean_text(tag.get_text())
        if not text:
            return None
        return ContentNode(
            type="heading",
            level=_heading_level(name),
            text=text,
            html=str(tag),
        )

    if name == "img":
        alt = tag.get("alt", "").strip()
        src = tag.get("src", "")
        text = alt or "Image"
        return ContentNode(
            type="image",
            level=0,
            text=text,
            html=str(tag),
            alt_text=alt or src,
        )

    if name in {"ul", "ol"}:
        items = []
        for li in tag.find_all("li", recursive=False):
            item_text = _clean_text(li.get_text())
            if item_text:
                items.append(
                    ContentNode(
                        type="list_item",
                        level=0,
                        text=item_text,
                        html=str(li),
                    )
                )
        if not items:
            return None
        return ContentNode(
            type="list",
            level=0,
            text=" ".join(item.text for item in items),
            html=str(tag),
            children=items,
        )

    if name == "table":
        rows: list[ContentNode] = []
        for row in tag.find_all("tr"):
            cells = []
            for cell in row.find_all(["td", "th"]):
                cell_text = _clean_text(cell.get_text())
                if cell_text:
                    cells.append(
                        ContentNode(
                            type="table_cell",
                            level=0,
                            text=cell_text,
                            html=str(cell),
                        )
                    )
            if cells:
                rows.append(
                    ContentNode(
                        type="table_row",
                        level=0,
                        text=" | ".join(c.text for c in cells),
                        html=str(row),
                        children=cells,
                    )
                )
        if not rows:
            return None
        return ContentNode(
            type="table",
            level=0,
            text=" ".join(row.text for row in rows),
            html=str(tag),
            children=rows,
        )

    if name in BLOCK_TAGS:
        text = _clean_text(tag.get_text())
        if not text:
            return None
        node_type = "list_item" if name == "li" else "paragraph"
        return ContentNode(
            type=node_type,
            level=0,
            text=text,
            html=str(tag),
        )

    return None


def _walk_body(body: Tag) -> list[ContentNode]:
    nodes: list[ContentNode] = []
    for child in body.children:
        if isinstance(child, NavigableString):
            text = _clean_text(str(child))
            if text:
                nodes.append(
                    ContentNode(
                        type="paragraph",
                        level=0,
                        text=text,
                        html=f"<p>{text}</p>",
                    )
                )
            continue
        if not isinstance(child, Tag):
            continue
        node = _node_from_tag(child)
        if node:
            nodes.append(node)
    return nodes


def parse_xhtml(content: str | bytes, title: str = "Untitled") -> Chapter:
    """Parse a single XHTML/HTML document into a chapter."""
    if isinstance(content, bytes):
        content = content.decode("utf-8", errors="replace")
    soup = BeautifulSoup(content, "xml")
    body = soup.find("body") or soup
    page_title = soup.find("title")
    chapter_title = _clean_text(page_title.get_text()) if page_title else title
    nodes = _walk_body(body)
    if not nodes:
        fallback = _clean_text(body.get_text())
        if fallback:
            nodes = [
                ContentNode(
                    type="paragraph",
                    level=0,
                    text=fallback,
                    html=f"<p>{fallback}</p>",
                )
            ]
    return Chapter(title=chapter_title or title, nodes=nodes)


def parse_xhtml_file(path: Path) -> Chapter:
    return parse_xhtml(path.read_bytes(), title=path.stem.replace("_", " ").title())


def parse_epub(source: BinaryIO | bytes | Path) -> Book:
    """Parse an EPUB file into a Book with chapters."""
    if isinstance(source, Path):
        book = epub.read_epub(str(source))
    elif isinstance(source, bytes):
        book = epub.read_epub(BytesIO(source))
    else:
        book = epub.read_epub(source)

    title = book.get_metadata("DC", "title")
    book_title = title[0][0] if title else "Untitled Book"

    chapters: list[Chapter] = []
    for item in book.get_items():
        if item.get_type() != 9:  # ITEM_DOCUMENT
            continue
        try:
            chapter = parse_xhtml(item.get_content(), title=item.get_name())
            if chapter.nodes:
                chapters.append(chapter)
        except Exception:
            continue

    if not chapters:
        chapters = [Chapter(title="Empty Book", nodes=[])]

    return Book(title=book_title, chapters=chapters)


def _group_pdf_blocks(blocks: list[tuple[float, float, str]]) -> list[str]:
    """Group PDF text blocks into paragraphs by vertical position."""
    if not blocks:
        return []
    blocks.sort(key=lambda b: (round(b[1], 1), b[0]))
    paragraphs: list[str] = []
    current_lines: list[str] = []
    last_y: float | None = None

    for _x, y, text in blocks:
        text = _clean_text(text)
        if not text:
            continue
        if last_y is not None and abs(y - last_y) > 15:
            if current_lines:
                paragraphs.append(" ".join(current_lines))
                current_lines = []
        current_lines.append(text)
        last_y = y

    if current_lines:
        paragraphs.append(" ".join(current_lines))
    return paragraphs


def parse_pdf(source: BinaryIO | bytes | Path) -> Book:
    """Parse a PDF file into a Book with one chapter per page."""
    if isinstance(source, Path):
        doc = fitz.open(str(source))
    elif isinstance(source, bytes):
        doc = fitz.open(stream=source, filetype="pdf")
    else:
        data = source.read()
        doc = fitz.open(stream=data, filetype="pdf")

    title = doc.metadata.get("title") or "PDF Document"
    chapters: list[Chapter] = []

    for page_num in range(len(doc)):
        page = doc[page_num]
        blocks = [
            (block[0], block[1], block[4])
            for block in page.get_text("blocks")
            if len(block) > 4 and block[4].strip()
        ]
        paragraphs = _group_pdf_blocks(blocks)
        nodes = [
            ContentNode(
                type="paragraph",
                level=0,
                text=para,
                html=f"<p>{para}</p>",
            )
            for para in paragraphs
        ]
        if nodes:
            chapters.append(Chapter(title=f"Page {page_num + 1}", nodes=nodes))

    doc.close()

    if not chapters:
        chapters = [Chapter(title="Empty PDF", nodes=[])]

    return Book(title=title, chapters=chapters)


def parse_file(path: Path) -> Book:
    """Parse a file by extension into a Book."""
    suffix = path.suffix.lower()
    if suffix == ".epub":
        return parse_epub(path)
    if suffix == ".pdf":
        return parse_pdf(path)
    if suffix in {".xhtml", ".html", ".htm"}:
        chapter = parse_xhtml_file(path)
        return Book(title=chapter.title, chapters=[chapter])
    raise ValueError(f"Unsupported file type: {suffix}")


def parse_upload(uploaded_bytes: bytes, filename: str) -> Book:
    """Parse uploaded file bytes by filename extension."""
    suffix = Path(filename).suffix.lower()
    if suffix == ".epub":
        return parse_epub(uploaded_bytes)
    if suffix == ".pdf":
        return parse_pdf(uploaded_bytes)
    if suffix in {".xhtml", ".html", ".htm"}:
        chapter = parse_xhtml(uploaded_bytes, title=Path(filename).stem)
        return Book(title=chapter.title, chapters=[chapter])
    raise ValueError(f"Unsupported file type: {suffix}")


def load_sample_books(directory: Path) -> dict[str, Book]:
    """Load all sample books from a directory."""
    books: dict[str, Book] = {}
    if not directory.exists():
        return books
    for path in sorted(directory.iterdir()):
        if path.suffix.lower() not in {".xhtml", ".html", ".htm", ".epub", ".pdf"}:
            continue
        try:
            book = parse_file(path)
            books[path.name] = book
        except Exception:
            continue
    return books
