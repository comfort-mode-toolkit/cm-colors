"""
CM-Colors - Accessible Color Science Library

A Python library for ensuring color accessibility based on WCAG guidelines.
Automatically tune colors to meet accessibility standards with minimal perceptual change.

CM-Colors takes your color choices and makes precise, barely-noticeable adjustments
to ensure they meet WCAG AA/AAA compliance while preserving your design intent.

Features:
- Tune colors to WCAG AA/AAA compliance with minimal visual change
- Calculate contrast ratios and determine WCAG compliance levels
- Convert between RGB, OKLCH, and LAB color spaces
- Measure perceptual color differences using Delta E 2000
- Mathematically rigorous color science algorithms

Ideal for students. web developers, designers, and for anyone who ever had to pick a pair of text,bg color for the web

License: GNU General Public License v3.0
"""

from typing import Tuple, Optional

from cm_colors.core.color_metrics import (
    rgb_to_lab,
    calculate_delta_e_2000,
)

from cm_colors.core.conversions import (
    rgb_to_oklch_safe,
    oklch_to_rgb_safe,
    is_valid_rgb,
    is_valid_oklch,
    parse_color_to_rgb,
)

from cm_colors.core.contrast import calculate_contrast_ratio, get_wcag_level

from cm_colors.core.optimisation import check_and_fix_contrast


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

    def tune_colors(
        self, text_rgb, bg_rgb, large_text: bool = False, details: bool = False
    ):
        """
        Checks the contrast between text and background colors and, if necessary,
        adjusts the text color to meet WCAG AAA requirements (or AA for large text)
        with minimal perceptual change.

        This function uses an optimized approach combining binary search and gradient descent.

        Args:
            text: Text color (any valid hex, rgb string or rgb tuple)
            bg: Background color (any valid hex, rgb string or rgb tuple)
            large: True for large text (18pt+ or 14pt+ bold), False for normal text
            details: If True, returns detailed report, else just (tuned_color, is_accessible)

        Returns:
                If details=False (default):
                   A tuple containing:
                    - The adjusted text color (RGB string i.e 'rgb(...)').
                    - A boolean indicating if the color pair is accessible (meets atleast WCAG AA).

                If details=True:
                   A detailed dict including:
                        - text: The original text color
                        - tuned_text: The adjusted text color
                        - bg: The background color
                        - large: Whether the text is considered large
                        - wcag_level: The WCAG compliance level
                        - improvement_percentage: The percentage improvement in contrast
                        - status: True if wcag_level != 'FAIL' else False,
                        - message: The status message
        """

        return check_and_fix_contrast(text_rgb, bg_rgb, large_text, details)

    def contrast_ratio(
        self, text_rgb: Tuple[int, int, int], bg_rgb: Tuple[int, int, int]
    ) -> float:
        """
        Calculates the WCAG contrast ratio between two RGB colors.

        Args:
            text_rgb (Tuple[int, int, int]): The RGB tuple for the text color (R, G, B).
            bg_rgb (Tuple[int, int, int]): The RGB tuple for the background color (R, G, B).

        Returns:
            float: The calculated contrast ratio.
        """
        if not (is_valid_rgb(text_rgb) and is_valid_rgb(bg_rgb)):
            raise ValueError(
                "Invalid RGB values provided. Each component must be between 0 and 255."
            )
        return calculate_contrast_ratio(text_rgb, bg_rgb)

    def wcag_level(
        self,
        text_rgb: Tuple[int, int, int],
        bg_rgb: Tuple[int, int, int],
        large_text: bool = False,
    ) -> str:
        """
        Determines the WCAG contrast level (AAA, AA, FAIL) based on the color pair and whether the text is considered 'large'.

        Args:
            text_rgb (Tuple[int, int, int]): The RGB tuple for the text color (R, G, B).
            bg_rgb (Tuple[int, int, int]): The RGB tuple for the background color (R, G, B).
            large_text (bool): True if the text is considered large (18pt or 14pt bold), False otherwise (default).

        Returns:
            str: The WCAG compliance level ("AAA", "AA", or "FAIL").
        """
        return get_wcag_level(text_rgb, bg_rgb, large_text)

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
            raise ValueError(
                "Invalid RGB values provided. Each component must be between 0 and 255."
            )
        return rgb_to_oklch_safe(rgb)

    def oklch_to_rgb(self, oklch: Tuple[float, float, float]) -> Tuple[int, int, int]:
        """
        Converts an OKLCH color back to the RGB color space.

        Args:
            oklch (Tuple[float, float, float]): The OKLCH tuple (Lightness, Chroma, Hue).

        Returns:
            Tuple[int, int, int]: The RGB tuple (R, G, B).
        """
        if not is_valid_oklch(oklch):
            raise ValueError(
                "Invalid OKLCH values provided. Lightness 0-1, Chroma >=0, Hue 0-360."
            )
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
            raise ValueError(
                "Invalid RGB values provided. Each component must be between 0 and 255."
            )
        return rgb_to_lab(rgb)

    def delta_e(self, rgb1: Tuple[int, int, int], rgb2: Tuple[int, int, int]) -> float:
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
            raise ValueError(
                "Invalid RGB values provided. Each component must be between 0 and 255."
            )
        return calculate_delta_e_2000(rgb1, rgb2)

    def parse_to_rgb(self, color: str) -> Tuple[int, int, int]:
        """
        Parses a color string (hex, rgb) to an RGB tuple.

        Args:
            color (str): The color string in hex (#RRGGBB), rgb(r, g, b), or named format.

        Returns:
            Tuple[int, int, int]: The RGB tuple (R, G, B).
        """
        return parse_color_to_rgb(color)


# Example Usage (for testing or direct script execution)
if __name__ == "__main__":

    cm_colors = CMColors()

    # Example 1: Check and fix contrast (simple return)
    text_color_orig = (100, 100, 100)  # Grey
    bg_color = (255, 255, 255)  # White

    print(f"Original Text Color: {text_color_orig}, Background Color: {bg_color}")

    # Simple usage - just get the tuned color and success status
    tuned_color, is_accessible = cm_colors.tune_colors(text_color_orig, bg_color)
    print(f"Tuned Color: {tuned_color}, Is Accessible: {is_accessible}")

    # Get detailed information
    detailed_result = cm_colors.tune_colors(text_color_orig, bg_color, details=True)
    print(f"Detailed result: {detailed_result['message']}")
    print(
        f"WCAG Level: {detailed_result['wcag_level']}, Improvement: {detailed_result['improvement_percentage']:.1f}%\n"
    )

    # Example 2: Another contrast check (already good colors)
    text_color_good = (0, 0, 0)  # Black
    bg_color_good = (255, 255, 255)  # White

    print(f"Original Text Color: {text_color_good}, Background Color: {bg_color_good}")

    # Simple check
    tuned_good, is_accessible_good = cm_colors.tune_colors(
        text_color_good, bg_color_good
    )
    print(f"Tuned Color: {tuned_good} (should be same as original)")

    # Detailed check
    detailed_good = cm_colors.tune_colors(text_color_good, bg_color_good, details=True)
    print(f"Status: {detailed_good['message']}")
    print(f"WCAG Level: {detailed_good['wcag_level']}\n")

    # Example 3: Large text example
    text_large = (150, 150, 150)  # Light grey
    bg_large = (255, 255, 255)  # White

    print(f"Large text example - Original: {text_large}, Background: {bg_large}")

    # Large text has different contrast requirements
    tuned_large, accessible_large = cm_colors.tune_colors(
        text_large, bg_large, large_text=True
    )
    detailed_large = cm_colors.tune_colors(
        text_large, bg_large, large_text=True, details=True
    )

    print(f"Large text tuned: {tuned_large}, Accessible: {accessible_large}")
    print(f"Large text WCAG level: {detailed_large['wcag_level']}\n")

    # Example 4: Color space conversions
    test_rgb = (123, 45, 200)  # A shade of purple
    print(f"Testing color conversions for RGB: {test_rgb}")

    oklch_color = cm_colors.rgb_to_oklch(test_rgb)
    print(
        f"OKLCH: L={oklch_color[0]:.3f}, C={oklch_color[1]:.3f}, H={oklch_color[2]:.1f}"
    )

    rgb_from_oklch = cm_colors.oklch_to_rgb(oklch_color)
    print(f"RGB back from OKLCH: {rgb_from_oklch}")

    lab_color = cm_colors.rgb_to_lab(test_rgb)
    print(f"LAB: L={lab_color[0]:.3f}, a={lab_color[1]:.3f}, b={lab_color[2]:.3f}\n")

    # Example 5: Delta E 2000 calculation
    color1 = (255, 0, 0)  # Red
    color2 = (250, 5, 5)  # Slightly different red
    delta_e = cm_colors.delta_e(color1, color2)
    print(f"Delta E 2000 between {color1} and {color2}: {delta_e:.2f}")

    color3 = (0, 0, 255)  # Blue
    color4 = (0, 255, 0)  # Green
    delta_e_large = cm_colors.delta_e(color3, color4)
    print(f"Delta E 2000 between {color3} and {color4}: {delta_e_large:.2f}\n")

    # Example 6: Direct contrast ratio and WCAG level checking
    print("Direct utility functions:")
    contrast = cm_colors.contrast_ratio((50, 50, 50), (255, 255, 255))
    wcag = cm_colors.wcag_level((50, 50, 50), (255, 255, 255))
    print(f"Contrast ratio: {contrast:.2f}, WCAG level: {wcag}")

    # Large text WCAG level
    wcag_large = cm_colors.wcag_level((50, 50, 50), (255, 255, 255), large_text=True)
    print(f"Same colors for large text WCAG level: {wcag_large}\n")
