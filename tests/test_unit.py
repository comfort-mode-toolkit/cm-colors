"""
Unit Tests for Individual CMColors Methods

Tests each public method in isolation with comprehensive input/output verification.
"""

import pytest
from cm_colors import CMColors


class TestCMColorsUnitTests:
    def setup_method(self):
        self.cm = CMColors()

    @pytest.mark.parametrize(
        'input_color,expected',
        [
            ('#000000', (0, 0, 0)),
            ('#ffffff', (255, 255, 255)),
            ('#ff0000', (255, 0, 0)),
            ('rgb(0, 0, 0)', (0, 0, 0)),
            ('rgb(255, 255, 255)', (255, 255, 255)),
        ],
    )
    def test_parse_to_rgb_valid_inputs(self, input_color, expected):
        assert self.cm.parse_to_rgb(input_color) == expected

    # @pytest.mark.parametrize("invalid_input", [
    #     "notacolor", "#gggggg", "rgb(256, 0, 0)", "rgb(-1, 0, 0)",
    #     "#12345", "rgb(0, 0)", "hsl(0, 100%, 50%)", "", None
    # ])
    # def test_parse_to_rgb_invalid_inputs(self, invalid_input):
    #     with pytest.raises(ValueError):
    #         self.cm.parse_to_rgb(invalid_input)

    @pytest.mark.parametrize(
        'text_rgb,bg_rgb,expected_min',
        [
            ((0, 0, 0), (255, 255, 255), 20.9),  # Black on white
            ((255, 255, 255), (0, 0, 0), 20.9),  # White on black
            ((128, 128, 128), (128, 128, 128), 0.9),  # Same colors
        ],
    )
    def test_contrast_ratio_known_values(self, text_rgb, bg_rgb, expected_min):
        result = self.cm.contrast_ratio(text_rgb, bg_rgb)
        assert result >= expected_min
        assert result <= 21.0  # Maximum possible contrast

    @pytest.mark.parametrize(
        'text_rgb,bg_rgb,large_text,expected',
        [
            ((0, 0, 0), (255, 255, 255), False, 'AAA'),
            ((0, 0, 0), (255, 255, 255), True, 'AAA'),
            ((200, 200, 200), (255, 255, 255), False, 'FAIL'),
            ((200, 200, 200), (255, 255, 255), True, 'FAIL'),
        ],
    )
    def test_wcag_level_classifications(
        self, text_rgb, bg_rgb, large_text, expected
    ):
        result = self.cm.wcag_level(text_rgb, bg_rgb, large_text)
        assert result == expected
