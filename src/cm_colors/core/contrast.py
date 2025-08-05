from typing import Tuple


def rgb_to_linear(rgb_value: float) -> float:
    """Convert RGB value to linear RGB for contrast calculation"""
    normalized = rgb_value / 255.0
    if normalized <= 0.03928:
        return normalized / 12.92
    else:
        return pow((normalized + 0.055) / 1.055, 2.4)


def calculate_relative_luminance(rgb: Tuple[int, int, int]) -> float:
    """Calculate relative luminance according to WCAG"""
    r, g, b = rgb
    r_linear = rgb_to_linear(r)
    g_linear = rgb_to_linear(g)
    b_linear = rgb_to_linear(b)

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
    text_rgb: Tuple[int, int, int], bg_rgb: Tuple[int, int, int], large: bool = False
) -> str:
    """
    Check WCAG contrast level for given text and background colors.
    Returns 'AAA', 'AA', or 'FAIL'.
    """
    contrast_ratio = calculate_contrast_ratio(text_rgb, bg_rgb)
    return get_contrast_level(contrast_ratio, large)
