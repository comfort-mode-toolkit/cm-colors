# colors.py
from typing import Tuple, Optional, Union
from .color_parser import parse_color_to_rgb
from .contrast import calculate_contrast_ratio, get_wcag_level
from .conversions import rgbint_to_string, rgb_to_oklch_safe
from .color_metrics import calculate_delta_e_2000


class Color:
    def __init__(
        self,
        color_input: Union[str, tuple, list],
        background_context: Optional['Color'] = None,
    ):
        """
        Parse and store a color value with optional background for RGBA compositing.

        :param color_input: The color value as a string, tuple, or list.
        :type color_input: Union[str, tuple, list]
        :param background_context: Optional Color instance used for RGBA compositing during parsing.
        :type background_context: Optional['Color']
        """
        self.original = color_input
        self.background_context = background_context
        self._rgb = None
        self._error = None
        self._parsed = False

        self._parse()

    def _parse(self) -> None:
        """
        Parse the instance's original color input into an RGB triple, using the optional background context for compositing.

        On success, stores the resulting RGB tuple in ``self._rgb`` and marks the instance as parsed. On failure due to invalid input, stores the error message in ``self._error`` and marks the instance as parsed.
        """
        if self._parsed:
            return

        try:
            bg_rgb = None
            if self.background_context and self.background_context.is_valid:
                bg_rgb = self.background_context.rgb

            self._rgb = parse_color_to_rgb(self.original, background=bg_rgb)
            self._parsed = True
        except ValueError as e:
            self._error = str(e)
            self._parsed = True

    @property
    def is_valid(self) -> bool:
        """
        Indicates whether the color was parsed successfully and an RGB value is available.

        :returns: ``True`` if a parsed RGB tuple is present, ``False`` otherwise.
        :rtype: bool
        """
        return self._rgb is not None

    @property
    def rgb(self) -> Optional[Tuple[int, int, int]]:
        """
        Parsed RGB components of the color if parsing succeeded.

        :returns: Red, green, and blue components (0â€“255) when available, or ``None`` if the input failed to parse.
        :rtype: Tuple[int, int, int]
        """
        return self._rgb

    @property
    def error(self) -> Optional[str]:
        """
        Return the parsing error message for the color, if any.

        :returns: The error message produced while parsing the original input, or ``None`` if parsing succeeded.
        :rtype: Optional[str]
        """
        return self._error

    def to_hex(self) -> Optional[str]:
        """
        Get the hexadecimal "#rrggbb" representation of the parsed color.

        :returns: The color as a lowercase "#rrggbb" hex string, or ``None`` if the color is invalid.
        :rtype: str
        """
        if not self.is_valid:
            return None
        r, g, b = self.rgb
        return f'#{r:02x}{g:02x}{b:02x}'

    def to_rgb_string(self) -> Optional[str]:
        """
        Return a CSS-style RGB string for the parsed color.

        :returns: A string like "rgb(r, g, b)" representing the color, or ``None`` if the color is invalid.
        :rtype: Optional[str]
        """
        if not self.is_valid:
            return None
        return rgbint_to_string(self.rgb)

    def to_oklch(self):
        """
        Convert the parsed RGB color to the OKLCH color space.

        :returns: An OKLCH tuple (L, C, h) representing the color, or None if the color could not be parsed.
        :rtype: Optional[Tuple[float, float, float]]
        """
        if not self.is_valid:
            return None
        return rgb_to_oklch_safe(self._rgb)


class ColorPair:
    def __init__(self, text_color, bg_color, large_text=False):
        # Parse background first for RGBA context
        """
        Initialize a ColorPair with a foreground (text) color, a background color, and a large-text flag.

        :param text_color: Color input for the foreground; parsed with the background used as compositing context for any alpha/RGBA values.
        :param bg_color: Color input for the background; parsed first and provided to the text color for RGBA compositing.
        :param large_text: Whether the text should be treated as large for WCAG contrast evaluation. Defaults to False.
        :type large_text: bool
        """
        self.bg = Color(bg_color)
        # Pass background context for RGBA compositing
        self.text = Color(text_color, background_context=self.bg)
        self.large_text = large_text

    @property
    def is_valid(self) -> bool:
        """
        Indicates whether both the text and background colors were parsed successfully.

        :returns: True if both text and background colors are valid, False otherwise.
        :rtype: bool
        """
        return self.text.is_valid and self.bg.is_valid

    @property
    def errors(self) -> list[str]:
        """
        Collects error messages for any invalid text or background Color in the pair.

        :returns: A list of error strings. Includes "Text: <message>" if the text color is invalid and "Background: <message>" if the background color is invalid; empty if both are valid.
        :rtype: list[str]
        """
        errors = []
        if not self.text.is_valid:
            errors.append(f'Text: {self.text.error}')
        if not self.bg.is_valid:
            errors.append(f'Background: {self.bg.error}')
        return errors

    @property
    def contrast_ratio(self) -> Optional[float]:
        """
        Compute the contrast ratio between the text and background colors.

        :returns: Contrast ratio according to WCAG, or ``None`` if either color is invalid.
        :rtype: Optional[float]
        """
        if not self.is_valid:
            return None
        return calculate_contrast_ratio(self.text.rgb, self.bg.rgb)

    @property
    def wcag_level(self) -> Optional[str]:
        """
        Determine the WCAG contrast compliance level for the text/background color pair.

        :returns: The WCAG contrast level identifier (for example "AA", "AAA", or "AA Large") for the current text and background colors, or ``None`` if the color pair is invalid.
        :rtype: Optional[str]
        """
        if not self.is_valid:
            return None
        return get_wcag_level(self.text.rgb, self.bg.rgb, self.large_text)

    @property
    def delta_e(self) -> Optional[float]:
        """
        Compute the CIEDE2000 color difference between the background and text colors.

        :returns: The CIEDE2000 Delta E between background and text colors, or ``None`` if either color is invalid.
        :rtype: Optional[float]
        """
        if not self.is_valid:
            return None
        return calculate_delta_e_2000(self.bg.rgb, self.text.rgb)

    def tune_colors(self, details: bool = False):
        """
        Adjusts the text/background colors to meet WCAG contrast requirements.

        When the color pair is invalid, returns an immediate failure:
        - If ``details`` is True, returns a dict ``{"status": False, "message": "<errors>"}`` where ``<errors>`` lists the invalid components.
        - If ``details`` is False, returns ``(None, False)``.

        :param details: If True, return a detailed result dictionary; if False, return a compact tuple.
        :type details: bool
        :returns: If ``details`` is True, a dictionary describing the operation result and any messages.
                  If ``details`` is False, a tuple ``(rgb, success)`` where ``rgb`` is the adjusted text color as an (R, G, B) tuple when ``success`` is True, or ``None`` when ``success`` is False.
        :rtype: Union[dict, tuple]
        """
        if not self.is_valid:
            if details:
                return {
                    'status': False,
                    'message': f"Invalid color pair: {', '.join(self.errors)}",
                }
            return None, False

        # Use your existing optimized function
        from .optimisation import check_and_fix_contrast

        return check_and_fix_contrast(
            self.text._rgb, self.bg._rgb, self.large_text, details
        )