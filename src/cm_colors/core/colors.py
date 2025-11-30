# colors.py
from typing import Tuple, Optional, Union
from .color_parser import parse_color_to_rgb, detect_color_format, format_color
from .contrast import calculate_contrast_ratio, get_wcag_level
from .conversions import rgbint_to_string
from .color_metrics import calculate_delta_e_2000


class Color:
    def __init__(
        self,
        color_input: Union[str, tuple, list],
        background_context: Optional['Color'] = None,
    ):
        """Parse and store a color value.

        Args:
            color_input: The color value (hex, rgb tuple, etc).
            background_context: Optional background color for handling transparency.
        """
        self.original = color_input
        self.background_context = background_context
        self._rgb = None
        self._error = None
        self._parsed = False
        self._format = 'unknown'

        self._parse()

    def _parse(self) -> None:
        """Parse the color input into RGB."""
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
        """Check if the color is valid.

        Returns:
            bool: True if the color is valid, False otherwise.
        """
        return self._rgb is not None

    @property
    def rgb(self) -> Optional[Tuple[int, int, int]]:
        """Get the RGB components of the color.

        Returns:
            tuple: (Red, Green, Blue) values (0-255), or None if invalid.
        """
        return self._rgb

    @property
    def error(self) -> Optional[str]:
        """Get the error message if the color is invalid.

        Returns:
            str: The error message, or None if valid.
        """
        return self._error

    def to_hex(self) -> Optional[str]:
        """Get the hex code of the color.

        Returns:
            str: The color as a hex string (e.g. "#ff0000"), or None if invalid.
        """
        if not self.is_valid:
            return None
        r, g, b = self.rgb
        return f'#{r:02x}{g:02x}{b:02x}'


class ColorPair:
    def __init__(self, text_color, bg_color, large_text=False):
        """Initialize a pair of colors (text and background).

        Args:
            text_color: The text color.
            bg_color: The background color.
            large_text (bool): Set to True if the text is large (24px+ or 19px+ bold).
        """
        self.bg = Color(bg_color)
        # Pass background context for RGBA compositing
        self.text = Color(text_color, background_context=self.bg)
        self.large = large_text

    @property
    def is_valid(self) -> bool:
        """Check if both colors are valid.

        Returns:
            bool: True if both colors are valid, False otherwise.
        """
        return self.text.is_valid and self.bg.is_valid

    @property
    def errors(self) -> list[str]:
        """Get a list of errors if any colors are invalid.

        Returns:
            list: A list of error messages.
        """
        errors = []
        if not self.text.is_valid:
            errors.append(f'Text: {self.text.error}')
        if not self.bg.is_valid:
            errors.append(f'Background: {self.bg.error}')
        return errors

    @property
    def is_readable(self) -> str:
        """Check if the text is readable on the background.

        Returns:
            str: "Not Readable", "Readable", or "Very Readable".
                 Returns "Not Readable" if colors are invalid.

        Example:
            >>> pair = ColorPair("#000000", "#ffffff")
            >>> pair.is_readable
            'Very Readable'
        """
        if not self.is_valid:
            return 'Not Readable'

        level = get_wcag_level(self.text.rgb, self.bg.rgb, self.large)

        if level == 'AAA':
            return 'Very Readable'
        elif level == 'AA' or level == 'AA Large':
            return 'Readable'
        else:
            return 'Not Readable'

    def make_readable(
        self,
        mode: int = 1,
        very_readable: bool = False,
        show: bool = False,
        save_report: bool = False,
    ):
        """Fix the text color to make it readable on the background.

        Args:
            mode (int): How strict should we be about color change? (0=Strict, 1=Default, 2=Relaxed).
            very_readable (bool): If True, aim for very readable colors (AAA standard).
            show (bool): If True, show a preview in the console.
            save_report (bool): If True, save an HTML report.

        Returns:
            Tuple: (readable_color, success) where readable_color is in the same format as input.

        Example:
            >>> pair = ColorPair("#666666", "#ffffff")
            >>> pair.make_readable()
            ('#595959', True)
        """
        if not self.is_valid:
            return None, False

        # Use your existing optimized function
        from .optimisation import check_and_fix_contrast

        # Map 'very_readable' to 'premium' for the internal function
        premium = very_readable

        result = check_and_fix_contrast(
            self.text._rgb, self.bg._rgb, self.large, mode, premium
        )

        # Convert result back to original format
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
        if show or save_report:
            from .visualiser import to_console, to_html_bulk

            # Extract needed data
            tuned_rgb = None
            # Get original level for visualizer
            original_level = get_wcag_level(
                self.text.rgb, self.bg.rgb, self.large
            )
            new_level = None

            tuned_rgb, success = result
            # Always use tuned_rgb (even if success=False, it's the best attempt)
            # Calculate new level for the tuned color
            if tuned_rgb:
                # tuned_rgb is in original format, need to parse it back to check level
                try:
                    c_tuned = Color(str(tuned_rgb))
                    if c_tuned.is_valid:
                        new_level = get_wcag_level(
                            c_tuned.rgb, self.bg.rgb, self.large
                        )
                except:
                    pass

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
                if (
                    isinstance(fg_hex, str)
                    and isinstance(tuned_hex, str)
                    and fg_hex.lower() == tuned_hex.lower()
                ):
                    print('Colors are already accessible. No changes needed.')
                else:
                    to_console(
                        fg_hex, bg_hex, tuned_hex, original_level, new_level
                    )

            if save_report:
                # For single pair, generate a quick report
                pair_data = {
                    'fg': rgbint_to_string(self.text.rgb)
                    if self.text.is_valid
                    else 'Invalid',
                    'bg': rgbint_to_string(self.bg.rgb)
                    if self.bg.is_valid
                    else 'Invalid',
                    'tuned_fg': str(tuned_rgb),
                    'original_level': original_level,
                    'new_level': new_level,
                    'selector': 'Manual Check',
                    'file': 'Python API',
                }
                report_path = to_html_bulk(
                    [pair_data], output_path='cm_colors_quick_report.html'
                )
                print(f'Report generated: {report_path}')

        return result
