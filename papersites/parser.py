"""
Parses the custom component syntax used by PaperSites:

    ::card
    ### Title
    body text
    ::img[path/to.png]
    ::end

`::tag[arg]` opens a block (closed by a matching `::end`), except `::img[path]`
which is a self-contained, immediate-insertion tag with no closing tag.

Blocks nest by depth: any non-`end`, non-`img` tag increases depth by one,
so `::card ... ::card ... ::end ::end` resolves correctly regardless of name.
"""

import sys
import re
from typing import Dict, List

TAG_PATTERN = re.compile(r"::([a-zA-Z][\w\-]*)(?:\[(.*?)\])?")


def _line_of(text: str, pos: int) -> int:
    """1-indexed line number for a character offset, used in warnings."""
    return text.count("\n", 0, pos) + 1


def _mask_code_spans(text: str) -> str:
    """
    Returns a same-length copy of `text` with every `:` inside backtick code
    spans (inline `` `...` `` and fenced ``` ``` ``` blocks) replaced with a
    space. Because the replacement is same-length, every match position found
    against the masked copy is still a valid index into the original text.

    Without this, writing documentation about PaperSites' own syntax — e.g.
    `` `::card` `` inside a sentence — gets misread as a real, unclosed
    `::card` tag.
    """
    masked = list(text)

    def blank_colons(span_match: "re.Match[str]") -> None:
        start, end = span_match.start(), span_match.end()
        for i in range(start, end):
            if masked[i] == ":":
                masked[i] = " "

    for m in re.finditer(r"```.*?```", text, re.S):
        blank_colons(m)
    for m in re.finditer(r"`[^`\n]+`", text):
        blank_colons(m)

    return "".join(masked)



def parse_component_blocks(text: str, source_name: str = "<content>") -> List[Dict]:
    """
    Parse `text` into a flat list of parts:
        {"type": "text", "content": str}
        {"type": "image", "path": str}
        {"type": "component", "name": str, "content": str}

    Unclosed blocks are not silently swallowed: a warning naming the tag and
    line number is printed to stderr, and the block is closed at end-of-text.
    """
    parts: List[Dict] = []
    text = text.replace("\\n", "\n")
    scan_text = _mask_code_spans(text)

    cursor = 0
    while cursor < len(text):
        match = TAG_PATTERN.search(scan_text, cursor)

        if not match:
            remainder = text[cursor:].strip()
            if remainder:
                parts.append({"type": "text", "content": remainder})
            break

        before = text[cursor : match.start()].strip()
        if before:
            parts.append({"type": "text", "content": before})

        tag_name = match.group(1).lower()
        tag_arg = match.group(2)
        tag_start = match.end()

        if tag_name == "end":
            # Stray ::end with nothing open — skip it rather than error;
            # it's harmless and more forgiving for hand-written markdown.
            cursor = tag_start
            continue

        if tag_name == "img":
            parts.append({"type": "image", "path": tag_arg if tag_arg else ""})
            cursor = tag_start
            continue

        depth = 1
        search_pos = tag_start
        content_end = len(text)
        closed = False

        while depth > 0:
            next_tag = TAG_PATTERN.search(scan_text, search_pos)
            if not next_tag:
                content_end = len(text)
                cursor = len(text)
                break

            name = next_tag.group(1).lower()
            if name == "end":
                depth -= 1
                if depth == 0:
                    content_end = next_tag.start()
                    cursor = next_tag.end()
                    closed = True
            elif name == "img":
                pass  # self-contained, doesn't affect nesting depth
            else:
                depth += 1

            search_pos = next_tag.end()

        if not closed:
            print(
                f"papersites: warning: '::{tag_name}' opened at "
                f"{source_name}:{_line_of(text, match.start())} has no matching "
                f"'::end' — treating the rest of the document as its content.",
                file=sys.stderr,
            )

        inner_content = text[tag_start:content_end].strip()
        parts.append({"type": "component", "name": tag_name, "content": inner_content})

    return parts
