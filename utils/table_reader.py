"""Intelligent table content formatting for text-to-speech."""

from __future__ import annotations

from utils.parser import ContentNode


def format_table_for_tts(node: ContentNode) -> str:
    """Read table content row-by-row with cell announcements."""
    if node.type != "table" or not node.children:
        return node.text

    parts: list[str] = ["Table with the following content."]
    for row_idx, row in enumerate(node.children):
        if row.type != "table_row" or not row.children:
            continue
        cell_parts: list[str] = []
        for col_idx, cell in enumerate(row.children):
            cell_parts.append(f"Column {col_idx + 1}: {cell.text}")
        parts.append(f"Row {row_idx + 1}. " + ". ".join(cell_parts) + ".")
    return " ".join(parts)


def format_table_html(node: ContentNode, active_row: int = -1) -> str:
    """Render table with optional active row highlight."""
    if node.type != "table":
        return node.html

    rows_html: list[str] = []
    for row_idx, row in enumerate(node.children):
        if row.type != "table_row":
            continue
        row_class = "reader-table-row-active" if row_idx == active_row else ""
        cells = "".join(f"<td>{cell.text}</td>" for cell in row.children)
        rows_html.append(f'<tr class="{row_class}">{cells}</tr>')

    return (
        '<table class="reader-table" role="table" aria-label="Data table">'
        + "".join(rows_html)
        + "</table>"
    )
