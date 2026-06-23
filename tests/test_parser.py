from papersites.parser import parse_component_blocks


def test_plain_text_only():
    parts = parse_component_blocks("just some text")
    assert parts == [{"type": "text", "content": "just some text"}]


def test_simple_component():
    parts = parse_component_blocks("::card\nhello\n::end")
    assert parts == [{"type": "component", "name": "card", "content": "hello"}]


def test_img_is_immediate_no_end_required():
    parts = parse_component_blocks("before ::img[a.png] after")
    assert parts == [
        {"type": "text", "content": "before"},
        {"type": "image", "path": "a.png"},
        {"type": "text", "content": "after"},
    ]


def test_nested_same_name_components():
    text = "::card\nouter\n::card\ninner\n::end\nstill outer\n::end"
    parts = parse_component_blocks(text)
    assert len(parts) == 1
    assert parts[0]["name"] == "card"
    assert "::card" in parts[0]["content"]  # inner block preserved for recursive parsing


def test_img_inside_block_does_not_affect_nesting_depth():
    text = "::gallery\n::img[a.png]\n::img[b.png]\n::end"
    parts = parse_component_blocks(text)
    assert len(parts) == 1
    assert parts[0]["type"] == "component"
    assert parts[0]["name"] == "gallery"


def test_unclosed_component_does_not_crash_and_warns(capsys):
    parts = parse_component_blocks("::card\nnever closed")
    assert len(parts) == 1
    assert parts[0]["content"] == "never closed"
    captured = capsys.readouterr()
    assert "no matching" in captured.err


def test_tag_syntax_mentioned_in_inline_code_is_not_parsed_as_a_real_tag():
    # Regression test: documenting the syntax itself (e.g. in a README-style
    # paragraph) used to be misread as a real, unclosed component.
    text = "::card\nUse `::gallery` and `::img[a.png]` for images.\n::end"
    parts = parse_component_blocks(text)
    assert len(parts) == 1
    assert parts[0]["type"] == "component"
    assert parts[0]["name"] == "card"
    assert "`::gallery`" in parts[0]["content"]


def test_tag_syntax_mentioned_in_fenced_code_is_not_parsed_as_a_real_tag():
    text = "::card\n```\n::img[a.png]\n```\n::end"
    parts = parse_component_blocks(text)
    assert len(parts) == 1
    assert parts[0]["name"] == "card"
