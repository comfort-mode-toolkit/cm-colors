from typing import Tuple
from cm_colors.core.conversions import srgb_to_linear


def calculate_relative_luminance(rgb: Tuple[int, int, int]) -> float:
    """Calculate relative luminance according to WCAG"""
    r, g, b = [x / 255.0 for x in rgb]
    r_linear = srgb_to_linear(r)
    g_linear = srgb_to_linear(g)
    b_linear = srgb_to_linear(b)

    return 0.2126 * r_linear + 0.7152 * g_linear + 0.0722 * b_linear


def calculate_contrast_ratio(
    text_rgb: Tuple[int, int, int], bg_rgb: Tuple[int, int, int]
) -> float:
    """Calculate WCAG contrast ratio between text and background colors"""
    text_luminance = calculate_relative_luminance(text_rgb)
    bg_luminance = calculate_relative_luminance(bg_rgb)

    lighter = max(text_luminance, bg_luminance)
    darker = min(text_luminance, bg_luminance)

    return (lighter + 0.05) / (darker + 0.05)


def get_contrast_level(contrast_ratio: float, large: bool = False) -> str:
    """Return WCAG contrast level based on ratio and text size"""
    if large:
        if contrast_ratio >= 4.5:
            return "AAA"
        elif contrast_ratio >= 3.0:
            return "AA"
        else:
            return "FAIL"
    else:
        if contrast_ratio >= 7.0:
            return "AAA"
        elif contrast_ratio >= 4.5:
            return "AA"
        else:
            return "FAIL"


def get_wcag_level(
    text_rgb: Tuple[int, int, int],
    bg_rgb: Tuple[int, int, int],
    large: bool = False,
) -> str:
    """
    Determine the WCAG contrast level for a text/background color pair.

    Parameters:
        text_rgb (Tuple[int, int, int]): Text color as an (R, G, B) tuple with components in the 0–255 range.
        bg_rgb (Tuple[int, int, int]): Background color as an (R, G, B) tuple with components in the 0–255 range.
        large (bool): If True, evaluate using WCAG thresholds for large-scale text; otherwise use normal text thresholds.

    Returns:
        str: One of 'AAA', 'AA', or 'FAIL' indicating the WCAG conformance level.
    """
    contrast_ratio = calculate_contrast_ratio(text_rgb, bg_rgb)
    return get_contrast_level(contrast_ratio, large)
