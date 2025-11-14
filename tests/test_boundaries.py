"""
Boundary Value Tests for CMColors

Tests edge cases and boundary conditions systematically.
"""

import pytest
from cm_colors import CMColors


class TestBoundaryValues:
    def setup_method(self):
        self.cm = CMColors()

    @pytest.mark.parametrize(
        'rgb',
        [
            (0, 0, 0),  # Minimum values
            (255, 255, 255),  # Maximum values
            (0, 255, 0),  # Mixed boundaries
            (255, 0, 255),  # Mixed boundaries
        ],
    )
    def test_rgb_boundaries(self, rgb):
        """Test RGB boundary values work correctly"""
        # Should not raise exceptions
        oklch = self.cm.rgb_to_oklch(rgb)
        lab = self.cm.rgb_to_lab(rgb)
        contrast = self.cm.contrast_ratio(rgb, (255, 255, 255))

        assert oklch is not None
        assert lab is not None
        assert contrast > 0

    @pytest.mark.parametrize(
        'invalid_rgb',
        [
            (-1, 0, 0),  # Below minimum
            (256, 0, 0),  # Above maximum
            (0, -1, 0),  # Mixed invalid
            (255, 256, 0),  # Mixed invalid
        ],
    )
    def test_invalid_rgb_boundaries(self, invalid_rgb):
        """Test that invalid RGB values raise appropriate errors"""
        with pytest.raises(ValueError):
            self.cm.contrast_ratio(invalid_rgb, (255, 255, 255))

    def test_near_identical_colors(self):
        """Test colors that are nearly identical"""
        color1 = (128, 128, 128)
        color2 = (128, 128, 129)  # Differ by 1

        contrast = self.cm.contrast_ratio(color1, color2)
        delta_e = self.cm.delta_e(color1, color2)

        assert contrast > 1.0  # Should be > 1 but very small
        assert contrast < 1.1  # Should be very close to 1
        assert delta_e > 0     # Should be > 0 but very small
        assert delta_e < 2     # Should be very small

    def test_maximum_contrast_colors(self):
        """Test maximum contrast color pairs"""
        black = (0, 0, 0)
        white = (255, 255, 255)

        contrast = self.cm.contrast_ratio(black, white)
        assert abs(contrast - 21.0) < 0.1
