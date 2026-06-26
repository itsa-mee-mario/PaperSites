<img width="457" height="326" alt="image" src="https://github.com/user-attachments/assets/b983961e-b04d-4db3-bfba-03d9e74a37a8" />


A small, opinionated Markdown → HTML static site generator with a custom
component syntax (`::card`, `::feature`, `::gallery`, `::stats`, `::img[...]`)
and a clean, minimal Tachyons-based default theme.

```
::feature
# Hello, world.
::end

::stats
- 12 | Repos
- 3  | Years writing Go
::end

::card
### A project
Some description, with regular **markdown** inside.
::img[assets/screenshot.png]
::end
```

→ a static `index.html`, no JS framework, no build step beyond Python.

## Why

Most static-site generators make you choose between "plain markdown" (no
layout control) and "full templating language" (Jinja/Liquid, front-matter
schemas, partials). PaperSites sits in between: a tiny block syntax for
layout, regular markdown for everything else, and one Python package you can
actually read end to end in an afternoon.

## Install

```bash
git clone https://github.com/<you>/papersites.git
cd papersites
pip install -e ".[dev]"
```

Requires Python 3.9+.

## Quickstart

```bash
papersites build              # reads ./content/*.md, writes ./site/
papersites serve               # serve ./site/ at http://localhost:8000
```

A working example lives in [`content/`](content) — run `papersites build`
and open `site/index.html` to see it rendered.

### Project layout

```
content/
  site.json     # site title, logo, nav links
  index.md      # -> site/index.html
  about.md      # -> site/about.html
  assets/       # copied to site/assets/ as-is
```

`content/site.json`:

```json
{
  "title": "Your Name",
  "logo": "Your Name",
  "nav": [["Github", "https://github.com/your-username"]]
}
```

Each markdown file may start with simple front matter to override the page
title:

```markdown
---
title: About me
---

# About

...
```

## Component syntax

| Syntax | Behavior |
|---|---|
| `::img[path]` | Inserts an image. Three consecutive `::img` tags auto-group into a 3-column row. |
| `::feature ... ::end` | Full-width hero section. |
| `::card ... ::end` | Bordered card with shadow. |
| `::article ... ::end` | Centered long-form text column. |
| `::gallery ... ::end` | Full-bleed section, typically wrapping a run of `::img` tags. |
| `::stats ... ::end` | Parses a markdown list of `number \| label` items into "big number" stat blocks. |
| any other `::tag` | Falls back to the `card` renderer, so unknown tags still degrade gracefully. |

Everything inside a block is itself parsed recursively — components can
nest, and the text in between is run through regular markdown (`extra`,
`fenced_code`, `tables`).

Mentioning the syntax itself in inline code or fenced code blocks (like the
table above, or this README) is parsed as plain text, not a real tag.

## Architecture

```
papersites/
  parser.py      ::tag[...] ... ::end  ->  list of {text | image | component} parts
  components.py  one render_* function per component, + COMPONENT_RENDERERS
  navbar.py      site navbar
  typography.py  Tachyons class injection over raw markdown HTML
  template.py    full-page HTML shell
  builder.py     markdown_with_components (single page) + build_site (content/ -> site/)
  config.py      site.json + per-page front matter
  cli.py         `papersites build` / `papersites serve`
```

`parser.py` has no knowledge of HTML or rendering; `components.py` has no
knowledge of the block syntax. `builder.py` is the only place that wires the
two together, which is what makes each half independently testable (see
`tests/`).

## Testing

```bash
pytest
```

The suite includes regression tests for three real bugs found while
hardening this from a single script into a package:

- a typography selector bug where `<ul>`/`<ol>` silently never received
  their list classes,
- a navbar bug where every nav link rendered with the same hardcoded `href`
  regardless of label,
- a parser bug where documenting the `::tag` syntax itself (in backticks)
  was misread as a real, unclosed component.


## License

MIT — see [LICENSE](LICENSE).
