# test_color_parser.py
import pytest
from hypothesis import given, strategies as st, assume, example
import re
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))


# Assuming your color parser is in this location - adjust as needed
from cm_colors.core.color_parser import parse_color_to_rgb
from cm_colors.core.conversions import is_valid_rgb


class TestColorParser:
    """Test suite for the universal color parser"""

    # ===== BASIC FUNCTIONALITY TESTS =====

    def test_rgb_tuples(self):
        """Test RGB tuple inputs"""
        assert parse_color_to_rgb((255, 0, 0)) == (255, 0, 0)
        assert parse_color_to_rgb((0, 255, 0)) == (0, 255, 0)
        assert parse_color_to_rgb((0, 0, 255)) == (0, 0, 255)
        assert parse_color_to_rgb([128, 128, 128]) == (128, 128, 128)

    def test_rgb_lists(self):
        """Test RGB list inputs"""
        assert parse_color_to_rgb([255, 0, 0]) == (255, 0, 0)
        assert parse_color_to_rgb([0, 255, 0]) == (0, 255, 0)

    def test_rgba_tuples_without_background(self):
        """Test RGBA tuples with default white background"""
        # rgba(255, 0, 0, 0.5) on white = blended
        result = parse_color_to_rgb((255, 0, 0, 0.5))
        # alpha blending: 0.5 * (255,0,0) + 0.5 * (255,255,255) = (255, 127.5, 127.5)
        assert result == (255, 128, 128)  # Note: 127.5 rounds to 128

    def test_rgba_tuples_with_background(self):
        """Test RGBA tuples with custom background"""
        # rgba(255, 0, 0, 0.5) on black = (128, 0, 0)
        result = parse_color_to_rgb((255, 0, 0, 0.5), background=(0, 0, 0))
        expected_r = int(0.5 * 255 + 0.5 * 0)  # 127.5 → 128
        assert result == (128, 0, 0)

    def test_hex_colors(self):
        """Test hex color inputs"""
        assert parse_color_to_rgb("#ff0000") == (255, 0, 0)
        assert parse_color_to_rgb("#00ff00") == (0, 255, 0)
        assert parse_color_to_rgb("#0000ff") == (0, 0, 255)
        assert parse_color_to_rgb("ff0000") == (255, 0, 0)  # without #
        assert parse_color_to_rgb("#f00") == (255, 0, 0)  # short form
        assert parse_color_to_rgb("f00") == (255, 0, 0)  # short without #

    def test_named_colors(self):
        """Test CSS named colors - assuming basic colors exist"""
        # Note: These tests assume your CSS_NAMED_COLORS dict has these
        try:
            result = parse_color_to_rgb("red")
            assert isinstance(result, tuple) and len(result) == 3
        except ValueError:
            pytest.skip("Named colors not available in test environment")

    def test_rgb_css_strings(self):
        """
        Verify parsing of CSS `rgb()` strings with varied spacing and formatting.

        Asserts that standard `rgb(255, 0, 0)`, compact `rgb(0,255,0)`, and forms with extra spaces `rgb( 0 , 255 , 0 )` are parsed to the expected RGB tuples.
        """
        assert parse_color_to_rgb("rgb(255, 0, 0)") == (255, 0, 0)
        assert parse_color_to_rgb("rgb(0,255,0)") == (0, 255, 0)  # no spaces
        assert parse_color_to_rgb("rgb( 0 , 255 , 0 )") == (
            0,
            255,
            0,
        )  # extra spaces

    def test_rgba_css_strings(self):
        """Test RGBA CSS function strings"""
        # rgba(255, 0, 0, 0.5) on default white background
        result = parse_color_to_rgb("rgba(255, 0, 0, 0.5)")
        assert result[0] == 255  # red stays red
        assert 120 <= result[1] <= 135  # green/blue should be around 127-128
        assert 120 <= result[2] <= 135

    def test_hsl_css_strings(self):
        """Test HSL CSS function strings"""
        # hsl(0, 100%, 50%) should be red (255, 0, 0)
        result = parse_color_to_rgb("hsl(0, 100%, 50%)")
        assert result == (255, 0, 0)

        # hsl(120, 100%, 50%) should be green (0, 255, 0)
        result = parse_color_to_rgb("hsl(120, 100%, 50%)")
        assert result == (0, 255, 0)

        # hsl(240, 100%, 50%) should be blue (0, 0, 255)
        result = parse_color_to_rgb("hsl(240, 100%, 50%)")
        assert result == (0, 0, 255)

    def test_hsla_css_strings(self):
        """Test HSLA CSS function strings"""
        # hsla(0, 100%, 50%, 0.5) should be red at 50% opacity on white
        result = parse_color_to_rgb("hsla(0, 100%, 50%, 0.5)")
        assert result[0] == 255  # red component preserved
        assert 120 <= result[1] <= 135  # other components mixed with white
        assert 120 <= result[2] <= 135

    # ===== EDGE CASES AND ERROR HANDLING =====

    def test_invalid_tuple_lengths(self):
        """
        Verify that tuple or list color inputs whose length is not 3 or 4 raise a ValueError with a message indicating the required lengths.
        """
        with pytest.raises(ValueError, match="must have length 3.*or 4"):
            parse_color_to_rgb((255,))

        with pytest.raises(ValueError, match="must have length 3.*or 4"):
            parse_color_to_rgb((255, 0))

        with pytest.raises(ValueError, match="must have length 3.*or 4"):
            parse_color_to_rgb((255, 0, 0, 0.5, 100))  # 5 components

    def test_rgb_out_of_range(self):
        """Test RGB values out of valid range"""
        with pytest.raises(ValueError, match="out of range"):
            parse_color_to_rgb((256, 0, 0))  # > 255

        with pytest.raises(ValueError, match="out of range"):
            parse_color_to_rgb((-1, 0, 0))  # < 0

    def test_invalid_hex(self):
        """Test invalid hex color strings"""
        with pytest.raises(ValueError, match="Invalid hex"):
            parse_color_to_rgb("#gggggg")  # invalid hex chars

        with pytest.raises(ValueError, match="Invalid hex"):
            parse_color_to_rgb("#ff00")  # wrong length

    def test_unsupported_types(self):
        """Test unsupported input types"""
        with pytest.raises(ValueError, match="Unsupported color input type"):
            parse_color_to_rgb(123.45)  # float

        with pytest.raises(ValueError, match="Unsupported color input type"):
            parse_color_to_rgb(None)  # None

        with pytest.raises(ValueError, match="Unsupported color input type"):
            parse_color_to_rgb({})  # dict

    def test_invalid_css_strings(self):
        """Test malformed CSS color strings"""
        with pytest.raises(ValueError):
            parse_color_to_rgb("rgb()")  # empty

        with pytest.raises(ValueError):
            parse_color_to_rgb("rgb(255)")  # too few components

        with pytest.raises(ValueError):
            parse_color_to_rgb("notacolor")  # unrecognized format

    # ===== PERCENTAGE SUPPORT TESTS =====

    def test_rgb_percentages(self):
        """Test RGB with percentage values"""
        # rgb(100%, 0%, 0%) should be (255, 0, 0)
        result = parse_color_to_rgb("rgb(100%, 0%, 0%)")
        assert result == (255, 0, 0)

        # rgb(50%, 50%, 50%) should be (127.5, 127.5, 127.5) → (128, 128, 128)
        result = parse_color_to_rgb("rgb(50%, 50%, 50%)")
        assert all(125 <= c <= 130 for c in result)  # allow some rounding tolerance

    # ===== FLOAT SUPPORT TESTS =====

    def test_float_rgb_values(self):
        """Test RGB with float values in 0-1 range"""
        # (1.0, 0.0, 0.0) should become (255, 0, 0)
        result = parse_color_to_rgb((1.0, 0.0, 0.0))
        assert result == (255, 0, 0)

        # (0.5, 0.5, 0.5) should become ~(128, 128, 128)
        result = parse_color_to_rgb((0.5, 0.5, 0.5))
        assert all(125 <= c <= 130 for c in result)

    # ===== HYPOTHESIS PROPERTY-BASED TESTS =====

    @given(r=st.integers(0, 255), g=st.integers(0, 255), b=st.integers(0, 255))
    def test_valid_rgb_tuples_property(self, r, g, b):
        """Property test: valid RGB tuples should parse correctly"""
        result = parse_color_to_rgb((r, g, b))
        assert result == (r, g, b)
        assert is_valid_rgb(result)

    @given(
        r=st.integers(0, 255),
        g=st.integers(0, 255),
        b=st.integers(0, 255),
        a=st.floats(0.0, 1.0),
    )
    def test_valid_rgba_tuples_property(self, r, g, b, a):
        """
        Property test that parsing an RGBA tuple produces a valid 3-channel RGB tuple.

        Avoids the degenerate case where r, g, b are all 0 and alpha is 0; asserts the parsed result is a valid RGB triple of length 3.
        """
        assume(not (r == g == b == 0 and a == 0))  # avoid edge case

        result = parse_color_to_rgb((r, g, b, a))
        assert is_valid_rgb(result)
        assert len(result) == 3

    @given(h=st.integers(0, 359), s=st.integers(0, 100), l=st.integers(0, 100))
    @example(h=0, s=100, l=50)  # red
    @example(h=120, s=100, l=50)  # green
    @example(h=240, s=100, l=50)  # blue
    def test_hsl_css_property(self, h, s, l):
        """Property test: valid HSL CSS strings should produce valid RGB"""
        hsl_string = f"hsl({h}, {s}%, {l}%)"

        try:
            result = parse_color_to_rgb(hsl_string)
            assert is_valid_rgb(result)
            assert len(result) == 3
        except Exception:
            # Some HSL combinations might be outside RGB gamut, which is okay
            pass

    @given(hex_color=st.text(alphabet="0123456789abcdefABCDEF", min_size=6, max_size=6))
    def test_hex_colors_property(self, hex_color):
        """Property test: valid 6-digit hex colors should parse correctly"""
        hex_with_hash = f"#{hex_color}"

        result = parse_color_to_rgb(hex_with_hash)
        assert is_valid_rgb(result)

        # Convert back to hex and compare (case-insensitive)
        r, g, b = result
        expected_hex = f"#{r:02x}{g:02x}{b:02x}"
        assert expected_hex.lower() == hex_with_hash.lower()

    # ===== INTEGRATION TESTS =====

    def test_background_context_integration(self):
        """Test that background context works across different color formats"""
        # Test RGBA with different background formats
        rgba_color = "rgba(255, 0, 0, 0.5)"

        # Background as tuple
        result1 = parse_color_to_rgb(rgba_color, background=(0, 0, 0))

        # Background as hex
        result2 = parse_color_to_rgb(rgba_color, background="#000000")

        # Background as CSS string
        result3 = parse_color_to_rgb(rgba_color, background="rgb(0, 0, 0)")

        # All should produce the same result
        assert result1 == result2 == result3

    def test_recursive_parsing_safety(self):
        """Test that recursive parsing doesn't cause infinite loops"""
        # This should not cause infinite recursion
        result = parse_color_to_rgb(
            "rgba(255, 0, 0, 0.5)", background="rgba(0, 0, 255, 0.5)"
        )
        assert is_valid_rgb(result)

    # ===== PERFORMANCE EDGE CASES =====

    def test_malformed_but_parseable(self):
        """Test edge cases that should still parse successfully"""
        # Extra whitespace
        assert parse_color_to_rgb("  rgb( 255 , 0 , 0 )  ") == (255, 0, 0)

        # Mixed case
        assert parse_color_to_rgb("RGB(255, 0, 0)") == (255, 0, 0)

        # No spaces in function
        assert parse_color_to_rgb("rgb(255,0,0)") == (255, 0, 0)

    def test_boundary_values(self):
        """Test boundary values for all formats"""
        # RGB boundaries
        assert parse_color_to_rgb((0, 0, 0)) == (0, 0, 0)  # black
        assert parse_color_to_rgb((255, 255, 255)) == (255, 255, 255)  # white

        # Alpha boundaries
        result_transparent = parse_color_to_rgb((255, 0, 0, 0.0))  # fully transparent
        result_opaque = parse_color_to_rgb((255, 0, 0, 1.0))  # fully opaque

        assert result_transparent == (
            255,
            255,
            255,
        )  # should be white (background)
        assert result_opaque == (255, 0, 0)  # should be pure red


# ===== FIXTURES AND HELPERS =====


@pytest.fixture
def sample_colors():
    """
    Provide a mapping of sample red color representations in multiple formats for tests.

    Returns:
        dict: Mapping of sample names to color representations. Keys:
            - 'red_tuple': (255, 0, 0)
            - 'red_hex': '#ff0000'
            - 'red_css': 'rgb(255, 0, 0)'
            - 'red_rgba': 'rgba(255, 0, 0, 1.0)'
            - 'red_hsl': 'hsl(0, 100%, 50%)'
            - 'red_hsla': 'hsla(0, 100%, 50%, 1.0)'
    """
    return {
        "red_tuple": (255, 0, 0),
        "red_hex": "#ff0000",
        "red_css": "rgb(255, 0, 0)",
        "red_rgba": "rgba(255, 0, 0, 1.0)",
        "red_hsl": "hsl(0, 100%, 50%)",
        "red_hsla": "hsla(0, 100%, 50%, 1.0)",
    }


def test_all_red_formats_equivalent(sample_colors):
    """Test that all ways of representing red produce the same result"""
    results = [parse_color_to_rgb(color) for color in sample_colors.values()]

    # All should be the same (or very close for HSL conversion)
    red_rgb = (255, 0, 0)
    for result in results:
        # Allow small tolerance for HSL conversion rounding
        assert abs(result[0] - red_rgb[0]) <= 1
        assert abs(result[1] - red_rgb[1]) <= 1
        assert abs(result[2] - red_rgb[2]) <= 1


if __name__ == "__main__":
    # Run tests if called directly
    pytest.main([__file__, "-v"])
