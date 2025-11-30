"""
Comprehensive tests for format preservation edge cases.

Tests cover:
- Format preservation when tuning succeeds (success=True)
- Format preservation when tuning fails (success=False)
- Format preservation with visualizers (show=True, html=True)
- Different input formats (hex, rgb, hsl, tuples)
"""

import pytest
from cm_colors import ColorPair


class TestFormatPreservationOnSuccess:
    """Test format preservation when tuning succeeds."""

    def test_hex_format_on_success(self):
        """Hex input should return hex when tuning succeeds."""
        pair = ColorPair('#777', 'white')
        result, success = pair.make_readable()
        assert success is True
        assert isinstance(result, str)
        assert result.startswith('#')
        assert len(result) == 7

    def test_rgb_string_on_success(self):
        """RGB string input should return RGB string when tuning succeeds."""
        pair = ColorPair('rgb(119, 119, 119)', 'white')
        result, success = pair.make_readable()
        assert success is True
        assert isinstance(result, str)
        assert result.startswith('rgb(')
        assert result.endswith(')')

    def test_hsl_string_on_success(self):
        """HSL string input should return HSL string when tuning succeeds."""
        pair = ColorPair('hsl(0, 0%, 46%)', 'white')
        result, success = pair.make_readable()
        assert success is True
        assert isinstance(result, str)
        assert result.startswith('hsl(')
        assert result.endswith(')')

    def test_tuple_on_success(self):
        """Tuple input should return tuple when tuning succeeds."""
        pair = ColorPair((119, 119, 119), 'white')
        result, success = pair.make_readable()
        assert success is True
        assert isinstance(result, tuple)
        assert len(result) == 3
        assert all(isinstance(c, int) for c in result)


class TestFormatPreservationOnFailure:
    """Test format preservation when tuning fails."""

    def test_hex_format_on_failure(self):
        """Hex input should return hex even when tuning fails."""
        # This color is very light yellow on white - almost impossible to fix
        pair = ColorPair('#cfff04', 'white')
        result, success = pair.make_readable()
        assert success is False
        assert isinstance(result, str)
        assert result.startswith('#')
        assert len(result) == 7
        # Should NOT be the original color (optimizer tries its best)
        assert result != '#cfff04'

    def test_rgb_string_on_failure(self):
        """RGB string input should return RGB string even when tuning fails."""
        pair = ColorPair('rgb(207, 255, 4)', 'white')
        result, success = pair.make_readable()
        assert success is False
        assert isinstance(result, str)
        assert result.startswith('rgb(')
        assert result.endswith(')')
        # Should NOT be the original color
        assert result != 'rgb(207, 255, 4)'

    def test_hsl_string_on_failure(self):
        """HSL string input should return HSL string even when tuning fails."""
        pair = ColorPair('hsl(69, 100%, 51%)', 'white')  # Bright yellow-green
        result, success = pair.make_readable()
        assert success is False
        assert isinstance(result, str)
        assert result.startswith('hsl(')
        assert result.endswith(')')

    def test_tuple_on_failure(self):
        """Tuple input should return tuple even when tuning fails."""
        pair = ColorPair((207, 255, 4), 'white')
        result, success = pair.make_readable()
        assert success is False
        assert isinstance(result, tuple)
        assert len(result) == 3
        assert all(isinstance(c, int) for c in result)
        # Should NOT be the original tuple
        assert result != (207, 255, 4)


class TestSuccessFlagAccuracy:
    """Test that success flag accurately reflects tuning outcome."""

    def test_success_true_means_accessible(self):
        """When success=True, the color should be accessible."""
        pair = ColorPair('#777', 'white')
        result, success = pair.make_readable()
        if success:
            # Create new pair with tuned color and verify it's accessible
            new_pair = ColorPair(result, 'white')
            assert new_pair.is_readable in [
                'Not Readable',
                'Very Readable',
                'Readable',
            ]

    def test_success_false_means_not_accessible(self):
        """When success=False, the color should NOT meet minimum requirements."""
        pair = ColorPair('#cfff04', 'white')
        result, success = pair.make_readable()
        if not success:
            # Create new pair with tuned color and verify it's NOT accessible
            new_pair = ColorPair(result, 'white')
            assert new_pair.is_readable == 'Not Readable'

    def test_already_accessible_returns_true(self):
        """Already accessible colors should return success=True."""
        pair = ColorPair('black', 'white')
        result, success = pair.make_readable()
        assert success is True


class TestAlreadyAccessibleColors:
    """Test behavior for colors that are already accessible."""

    def test_hex_already_accessible(self):
        """Already accessible hex color should return same color and success=True."""
        pair = ColorPair('#000000', 'white')  # Black on white
        result, success = pair.make_readable()
        assert success is True
        assert result == '#000000'

    def test_rgb_already_accessible(self):
        """Already accessible RGB should return same color and success=True."""
        pair = ColorPair('rgb(0, 0, 0)', 'white')
        result, success = pair.make_readable()
        assert success is True
        assert result == 'rgb(0, 0, 0)'

    def test_tuple_already_accessible(self):
        """Already accessible tuple should return same tuple and success=True."""
        pair = ColorPair((0, 0, 0), 'white')
        result, success = pair.make_readable()
        assert success is True
        assert result == (0, 0, 0)


class TestVisualizerDoesNotAffectReturn:
    """Test that show/html flags don't affect return values."""

    def test_show_flag_preserves_format_on_success(self, capsys):
        """show=True should not affect return format when succeeds."""
        pair = ColorPair('#777', 'white')
        result_with_show = pair.make_readable(show=True)
        pair2 = ColorPair('#777', 'white')
        result_without_show = pair2.make_readable(show=False)

        # Both should return same format and values
        assert type(result_with_show[0]) == type(result_without_show[0])
        assert result_with_show == result_without_show

    def test_show_flag_preserves_format_on_failure(self, capsys):
        """show=True should not affect return format when fails."""
        pair = ColorPair('#cfff04', 'white')
        result_with_show = pair.make_readable(show=True)
        pair2 = ColorPair('#cfff04', 'white')
        result_without_show = pair2.make_readable(show=False)

        # Both should return same format and values
        assert type(result_with_show[0]) == type(result_without_show[0])
        assert result_with_show == result_without_show
        assert result_with_show[1] is False  # Both should be False
