# colors.py
from typing import Tuple, Optional, Union
from .color_parser import parse_color_to_rgb, detect_color_format, format_color
from .contrast import calculate_contrast_ratio, get_wcag_level
from .conversions import rgbint_to_string, rgb_to_oklch_safe
from .color_metrics import calculate_delta_e_2000


class Color:
    def __init__(
        self,
        color_input: Union[str, tuple, list],
        background_context: Optional['Color'] = None,
    ):
        """Parse and store a color value with optional background for RGBA compositing.

        Args:
            color_input (Union[str, tuple, list]): The color value as a string, tuple, or list.
            background_context (Optional['Color']): Optional Color instance used for RGBA compositing during parsing.
        """
        self.original = color_input
        self.background_context = background_context
        self._rgb = None
        self._error = None
        self._parsed = False
        self._format = 'unknown'

        self._parse()

    def _parse(self) -> None:
        """Parse the instance's original color input into an RGB triple, using the optional background context for compositing.

        On success, stores the resulting RGB tuple in ``self._rgb`` and marks the instance as parsed. On failure due to invalid input, stores the error message in ``self._error`` and marks the instance as parsed.
        """
        if self._parsed:
            return

        try:
            # Detect format
            self._format = detect_color_format(self.original)
            
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
        """Indicates whether the color was parsed successfully and an RGB value is available.

        Returns:
            bool: ``True`` if a parsed RGB tuple is present, ``False`` otherwise.
        """
        return self._rgb is not None

    @property
    def rgb(self) -> Optional[Tuple[int, int, int]]:
        """Parsed RGB components of the color if parsing succeeded.

        Returns:
            Tuple[int, int, int]: Red, green, and blue components (0–255) when available, or ``None`` if the input failed to parse.
        """
        return self._rgb

    @property
    def error(self) -> Optional[str]:
        """Return the parsing error message for the color, if any.

        Returns:
            Optional[str]: The error message produced while parsing the original input, or ``None`` if parsing succeeded.
        """
        return self._error

    def to_hex(self) -> Optional[str]:
        """Get the hexadecimal "#rrggbb" representation of the parsed color.

        Returns:
            str: The color as a lowercase "#rrggbb" hex string, or ``None`` if the color is invalid.
        """
        if not self.is_valid:
            return None
        r, g, b = self.rgb
        return f'#{r:02x}{g:02x}{b:02x}'

    def to_rgb_string(self) -> Optional[str]:
        """Return a CSS-style RGB string for the parsed color.

        Returns:
            Optional[str]: A string like "rgb(r, g, b)" representing the color, or ``None`` if the color is invalid.
        """
        if not self.is_valid:
            return None
        return rgbint_to_string(self.rgb)

    def to_oklch(self):
        """Convert the parsed RGB color to the OKLCH color space.

        Returns:
            Optional[Tuple[float, float, float]]: An OKLCH tuple (L, C, h) representing the color, or None if the color could not be parsed.
        """
        if not self.is_valid:
            return None
        return rgb_to_oklch_safe(self._rgb)


class ColorPair:
    def __init__(self, text_color, bg_color, large_text=False):
        # Parse background first for RGBA context
        """Initialize a ColorPair with a foreground (text) color, a background color, and a large-text flag.

        Args:
            text_color: Color input for the foreground; parsed with the background used as compositing context for any alpha/RGBA values.
            bg_color: Color input for the background; parsed first and provided to the text color for RGBA compositing.
            large_text (bool): Whether the text should be treated as large for WCAG contrast evaluation. Defaults to False.
        """
        self.bg = Color(bg_color)
        # Pass background context for RGBA compositing
        self.text = Color(text_color, background_context=self.bg)
        self.large_text = large_text

    @property
    def is_valid(self) -> bool:
        """Indicates whether both the text and background colors were parsed successfully.

        Returns:
            bool: True if both text and background colors are valid, False otherwise.
        """
        return self.text.is_valid and self.bg.is_valid

    @property
    def errors(self) -> list[str]:
        """Collects error messages for any invalid text or background Color in the pair.

        Returns:
            list[str]: A list of error strings. Includes "Text: <message>" if the text color is invalid and "Background: <message>" if the background color is invalid; empty if both are valid.
        """
        errors = []
        if not self.text.is_valid:
            errors.append(f'Text: {self.text.error}')
        if not self.bg.is_valid:
            errors.append(f'Background: {self.bg.error}')
        return errors

    @property
    def contrast_ratio(self) -> Optional[float]:
        """Compute the contrast ratio between the text and background colors.

        Returns:
            Optional[float]: Contrast ratio according to WCAG, or ``None`` if either color is invalid.
        """
        if not self.is_valid:
            return None
        return calculate_contrast_ratio(self.text.rgb, self.bg.rgb)

    @property
    def wcag_level(self) -> Optional[str]:
        """Determine the WCAG contrast compliance level for the text/background color pair.

        Returns:
            Optional[str]: The WCAG contrast level identifier (for example "AA", "AAA", or "AA Large") for the current text and background colors, or ``None`` if the color pair is invalid.
        """
        if not self.is_valid:
            return None
        return get_wcag_level(self.text.rgb, self.bg.rgb, self.large_text)

    @property
    def delta_e(self) -> Optional[float]:
        """Compute the CIEDE2000 color difference between the background and text colors.

        Returns:
            Optional[float]: The CIEDE2000 Delta E between background and text colors, or ``None`` if either color is invalid.
        """
        if not self.is_valid:
            return None
        return calculate_delta_e_2000(self.bg.rgb, self.text.rgb)

    def tune_colors(self, details: bool = False, mode: int = 1, premium: bool = False, show: bool = False, html: bool = False):
        """Adjusts the text/background colors to meet WCAG contrast requirements.

        When the color pair is invalid, returns an immediate failure:
        - If ``details`` is True, returns a dict ``{"status": False, "message": "<errors>"}`` where ``<errors>`` lists the invalid components.
        - If ``details`` is False, returns ``(None, False)``.

        Args:
            details (bool): If True, return a detailed result dictionary; if False, return a compact tuple.
            mode (int): Optimization mode (0=Strict, 1=Default, 2=Relaxed).
            premium (bool): If True, aim for AAA compliance (7.0 ratio).
            show (bool): If True, print a visual comparison to the console.
            html (bool): If True, generate an HTML report (for single pair usage).

        Returns:
            Union[dict, tuple]: If ``details`` is True, a dictionary describing the operation result and any messages.
                If ``details`` is False, a tuple ``(rgb, success)`` where ``rgb`` is the adjusted text color as an (R, G, B) tuple when ``success`` is True, or ``None`` when ``success`` is False.
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
        
        result = check_and_fix_contrast(
            self.text._rgb, self.bg._rgb, self.large_text, details, mode, premium
        )
        
        # Convert result back to original format
        if details:
            tuned_rgb_str = result.get('tuned_text')
            # Parse tuned_rgb_str to get RGB tuple
            if tuned_rgb_str:
                try:
                    c = Color(tuned_rgb_str)
                    if c.is_valid:
                        # Format back to original type
                        formatted_color = format_color(c.rgb, self.text._format)
                        result['tuned_text'] = formatted_color
                except:
                    pass
        else:
            tuned_rgb_str, success = result
            # Always convert to original format, regardless of success status
            if tuned_rgb_str:
                try:
                    c = Color(tuned_rgb_str)
                    if c.is_valid:
                        formatted_color = format_color(c.rgb, self.text._format)
                        result = (formatted_color, success)
                except:
                    pass

        # Handle visualizers
        if show or html:
            from .visualiser import to_console, to_html_bulk
            
            # Extract needed data
            tuned_rgb = None
            original_level = self.wcag_level
            new_level = None
            
            if details:
                tuned_rgb = result.get('tuned_text')
                new_level = result.get('wcag_level')
            else:
                tuned_rgb, success = result
                # Always use tuned_rgb (even if success=False, it's the best attempt)
                # Calculate new level for the tuned color
                new_pair = ColorPair(tuned_rgb, self.bg.original)
                new_level = new_pair.wcag_level

            if show:
                # Convert to hex for safer rich compatibility
                fg_hex = self.text.to_hex()
                bg_hex = self.bg.to_hex()
                
                # tuned_rgb is now in original format, parse it to get hex for visualizer
                tuned_hex = tuned_rgb
                
                # Handle different types of tuned_rgb
                if isinstance(tuned_rgb, tuple):
                    # It's an RGB tuple, convert to hex
                    r, g, b = tuned_rgb
                    tuned_hex = f'#{r:02x}{g:02x}{b:02x}'
                else:
                    try:
                        c = Color(str(tuned_rgb))
                        if c.is_valid:
                            tuned_hex = c.to_hex()
                    except:
                        pass

                # Check if colors are effectively the same
                if isinstance(fg_hex, str) and isinstance(tuned_hex, str) and fg_hex.lower() == tuned_hex.lower():
                    print("Colors are already accessible. No changes needed.")
                else:
                    to_console(
                        fg_hex, 
                        bg_hex, 
                        tuned_hex,
                        original_level,
                        new_level
                    )
                
            if html:
                # For single pair, generate a quick report
                pair_data = {
                    'fg': self.text.to_rgb_string(),
                    'bg': self.bg.to_rgb_string(),
                    'tuned_fg': str(tuned_rgb),
                    'original_level': original_level,
                    'new_level': new_level,
                    'selector': 'Manual Check',
                    'file': 'Python API'
                }
                report_path = to_html_bulk([pair_data], output_path="cm_colors_quick_report.html")
                print(f"Report generated: {report_path}")

        return result