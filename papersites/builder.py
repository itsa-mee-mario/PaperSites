"""
Core render pipeline (single string -> HTML) and the multi-page site builder.

Bug fixed here vs. the original script: `build_site()` defined `content_dir =
"content"` but never actually read anything from it — the entire homepage was
a string hardcoded inside `build_site()` itself, so a `content/*.md` file had
no effect on the output. `build_site()` now actually walks `content_dir` and
builds one HTML page per markdown file.
"""

import os
import shutil
from typing import List, Optional

import markdown

from .components import COMPONENT_RENDERERS, render_image_grid, render_feature
from .config import load_site_config, split_front_matter
from .navbar import NavItem
from .parser import parse_component_blocks
from .template import create_clean_template
from .typography import add_serif_typography

MARKDOWN_EXTENSIONS = ["extra", "fenced_code", "tables"]


def markdown_with_components(md_text: str, source_name: str = "<content>") -> str:
    parts = parse_component_blocks(md_text, source_name=source_name)
    html_parts: List[str] = []

    image_buffer: List[str] = []

    def flush_images() -> None:
        if image_buffer:
            html_parts.append(render_image_grid(image_buffer.copy()))
            image_buffer.clear()

    for part in parts:
        if part["type"] == "image":
            image_buffer.append(part["path"])
            if len(image_buffer) == 3:
                flush_images()
            continue

        flush_images()

        if part["type"] == "text":
            inner = markdown.markdown(part["content"], extensions=MARKDOWN_EXTENSIONS)
            html_parts.append(add_serif_typography(inner))
        elif part["type"] == "component":
            name = part["name"].lower()
            inner_html = markdown_with_components(part["content"], source_name=source_name)

            if name == "feature":
                html_parts.append(render_feature(inner_html))
            elif name == "navbar":
                # Page navbars are rendered once by create_clean_template from
                # site.json, so an inline ::navbar block is a no-op rather
                # than rendering a second, unconfigurable navbar.
                continue
            elif name in COMPONENT_RENDERERS:
                html_parts.append(COMPONENT_RENDERERS[name](inner_html))
            else:
                html_parts.append(COMPONENT_RENDERERS["card"](inner_html))

    flush_images()
    return "\n".join(p.strip() for p in html_parts)


def markdown_to_tachyons_page(
    md_text: str,
    title: str,
    pages: Optional[List[NavItem]] = None,
    logo: str = "Site",
    source_name: str = "<content>",
) -> str:
    content = markdown_with_components(md_text, source_name=source_name)
    return create_clean_template(title, f'<div class="mw8 center">{content}</div>', pages, logo=logo)


def build_site(content_dir: str = "content", out_dir: str = "site", config_path: str = None) -> List[str]:
    """
    Build every `*.md` file directly under `content_dir` into a matching
    `*.html` file under `out_dir`. `content/index.md` -> `site/index.html`,
    `content/about.md` -> `site/about.html`, etc.

    Nav, site title, and logo come from `content/site.json` (see config.py).
    A per-page `title:` front matter entry overrides the site title for that
    page. An `assets/` directory next to the markdown files, if present, is
    copied into `out_dir/assets` as-is (images, etc.).

    Returns the list of output file paths written.
    """
    if not os.path.isdir(content_dir):
        raise FileNotFoundError(f"content directory not found: {content_dir}")

    os.makedirs(out_dir, exist_ok=True)
    config = load_site_config(content_dir, config_path)

    md_files = sorted(f for f in os.listdir(content_dir) if f.endswith(".md"))
    if not md_files:
        raise FileNotFoundError(f"no .md files found in {content_dir}")

    written: List[str] = []
    for filename in md_files:
        src_path = os.path.join(content_dir, filename)
        with open(src_path, "r", encoding="utf-8") as f:
            raw = f.read()

        front, body = split_front_matter(raw)
        page_title = front.get("title", config["title"])

        html = markdown_to_tachyons_page(
            body,
            page_title,
            pages=config["nav"],
            logo=config["logo"],
            source_name=src_path,
        )

        out_name = "index.html" if filename == "index.md" else os.path.splitext(filename)[0] + ".html"
        out_path = os.path.join(out_dir, out_name)
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(html)
        written.append(out_path)

    assets_dir = os.path.join(content_dir, "assets")
    if os.path.isdir(assets_dir):
        out_assets = os.path.join(out_dir, "assets")
        shutil.copytree(assets_dir, out_assets, dirs_exist_ok=True)

    return written
