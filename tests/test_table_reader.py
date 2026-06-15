"""Unit tests for table reading utilities."""

from utils.parser import ContentNode
from utils.table_reader import format_table_for_tts, format_table_html


def _make_table() -> ContentNode:
    return ContentNode(
        type="table",
        level=0,
        text="Field | Discovery",
        html="<table></table>",
        children=[
            ContentNode(
                type="table_row",
                level=0,
                text="Biology | Cells",
                html="<tr></tr>",
                children=[
                    ContentNode(type="table_cell", level=0, text="Biology", html="<td>Biology</td>"),
                    ContentNode(type="table_cell", level=0, text="Cells", html="<td>Cells</td>"),
                ],
            ),
            ContentNode(
                type="table_row",
                level=0,
                text="Physics | Light",
                html="<tr></tr>",
                children=[
                    ContentNode(type="table_cell", level=0, text="Physics", html="<td>Physics</td>"),
                    ContentNode(type="table_cell", level=0, text="Light", html="<td>Light</td>"),
                ],
            ),
        ],
    )


class TestTableReader:
    def test_format_table_for_tts(self):
        text = format_table_for_tts(_make_table())
        assert "Row 1" in text
        assert "Column 1: Biology" in text
        assert "Row 2" in text
        assert "Column 2: Light" in text

    def test_format_table_html(self):
        html = format_table_html(_make_table(), active_row=0)
        assert "Biology" in html
        assert "reader-table-row-active" in html

    def test_format_table_html_no_active(self):
        html = format_table_html(_make_table(), active_row=-1)
        assert "reader-table-row-active" not in html
