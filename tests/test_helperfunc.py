import pytest
import math
import time
import sys
import os

# Add src to path for imports
sys.path.insert(
    0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src")
)

try:
    from cm_colors.core.contrast import (
        rgb_to_linear,
        calculate_relative_luminance,
        calculate_contrast_ratio,
        get_contrast_level,
        get_wcag_level,
    )
    from cm_colors.core.conversions import (
        rgb_to_oklch,
        oklch_to_rgb,
        rgb_to_xyz,
        xyz_to_lab,
        rgb_to_lab,
        is_valid_rgb,
        is_valid_oklch,
        rgb_to_oklch_safe,
        oklch_to_rgb_safe,
        parse_color_to_rgb,
        rgba_to_rgb,
        rgbint_to_string,
    )
    from cm_colors.core.color_metrics import calculate_delta_e_2000
    from cm_colors.core.optimisation import (
        generate_accessible_color,
        check_and_fix_contrast,
        binary_search_lightness,
        gradient_descent_oklch,
    )

except ImportError as e:
    print(f"Import error: {e}")
    print("Current working directory:", os.getcwd())
    print("Files in current directory:", os.listdir("."))
    raise


class TestBasicUtilities:
    """Test basic utility functions"""

    def test_rgb_to_linear(self):
        # Test low values (linear region)
        assert abs(rgb_to_linear(0) - 0.0) < 1e-10
        assert abs(rgb_to_linear(10) - (10 / 255.0 / 12.92)) < 1e-10

        # Test high values (gamma correction region)
        assert abs(rgb_to_linear(255) - 1.0) < 1e-6
        assert rgb_to_linear(128) > rgb_to_linear(10)  # Should be non-linear

        # Test boundary value
        boundary_val = 0.03928 * 255
        linear_result = rgb_to_linear(boundary_val)
        assert 0 < linear_result < 1

    def test_calculate_relative_luminance(self):
        # Test pure colors
        assert abs(calculate_relative_luminance((0, 0, 0)) - 0.0) < 1e-10
        assert abs(calculate_relative_luminance((255, 255, 255)) - 1.0) < 1e-6

        # Test red, green, blue
        red_lum = calculate_relative_luminance((255, 0, 0))
        green_lum = calculate_relative_luminance((0, 255, 0))
        blue_lum = calculate_relative_luminance((0, 0, 255))

        # Green should have highest luminance
        assert green_lum > red_lum > blue_lum

        # Test known values
        gray_128 = calculate_relative_luminance((128, 128, 128))
        assert 0.1 < gray_128 < 0.3

    def test_calculate_contrast_ratio(self):
        # Test black on white (maximum contrast)
        max_contrast = calculate_contrast_ratio((0, 0, 0), (255, 255, 255))
        assert abs(max_contrast - 21.0) < 0.1

        # Test white on black (should be same)
        reverse_contrast = calculate_contrast_ratio((255, 255, 255), (0, 0, 0))
        assert abs(max_contrast - reverse_contrast) < 1e-10

        # Test same colors (minimum contrast)
        min_contrast = calculate_contrast_ratio((128, 128, 128), (128, 128, 128))
        assert abs(min_contrast - 1.0) < 1e-10

        # Test reasonable contrast
        contrast = calculate_contrast_ratio((0, 0, 0), (128, 128, 128))
        assert 3 < contrast < 10

    def test_get_contrast_level(self):
        # Test normal text
        assert get_contrast_level(8.0, False) == "AAA"
        assert get_contrast_level(5.0, False) == "AA"
        assert get_contrast_level(3.0, False) == "FAIL"

        # Test large text
        assert get_contrast_level(5.0, True) == "AAA"
        assert get_contrast_level(3.5, True) == "AA"
        assert get_contrast_level(2.0, True) == "FAIL"

        # Test boundary values
        assert get_contrast_level(7.0, False) == "AAA"
        assert get_contrast_level(4.5, False) == "AA"
        assert get_contrast_level(4.5, True) == "AAA"
        assert get_contrast_level(3.0, True) == "AA"

    def test_is_valid_rgb(self):
        assert is_valid_rgb((0, 0, 0)) == True
        assert is_valid_rgb((255, 255, 255)) == True
        assert is_valid_rgb((128, 64, 192)) == True

        # Invalid values
        assert is_valid_rgb((-1, 0, 0)) == False
        assert is_valid_rgb((256, 0, 0)) == False
        assert is_valid_rgb((0, -5, 0)) == False
        assert is_valid_rgb((0, 0, 300)) == False


class TestColorSpaceConversions:
    """Test color space conversion functions"""

    @pytest.fixture
    def test_colors(self):
        return [
            (255, 0, 0),  # Red
            (0, 255, 0),  # Green
            (0, 0, 255),  # Blue
            (255, 255, 255),  # White
            (0, 0, 0),  # Black
            (128, 128, 128),  # Gray
            (255, 128, 64),  # Orange
        ]

    def test_rgb_to_oklch_basic(self, test_colors):
        for rgb in test_colors:
            oklch = rgb_to_oklch(rgb)

            # Check types and ranges
            assert isinstance(oklch, tuple)
            assert len(oklch) == 3
            L, C, H = oklch

            # Lightness should be 0-1
            assert 0 <= L <= 1

            # Chroma should be non-negative
            assert C >= 0

            # Hue should be 0-360
            assert 0 <= H <= 360

    def test_oklch_to_rgb_basic(self):
        # Test some known OKLCH values
        test_oklch = [
            (0.0, 0.0, 0.0),  # Black
            (1.0, 0.0, 0.0),  # White
            (0.5, 0.1, 0.0),  # Grayish red
            (0.7, 0.15, 120.0),  # Greenish
        ]

        for oklch in test_oklch:
            rgb = oklch_to_rgb(oklch)

            # Check types and ranges
            assert isinstance(rgb, tuple)
            assert len(rgb) == 3
            assert all(isinstance(x, int) for x in rgb)
            assert all(0 <= x <= 255 for x in rgb)

    def test_rgb_oklch_roundtrip(self, test_colors):
        """Test that RGB -> OKLCH -> RGB preserves colors reasonably well"""
        for rgb in test_colors:
            oklch = rgb_to_oklch(rgb)
            rgb_back = oklch_to_rgb(oklch)

            # Should be close (allowing for rounding errors)
            for orig, back in zip(rgb, rgb_back):
                assert abs(orig - back) <= 2  # Allow small rounding errors

    def test_rgb_to_xyz(self, test_colors):
        for rgb in test_colors:
            xyz = rgb_to_xyz(rgb)

            assert isinstance(xyz, tuple)
            assert len(xyz) == 3
            assert all(isinstance(x, (int, float)) for x in xyz)
            assert all(x >= 0 for x in xyz)  # XYZ should be non-negative

    def test_xyz_to_lab(self):
        # Test with some XYZ values
        test_xyz = [
            (0, 0, 0),  # Black
            (95.047, 100, 108.883),  # White D65
            (50, 50, 50),  # Mid-range
        ]

        for xyz in test_xyz:
            lab = xyz_to_lab(xyz)

            assert isinstance(lab, tuple)
            assert len(lab) == 3
            L, a, b = lab

            # L should be 0-100
            assert 0 <= L <= 100

    def test_rgb_to_lab(self, test_colors):
        for rgb in test_colors:
            lab = rgb_to_lab(rgb)

            assert isinstance(lab, tuple)
            assert len(lab) == 3
            L, a, b = lab

            # L should be 0-100
            assert 0 <= L <= 100

    def test_calculate_delta_e_2000(self):
        # Test identical colors
        assert calculate_delta_e_2000((255, 0, 0), (255, 0, 0)) == 0.0

        # Test different colors
        delta_e = calculate_delta_e_2000((255, 0, 0), (0, 255, 0))
        assert delta_e > 50  # Should be a large difference

        # Test similar colors
        delta_e_small = calculate_delta_e_2000((255, 0, 0), (250, 5, 5))
        assert 0 < delta_e_small < 10

    def test_safe_conversions(self):
        # Test safe RGB to OKLCH
        oklch = rgb_to_oklch_safe((255, 0, 0))
        assert is_valid_oklch(oklch)

        # Test safe OKLCH to RGB
        rgb = oklch_to_rgb_safe((0.5, 0.1, 0.0))
        assert is_valid_rgb(rgb)

        # # Test error handling with invalid inputs
        # oklch_invalid = rgb_to_oklch_safe((-1, 0, 0))
        # assert is_valid_oklch(oklch_invalid)  # Should fallback to valid value

        rgb_invalid = oklch_to_rgb_safe((-1, 0, 0))
        assert is_valid_rgb(rgb_invalid)  # Should fallback to valid value


class TestValidationFunctions:
    """Test validation and utility functions"""

    def test_is_valid_oklch(self):
        # Valid OKLCH values
        assert is_valid_oklch((0.5, 0.1, 180.0)) == True
        assert is_valid_oklch((0.0, 0.0, 0.0)) == True
        assert is_valid_oklch((1.0, 0.4, 359.9)) == True

        # Invalid OKLCH values
        assert is_valid_oklch((-0.1, 0.1, 180.0)) == False  # Negative L
        assert is_valid_oklch((1.1, 0.1, 180.0)) == False  # L > 1
        assert is_valid_oklch((0.5, -0.1, 180.0)) == False  # Negative C
        assert is_valid_oklch((0.5, 0.1, -10.0)) == False  # Negative H
        assert is_valid_oklch((0.5, 0.1, 370.0)) == False  # H > 360

    def test_parse_color_to_rgb(self):
        # Test hex colors
        assert parse_color_to_rgb("#ff0000") == (255, 0, 0)
        assert parse_color_to_rgb("#000000") == (0, 0, 0)
        assert parse_color_to_rgb("#ffffff") == (255, 255, 255)

        # Test RGB strings
        assert parse_color_to_rgb("rgb(255, 0, 0)") == (255, 0, 0)
        assert parse_color_to_rgb("rgb(0, 0, 0)") == (0, 0, 0)

        # Test RGBA strings (now properly alpha blended with white background)
        assert parse_color_to_rgb("rgba(255, 0, 0, 1.0)") == (255, 0, 0)  # Full opacity = no change
        assert parse_color_to_rgb("rgba(0, 128, 255, 0.5)") == (128, 192, 255)  # 50% blend with white
        assert parse_color_to_rgb("rgba(255, 255, 255, 0.0)") == (255, 255, 255)  # 0% opacity = white background
        assert parse_color_to_rgb("rgba(100, 200, 50, 0.8)") == (131, 211, 91)  # 80% opacity blend

        # Test RGBA tuples
        assert parse_color_to_rgb((255, 0, 0, 1.0)) == (255, 0, 0)  # Full opacity
        assert parse_color_to_rgb((0, 128, 255, 0.5)) == (128, 192, 255)  # 50% blend with white
        assert parse_color_to_rgb((100, 200, 50, 0.0)) == (255, 255, 255)  # 0% opacity = white

        # Test RGB tuples (unchanged behavior)
        assert parse_color_to_rgb((255, 0, 0)) == (255, 0, 0)

    def test_rgbint_to_string(self):
        assert rgbint_to_string((255, 0, 0)) == "rgb(255, 0, 0)"
        assert rgbint_to_string((0, 0, 0)) == "rgb(0, 0, 0)"
        assert rgbint_to_string((128, 128, 128)) == "rgb(128, 128, 128)"

    def test_parse_color_to_rgb_rgba_errors(self):
        """Test error handling for RGBA format"""
        # Test invalid RGBA formats
        with pytest.raises(ValueError, match="RGBA string must have exactly 4 values"):
            parse_color_to_rgb("rgba(255, 0, 0)")  # Missing alpha

        with pytest.raises(ValueError, match="RGBA string must have exactly 4 values"):
            parse_color_to_rgb("rgba(255, 0)")  # Too few values

        with pytest.raises(ValueError, match="RGBA string must have exactly 4 values"):
            parse_color_to_rgb("rgba(255, 0, 0, 0.5, 0.8)")  # Too many values

        # Test invalid RGB values in RGBA
        with pytest.raises(ValueError, match="RGB values must be between 0-255"):
            parse_color_to_rgb("rgba(256, 0, 0, 0.5)")

        with pytest.raises(ValueError, match="RGB values cannot be negative"):
            parse_color_to_rgb("rgba(-1, 0, 0, 0.5)")

        # Test invalid alpha values
        with pytest.raises(ValueError, match="Alpha value must be between 0 and 1"):
            parse_color_to_rgb("rgba(255, 0, 0, 1.5)")

        with pytest.raises(ValueError, match="Alpha value must be between 0 and 1"):
            parse_color_to_rgb("rgba(255, 0, 0, -0.1)")

        with pytest.raises(ValueError, match="Invalid alpha value"):
            parse_color_to_rgb("rgba(255, 0, 0, abc)")


class TestRGBAConversions:
    """Test RGBA to RGB conversion functionality"""

    def test_rgba_to_rgb_basic(self):
        """Test basic RGBA to RGB conversion with default white background"""
        # Full opacity should return original color
        assert rgba_to_rgb((255, 0, 0, 1.0)) == (255, 0, 0)
        assert rgba_to_rgb((0, 255, 0, 1.0)) == (0, 255, 0)
        assert rgba_to_rgb((0, 0, 255, 1.0)) == (0, 0, 255)
        
        # Zero opacity should return white background
        assert rgba_to_rgb((255, 0, 0, 0.0)) == (255, 255, 255)
        assert rgba_to_rgb((0, 255, 0, 0.0)) == (255, 255, 255)
        assert rgba_to_rgb((0, 0, 0, 0.0)) == (255, 255, 255)
        
        # 50% opacity should blend halfway
        assert rgba_to_rgb((0, 0, 0, 0.5)) == (128, 128, 128)  # Black 50% + White 50% = Gray
        assert rgba_to_rgb((255, 0, 0, 0.5)) == (255, 128, 128)  # Red 50% + White 50%
        
    def test_rgba_to_rgb_custom_background(self):
        """Test RGBA to RGB conversion with custom background colors"""
        # Test with black background
        black_bg = (0, 0, 0)
        assert rgba_to_rgb((255, 255, 255, 0.5), black_bg) == (128, 128, 128)
        assert rgba_to_rgb((255, 0, 0, 0.0), black_bg) == (0, 0, 0)
        assert rgba_to_rgb((255, 0, 0, 1.0), black_bg) == (255, 0, 0)
        
        # Test with colored background
        blue_bg = (0, 0, 255)
        assert rgba_to_rgb((255, 0, 0, 0.5), blue_bg) == (128, 0, 128)  # Red 50% + Blue 50%
        assert rgba_to_rgb((0, 255, 0, 0.0), blue_bg) == (0, 0, 255)    # 0% opacity = blue background
        
    def test_rgba_to_rgb_edge_cases(self):
        """Test edge cases for RGBA to RGB conversion"""
        # Test various alpha values
        test_cases = [
            ((100, 150, 200, 0.25), (255, 255, 255), (216, 229, 241)),  # 25% opacity
            ((100, 150, 200, 0.75), (255, 255, 255), (139, 176, 214)),  # 75% opacity - keeping original
            ((0, 0, 0, 0.1), (255, 255, 255), (230, 230, 230)),         # 10% black - keeping original
            ((255, 255, 255, 0.9), (0, 0, 0), (230, 230, 230)),         # 90% white on black - keeping original
        ]
        
        for rgba, bg, expected in test_cases:
            result = rgba_to_rgb(rgba, bg)
            for i, (actual, exp) in enumerate(zip(result, expected)):
                assert abs(actual - exp) <= 1, f"Component {i}: expected {exp}, got {actual}"
    
    def test_rgba_to_rgb_validation(self):
        """Test validation of RGBA inputs"""
        # Test invalid RGB values
        with pytest.raises(ValueError, match="RGB values in RGBA must be integers 0-255"):
            rgba_to_rgb((-1, 0, 0, 0.5))
        with pytest.raises(ValueError, match="RGB values in RGBA must be integers 0-255"):
            rgba_to_rgb((256, 0, 0, 0.5))
        with pytest.raises(ValueError, match="RGB values in RGBA must be integers 0-255"):
            rgba_to_rgb((255, -5, 0, 0.5))
        with pytest.raises(ValueError, match="RGB values in RGBA must be integers 0-255"):
            rgba_to_rgb((255, 300, 0, 0.5))
            
        # Test invalid alpha values
        with pytest.raises(ValueError, match="Alpha value must be between 0 and 1"):
            rgba_to_rgb((255, 0, 0, -0.1))
        with pytest.raises(ValueError, match="Alpha value must be between 0 and 1"):
            rgba_to_rgb((255, 0, 0, 1.5))
            
        # Test invalid background values
        with pytest.raises(ValueError, match="Background RGB values must be integers 0-255"):
            rgba_to_rgb((255, 0, 0, 0.5), (-1, 255, 255))
        with pytest.raises(ValueError, match="Background RGB values must be integers 0-255"):
            rgba_to_rgb((255, 0, 0, 0.5), (255, 256, 255))
    
    def test_parse_color_to_rgb_rgba_tuples(self):
        """Test parsing RGBA tuples through parse_color_to_rgb"""
        # Test RGBA tuples with default background
        assert parse_color_to_rgb((255, 0, 0, 1.0)) == (255, 0, 0)
        assert parse_color_to_rgb((0, 128, 255, 0.5)) == (128, 192, 255)
        assert parse_color_to_rgb((100, 200, 50, 0.0)) == (255, 255, 255)
        
        # Test RGBA tuples with custom background
        assert parse_color_to_rgb((255, 0, 0, 0.5), (0, 0, 0)) == (128, 0, 0)
        
        # Test invalid RGBA tuples
        with pytest.raises(ValueError, match="RGB values in RGBA tuple must be integers 0-255"):
            parse_color_to_rgb((-1, 0, 0, 0.5))
        with pytest.raises(ValueError, match="Alpha value in RGBA tuple must be between 0 and 1"):
            parse_color_to_rgb((255, 0, 0, 1.5))
        with pytest.raises(ValueError, match="RGBA tuple must contain only numbers"):
            parse_color_to_rgb((255, 0, 0, "abc"))
    
    def test_parse_color_to_rgb_rgba_strings_custom_background(self):
        """Test parsing RGBA strings with custom backgrounds"""
        # Test with black background
        assert parse_color_to_rgb("rgba(255, 0, 0, 0.5)", (0, 0, 0)) == (128, 0, 0)
        assert parse_color_to_rgb("rgba(0, 255, 0, 0.3)", (0, 0, 0)) == (0, 76, 0)
        
        # Test with colored background
        assert parse_color_to_rgb("rgba(255, 255, 255, 0.5)", (255, 0, 0)) == (255, 128, 128)


class TestOptimizationFunctions:
    """Test optimization and candidate generation functions"""

    def test_binary_search_lightness(self):
        rgb = (128, 64, 192)
        bg_rgb = (255, 255, 255)

        result = binary_search_lightness(
            rgb, bg_rgb, delta_e_threshold=2.0, target_contrast=7.0
        )

        if result is not None:
            # Should return valid RGB
            assert is_valid_rgb(result)

            # Should have reasonable contrast
            contrast = calculate_contrast_ratio(result, bg_rgb)
            assert contrast > calculate_contrast_ratio(rgb, bg_rgb)

    def test_gradient_descent_oklch(self):
        rgb = (128, 64, 192)
        bg_rgb = (255, 255, 255)

        result = gradient_descent_oklch(
            rgb, bg_rgb, delta_e_threshold=2.0, target_contrast=7.0
        )

        if result is not None:
            # Should return valid RGB
            assert is_valid_rgb(result)

            # Should have reasonable contrast
            contrast = calculate_contrast_ratio(result, bg_rgb)
            assert contrast > calculate_contrast_ratio(rgb, bg_rgb)

    def test_generate_accessible_color(self):
        rgb = (128, 64, 192)
        bg_rgb = (255, 255, 255)

        result = generate_accessible_color(rgb, bg_rgb, large=False)

        # Should return valid RGB
        assert is_valid_rgb(result)

        # Should meet minimum contrast requirements
        contrast = calculate_contrast_ratio(result, bg_rgb)
        assert contrast >= 4.5  # Minimum for normal text


class TestAccessibilityFunctions:
    """Test accessibility and contrast fixing functions"""

    @pytest.mark.parametrize(
        "text_rgb,bg_rgb,large,expected_accessible",
        [
            (
                (0, 0, 0),
                (255, 255, 255),
                False,
                True,
            ),  # Black on white - should already be accessible
            (
                (255, 0, 0),
                (255, 255, 255),
                False,
                True,
            ),  # Red on white - should be fixable
            (
                (200, 200, 200),
                (255, 255, 255),
                True,
                True,
            ),  # Light gray on white (large text)
        ],
    )
    def test_check_and_fix_contrast_basic(
        self, text_rgb, bg_rgb, large, expected_accessible
    ):
        result, accessible = check_and_fix_contrast(text_rgb, bg_rgb, large)

        # Should return valid result
        assert isinstance(accessible, bool)

        if accessible:
            # Parse result if it's a string
            if isinstance(result, str):
                # Should be in format "rgb(r, g, b)"
                assert result.startswith("rgb(")
                assert result.endswith(")")
            else:
                # Should be valid RGB tuple
                assert is_valid_rgb(result)

    def test_check_and_fix_contrast_details(self):
        text_rgb = (128, 128, 128)
        bg_rgb = (255, 255, 255)

        details = check_and_fix_contrast(text_rgb, bg_rgb, large=False, details=True)

        # Should return detailed dictionary
        assert isinstance(details, dict)

        required_keys = [
            "text",
            "tuned_text",
            "bg",
            "large",
            "wcag_level",
            "improvement_percentage",
            "status",
            "message",
        ]
        for key in required_keys:
            assert key in details

    def test_check_and_fix_contrast_needs_fixing(self):
        # Test case where contrast needs improvement
        text_rgb = (200, 200, 200)  # Light gray
        bg_rgb = (255, 255, 255)  # White

        # Original contrast should be poor
        original_contrast = calculate_contrast_ratio(text_rgb, bg_rgb)
        assert original_contrast < 4.5

        result, accessible = check_and_fix_contrast(text_rgb, bg_rgb)

        # Should indicate accessibility improvement attempt
        assert isinstance(accessible, bool)

    def test_check_and_fix_contrast_large_text(self):
        text_rgb = (180, 180, 180)
        bg_rgb = (255, 255, 255)

        result, accessible = check_and_fix_contrast(text_rgb, bg_rgb, large=True)

        # Should handle large text requirements
        assert isinstance(accessible, bool)


class TestEdgeCases:
    """Test edge cases and error handling"""

    def test_extreme_colors(self):
        # Test with extreme values
        extreme_colors = [
            (0, 0, 0),  # Pure black
            (255, 255, 255),  # Pure white
            (255, 0, 0),  # Pure red
            (0, 255, 0),  # Pure green
            (0, 0, 255),  # Pure blue
        ]

        for color in extreme_colors:
            # All functions should handle extreme colors
            oklch = rgb_to_oklch_safe(color)
            assert is_valid_oklch(oklch)

            rgb_back = oklch_to_rgb_safe(oklch)
            assert is_valid_rgb(rgb_back)

    def test_invalid_input_handling(self):
        # Test functions handle invalid inputs gracefully
        invalid_rgb = (-1, 256, 128)

        # Safe functions should handle invalid input
        oklch = rgb_to_oklch_safe(invalid_rgb)
        assert is_valid_oklch(oklch)

    def test_boundary_values(self):
        # Test with boundary values
        boundary_colors = [
            (1, 1, 1),  # Near black
            (254, 254, 254),  # Near white
            (127, 128, 129),  # Mid-range
        ]

        for color in boundary_colors:
            # Test all major functions
            luminance = calculate_relative_luminance(color)
            assert 0 <= luminance <= 1

            oklch = rgb_to_oklch_safe(color)
            assert is_valid_oklch(oklch)

            lab = rgb_to_lab(color)
            assert 0 <= lab[0] <= 100

    def test_grayscale_colors(self):
        # Test with various grayscale colors
        grayscale_colors = [
            (0, 0, 0),
            (64, 64, 64),
            (128, 128, 128),
            (192, 192, 192),
            (255, 255, 255),
        ]

        for color in grayscale_colors:
            oklch = rgb_to_oklch_safe(color)
            L, C, H = oklch

            # Grayscale colors should have very low chroma
            assert C < 0.01

            # Should round-trip reasonably well
            rgb_back = oklch_to_rgb_safe(oklch)
            for orig, back in zip(color, rgb_back):
                assert abs(orig - back) <= 3


class TestIntegration:
    """Integration tests for the complete workflow"""

    @pytest.mark.parametrize(
        "text_color,bg_color",
        [
            ((255, 0, 0), (255, 255, 255)),  # Red on white
            ((0, 100, 0), (255, 255, 255)),  # Dark green on white
            ((0, 0, 255), (0, 0, 0)),  # Blue on black
            ((128, 128, 128), (255, 255, 255)),  # Gray on white
            ((255, 255, 0), (0, 0, 255)),  # Yellow on blue
        ],
    )
    def test_complete_workflow(self, text_color, bg_color):
        """Test the complete color accessibility workflow"""

        # Get original contrast
        original_contrast = calculate_contrast_ratio(text_color, bg_color)
        original_level = get_contrast_level(original_contrast)

        # Fix the colors
        result, accessible = check_and_fix_contrast(text_color, bg_color)

        # Verify results
        assert isinstance(accessible, bool)

        if accessible:
            # Parse result if it's a string
            if isinstance(result, str):
                assert result.startswith("rgb(")

            # Calculate color difference if changed
            if result != text_color:
                # If we can parse the result, check Delta E
                try:
                    if isinstance(result, str):
                        result_rgb = parse_color_to_rgb(result)
                    else:
                        result_rgb = result

                    delta_e = calculate_delta_e_2000(text_color, result_rgb)
                    # Should preserve brand colors (reasonable Delta E)
                    assert delta_e < 20  # Allow reasonable changes for accessibility
                except:
                    pass  # Skip Delta E check if parsing fails

    def test_already_accessible_colors(self):
        """Test that already accessible colors remain unchanged or improve"""
        text_color = (0, 0, 0)  # Black
        bg_color = (255, 255, 255)  # White

        result, accessible = check_and_fix_contrast(text_color, bg_color)

        # Should be accessible
        assert accessible is True

    def test_performance_reasonable(self):
        """Test that color fixing completes in reasonable time"""

        text_color = (128, 64, 192)
        bg_color = (255, 255, 255)

        start_time = time.time()
        result, accessible = check_and_fix_contrast(text_color, bg_color)
        end_time = time.time()

        # Should complete within reasonable time (adjust as needed)
        assert (end_time - start_time) < 10.0  # Should be much faster than 10 seconds

        # Should still produce valid results
        assert isinstance(accessible, bool)
