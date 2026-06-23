"""
Renderers for each `::component` block, plus the immediate-insertion image grid.

`gallery` and `stats` were stubs in the original script (mapped straight to
generic markup with a `# todo: impl` comment and no real layout). Both are
now implemented for real:

  - gallery: a true full-bleed layout instead of squeezing all of its content
    into a single one-third-width column (the original bug).
  - stats: parses `number | label` list items into "big number" stat blocks,
    e.g.

        ::stats
        - 50+ | Projects shipped
        - 3 | Years building agent systems
        ::end
"""

import re
from html import escape
from typing import Callable, Dict, List, Optional

_LI_PATTERN = re.compile(r"<li[^>]*>(.*?)</li>", re.S)


def render_image_grid(image_paths: List[str]) -> str:
    """Renders a grid of images (up to 3 per row)."""
    if not image_paths:
        return ""

    imgs = "".join(
        f'<div class="fl w-100 w-33-ns pa2"><img src="{escape(p)}" class="w-100 db br2 ba b--black-10"></div>'
        for p in image_paths
    )
    return f'<div class="cf mw9 center mb4">{imgs}</div>'


def render_feature(content_html: str, bg_image: Optional[str] = None) -> str:
    """Simple hero with optional subtle image."""
    bg_style = (
        f"background-image: url('{escape(bg_image, quote=True)}'); background-size: cover;"
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


def render_card(content_html: str, image: Optional[str] = None) -> str:
    """Clean simple card."""
    img_html = (
        f'<div class="h4 bg-light-silver br2 mb3" style="background-image: url({escape(image, quote=True)}); '
        f'background-size: cover; background-position: center;"></div>'
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


def render_gallery(content_html: str) -> str:
    """
    Full-bleed gallery section. `content_html` typically already contains one
    or more `render_image_grid` outputs (PaperSites groups every run of
    `::img` tags into rows of 3 automatically) plus any caption text.

    The original implementation wrapped this in a single `w-100 w-33-ns`
    column, which squeezed an entire gallery — grid rows and all — into one
    third of the page width. This just gives it room.
    """
    return f"""
<div class="mw9 center ph3 pv4">
  {content_html}
</div>
""".strip()


def render_stats(content_html: str) -> str:
    """
    Renders a row of "big number" stats from a markdown list where each item
    is formatted as `number | label`, e.g. `- 50+ | Projects shipped`.

    Falls back to displaying the raw content unstyled if no `<li>` items with
    a `|` separator are found, so non-list content doesn't just disappear.
    """
    items = _LI_PATTERN.findall(content_html)
    parsed = [item.split("|", 1) for item in items if "|" in item]

    if not parsed:
        return f'<div class="flex flex-wrap justify-center items-center pv4">{content_html}</div>'

    blocks = "".join(
        f"""
<div class="tc ph4 pv3">
  <div class="f1 fw7 dark-gray serif">{number.strip()}</div>
  <div class="f6 ttu tracked black-50">{label.strip()}</div>
</div>"""
        for number, label in parsed
    )
    return f'<div class="flex flex-wrap justify-center items-center pv4">{blocks}</div>'


COMPONENT_RENDERERS: Dict[str, Callable[[str], str]] = {
    "card": render_card,
    "article": render_article,
    "gallery": render_gallery,
    "stats": render_stats,
}
