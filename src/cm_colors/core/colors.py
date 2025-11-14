# colors.py
from typing import Tuple, Optional, Union
from .color_parser import parse_color_to_rgb
from .contrast import calculate_contrast_ratio, get_wcag_level
from .conversions import rgbint_to_string,rgb_to_oklch_safe
from .color_metrics import calculate_delta_e_2000

class Color:
    def __init__(self, color_input: Union[str, tuple, list], background_context: Optional['Color'] = None):
        """
        Initialize a Color from a user-provided representation and optional background context.
        
        Parameters:
            color_input (str | tuple | list): Color representation to parse (e.g., hex string, rgb tuple, or other supported formats).
            background_context (Optional[Color]): Optional background Color used for RGBA compositing when parsing semitransparent inputs.
        
        Notes:
            Parses and stores parsed RGB on initialization; parsing errors are recorded on the instance.
        """
        self.original = color_input
        self.background_context = background_context
        self._rgb = None
        self._error = None
        self._parsed = False

        self._parse()
    
    def _parse(self) -> None:
        """
        Parse the original color input into an internal RGB representation using an optional background context.
        
        If parsing succeeds, stores the resulting RGB tuple and marks the color as parsed. If parsing fails with a ValueError, captures the error message and marks the color as parsed.
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
        Whether the Color represents a successfully parsed RGB color.
        
        Returns:
            `True` if the color was parsed to an RGB value, `False` otherwise.
        """
        return self._rgb is not None
    
    @property
    def rgb(self) -> Optional[Tuple[int, int, int]]:
        """
        Return the parsed RGB components for this color.
        
        Returns:
            Optional[Tuple[int, int, int]]: A tuple (R, G, B) with each channel in the 0–255 range if parsing succeeded, otherwise `None`.
        """
        return self._rgb
    
    @property
    def error(self) -> Optional[str]:
        """
        Error message from the most recent parse attempt, if one occurred.
        
        Returns:
            error (Optional[str]): The parse error message, or `None` if parsing succeeded or no error was recorded.
        """
        return self._error
    
    def to_hex(self) -> Optional[str]:
        """
        Format the parsed color as a lowercase `#rrggbb` hex string.
        
        Returns:
            hex_string (Optional[str]): `#rrggbb` representing the color, or `None` if the color is invalid.
        """
        if not self.is_valid:
            return None
        r, g, b = self.rgb
        return f"#{r:02x}{g:02x}{b:02x}"
    
    def to_rgb_string(self) -> Optional[str]:
        """
        Return the color formatted as an `rgb(r, g, b)` string.
        
        Returns:
            The RGB string (e.g., "rgb(255, 0, 0)"), or `None` if the color is invalid.
        """
        if not self.is_valid:
            return None
        return rgbint_to_string(self.rgb)
    
    def to_oklch(self):
        """
        Convert the color's parsed RGB value to the OKLCH color space.
        
        Returns:
            `None` if the color is invalid, otherwise a tuple `(L, C, h)` representing the OKLCH coordinates as floats.
        """
        if not self.is_valid:
            return None
        return rgb_to_oklch_safe(self._rgb)

class ColorPair:
    def __init__(self, text_color, bg_color):
        # Parse background first for RGBA context
        """
        Create a ColorPair by parsing the background and text colors, with the text parsed using the background as compositing context.
        
        Parameters:
            text_color (str | tuple | list): Color for the foreground/text. May be a color string or an RGB(A) tuple/list. If the color includes alpha, it will be composited against `bg_color`.
            bg_color (str | tuple | list): Color for the background. May be a color string or an RGB(A) tuple/list.
        """
        self.bg = Color(bg_color)
        # Pass background context for RGBA compositing
        self.text = Color(text_color, background_context=self.bg)
    
    @property
    def is_valid(self) -> bool:
        """
        Whether both text and background colors are valid.
        
        Returns:
            bool: True if both text and background colors are valid, False otherwise.
        """
        return self.text.is_valid and self.bg.is_valid
    
    @property
    def errors(self) -> list[str]:
        """
        Collect parsing error messages for the text and background colors in the pair.
        
        Returns:
            list[str]: A list of error messages; entries are prefixed with "Text: " or "Background: ". Returns an empty list if both colors are valid.
        """
        errors = []
        if not self.text.is_valid:
            errors.append(f"Text: {self.text.error}")
        if not self.bg.is_valid:
            errors.append(f"Background: {self.bg.error}")
        return errors
    
    @property
    def contrast_ratio(self) -> Optional[float]:
        """
        Compute the contrast ratio between the text and background colors.
        
        Returns:
            float: Contrast ratio between the two colors (typically between 1.0 and 21.0), or `None` if either color is invalid.
        """
        if not self.is_valid:
            return None
        return calculate_contrast_ratio(self.text.rgb, self.bg.rgb)
    
    @property
    def wcag_level(self) -> Optional[str]:
        """
        Determine the WCAG conformance level for the text/background color pair.
        
        Returns:
            WCAG level as a string (for example, "AA" or "AAA") if both colors are valid, `None` otherwise.
        """
        if not self.is_valid:
            return None
        return get_wcag_level(self.text.rgb, self.bg.rgb)
    
    @property
    def delta_e(self) -> Optional[int]:
        """
        Compute the Delta E 2000 color difference between the background and text colors.
        
        Returns:
            delta_e (int): The Delta E 2000 value comparing background and text color, or `None` if either color is invalid.
        """
        if not self.is_valid:
            return None
        return calculate_delta_e_2000(self.bg.rgb,self.text.rgb)

    def tune_colors(self, large_text: bool = False, details: bool = False):
        """
        Attempt to adjust the text color to meet contrast requirements against the background.
        
        Parameters:
        	large_text (bool): If True, use large-text contrast thresholds during tuning.
        	details (bool): If True, return detailed results or error information.
        
        Returns:
        	On invalid color pair:
        		If details is True, a dict with keys `status` (False) and `message` (str) describing the errors.
        		If details is False, a tuple `(None, False)`.
        	On valid color pair:
        		The result produced by the contrast-fixing routine — typically a tuple `(updated_text_rgb, success)` or a detailed result when `details` is True.
        """
        if not self.is_valid:
            if details:
                return {
                    "status": False,
                    "message": f"Invalid color pair: {', '.join(self.errors)}"
                }
            return None, False
        
        # Use your existing optimized function
        from .optimisation import check_and_fix_contrast
        return check_and_fix_contrast(
            self.text._rgb, 
            self.bg._rgb, 
            large_text, 
            details
        )