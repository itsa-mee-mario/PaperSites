"""
Navbar rendering.

Bug fixed here vs. the original script: `render_navbar` took a list of page
*labels* but rendered every link with the same hardcoded
`href="https://github.com/.../"`, regardless of label — so a navbar with
"Github", "Blog", "Contact" would point all three links at the same place.
It now takes (label, href) pairs.
"""

from html import escape
from typing import List, Tuple

NavItem = Tuple[str, str]

DEFAULT_NAV: List[NavItem] = [("Github", "#")]


def render_navbar(pages: List[NavItem] = None, logo: str = "Shrey") -> str:
    """Simple clean navbar. `pages` is a list of (label, href) tuples."""
    if not pages:
        pages = DEFAULT_NAV

    nav_links = "".join(
        f'<a href="{escape(href)}" class="f6 link dim dark-gray dib pv2 ph3 mr2 hover-blue">{escape(label)}</a>'
        for label, href in pages
    )

    return f"""
<nav class="pv3 ph3 ph4-l bg-white black ba b--light-silver">
  <div class="mw8 center flex items-center justify-between">
    <h1 class="f3 fw6 dark-gray mb0 lh-title dib no-underline">{escape(logo)}</h1>
    <div class="flex items-center">
      {nav_links}
    </div>
  </div>
</nav>
"""
