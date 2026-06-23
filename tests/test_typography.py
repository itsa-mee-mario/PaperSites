from papersites.typography import add_serif_typography


def test_ul_and_ol_both_get_classes():
    # Regression test: the original dict key "ul, ol" built the regex
    # `<ul, ol(?=[ >])`, which never matches real <ul>/<ol> tags.
    html = "<ul><li>one</li></ul><ol><li>two</li></ol>"
    result = add_serif_typography(html)
    assert '<ul class="' in result
    assert '<ol class="' in result


def test_headings_get_classes():
    result = add_serif_typography("<h1>Title</h1>")
    assert '<h1 class="' in result


def test_inline_code_gets_class():
    result = add_serif_typography("<p>see <code>x = 1</code></p>")
    assert '<code class="' in result


def test_fenced_code_block_code_tag_not_double_styled():
    # python-markdown emits fenced code as <pre><code ...> with no gap.
    html = '<pre><code class="language-python">x = 1</code></pre>'
    result = add_serif_typography(html)
    # <pre> gets styled, but the adjacent <code> should not get the inline
    # pill styling stacked on top of it.
    assert '<pre class="' in result
    assert 'class="f6 bg-light-gray pa1 br1 black-80"' not in result


def test_links_get_class():
    result = add_serif_typography('<a href="https://example.com">link</a>')
    assert "link dim fw6" in result
