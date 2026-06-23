"""
Site-wide config (`site.json`) and per-page front matter.

Kept deliberately small: no YAML dependency, no schema validation framework —
just enough structure to configure a nav bar and per-page titles without
hardcoding them into the generator.

site.json:
    {
      "title": "Shrey Arora",
      "logo": "Shrey",
      "nav": [["Github", "https://github.com/your-username"]]
    }

Front matter (optional, top of any .md file):
    ---
    title: About
    ---
    # page content...
"""

import json
import os
from typing import Dict, List, Tuple

DEFAULT_CONFIG: Dict = {
    "title": "PaperSites",
    "logo": "Site",
    "nav": [["Github", "#"]],
}


def load_site_config(content_dir: str, config_path: str = None) -> Dict:
    path = config_path or os.path.join(content_dir, "site.json")
    if not os.path.isfile(path):
        return dict(DEFAULT_CONFIG)

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    config = dict(DEFAULT_CONFIG)
    config.update(data)
    # JSON gives lists, not tuples — normalize the nav shape either way.
    config["nav"] = [tuple(item) for item in config.get("nav", [])]
    return config


def split_front_matter(text: str) -> Tuple[Dict, str]:
    """
    Splits a leading `---\\nkey: value\\n---` block off of `text`.
    Returns (front_matter_dict, remaining_body). If there's no front matter
    block, returns ({}, text) unchanged.
    """
    if not text.startswith("---"):
        return {}, text

    lines = text.split("\n")
    if lines[0].strip() != "---":
        return {}, text

    front: Dict[str, str] = {}
    i = 1
    while i < len(lines) and lines[i].strip() != "---":
        line = lines[i]
        if ":" in line:
            key, _, value = line.partition(":")
            front[key.strip()] = value.strip()
        i += 1

    if i >= len(lines):
        # No closing '---' found — treat the whole thing as body, not front matter.
        return {}, text

    body = "\n".join(lines[i + 1 :])
    return front, body
