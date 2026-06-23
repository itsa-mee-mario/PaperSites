from papersites.navbar import render_navbar


def test_each_nav_item_gets_its_own_href():
    # Regression test: the original always rendered the same hardcoded href
    # for every page label, regardless of which page was passed in.
    html = render_navbar([("Github", "https://github.com/a"), ("Blog", "https://blog.example.com")])
    assert 'href="https://github.com/a"' in html
    assert 'href="https://blog.example.com"' in html


def test_default_nav_used_when_none_given():
    html = render_navbar(None)
    assert "<nav" in html


def test_logo_and_href_are_escaped():
    html = render_navbar([("X", 'javascript:alert(1)"')], logo='<script>')
    assert "<script>" not in html
