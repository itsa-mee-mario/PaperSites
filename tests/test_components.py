from papersites.components import render_gallery, render_stats, render_image_grid


def test_stats_parses_number_and_label():
    content_html = "<ul><li>50+ | Projects shipped</li><li>3 | Years</li></ul>"
    html = render_stats(content_html)
    assert "50+" in html
    assert "Projects shipped" in html
    assert "3" in html
    assert "Years" in html


def test_stats_falls_back_when_no_pipe_items():
    html = render_stats("<p>no list here</p>")
    assert "no list here" in html


def test_gallery_does_not_constrain_to_one_third_width():
    # Regression test: the original wrapped gallery content in a
    # `w-100 w-50-m w-33-l` cell, squeezing the whole gallery (including
    # already-gridded image rows) into one third of the page.
    html = render_gallery("<div>content</div>")
    assert "w-33-l" not in html


def test_image_grid_escapes_path():
    html = render_image_grid(['a.png" onerror="alert(1)'])
    assert "onerror=\"alert(1)\"" not in html
    assert "&quot;" in html
