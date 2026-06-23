"""
PaperSites — a small, opinionated Markdown -> HTML static site generator.

Public API:
    parse_component_blocks   parse `::component[...] ... ::end` syntax
    markdown_with_components render a single markdown string (with components) to HTML
    build_site                build an entire content/ directory into an output directory
"""

from .parser import parse_component_blocks
from .builder import markdown_with_components, markdown_to_tachyons_page, build_site

__all__ = [
    "parse_component_blocks",
    "markdown_with_components",
    "markdown_to_tachyons_page",
    "build_site",
]

__version__ = "0.1.0"
