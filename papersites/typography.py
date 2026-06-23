"""
Adds Tachyons utility classes to the raw HTML produced by `markdown.markdown`.

Bug fixed here vs. the original script: the typography table used a combined
dict key `"ul, ol"` and then built a regex as `f"<{tag}(?=[ >])"`, which
produced the literal pattern `<ul, ol(?=[ >])`. That string never matches a
real `<ul>` or `<ol>` tag, so list styling silently never applied. Each tag
now gets its own entry.
"""

import re
from typing import Dict

TYPOGRAPHY_CLASSES: Dict[str, str] = {
    "h1": "f1 f2-l fw1 lh-title mb4 mt0 dark-gray serif",
    "h2": "f2 fw4 lh-title mb4 mt5 dark-gray serif",
    "h3": "f3 fw6 lh-title mb3 mt4 black serif",
    "h4": "f4 fw6 lh-copy mb3 black serif",
    "p": "lh-copy measure f5 black-70 mb4",
    "ul": "list pl4 lh-copy f5 black-70 mb4",
    "ol": "list pl4 lh-copy f5 black-70 mb4",
    "blockquote": "serif f4 lh-copy fw1 black-60 mt0 mb5 pl4 bl bw2 b--light-silver",
    "pre": "pa4 mb4 br2 bg-light-gray black-80 f6 overflow-x-auto",
}

INLINE_CODE_CLASS = "f6 bg-light-gray pa1 br1 black-80"
LINK_CLASS = "link dim fw6 black-70 hover-blue underline"


def add_serif_typography(html: str) -> str:
    """Apply the PaperSites typographic system to a fragment of HTML."""
    # Inline `code` gets its own padded pill, but `<pre><code>` (fenced code
    # blocks) shouldn't double up on the background/padding `<pre>` already
    # has. python-markdown emits fenced code as `<pre><code ...>` with no
    # whitespace between the tags, so a negative lookbehind distinguishes
    # them — this MUST run before the `pre` tag below gets its own class
    # injected, or the literal "<pre>" the lookbehind checks for no longer
    # immediately precedes "<code" by the time we get to it.
    html = re.sub(
        r"(?<!<pre>)<code(?=[ >])",
        f'<code class="{INLINE_CODE_CLASS}"',
        html,
        flags=re.IGNORECASE,
    )

    for tag, classes in TYPOGRAPHY_CLASSES.items():
        pattern = rf"<{tag}(?=[ >])"
        html = re.sub(
            pattern,
            lambda m, t=tag, c=classes: f'<{t} class="{c}"',
            html,
            flags=re.IGNORECASE,
        )

    def enhance_links(match: "re.Match[str]") -> str:
        attrs = match.group(1) or ""
        if 'class="' in attrs:
            return f"<a{attrs.replace('class=\"', f'class=\"{LINK_CLASS} ')}>"
        return f'<a class="{LINK_CLASS}"{attrs}>'

    html = re.sub(r"<a([^>]*)>", enhance_links, html, flags=re.IGNORECASE)
    return html
