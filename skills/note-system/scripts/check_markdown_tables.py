#!/usr/bin/env python3
"""Find unescaped wikilink pipes in Markdown table rows."""

from __future__ import annotations

import argparse
import re
import sys
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import cast

FENCE_PATTERN = re.compile(r"^ {0,3}(?P<marker>`{3,}|~{3,})(?P<info>.*)$")
LIST_ITEM_PATTERN = re.compile(r"^(?P<indent> *)(?:[-+*]|\d{1,9}[.)])(?P<spacing> +)")
DELIMITER_CELL_PATTERN = re.compile(r":?-{2,}:?")
WIKILINK_PATTERN = re.compile(r"!?\[\[[^\]\r\n]+\]\]")


@dataclass(frozen=True)
class Fence:
    character: str
    length: int
    quote_depth: int
    container_indent: int


@dataclass(frozen=True)
class Violation:
    path: Path
    line_number: int
    link: str


def strip_blockquote_prefix(line: str) -> tuple[int, str]:
    depth = 0
    content = line
    while True:
        match = re.match(r"^ {0,3}>[ \t]?", content)
        if match is None:
            return depth, content
        depth += 1
        content = content[match.end() :]


def is_escaped(text: str, index: int) -> bool:
    preceding_backslashes = 0
    cursor = index - 1
    while cursor >= 0 and text[cursor] == "\\":
        preceding_backslashes += 1
        cursor -= 1
    return preceding_backslashes % 2 == 1


def unescaped_pipe_indexes(text: str) -> list[int]:
    return [
        index
        for index, character in enumerate(text)
        if character == "|" and not is_escaped(text, index)
    ]


def structural_pipe_indexes(text: str) -> list[int]:
    wikilink_spans = [match.span() for match in WIKILINK_PATTERN.finditer(text)]
    return [
        index
        for index in unescaped_pipe_indexes(text)
        if not any(start <= index < end for start, end in wikilink_spans)
    ]


def split_at_structural_pipes(text: str) -> list[str] | None:
    indexes = structural_pipe_indexes(text)
    if not indexes:
        return None
    cells: list[str] = []
    start = 0
    for index in indexes:
        cells.append(text[start:index])
        start = index + 1
    cells.append(text[start:])
    if cells[0].strip() == "":
        cells.pop(0)
    if cells and cells[-1].strip() == "":
        cells.pop()
    return cells


def table_cells(line: str) -> tuple[int, list[str]] | None:
    quote_depth, content = strip_blockquote_prefix(line)
    cells = split_at_structural_pipes(content.strip())
    if not cells:
        return None
    return quote_depth, cells


def delimiter_row(line: str) -> tuple[int, list[str]] | None:
    parsed = table_cells(line)
    if parsed is None:
        return None
    quote_depth, cells = parsed
    valid = all(
        DELIMITER_CELL_PATTERN.fullmatch(cell.strip()) is not None for cell in cells
    )
    return (quote_depth, cells) if valid else None


def content_in_list_container(content: str, indents: list[int]) -> tuple[int, str]:
    expanded = content.expandtabs(4)
    if expanded.strip() == "":
        container_indent = indents[-1] if indents else 0
        return container_indent, ""

    list_item = LIST_ITEM_PATTERN.match(expanded)
    if list_item is not None:
        marker_indent = len(list_item.group("indent"))
        while indents and marker_indent < indents[-1]:
            indents.pop()
        container_indent = list_item.end()
        if not indents or container_indent > indents[-1]:
            indents.append(container_indent)
        else:
            indents[-1] = container_indent
        return container_indent, expanded[container_indent:]

    line_indent = len(expanded) - len(expanded.lstrip(" "))
    while indents and line_indent < indents[-1]:
        indents.pop()
    container_indent = indents[-1] if indents else 0
    return container_indent, expanded[container_indent:]


def fenced_line_indexes(lines: list[str]) -> set[int]:
    excluded: set[int] = set()
    active: Fence | None = None
    list_indents: dict[int, list[int]] = {}
    previous_quote_depth = 0
    for index, line in enumerate(lines):
        quote_depth, content = strip_blockquote_prefix(line)
        if active is not None:
            expanded = content.expandtabs(4)
            line_indent = len(expanded) - len(expanded.lstrip(" "))
            container_ended = (
                active.container_indent > 0
                and expanded.strip() != ""
                and line_indent < active.container_indent
            )
            if quote_depth < active.quote_depth or container_ended:
                active = None
            else:
                excluded.add(index)
                relative = expanded[active.container_indent :]
                closing = re.fullmatch(
                    rf" {{0,3}}{re.escape(active.character)}"
                    rf"{{{active.length},}}[ \t]*",
                    relative,
                )
                if closing is not None and quote_depth == active.quote_depth:
                    active = None
                continue

        if quote_depth < previous_quote_depth:
            for depth in tuple(list_indents):
                if depth > quote_depth:
                    del list_indents[depth]
        elif quote_depth > previous_quote_depth:
            list_indents.pop(quote_depth, None)
        previous_quote_depth = quote_depth

        indents = list_indents.setdefault(quote_depth, [])
        container_indent, relative = content_in_list_container(content, indents)
        opening = FENCE_PATTERN.match(relative)
        if opening is None:
            continue
        marker = opening.group("marker")
        info = opening.group("info")
        if marker[0] == "`" and "`" in info:
            continue
        active = Fence(marker[0], len(marker), quote_depth, container_indent)
        excluded.add(index)
    return excluded


def table_row_indexes(lines: list[str]) -> set[int]:
    excluded = fenced_line_indexes(lines)
    rows: set[int] = set()
    index = 0
    while index + 1 < len(lines):
        if index in excluded or index + 1 in excluded:
            index += 1
            continue
        header = table_cells(lines[index])
        delimiter = delimiter_row(lines[index + 1])
        if (
            header is None
            or delimiter is None
            or header[0] != delimiter[0]
            or len(header[1]) != len(delimiter[1])
        ):
            index += 1
            continue

        quote_depth, _ = header
        rows.add(index)
        body_index = index + 2
        while body_index < len(lines) and body_index not in excluded:
            parsed = table_cells(lines[body_index])
            if parsed is None or parsed[0] != quote_depth:
                break
            rows.add(body_index)
            body_index += 1
        index = body_index
    return rows


def unescaped_links(line: str) -> list[str]:
    violations: list[str] = []
    for match in WIKILINK_PATTERN.finditer(line):
        link = match.group(0)
        body_start = link.index("[[") + 2
        body = link[body_start:-2]
        if unescaped_pipe_indexes(body):
            violations.append(link)
    return violations


def check_file(path: Path) -> list[Violation]:
    lines = path.read_text(encoding="utf-8").splitlines()
    return [
        Violation(path, index + 1, link)
        for index in sorted(table_row_indexes(lines))
        for link in unescaped_links(lines[index])
    ]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Check Markdown tables for unescaped wikilink pipes."
    )
    parser.add_argument("files", nargs="+", type=Path)
    return parser


def run(paths: Sequence[Path]) -> int:
    violations: list[Violation] = []
    input_error = False
    for path in paths:
        if path.suffix.lower() != ".md":
            print(f"{path}: expected a Markdown file", file=sys.stderr)
            input_error = True
            continue
        try:
            violations.extend(check_file(path))
        except (OSError, UnicodeError) as error:
            print(f"{path}: {error}", file=sys.stderr)
            input_error = True

    for violation in violations:
        print(
            f"{violation.path}:{violation.line_number}: "
            f"unescaped pipe in Markdown table link: {violation.link}"
        )
    if input_error:
        return 2
    return 1 if violations else 0


def main(argv: Sequence[str] | None = None) -> int:
    arguments = build_parser().parse_args(argv)
    return run(cast(list[Path], arguments.files))


if __name__ == "__main__":
    raise SystemExit(main())
