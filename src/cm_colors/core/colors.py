# colors.py
from typing import Tuple, Optional, Union
from .color_parser import parse_color_to_rgb
from .contrast import calculate_contrast_ratio, get_wcag_level
from .conversions import rgbint_to_string,rgb_to_oklch_safe
from .color_metrics import calculate_delta_e_2000

class Color:
    def __init__(self, color_input: Union[str, tuple, list], background_context: Optional['Color'] = None):
        self.original = color_input
        self.background_context = background_context
        self._rgb = None
        self._error = None
        self._parsed = False

        self._parse()
    
    def _parse(self) -> None:
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
        return self._rgb is not None
    
    @property
    def rgb(self) -> Optional[Tuple[int, int, int]]:
        return self._rgb
    
    @property
    def error(self) -> Optional[str]:
        return self._error
    
    def to_hex(self) -> Optional[str]:
        if not self.is_valid:
            return None
        r, g, b = self.rgb
        return f"#{r:02x}{g:02x}{b:02x}"
    
    def to_rgb_string(self) -> Optional[str]:
        if not self.is_valid:
            return None
        return rgbint_to_string(self.rgb)
    
    def to_oklch(self):
        if not self.is_valid:
            return None
        return rgb_to_oklch_safe(self._rgb)

class ColorPair:
    def __init__(self, text_color, bg_color,large_text=False):
        # Parse background first for RGBA context
        self.bg = Color(bg_color)
        # Pass background context for RGBA compositing
        self.text = Color(text_color, background_context=self.bg)
        self.large_text = large_text
    
    @property
    def is_valid(self) -> bool:
        return self.text.is_valid and self.bg.is_valid
    
    @property
    def errors(self) -> list[str]:
        errors = []
        if not self.text.is_valid:
            errors.append(f"Text: {self.text.error}")
        if not self.bg.is_valid:
            errors.append(f"Background: {self.bg.error}")
        return errors
    
    @property
    def contrast_ratio(self) -> Optional[float]:
        if not self.is_valid:
            return None
        return calculate_contrast_ratio(self.text.rgb, self.bg.rgb)
    
    @property
    def wcag_level(self) -> Optional[str]:
        if not self.is_valid:
            return None
        return get_wcag_level(self.text.rgb, self.bg.rgb,self.large_text)
    
    @property
    def delta_e(self) -> Optional[float]:
        if not self.is_valid:
            return None
        return calculate_delta_e_2000(self.bg.rgb,self.text.rgb)

    def tune_colors(self, details: bool = False):
        """
        Tune colors to fix contrast using the algorithm 
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
            self.large_text, 
            details
        )