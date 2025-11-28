"""
Property-Based Tests for CMColors

Tests mathematical properties and invariants that should always hold.
"""

import pytest
from hypothesis import given, strategies as st, settings
from cm_colors import CMColors

# Generate valid RGB tuples
rgb_strategy = st.tuples(
    st.integers(min_value=0, max_value=255),
    st.integers(min_value=0, max_value=255),
    st.integers(min_value=0, max_value=255),
)


class TestMathematicalProperties:
    def setup_method(self):
        self.cm = CMColors()

    @given(rgb_strategy, rgb_strategy)
    def test_contrast_ratio_symmetry(self, color1, color2):
        """Contrast ratio should be symmetric: contrast(A,B) == contrast(B,A)"""
        ratio1 = self.cm.contrast_ratio(color1, color2)
        ratio2 = self.cm.contrast_ratio(color2, color1)
        assert abs(ratio1 - ratio2) < 1e-10

    @given(rgb_strategy)
    def test_contrast_ratio_identity(self, color):
        """Contrast ratio of a color with itself should be 1.0"""
        ratio = self.cm.contrast_ratio(color, color)
        assert abs(ratio - 1.0) < 1e-10

    @given(rgb_strategy, rgb_strategy)
    def test_contrast_ratio_bounds(self, color1, color2):
        """Contrast ratio should always be between 1.0 and 21.0"""
        ratio = self.cm.contrast_ratio(color1, color2)
        assert 1.0 <= ratio <= 21.0

    @given(rgb_strategy)
    def test_color_space_roundtrip_stability(self, rgb_color):
        """RGB -> OKLCH -> RGB should be approximately stable"""
        oklch = self.cm.rgb_to_oklch(rgb_color)
        rgb_back = self.cm.oklch_to_rgb(oklch)

        for orig, back in zip(rgb_color, rgb_back):
            assert abs(orig - back) <= 5  # Allow for rounding errors

    @given(rgb_strategy)
    def test_delta_e_identity(self, color):
        """Delta E of a color with itself should be 0"""
        delta = self.cm.delta_e(color, color)
        assert abs(delta) < 1e-10

    @given(rgb_strategy, rgb_strategy)
    def test_delta_e_symmetry(self, color1, color2):
        """Delta E should be symmetric: ΔE(A,B) == ΔE(B,A)"""
        delta1 = self.cm.delta_e(color1, color2)
        delta2 = self.cm.delta_e(color2, color1)
        assert abs(delta1 - delta2) < 1e-10

    @given(rgb_strategy, rgb_strategy)
    @settings(deadline=None)
    def test_tune_colors_improves_or_maintains_contrast(
        self, text_rgb, bg_rgb
    ):
        """Tuned colors should never have worse contrast than original"""
        original_contrast = self.cm.contrast_ratio(text_rgb, bg_rgb)
        tuned, accessible = self.cm.tune_colors(text_rgb, bg_rgb)

        if accessible and isinstance(tuned, tuple):
            tuned_contrast = self.cm.contrast_ratio(tuned, bg_rgb)
            assert (
                tuned_contrast >= original_contrast - 0.1
            )  # Allow small tolerance
