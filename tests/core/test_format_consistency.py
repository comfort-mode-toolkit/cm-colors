import pytest
from cm_colors import ColorPair


def test_hex_format_preserved():
    pair = ColorPair("#777", "white")
    result, success = pair.make_readable()
    assert isinstance(result, str)
    assert result.startswith("#")
    # Should be 7 chars (#RRGGBB)
    assert len(result) == 7


def test_rgb_string_format_preserved():
    pair = ColorPair("rgb(119, 119, 119)", "white")
    result, success = pair.make_readable()
    assert isinstance(result, str)
    assert result.startswith("rgb(")
    assert result.endswith(")")


def test_hsl_string_format_preserved():
    pair = ColorPair("hsl(0, 0%, 46%)", "white")
    result, success = pair.make_readable()
    assert isinstance(result, str)
    assert result.startswith("hsl(")
    assert result.endswith(")")


def test_named_color_to_hex():
    pair = ColorPair("grey", "white")
    result, success = pair.make_readable()
    assert isinstance(result, str)
    assert result.startswith("#")


def test_rgb_tuple_format_preserved():
    pair = ColorPair((119, 119, 119), "white")
    result, success = pair.make_readable()
    assert isinstance(result, tuple)
    assert len(result) == 3
    assert all(isinstance(c, int) for c in result)


def test_rgba_string_defaults_to_hex():
    # Since we don't support returning RGBA yet (as per implementation details),
    # it should default to Hex
    pair = ColorPair("rgba(119, 119, 119, 1)", "white")
    result, success = pair.make_readable()
    assert isinstance(result, str)
    assert result.startswith("#")
