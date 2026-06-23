import json
import os

from papersites.builder import build_site


def _write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


def test_build_site_reads_from_content_dir(tmp_path):
    content_dir = tmp_path / "content"
    out_dir = tmp_path / "site"

    _write(
        str(content_dir / "index.md"),
        "---\ntitle: Home\n---\n::card\nHello world\n::end",
    )
    _write(str(content_dir / "about.md"), "# About me")
    _write(
        str(content_dir / "site.json"),
        json.dumps({"title": "Test Site", "logo": "T", "nav": [["Home", "/"]]}),
    )

    written = build_site(str(content_dir), str(out_dir))

    assert len(written) == 2
    assert (out_dir / "index.html").exists()
    assert (out_dir / "about.html").exists()

    index_html = (out_dir / "index.html").read_text(encoding="utf-8")
    assert "Hello world" in index_html
    assert "<title>Home</title>" in index_html  # front matter title wins
    assert "Home</a>" in index_html  # nav from site.json


def test_build_site_copies_assets(tmp_path):
    content_dir = tmp_path / "content"
    out_dir = tmp_path / "site"
    _write(str(content_dir / "index.md"), "hello")
    _write(str(content_dir / "assets" / "pic.svg"), "<svg></svg>")

    build_site(str(content_dir), str(out_dir))

    assert (out_dir / "assets" / "pic.svg").exists()


def test_build_site_raises_on_missing_content_dir(tmp_path):
    import pytest

    with pytest.raises(FileNotFoundError):
        build_site(str(tmp_path / "nope"), str(tmp_path / "site"))
