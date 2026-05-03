#!/usr/bin/env python3
"""
A highly opinionated Markdown → HTML converter.
"""

import os
import re
from typing import Callable, Dict, List

import markdown


# --- 1. Parser ---
def parse_component_blocks(text: str) -> List[Dict]:
    """
    Parses text into a list of parts.
    Handles nesting by finding the matching ::end for the current component level.
    """
    parts = []
    text = text.replace("\\n", "\n")

    # Regex to find ::tag or ::tag[argument]
    tag_pattern = re.compile(r"::([a-zA-Z][\w\-]*)(?:\[(.*?)\])?")

    cursor = 0
    while cursor < len(text):
        match = tag_pattern.search(text, cursor)

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
            cursor = tag_start
            continue

        # Immediate insertion component (no ::end required)
        if tag_name == "img":
            parts.append({"type": "image", "path": tag_arg if tag_arg else ""})
            cursor = tag_start
            continue

        # Block components requiring ::end
        depth = 1
        search_pos = tag_start
        content_end = len(text)

        while depth > 0:
            next_tag = tag_pattern.search(text, search_pos)
            if not next_tag:
                content_end = len(text)
                cursor = len(text)
                break

            if next_tag.group(1).lower() == "end":
                depth -= 1
                if depth == 0:
                    content_end = next_tag.start()
                    cursor = next_tag.end()
            elif next_tag.group(1).lower() == "img":
                # ::img is self-contained, doesn't increase depth
                pass
            else:
                depth += 1

            search_pos = next_tag.end()

        inner_content = text[tag_start:content_end].strip()
        parts.append({"type": "component", "name": tag_name, "content": inner_content})

    return parts


# --- 2. CLEAN NAVBAR (simple black/white) ---
def render_navbar(pages: List[str] = None, logo: str = "Shrey") -> str:
    """Simple clean navbar."""
    if pages is None:
        pages = ["Github"]

    nav_links = "".join(
        [
            f'<a href="https://github.com/itsa-mee-mario/" class="f6 link dim dark-gray dib pv2 ph3 mr2 hover-blue">{page}</a>'
            for page in pages
        ]
    )

    return f"""
<nav class="pv3 ph3 ph4-l bg-white black ba b--light-silver">
  <div class="mw8 center flex items-center justify-between">
    <h1 class="f3 fw6 dark-gray mb0 lh-title dib no-underline">{logo}</h1>
    <div class="flex items-center">
      {nav_links}
    </div>
  </div>
</nav>
"""


# ---- 3. COMPONENTS -----


def render_image_grid(image_paths: List[str]) -> str:
    """Renders a grid of images (up to 3 per row)."""
    if not image_paths:
        return ""

    imgs = "".join(
        [
            f'<div class="fl w-100 w-33-ns pa2"><img src="{p}" class="w-100 db br2 ba b--black-10"></div>'
            for p in image_paths
        ]
    )
    return f'<div class="cf mw9 center mb4">{imgs}</div>'


def render_feature(content_html: str, bg_image: str = None) -> str:
    """Simple hero with optional subtle image."""
    bg_style = (
        f"background-image: url('{bg_image}'); background-size: cover;"
        if bg_image
        else ""
    )
    return f"""
<section class="pv5 ph3 ph4-l bg-light-gray" style="{bg_style}">
  <div class="mw8 center tc">
    <div class="f2 f1-l fw1 lh-title measure-wide center mb0 dark-gray">
      {content_html}
    </div>
  </div>
</section>
""".strip()


def render_card(content_html: str, image: str = None) -> str:
    """Clean simple card."""
    img_html = (
        f'<div class="h4 bg-light-silver br2 mb3" style="background-image: url({image}); background-size: cover; background-position: center;"></div>'
        if image
        else ""
    )

    return f"""
<div class="br2 ba b--light-silver bg-white mb4 shadow-1 hover-shadow-3 pa4">
  {img_html}
  <div class="">
    {content_html}
  </div>
</div>
""".strip()


def render_article(content_html: str) -> str:
    """Simple article layout."""
    return f"""
<article class="mw7 mw8-l center ph3 ph4-l pv5">
  <div class="serif f4 lh-copy measure-wide center">
    {content_html}
  </div>
</article>
""".strip()


def render_gallery(items_html: str) -> str:
    """Simple responsive grid."""
    return f"""
<div class="cf ph3">
  <div class="fl w-100 w-50-m w-33-l pa3">
    {items_html}
  </div>
</div>
""".strip()


def render_stats(content_html: str) -> str:
    """Simple stats row."""
    return f"""
<div class="flex flex-wrap justify-center items-center pv4">
  {content_html}
</div>
""".strip()


COMPONENT_RENDERERS = {
    "card": render_card,
    "article": render_article,
    "gallery": render_gallery,  # todo: impl
    "stats": render_stats,  # todo: impl
}


# --- 4. TYPOGRAPHY SYSTEM ---
def add_serif_typography(html: str) -> str:
    """Clean serif typography system."""
    typography = {
        "h1": "f1 f2-l fw1 lh-title mb4 mt0 dark-gray serif",
        "h2": "f2 fw4 lh-title mb4 mt5 dark-gray serif",
        "h3": "f3 fw6 lh-title mb3 mt4 black serif",
        "h4": "f4 fw6 lh-copy mb3 black serif",
        "p": "lh-copy measure f5 black-70 mb4",
        "ul, ol": "list pl4 lh-copy f5 black-70 mb4",
        "blockquote": "serif f4 lh-copy fw1 black-60 mt0 mb5 pl4 bl bw2 b--light-silver",
        "pre": "pa4 mb4 br2 bg-light-gray black-80 f6 overflow-x-auto",
        "code": "f6 bg-light-gray pa1 br1 black-80",
    }

    for tag, classes in typography.items():
        pattern = rf"<{tag}(?=[ >])"

        def replace_tag(match):
            return f'<{tag} class="{classes}"'

        html = re.sub(pattern, replace_tag, html, flags=re.IGNORECASE)

    def enhance_links(match):
        attrs = match.group(1) or ""
        link_class = "link dim fw6 black-70 hover-blue underline"
        if 'class="' in attrs:
            return f"<a{attrs.replace('class="', f'class="{link_class} ')}>"
        return f'<a class="{link_class}"{attrs}>'

    html = re.sub(r"<a([^>]*)>", enhance_links, html, flags=re.IGNORECASE)
    return html


# --- 5. Processing ---
def markdown_with_components(md_text: str) -> str:
    parts = parse_component_blocks(md_text)
    html_parts = []

    # Collect consecutive images to form a grid
    image_buffer = []

    def flush_images():
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
            inner = markdown.markdown(
                part["content"], extensions=["extra", "fenced_code", "tables"]
            )
            styled = add_serif_typography(inner)
            html_parts.append(styled)
        elif part["type"] == "component":
            name = part["name"].lower()
            inner_html = markdown_with_components(part["content"])

            if name == "feature":
                html_parts.append(render_feature(inner_html))
            elif name == "navbar":
                html_parts.append(render_navbar())
            elif name in COMPONENT_RENDERERS:
                html_parts.append(COMPONENT_RENDERERS[name](inner_html))
            else:
                html_parts.append(render_card(inner_html))

    flush_images()
    return "\n".join([p.strip() for p in html_parts])


# --- 6. MINIMAL CLEAN TEMPLATE ---
def create_clean_template(title: str, content: str, pages: List[str] = None) -> str:
    """Simple clean template - no gradients."""
    navbar = render_navbar(pages)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title}</title>
  <link rel="stylesheet" href="https://unpkg.com/tachyons@4.12.0/css/tachyons.min.css"/>
  <style>
    body {{
      background: white;
      font-feature-settings: "liga" 1, "rlig" 1, "calt" 1;
    }}
    .serif {{ font-family: Georgia, Times, serif; }}
    .shadow-1 {{ box-shadow: 0 1px 3px rgba(0,0,0,0.12); }}
    .shadow-3 {{ box-shadow: 0 8px 24px rgba(0,0,0,0.12); }}
    .hover-shadow-3:hover {{ box-shadow: 0 8px 24px rgba(0,0,0,0.18); }}
  </style>
</head>
<body class="w-100 sans-serif">
  {navbar}

  <main class="mw9 center ph3 ph4-l">
    <section class="pt5 pb5">
      {content}
    </section>
  </main>

  <footer class="bg-light-gray gray pv4 ph3 ph5-m ph7-l mt5 bt b--light-silver">
    <div class="mw9 center tc">
      <p class="f6 black-50 mb0">Built With PaperSites <3</p>
    </div>
  </footer>
</body>
</html>"""


def markdown_to_tachyons_page(md_text: str, title: str, pages: List[str] = None) -> str:
    content = markdown_with_components(md_text)
    return create_clean_template(
        title, f'<div class="mw8 center">{content}</div>', pages
    )


# --- 7. CLEAN EXAMPLES ---


def build_site():
    content_dir = "content"
    site_dir = "site"
    os.makedirs(site_dir, exist_ok=True)
    pages_list = None

    with open(os.path.join(site_dir, "index.html"), "w", encoding="utf-8") as f:
        html = markdown_to_tachyons_page(
            """



::feature
# Porfolio. \n

    ::card
    ### Generative Art & Physics Simulations
    A creative playground exploring computational art through Processing. \n
    Projects include physics-based fluid flows, procedurally generated \n
    patterns, algorithmic art, and real-time visualizations \n
    powered by mathematical beauty.

    ::img[processing1.png]
    ::img[processing2.png]
    ::img[processing3.png]
    ::end

    ::card
    ### Paper Sites- a Text-First Static Publishing System
    A custom Markdown-based engine that transforms text into structured web \n
    artifacts (like this website). Guided by a philosophy of minimal, user-respecting\n
    design, it stays out of the way by reducing friction while preserving ownership.
    ::img[pages.png]
    ::img[pages2.png]
    ::end

    ::card
    ### Local Mesh- Decentralized Communication Objects
    esp32 nodes programmed to form a mesh network for off-grid communication \n
    Investigates alternative, independent, infrastructure-light systems and how information \n
    propagates without centralized networks at Ashoka Makerspace.
    ::end

    ::card
    ### Multi-Agent Orchestrator
    An orchestration system that uses an LLM-based decision layer to select, \n
    sequence, and manage tool calls. It maintains memory and system state \n
    to enable context-aware execution across heterogeneous services.
    ::img[mcp1.png]
    ::img[mcp2.png]
    ::end

    ::card
    ### Ledger Terminal- Personal Finance CLI
    A terminal-based portfolio manager built in Go, designed as a focused interface for tracking \n
    and interacting with financial data. Based on the idea that interfaces shape behavior, \n
    it uses the constraints of the terminal to promote clarity, patience, and control in \n
    financial decision-making.
    ::end
::end


            """,
            "Shrey Arora",
            pages_list,
        )
        f.write(html)

    print("📁 site/index.html")


if __name__ == "__main__":
    build_site()
