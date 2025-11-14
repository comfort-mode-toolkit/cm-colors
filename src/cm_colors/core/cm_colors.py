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
    is_valid_oklch
)

from cm_colors.core.colors import Color,ColorPair

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
        self, text_rgb, bg_rgb, large_text: bool = False, details: bool = False
    ):
        """
        Adjusts a text color so it meets WCAG contrast requirements against a given background.
        
        Parameters:
            text_rgb: Text color in any supported format (hex string, rgb/rgba string, named color, or RGB tuple).
            bg_rgb: Background color in any supported format (hex string, rgb/rgba string, named color, or RGB tuple). RGBA inputs are composited over their backgrounds.
            large_text (bool): Treat the text as large (WCAG large-text thresholds) when True.
            details (bool): If True, return a detailed report dictionary instead of the simple tuple.
        
        Returns:
            If details is False: A tuple (adjusted_text_rgb, accessible) where `adjusted_text_rgb` is the tuned text color as an RGB string (e.g., "rgb(...)") and `accessible` is `True` if the pair meets at least WCAG AA, `False` otherwise.
        
            If details is True: A dictionary with keys:
                - text: original text color input
                - tuned_text: adjusted text color as an RGB string
                - bg: background color input
                - large: boolean indicating large-text mode
                - wcag_level: resulting WCAG level ("AAA", "AA", or "FAIL")
                - improvement_percentage: numeric percentage improvement in contrast
                - status: `True` if wcag_level != "FAIL", `False` otherwise
                - message: human-readable status message
        """

        return check_and_fix_contrast(text_rgb, bg_rgb, large_text, details)

    def contrast_ratio(self, text_color, bg_color) -> float:
        """
        Compute the WCAG contrast ratio between two colors.
        
        Parameters:
            text_color: Text color in any supported format (hex string, `rgb()`/`rgba()` string, tuple, named color, etc.).
            bg_color: Background color in any supported format.
        
        Returns:
            contrast_ratio (float): Contrast ratio according to WCAG.
        
        Raises:
            ValueError: If one or both colors cannot be parsed or are invalid.
        """
        pair = ColorPair(text_color, bg_color)
        
        if not pair.is_valid:
            error_msgs = ", ".join(pair.errors)
            raise ValueError(f"Invalid color input(s): {error_msgs}")
        
        return pair.contrast_ratio

    def wcag_level(self, text_color, bg_color, large_text: bool = False) -> str:
        """
        Determines the WCAG contrast level (AAA, AA, FAIL) based on the color pair and text size.
        
        Now accepts any color format: hex, rgb(), rgba(), tuples, named colors, etc.
        RGBA colors are automatically composited over backgrounds.

        Args:
            text_color: Text color in any supported format (hex, rgb/rgba strings, tuples, named colors)
            bg_color: Background color in any supported format  
            large_text (bool): True if text is large (18pt+ or 14pt+ bold), False otherwise

        Returns:
            str: WCAG compliance level ("AAA", "AA", or "FAIL")
            
        Raises:
            ValueError: If either color cannot be parsed
            
        Examples:
            wcag_level("#ff0000", "white")                    # hex + named
            wcag_level("rgba(255,0,0,0.8)", "#ffffff")       # rgba with auto-compositing  
            wcag_level((255,0,0), (255,255,255))             # tuples
            wcag_level("red", "rgb(255,255,255)")            # mixed formats
        """
        pair = ColorPair(text_color, bg_color)
        
        if not pair.is_valid:
            error_msgs = ", ".join(pair.errors)
            raise ValueError(f"Cannot determine WCAG level - invalid color input(s): {error_msgs}")
        
        return pair.wcag_level

    def rgb_to_oklch(self, rgb: Tuple[int, int, int]) -> Tuple[float, float, float]:
        """
        Convert an RGB color tuple to the OKLCH color space.
        
        Parameters:
            rgb (Tuple[int, int, int]): RGB tuple (R, G, B) with each component in the range 0–255.
        
        Returns:
            Tuple[float, float, float]: OKLCH tuple (Lightness, Chroma, Hue).
                - Lightness: 0.0–1.0
                - Chroma: non-negative (typical upper range ≈ 0.4)
                - Hue: degrees in the range 0–360
        
        Raises:
            ValueError: If any RGB component is outside the 0–255 range.
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
        Convert an RGB color to the CIELAB color space (L*, a*, b*).
        
        Parameters:
            rgb (Tuple[int, int, int]): RGB components as integers in the range 0–255.
        
        Returns:
            Tuple[float, float, float]: CIELAB coordinates (L*, a*, b*).
        
        Raises:
            ValueError: If any RGB component is outside the 0–255 range.
        """
        if not is_valid_rgb(rgb):
            raise ValueError(
                "Invalid RGB values provided. Each component must be between 0 and 255."
            )
        return rgb_to_lab(rgb)

    def delta_e(self, color1,color2) -> float:
        """
        Compute the Delta E 2000 color difference between two colors.
        
        Args:
            color1: First color; accepts hex, rgb/rgba strings, tuples, named colors, or any format supported by the library.
            color2: Second color in any supported format.
        
        Returns:
            float: The Delta E 2000 value. Values less than 2.3 are generally imperceptible to the average human eye.
        
        Raises:
            ValueError: If either input cannot be parsed as a valid color (error messages from parsing are combined).
        """

        pair = ColorPair(color1, color2)
        
        if not pair.is_valid:
            error_msgs = ", ".join(pair.errors)
            raise ValueError(f"Invalid color input(s): {error_msgs}")
        
        return pair.delta_e

    def parse_to_rgb(self, color: str) -> Tuple[int, int, int]:
        """
        Parse a color string into an RGB tuple.
        
        Accepts hex (e.g. "#RRGGBB"), `rgb()`/`rgba()` strings, and named color strings.
        
        Parameters:
        	color (str): Color string to parse.
        
        Returns:
        	Tuple[int, int, int]: RGB tuple (R, G, B) with channels in the range 0–255.
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