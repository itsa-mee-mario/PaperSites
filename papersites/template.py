"""Minimal clean page template (Tachyons, no gradients)."""

from html import escape
from typing import List, Optional

from .navbar import render_navbar, NavItem


def create_clean_template(
    title: str,
    content: str,
    pages: Optional[List[NavItem]] = None,
    logo: str = "Shrey",
) -> str:
    navbar = render_navbar(pages, logo=logo)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{escape(title)}</title>
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
      <p class="f6 black-50 mb0">Built with PaperSites</p>
    </div>
  </footer>
</body>
</html>"""
