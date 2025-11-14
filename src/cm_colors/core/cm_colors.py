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

from typing import Tuple

from cm_colors.core.color_metrics import (
    rgb_to_lab,
)

from cm_colors.core.conversions import (
    rgb_to_oklch_safe,
    oklch_to_rgb_safe,
    is_valid_rgb,
    is_valid_oklch,
)

from cm_colors.core.colors import Color, ColorPair

from cm_colors.core.color_parser import parse_color_to_rgb

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
        self, text, bg, large_text: bool = False, details: bool = False
    ):
        """
        Adjusts the text color to meet WCAG contrast requirements against a background.

        Parameters:
            text (str|tuple): Text color in any supported format (hex string, rgb(a) string, named color, or RGB tuple).
            bg (str|tuple): Background color in any supported format (hex string, rgb(a) string, named color, or RGB tuple).
            large_text (bool): True when text is considered large (18pt+ or 14pt+ bold); affects required WCAG level.
            details (bool): If True, return a detailed report instead of the simple result tuple.

        Returns:
            If details is False:
                tuple: (tuned_text_rgb_str, is_accessible)
                    tuned_text_rgb_str (str): Adjusted text color as an 'rgb(...)' string.
                    is_accessible (bool): `True` if the adjusted pair meets at least WCAG AA, `False` otherwise.
            If details is True:
                dict: Detailed report with keys:
                    - text: original text color input
                    - tuned_text: adjusted text color as an 'rgb(...)' string
                    - bg: background color input
                    - large: value of the large_text parameter
                    - wcag_level: resulting WCAG compliance level ('AAA', 'AA', or 'FAIL')
                    - improvement_percentage: percentage improvement in contrast
                    - status: `True` if wcag_level != 'FAIL', `False` otherwise
                    - message: human-readable status message
        """
        pair = ColorPair(text, bg, large_text)
        if not pair.is_valid:
            raise ValueError(f"Invalid color pair: {', '.join(pair.errors)}")

        return pair.tune_colors(details)

    def contrast_ratio(self, text_color, bg_color) -> float:
        """
        Compute the WCAG contrast ratio between two colors.

        Parameters:
            text_color: Text color in any supported format (hex, "rgb(...)", "rgba(...)", 3-tuple, named color, etc.).
            bg_color: Background color in any supported format.

        Returns:
            float: The computed contrast ratio between the text and background colors.

        Raises:
            ValueError: If either color cannot be parsed or the color pair is invalid.
        """
        pair = ColorPair(text_color, bg_color)

        if not pair.is_valid:
            error_msgs = ', '.join(pair.errors)
            raise ValueError(f'Invalid color input(s): {error_msgs}')

        return pair.contrast_ratio

    def wcag_level(
        self, text_color, bg_color, large_text: bool = False
    ) -> str:
        """
        Determine the WCAG contrast compliance level for a text/background color pair, considering large-text rules.

        Parameters:
            text_color: Text color in any supported format (hex, rgb/rgba string, (r,g,b) tuple, named color, etc.). RGBA colors will be composited as needed.
            bg_color: Background color in any supported format.
            large_text (bool): True when text is considered large (18pt+ or 14pt+ bold), False otherwise.

        Returns:
            str: `'AAA'`, `'AA'`, or `'FAIL'` indicating the WCAG compliance level.

        Raises:
            ValueError: If one or both colors cannot be parsed or are otherwise invalid.
        """
        pair = ColorPair(text_color, bg_color, large_text)

        if not pair.is_valid:
            error_msgs = ', '.join(pair.errors)
            raise ValueError(
                f'Cannot determine WCAG level - invalid color input(s): {error_msgs}'
            )

        return pair.wcag_level

    def rgb_to_oklch(
        self, rgb: Tuple[int, int, int]
    ) -> Tuple[float, float, float]:
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
                'Invalid RGB values provided. Each component must be between 0 and 255.'
            )
        return rgb_to_oklch_safe(rgb)

    def oklch_to_rgb(
        self, oklch: Tuple[float, float, float]
    ) -> Tuple[int, int, int]:
        """
        Converts an OKLCH color back to the RGB color space.

        Args:
            oklch (Tuple[float, float, float]): The OKLCH tuple (Lightness, Chroma, Hue).

        Returns:
            Tuple[int, int, int]: The RGB tuple (R, G, B).
        """
        if not is_valid_oklch(oklch):
            raise ValueError(
                'Invalid OKLCH values provided. Lightness 0-1, Chroma >=0, Hue 0-360.'
            )
        return oklch_to_rgb_safe(oklch)

    def rgb_to_lab(
        self, rgb: Tuple[int, int, int]
    ) -> Tuple[float, float, float]:
        """
        Converts an RGB color to the CIELAB (LAB) color space.

        Parameters:
            rgb (Tuple[int, int, int]): RGB components (R, G, B) with values 0–255.

        Returns:
            Tuple[float, float, float]: LAB tuple (L, a, b) where L is perceptual lightness.
        """
        if not is_valid_rgb(rgb):
            raise ValueError(
                'Invalid RGB values provided. Each component must be between 0 and 255.'
            )
        return rgb_to_lab(rgb)

    def delta_e(self, color1, color2) -> float:
        """
        Compute the Delta E 2000 color difference between two colors.

        Accepts color inputs in any supported format (hex, rgb/rgba strings, tuples, named colors, etc.). RGBA inputs will be composited as needed before comparison.

        Parameters:
            color1: First color (text or sample) in any supported format.
            color2: Second color (background or reference) in any supported format.

        Returns:
            float: The Delta E 2000 distance. Values below about 2.3 are typically imperceptible to the average observer.
        """

        pair = ColorPair(color1, color2)

        if not pair.is_valid:
            error_msgs = ', '.join(pair.errors)
            raise ValueError(f'Invalid color input(s): {error_msgs}')

        return pair.delta_e

    def parse_to_rgb(self, color: str) -> Tuple[int, int, int]:
        """
        Convert a color string in common formats to an RGB triple.

        Accepts hex (#RRGGBB, #RGB), functional rgb()/rgba() (alpha composited over white), and CSS color names. Parsing is case-insensitive and will composite RGBA into an opaque RGB when an alpha channel is provided.

        Parameters:
            color (str): Color value in hex, rgb(a) function notation, or named color.

        Returns:
            tuple: (R, G, B) with each component as an integer in the range 0–255.
        """
        return parse_color_to_rgb(color)


# Example Usage (for testing or direct script execution)
if __name__ == '__main__':

    cm_colors = CMColors()

    # Example 1: Check and fix contrast (simple return)
    text_color_orig = (100, 100, 100)  # Grey
    bg_color = (255, 255, 255)  # White

    print(
        f'Original Text Color: {text_color_orig}, Background Color: {bg_color}'
    )

    # Simple usage - just get the tuned color and success status
    tuned_color, is_accessible = cm_colors.tune_colors(
        text_color_orig, bg_color
    )
    print(f'Tuned Color: {tuned_color}, Is Accessible: {is_accessible}')

    # Get detailed information
    detailed_result = cm_colors.tune_colors(
        text_color_orig, bg_color, details=True
    )
    print(f"Detailed result: {detailed_result['message']}")
    print(
        f"WCAG Level: {detailed_result['wcag_level']}, Improvement: {detailed_result['improvement_percentage']:.1f}%\n"
    )

    # Example 2: Another contrast check (already good colors)
    text_color_good = (0, 0, 0)  # Black
    bg_color_good = (255, 255, 255)  # White

    print(
        f'Original Text Color: {text_color_good}, Background Color: {bg_color_good}'
    )

    # Simple check
    tuned_good, is_accessible_good = cm_colors.tune_colors(
        text_color_good, bg_color_good
    )
    print(f'Tuned Color: {tuned_good} (should be same as original)')

    # Detailed check
    detailed_good = cm_colors.tune_colors(
        text_color_good, bg_color_good, details=True
    )
    print(f"Status: {detailed_good['message']}")
    print(f"WCAG Level: {detailed_good['wcag_level']}\n")

    # Example 3: Large text example
    text_large = (150, 150, 150)  # Light grey
    bg_large = (255, 255, 255)  # White

    print(
        f'Large text example - Original: {text_large}, Background: {bg_large}'
    )

    # Large text has different contrast requirements
    tuned_large, accessible_large = cm_colors.tune_colors(
        text_large, bg_large, large_text=True
    )
    detailed_large = cm_colors.tune_colors(
        text_large, bg_large, large_text=True, details=True
    )

    print(f'Large text tuned: {tuned_large}, Accessible: {accessible_large}')
    print(f"Large text WCAG level: {detailed_large['wcag_level']}\n")

    # Example 4: Color space conversions
    test_rgb = (123, 45, 200)  # A shade of purple
    print(f'Testing color conversions for RGB: {test_rgb}')

    oklch_color = cm_colors.rgb_to_oklch(test_rgb)
    print(
        f'OKLCH: L={oklch_color[0]:.3f}, C={oklch_color[1]:.3f}, H={oklch_color[2]:.1f}'
    )

    rgb_from_oklch = cm_colors.oklch_to_rgb(oklch_color)
    print(f'RGB back from OKLCH: {rgb_from_oklch}')

    lab_color = cm_colors.rgb_to_lab(test_rgb)
    print(
        f'LAB: L={lab_color[0]:.3f}, a={lab_color[1]:.3f}, b={lab_color[2]:.3f}\n'
    )

    # Example 5: Delta E 2000 calculation
    color1 = (255, 0, 0)  # Red
    color2 = (250, 5, 5)  # Slightly different red
    delta_e = cm_colors.delta_e(color1, color2)
    print(f'Delta E 2000 between {color1} and {color2}: {delta_e:.2f}')

    color3 = (0, 0, 255)  # Blue
    color4 = (0, 255, 0)  # Green
    delta_e_large = cm_colors.delta_e(color3, color4)
    print(f'Delta E 2000 between {color3} and {color4}: {delta_e_large:.2f}\n')

    # Example 6: Direct contrast ratio and WCAG level checking
    print('Direct utility functions:')
    contrast = cm_colors.contrast_ratio((50, 50, 50), (255, 255, 255))
    wcag = cm_colors.wcag_level((50, 50, 50), (255, 255, 255))
    print(f'Contrast ratio: {contrast:.2f}, WCAG level: {wcag}')

    # Large text WCAG level
    wcag_large = cm_colors.wcag_level(
        (50, 50, 50), (255, 255, 255), large_text=True
    )
    print(f'Same colors for large text WCAG level: {wcag_large}\n')
