"""
Smoke and Regression Tests for CMColors

These tests ensure basic functionality works and catch fundamental breakages.
Run these first - if they fail, something is seriously wrong.
"""

import pytest
from cm_colors import CMColors


class TestSmokeTests:
    """Basic smoke tests - does the package work at all?"""

    def setup_method(self):
        """Setup for each test method"""
        self.cm = CMColors()

    def test_package_imports(self):
        """Test that the package imports without errors"""
        from cm_colors import CMColors

        assert CMColors is not None

    def test_cmcolors_instantiation(self):
        """Test that CMColors can be instantiated"""
        cm = CMColors()
        assert cm is not None
        assert isinstance(cm, CMColors)

    def test_all_public_methods_exist(self):
        """Test that all expected public methods exist and are callable"""
        expected_methods = [
            'tune_colors',
            'contrast_ratio',
            'wcag_level',
            'rgb_to_oklch',
            'oklch_to_rgb',
            'rgb_to_lab',
            'delta_e',
            'parse_to_rgb',
        ]

        for method_name in expected_methods:
            assert hasattr(
                self.cm, method_name
            ), f'Method {method_name} not found'
            assert callable(
                getattr(self.cm, method_name)
            ), f'Method {method_name} is not callable'

    def test_basic_functionality_no_exceptions(self):
        """Test that basic operations don't throw unexpected exceptions"""
        # These should not raise exceptions with valid inputs
        try:
            self.cm.contrast_ratio((0, 0, 0), (255, 255, 255))
            self.cm.wcag_level((0, 0, 0), (255, 255, 255))
            self.cm.tune_colors((100, 100, 100), (255, 255, 255))
            self.cm.rgb_to_oklch((123, 45, 200))
            self.cm.oklch_to_rgb((0.5, 0.1, 180))
            self.cm.rgb_to_lab((123, 45, 200))
            self.cm.delta_e((255, 0, 0), (0, 255, 0))
            self.cm.parse_to_rgb('#ffffff')
        except Exception as e:
            pytest.fail(
                f'Basic functionality raised unexpected exception: {e}'
            )


class TestRegressionTests:
    """Regression tests - ensure previously working functionality still works"""

    def setup_method(self):
        """Setup for each test method"""
        self.cm = CMColors()

    def test_contrast_ratio_known_values(self):
        """Regression: Test contrast ratios for known color pairs"""
        # Black on white should be 21:1
        assert self.cm.contrast_ratio(
            (0, 0, 0), (255, 255, 255)
        ) == pytest.approx(21.0, abs=0.1)

        # White on black should be 21:1
        assert self.cm.contrast_ratio(
            (255, 255, 255), (0, 0, 0)
        ) == pytest.approx(21.0, abs=0.1)

        # Same color should be 1:1
        assert self.cm.contrast_ratio(
            (128, 128, 128), (128, 128, 128)
        ) == pytest.approx(1.0, abs=0.1)

        # Known failing combination
        assert self.cm.contrast_ratio((200, 200, 200), (255, 255, 255)) < 4.5

    def test_wcag_levels_known_combinations(self):
        """Regression: Test WCAG levels for known color combinations"""
        # Black on white - should be AAA
        assert self.cm.wcag_level((0, 0, 0), (255, 255, 255)) == 'AAA'
        assert (
            self.cm.wcag_level((0, 0, 0), (255, 255, 255), large_text=True)
            == 'AAA'
        )

        # Light grey on white - should fail for normal text
        assert self.cm.wcag_level((200, 200, 200), (255, 255, 255)) == 'FAIL'

        # Medium grey on white - might pass for large text
        wcag_normal = self.cm.wcag_level((100, 100, 100), (255, 255, 255))
        wcag_large = self.cm.wcag_level(
            (100, 100, 100), (255, 255, 255), large_text=True
        )
        assert wcag_normal in ['AAA', 'AA', 'FAIL']
        assert wcag_large in ['AAA', 'AA', 'FAIL']

    def test_tune_colors_basic_behavior(self):
        """Regression: Test that tune_colors behaves predictably"""
        # Good colors should remain unchanged
        tuned, accessible = self.cm.tune_colors((0, 0, 0), (255, 255, 255))
        assert accessible is True
        assert 'rgb(0, 0, 0)' in tuned or tuned == (0, 0, 0)

        # Bad colors should be improved
        tuned_bad, accessible_bad = self.cm.tune_colors(
            (100, 100, 100), (255, 255, 255)
        )
        assert accessible_bad is True

        # Details mode should return dict
        details = self.cm.tune_colors(
            (100, 100, 100), (255, 255, 255), details=True
        )
        assert isinstance(details, dict)
        required_keys = [
            'text',
            'tuned_text',
            'bg',
            'wcag_level',
            'status',
            'message',
        ]
        for key in required_keys:
            assert key in details, f'Missing key in details: {key}'

    def test_color_parsing_standard_formats(self):
        """Regression: Test that standard color formats parse correctly"""
        # Hex colors
        assert self.cm.parse_to_rgb('#000000') == (0, 0, 0)
        assert self.cm.parse_to_rgb('#ffffff') == (255, 255, 255)
        assert self.cm.parse_to_rgb('#ff0000') == (255, 0, 0)

        # RGB colors
        assert self.cm.parse_to_rgb('rgb(0, 0, 0)') == (0, 0, 0)
        assert self.cm.parse_to_rgb('rgb(255, 255, 255)') == (255, 255, 255)
        assert self.cm.parse_to_rgb('rgb(123, 45, 200)') == (123, 45, 200)

    def test_color_space_conversions_roundtrip(self):
        """Regression: Test that color space conversions are reasonably stable"""
        test_colors = [
            (0, 0, 0),  # Black
            (255, 255, 255),  # White
            (255, 0, 0),  # Red
            (0, 255, 0),  # Green
            (0, 0, 255),  # Blue
            (123, 45, 200),  # Random color
        ]

        for rgb in test_colors:
            # RGB -> OKLCH -> RGB roundtrip
            oklch = self.cm.rgb_to_oklch(rgb)
            rgb_back = self.cm.oklch_to_rgb(oklch)

            # Should be close to original (allowing for small rounding errors)
            for orig, back in zip(rgb, rgb_back):
                assert (
                    abs(orig - back) <= 2
                ), f'RGB roundtrip failed: {rgb} -> {oklch} -> {rgb_back}'

            # RGB -> LAB conversion should work
            lab = self.cm.rgb_to_lab(rgb)
            assert len(lab) == 3
            assert isinstance(lab[0], (int, float))

    def test_delta_e_basic_properties(self):
        """Regression: Test that Delta E has expected basic properties"""
        # Same color should have Delta E of 0
        assert self.cm.delta_e(
            (128, 128, 128), (128, 128, 128)
        ) == pytest.approx(0.0, abs=0.1)

        # Very different colors should have high Delta E
        assert self.cm.delta_e((0, 0, 0), (255, 255, 255)) > 50

        # Similar colors should have low Delta E
        assert self.cm.delta_e((100, 100, 100), (101, 101, 101)) < 5

    def test_error_handling_stability(self):
        """Regression: Test that error handling works consistently"""
        # These should all raise ValueError consistently
        invalid_inputs = [
            (lambda: self.cm.contrast_ratio((256, 0, 0), (0, 0, 0))),
            (lambda: self.cm.contrast_ratio((0, 0, 0), (-1, 0, 0))),
            (lambda: self.cm.rgb_to_oklch((300, 0, 0))),
            (lambda: self.cm.oklch_to_rgb((2.0, 0.1, 180))),  # L > 1
            (lambda: self.cm.oklch_to_rgb((0.5, -0.1, 180))),  # C < 0
            (lambda: self.cm.rgb_to_lab((0, 0, 300))),
            (lambda: self.cm.delta_e((0, 0, 0), (256, 0, 0))),
            (lambda: self.cm.parse_to_rgb('invalid_color')),
        ]

        for invalid_call in invalid_inputs:
            with pytest.raises(ValueError):
                invalid_call()


class TestCriticalPathSmoke:
    """Critical path smoke tests - the most important workflows"""

    def setup_method(self):
        self.cm = CMColors()

    def test_accessibility_workflow(self):
        """Test the main accessibility workflow end-to-end"""
        # Parse a color string
        text_rgb = self.cm.parse_to_rgb('#808080')  # Medium grey
        bg_rgb = self.cm.parse_to_rgb('#ffffff')    # White

        # Check original accessibility
        original_contrast = self.cm.contrast_ratio(text_rgb, bg_rgb)
        original_wcag = self.cm.wcag_level(text_rgb, bg_rgb)

        # Tune for accessibility
        tuned_color, is_accessible = self.cm.tune_colors(text_rgb, bg_rgb)

        # Verify improvement
        assert (
            is_accessible is True
        ), 'Tuning should result in accessible colors'

        # Get detailed results
        details = self.cm.tune_colors(text_rgb, bg_rgb, details=True)
        assert details['status'] is True
        assert details['wcag_level'] in ['AA', 'AAA']

    def test_color_science_workflow(self):
        """Test color science operations work together"""
        color1 = (255, 100, 50)
        color2 = (200, 120, 80)

        # Convert to different color spaces
        oklch1 = self.cm.rgb_to_oklch(color1)
        lab1 = self.cm.rgb_to_lab(color1)

        # Calculate color difference
        delta_e = self.cm.delta_e(color1, color2)

        # Verify reasonable results
        assert len(oklch1) == 3
        assert len(lab1) == 3
        assert delta_e > 0
        assert isinstance(delta_e, (int, float))


# Convenience function to run just smoke tests
def test_smoke_only():
    """Run this single test to do a quick smoke check"""
    cm = CMColors()

    # Most basic operations
    assert cm.contrast_ratio((0, 0, 0), (255, 255, 255)) > 20
    assert cm.wcag_level((0, 0, 0), (255, 255, 255)) == 'AAA'

    tuned, accessible = cm.tune_colors((128, 128, 128), (255, 255, 255))
    assert accessible is True

    print('✅ Basic smoke test passed!')


if __name__ == '__main__':
    # Run smoke test if called directly
    test_smoke_only()
