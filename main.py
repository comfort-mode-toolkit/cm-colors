# main.py
"""
CMColors - Mathematically Rigorous Accessible Color Science Library

This library provides tools for ensuring color accessibility based on WCAG guidelines,
offering functions to calculate contrast ratios, find accessible color alternatives,
and convert between color spaces (RGB, OKLCH, LAB).

License: GNU General Public License v3.0
"""

from typing import Tuple, Optional

# Import functions from helper.py and accessible_palatte.py
# Assuming these files are in the same directory or accessible via PYTHONPATH
from helper import (
    calculate_contrast_ratio,
    get_contrast_level,
    rgb_to_oklch_safe,
    oklch_to_rgb_safe,
    rgb_to_lab,
    calculate_delta_e_2000,
    is_valid_rgb,
    oklch_color_distance,
    validate_oklch,
)
from accessible_palatte import (
    check_and_fix_contrast_optimized,
    generate_accessible_color_optimized,
    binary_search_lightness,
    gradient_descent_oklch,
)

class CMColors:
    """
    CMColors provides a comprehensive API for color accessibility and manipulation.
    All core functionalities are exposed as methods of this class.
    """

    def __init__(self):
        """
        Initializes the CMColors instance.
        Currently, no specific parameters are needed for initialization.
        """
        pass

    def calculate_contrast(self, text_rgb: Tuple[int, int, int], bg_rgb: Tuple[int, int, int]) -> float:
        """
        Calculates the WCAG contrast ratio between two RGB colors.

        Args:
            text_rgb (Tuple[int, int, int]): The RGB tuple for the text color (R, G, B).
            bg_rgb (Tuple[int, int, int]): The RGB tuple for the background color (R, G, B).

        Returns:
            float: The calculated contrast ratio.
        """
        if not (is_valid_rgb(text_rgb) and is_valid_rgb(bg_rgb)):
            raise ValueError("Invalid RGB values provided. Each component must be between 0 and 255.")
        return calculate_contrast_ratio(text_rgb, bg_rgb)

    def get_wcag_level(self, contrast_ratio: float, large_text: bool = False) -> str:
        """
        Determines the WCAG contrast level (AAA, AA, FAIL) based on the contrast ratio
        and whether the text is considered 'large'.

        Args:
            contrast_ratio (float): The calculated contrast ratio.
            large_text (bool): True if the text is considered large (18pt or 14pt bold),
                               False otherwise (default).

        Returns:
            str: The WCAG compliance level ("AAA", "AA", or "FAIL").
        """
        return get_contrast_level(contrast_ratio, large_text)

    def ensure_accessible_colors(self, text_rgb: Tuple[int, int, int], bg_rgb: Tuple[int, int, int],
                                 large_text: bool = False) -> Tuple[Tuple[int, int, int], Tuple[int, int, int]]:
        """
        Checks the contrast between text and background colors and, if necessary,
        adjusts the text color to meet WCAG AAA requirements (or AA for large text)
        with minimal perceptual change.

        This function uses an optimized approach combining binary search and gradient descent.

        Args:
            text_rgb (Tuple[int, int, int]): The original RGB tuple for the text color.
            bg_rgb (Tuple[int, int, int]): The RGB tuple for the background color.
            large_text (bool): True if the text is considered large (18pt or 14pt bold),
                               False otherwise (default).

        Returns:
            Tuple[Tuple[int, int, int], Tuple[int, int, int]]: A tuple containing
            the (potentially adjusted) accessible text RGB and the original background RGB.
        """
        if not (is_valid_rgb(text_rgb) and is_valid_rgb(bg_rgb)):
            raise ValueError("Invalid RGB values provided. Each component must be between 0 and 255.")
        return check_and_fix_contrast_optimized(text_rgb, bg_rgb, large_text)

    def find_accessible_text_color(self, text_rgb: Tuple[int, int, int], bg_rgb: Tuple[int, int, int],
                                   large_text: bool = False) -> Tuple[int, int, int]:
        """
        Generates an accessible text color that meets WCAG AAA requirements (or AA for large text)
        relative to the background color, attempting to preserve the original color's hue
        and minimize perceptual difference (Delta E 2000).

        This function uses an optimized approach combining binary search and gradient descent.

        Args:
            text_rgb (Tuple[int, int, int]): The original RGB tuple for the text color.
            bg_rgb (Tuple[int, int, int]): The RGB tuple for the background color.
            large_text (bool): True if the text is considered large (18pt or 14pt bold),
                               False otherwise (default).

        Returns:
            Tuple[int, int, int]: The accessible text RGB color.
        """
        if not (is_valid_rgb(text_rgb) and is_valid_rgb(bg_rgb)):
            raise ValueError("Invalid RGB values provided. Each component must be between 0 and 255.")
        return generate_accessible_color_optimized(text_rgb, bg_rgb, large_text)

    def rgb_to_oklch(self, rgb: Tuple[int, int, int]) -> Tuple[float, float, float]:
        """
        Converts an RGB color to the OKLCH color space.
        OKLCH is a perceptually uniform color space, making it ideal for color manipulation.

        Args:
            rgb (Tuple[int, int, int]): The RGB tuple (R, G, B).

        Returns:
            Tuple[float, float, float]: The OKLCH tuple (Lightness, Chroma, Hue).
                                        Lightness is 0-1, Chroma is 0-~0.4, Hue is 0-360.
        """
        if not is_valid_rgb(rgb):
            raise ValueError("Invalid RGB values provided. Each component must be between 0 and 255.")
        return rgb_to_oklch_safe(rgb)

    def oklch_to_rgb(self, oklch: Tuple[float, float, float]) -> Tuple[int, int, int]:
        """
        Converts an OKLCH color back to the RGB color space.

        Args:
            oklch (Tuple[float, float, float]): The OKLCH tuple (Lightness, Chroma, Hue).

        Returns:
            Tuple[int, int, int]: The RGB tuple (R, G, B).
        """
        if not validate_oklch(oklch):
            raise ValueError("Invalid OKLCH values provided. Lightness 0-1, Chroma >=0, Hue 0-360.")
        return oklch_to_rgb_safe(oklch)

    def rgb_to_lab(self, rgb: Tuple[int, int, int]) -> Tuple[float, float, float]:
        """
        Converts an RGB color to the CIELAB color space.

        Args:
            rgb (Tuple[int, int, int]): The RGB tuple (R, G, B).

        Returns:
            Tuple[float, float, float]: The LAB tuple (Lightness, a*, b*).
        """
        if not is_valid_rgb(rgb):
            raise ValueError("Invalid RGB values provided. Each component must be between 0 and 255.")
        return rgb_to_lab(rgb)

    def calculate_delta_e_2000(self, rgb1: Tuple[int, int, int], rgb2: Tuple[int, int, int]) -> float:
        """
        Calculates the Delta E 2000 color difference between two RGB colors.
        Delta E 2000 is a perceptually uniform measure of color difference.

        Args:
            rgb1 (Tuple[int, int, int]): The first RGB color.
            rgb2 (Tuple[int, int, int]): The second RGB color.

        Returns:
            float: The Delta E 2000 value. A value less than 2.3 is generally
                   considered imperceptible to the average human eye.
        """
        if not (is_valid_rgb(rgb1) and is_valid_rgb(rgb2)):
            raise ValueError("Invalid RGB values provided. Each component must be between 0 and 255.")
        return calculate_delta_e_2000(rgb1, rgb2)

    def calculate_oklch_distance(self, oklch1: Tuple[float, float, float], oklch2: Tuple[float, float, float]) -> float:
        """
        Calculates the perceptual distance between two OKLCH colors.
        This provides a more accurate measure of perceived difference than Euclidean
        distance in RGB space.

        Args:
            oklch1 (Tuple[float, float, float]): The first OKLCH color.
            oklch2 (Tuple[float, float, float]): The second OKLCH color.

        Returns:
            float: The perceptual distance between the two OKLCH colors.
        """
        if not (validate_oklch(oklch1) and validate_oklch(oklch2)):
            raise ValueError("Invalid OKLCH values provided. Lightness 0-1, Chroma >=0, Hue 0-360.")
        return oklch_color_distance(oklch1, oklch2)

    # Exposing the internal optimized functions for advanced use, if needed
    # These are generally called by ensure_accessible_colors and find_accessible_text_color
    def _binary_search_lightness(self, text_rgb: Tuple[int, int, int], bg_rgb: Tuple[int, int, int],
                                 delta_e_threshold: float = 2.0, target_contrast: float = 7.0,
                                 large_text: bool = False) -> Optional[Tuple[int, int, int]]:
        """
        Internal method: Performs a binary search on the lightness component in OKLCH
        to find a color that meets contrast while minimizing Delta E.
        """
        if not (is_valid_rgb(text_rgb) and is_valid_rgb(bg_rgb)):
            raise ValueError("Invalid RGB values provided. Each component must be between 0 and 255.")
        return binary_search_lightness(text_rgb, bg_rgb, delta_e_threshold, target_contrast, large_text)

    def _gradient_descent_oklch(self, text_rgb: Tuple[int, int, int], bg_rgb: Tuple[int, int, int],
                                delta_e_threshold: float = 2.0, target_contrast: float = 7.0,
                                large_text: bool = False, max_iter: int = 50) -> Optional[Tuple[int, int, int]]:
        """
        Internal method: Performs gradient descent optimization in OKLCH space
        for lightness and chroma to find a color meeting contrast and Delta E criteria.
        """
        if not (is_valid_rgb(text_rgb) and is_valid_rgb(bg_rgb)):
            raise ValueError("Invalid RGB values provided. Each component must be between 0 and 255.")
        return gradient_descent_oklch(text_rgb, bg_rgb, delta_e_threshold, target_contrast, large_text, max_iter)

# Example Usage (for testing or direct script execution)
if __name__ == "__main__":
    cm_colors = CMColors()

    # Example 1: Check and fix contrast
    text_color_orig = (100, 100, 100) # Grey
    bg_color = (255, 255, 255)     # White

    print(f"Original Text Color: {text_color_orig}, Background Color: {bg_color}")
    initial_contrast = cm_colors.calculate_contrast(text_color_orig, bg_color)
    initial_level = cm_colors.get_wcag_level(initial_contrast)
    print(f"Initial Contrast Ratio: {initial_contrast:.2f}, WCAG Level: {initial_level}")

    accessible_text, _ = cm_colors.ensure_accessible_colors(text_color_orig, bg_color)
    final_contrast = cm_colors.calculate_contrast(accessible_text, bg_color)
    final_level = cm_colors.get_wcag_level(final_contrast)
    print(f"Adjusted Text Color: {accessible_text}, Final Contrast Ratio: {final_contrast:.2f}, WCAG Level: {final_level}\n")

    # Example 2: Another contrast check (already good)
    text_color_good = (0, 0, 0) # Black
    bg_color_good = (255, 255, 255) # White
    print(f"Original Text Color: {text_color_good}, Background Color: {bg_color_good}")
    initial_contrast_good = cm_colors.calculate_contrast(text_color_good, bg_color_good)
    initial_level_good = cm_colors.get_wcag_level(initial_contrast_good)
    print(f"Initial Contrast Ratio: {initial_contrast_good:.2f}, WCAG Level: {initial_level_good}")
    accessible_text_good, _ = cm_colors.ensure_accessible_colors(text_color_good, bg_color_good)
    print(f"Adjusted Text Color: {accessible_text_good} (should be same as original)\n")


    # Example 3: Color space conversions
    test_rgb = (123, 45, 200) # A shade of purple
    print(f"Testing color conversions for RGB: {test_rgb}")

    oklch_color = cm_colors.rgb_to_oklch(test_rgb)
    print(f"OKLCH: L={oklch_color[0]:.3f}, C={oklch_color[1]:.3f}, H={oklch_color[2]:.1f}")

    rgb_from_oklch = cm_colors.oklch_to_rgb(oklch_color)
    print(f"RGB back from OKLCH: {rgb_from_oklch}")

    lab_color = cm_colors.rgb_to_lab(test_rgb)
    print(f"LAB: L={lab_color[0]:.3f}, a={lab_color[1]:.3f}, b={lab_color[2]:.3f}\n")

    # Example 4: Delta E 2000 calculation
    color1 = (255, 0, 0) # Red
    color2 = (250, 5, 5) # Slightly different red
    delta_e = cm_colors.calculate_delta_e_2000(color1, color2)
    print(f"Delta E 2000 between {color1} and {color2}: {delta_e:.2f}")

    color3 = (0, 0, 255) # Blue
    color4 = (0, 255, 0) # Green
    delta_e_large = cm_colors.calculate_delta_e_2000(color3, color4)
    print(f"Delta E 2000 between {color3} and {color4}: {delta_e_large:.2f}\n")

    # Example 5: OKLCH distance
    oklch_1 = cm_colors.rgb_to_oklch((255, 100, 0)) # Orange
    oklch_2 = cm_colors.rgb_to_oklch((255, 150, 50)) # Lighter orange
    oklch_dist = cm_colors.calculate_oklch_distance(oklch_1, oklch_2)
    print(f"OKLCH distance between {oklch_1} and {oklch_2}: {oklch_dist:.3f}")
