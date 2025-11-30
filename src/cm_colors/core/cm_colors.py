"""CM-Colors - Accessible Color Science Library.

A Python library for ensuring color accessibility based on WCAG guidelines.
Automatically fix colors to be readable with minimal visual change.

Ideal for students, web developers, designers, and for anyone who ever had to pick a pair of text,bg color for the web.

License:
    GNU General Public License v3.0
"""

from cm_colors.core.colors import ColorPair, Color
from cm_colors.core.visualiser import to_html_bulk
from cm_colors.core.contrast import get_wcag_level
from cm_colors.core.conversions import rgbint_to_string


def make_readable_bulk(pairs, mode=1, very_readable=False, save_report=False):
    """Fix multiple color pairs to make them readable.

    Takes a list of color pairs and makes sure the text is readable on each
    background. Returns the fixed colors along with their readability status.

    Args:
        pairs (list): List of color pairs. Each pair is a tuple of (text_color, bg_color)
            or (text_color, bg_color, large) where large is a bool for large text.
        mode (int): How strict to be about color changes (0=Strict, 1=Default, 2=Relaxed).
        very_readable (bool): If True, aim for very readable colors (AAA).
        save_report (bool): If True, generate an HTML report showing all changes.

    Returns:
        list: List of tuples (fixed_color, status) where status is "readable",
            "very readable", or "not readable".

    Example:
        >>> pairs = [("#777", "#fff"), ("#000", "#000")]
        >>> make_readable_bulk(pairs)
        >>> [('#757575', 'readable'), ('#8e8e8e', 'not readable')]
    """
    results = []
    report_data = []

    for i, item in enumerate(pairs):
        # Handle tuple unpacking based on length
        if len(item) == 3:
            text, bg, large = item
        else:
            text, bg = item
            large = False

        pair = ColorPair(text, bg, large)

        # Determine target readability for the return status
        # We want to return the status of the *tuned* color

        if not pair.is_valid:
            results.append((text, 'invalid color'))
            continue

        # Tune the color - returns (color, success)
        tuned_color, success = pair.make_readable(
            mode=mode, very_readable=very_readable
        )

        # Check readability of the result
        # We need to create a new pair to check the level of the result
        current_readability = 'not readable'
        original_level = get_wcag_level(
            pair.text.rgb, pair.bg.rgb, large
        )   # Get original WCAG level
        new_level = 'FAIL'

        if tuned_color:
            new_pair = ColorPair(tuned_color, bg, large)
            current_readability = (
                new_pair.is_readable.lower()
            )   # "readable", "very readable", "not readable"
            # Calculate new level for reporting
            try:
                c_tuned = Color(str(tuned_color))
                if c_tuned.is_valid:
                    new_level = get_wcag_level(c_tuned.rgb, pair.bg.rgb, large)
            except:
                pass
            results.append((tuned_color, current_readability))
        else:
            # If tuning failed (shouldn't happen often with default mode), return original and its status
            current_readability = pair.is_readable.lower()
            new_level = original_level
            results.append((text, current_readability))

        if save_report:
            # Preserve input format for strings (e.g. Hex), use composited RGB for tuples
            fg_str = str(text)
            bg_str = str(bg)

            if isinstance(text, (tuple, list)) and pair.text.is_valid:
                fg_str = rgbint_to_string(pair.text.rgb)
            if isinstance(bg, (tuple, list)) and pair.bg.is_valid:
                bg_str = rgbint_to_string(pair.bg.rgb)

            # Format tuned color for HTML (must be valid CSS)
            tuned_fg_str = fg_str   # Default to original if no change
            if tuned_color:
                if isinstance(tuned_color, (tuple, list)):
                    tuned_fg_str = rgbint_to_string(tuned_color)
                else:
                    tuned_fg_str = str(tuned_color)

            report_data.append(
                {
                    'fg': fg_str,
                    'bg': bg_str,
                    'tuned_fg': tuned_fg_str,
                    'original_level': original_level,
                    'new_level': new_level,
                    'selector': f'Pair {i+1}',
                    'file': 'Bulk API',
                }
            )

    if save_report and report_data:
        report_path = to_html_bulk(
            report_data, output_path='cm_colors_bulk_report.html'
        )
        print(f'Report generated: {report_path}')

    return results
