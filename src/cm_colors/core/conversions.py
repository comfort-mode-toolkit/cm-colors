import math
from typing import Tuple


def hex_to_rgb(hex_str: str, string: bool = False) -> Tuple[int, int, int] | str:
    """
    Converts a hex color string to an RGB tuple or CSS rgb() string.

    Args:
        hex_str (str): Hex color string, with or without leading '#'.
        string (bool): If True, returns CSS 'rgb(r, g, b)' string. If False, returns (r, g, b) tuple.

    Returns:
        Tuple[int, int, int] or str: RGB tuple or CSS string.

    Raises:
        ValueError: If hex_str is not a valid hex color.
    """
    hex_str = hex_str.strip().lstrip("#")
    if len(hex_str) == 3:
        hex_str = "".join([c * 2 for c in hex_str])
    if len(hex_str) != 6 or not all(c in "0123456789abcdefABCDEF" for c in hex_str):
        raise ValueError(f"Invalid hex color: {hex_str}")
    r = int(hex_str[0:2], 16)
    g = int(hex_str[2:4], 16)
    b = int(hex_str[4:6], 16)
    if string:
        return f"rgb({r}, {g}, {b})"
    return (r, g, b)


def rgb_to_hex(rgb: Tuple[int, int, int] | str) -> str:
    """
    Converts an RGB tuple or CSS rgb() string to a hex color string (with leading '#').

    Args:
        rgb (Tuple[int, int, int] or str): RGB tuple (r, g, b) or CSS 'rgb(r, g, b)' string.

    Returns:
        str: Hex color string, e.g. '#aabbcc'.

    Raises:
        ValueError: If input is not a valid RGB tuple or string.
    """
    if isinstance(rgb, str):
        import re

        match = re.fullmatch(
            r"rgb\(\s*(\d{1,3})\s*,\s*(\d{1,3})\s*,\s*(\d{1,3})\s*\)", rgb.strip()
        )
        if not match:
            raise ValueError(f"Invalid CSS rgb() string: {rgb}")
        r, g, b = map(int, match.groups())
    elif isinstance(rgb, tuple) and len(rgb) == 3:
        r, g, b = rgb
    else:
        raise ValueError(f"Invalid RGB input: {rgb}")
    if not all(isinstance(x, int) and 0 <= x <= 255 for x in (r, g, b)):
        raise ValueError(f"RGB values must be integers in 0-255: {rgb}")
    return "#{:02x}{:02x}{:02x}".format(r, g, b)


def rgb_to_oklch(rgb: Tuple[int, int, int]) -> Tuple[float, float, float]:
    """
    Convert RGB to OKLCH color space with full mathematical rigor
    Uses the official OKLab transformation matrices
    """
    r, g, b = [x / 255.0 for x in rgb]

    # Step 1: Convert sRGB to linear RGB with precise gamma correction
    def srgb_to_linear(channel):
        if channel <= 0.04045:
            return channel / 12.92
        else:
            return pow((channel + 0.055) / 1.055, 2.4)

    r_linear = srgb_to_linear(r)
    g_linear = srgb_to_linear(g)
    b_linear = srgb_to_linear(b)

    # Step 2: Linear RGB to LMS (Long, Medium, Short cone responses)
    # Using the official OKLab transformation matrix
    l_cone = 0.4122214708 * r_linear + 0.5363325363 * g_linear + 0.0514459929 * b_linear
    m_cone = 0.2119034982 * r_linear + 0.6806995451 * g_linear + 0.1073969566 * b_linear
    s_cone = 0.0883024619 * r_linear + 0.2817188376 * g_linear + 0.6299787005 * b_linear

    # Step 3: Apply cube root transformation (perceptual uniformity)
    # Handle negative values properly
    def safe_cbrt(x):
        if x >= 0:
            return pow(x, 1 / 3)
        else:
            return -pow(-x, 1 / 3)

    l_prime = safe_cbrt(l_cone)
    m_prime = safe_cbrt(m_cone)
    s_prime = safe_cbrt(s_cone)

    # Step 4: LMS' to OKLab using the official transformation matrix
    L = 0.2104542553 * l_prime + 0.7936177850 * m_prime - 0.0040720468 * s_prime
    a = 1.9779984951 * l_prime - 2.4285922050 * m_prime + 0.4505937099 * s_prime
    b = 0.0259040371 * l_prime + 0.7827717662 * m_prime - 0.8086757660 * s_prime

    # Step 5: OKLab to OKLCH conversion
    # Chroma calculation
    C = math.sqrt(a * a + b * b)

    # Hue calculation with proper quadrant handling
    if C < 1e-10:  # Very small chroma, hue is undefined
        H = 0.0
    else:
        H = math.atan2(b, a) * 180.0 / math.pi
        if H < 0:
            H += 360.0

    # Clamp lightness to valid range
    L = max(0.0, min(1.0, L))

    return (L, C, H)


def oklch_to_rgb(oklch: Tuple[float, float, float]) -> Tuple[int, int, int]:
    """
    Convert OKLCH to RGB color space with full mathematical rigor
    Uses the official OKLab inverse transformation matrices
    """
    L, C, H = oklch

    # Step 1: OKLCH to OKLab
    H_rad = H * math.pi / 180.0
    a = C * math.cos(H_rad)
    b = C * math.sin(H_rad)

    # Step 2: OKLab to LMS' using inverse transformation matrix
    l_prime = L + 0.3963377774 * a + 0.2158037573 * b
    m_prime = L - 0.1055613458 * a - 0.0638541728 * b
    s_prime = L - 0.0894841775 * a - 1.2914855480 * b

    # Step 3: Apply cube transformation (inverse of cube root)
    # Handle negative values properly
    def safe_cube(x):
        if x >= 0:
            return x * x * x
        else:
            return -((-x) * (-x) * (-x))

    l_cone = safe_cube(l_prime)
    m_cone = safe_cube(m_prime)
    s_cone = safe_cube(s_prime)

    # Step 4: LMS to Linear RGB using inverse transformation matrix
    r_linear = +4.0767416621 * l_cone - 3.3077115913 * m_cone + 0.2309699292 * s_cone
    g_linear = -1.2684380046 * l_cone + 2.6097574011 * m_cone - 0.3413193965 * s_cone
    b_linear = -0.0041960863 * l_cone - 0.7034186147 * m_cone + 1.7076147010 * s_cone

    # Step 5: Linear RGB to sRGB with precise gamma correction
    def linear_to_srgb(channel):
        if channel <= 0.0031308:
            return 12.92 * channel
        else:
            return 1.055 * pow(channel, 1.0 / 2.4) - 0.055

    # Clamp to valid range before gamma correction
    r_linear = max(0.0, min(1.0, r_linear))
    g_linear = max(0.0, min(1.0, g_linear))
    b_linear = max(0.0, min(1.0, b_linear))

    r_srgb = linear_to_srgb(r_linear)
    g_srgb = linear_to_srgb(g_linear)
    b_srgb = linear_to_srgb(b_linear)

    # Step 6: Convert to 8-bit RGB with proper rounding
    r_8bit = max(0, min(255, round(r_srgb * 255)))
    g_8bit = max(0, min(255, round(g_srgb * 255)))
    b_8bit = max(0, min(255, round(b_srgb * 255)))

    return (r_8bit, g_8bit, b_8bit)


def rgb_to_xyz(rgb: Tuple[int, int, int]) -> Tuple[float, float, float]:
    """Convert RGB to XYZ color space with proper gamma correction"""
    r, g, b = [x / 255.0 for x in rgb]

    # Apply gamma correction (sRGB to linear RGB)
    def gamma_correct(channel):
        if channel <= 0.04045:
            return channel / 12.92
        else:
            return pow((channel + 0.055) / 1.055, 2.4)

    r_linear = gamma_correct(r)
    g_linear = gamma_correct(g)
    b_linear = gamma_correct(b)

    # Convert to XYZ using sRGB matrix (D65 illuminant)
    x = r_linear * 0.4124564 + g_linear * 0.3575761 + b_linear * 0.1804375
    y = r_linear * 0.2126729 + g_linear * 0.7151522 + b_linear * 0.0721750
    z = r_linear * 0.0193339 + g_linear * 0.1191920 + b_linear * 0.9503041

    # Scale to D65 illuminant (X=95.047, Y=100.000, Z=108.883)
    return (x * 100, y * 100, z * 100)


def xyz_to_lab(xyz: Tuple[float, float, float]) -> Tuple[float, float, float]:
    """Convert XYZ to LAB color space"""
    x, y, z = xyz

    # D65 illuminant reference values
    xn, yn, zn = 95.047, 100.000, 108.883

    # Normalize
    x = x / xn
    y = y / yn
    z = z / zn

    # Apply LAB transformation function
    def lab_transform(t):
        if t > 0.008856:
            return pow(t, 1 / 3)
        else:
            return (7.787 * t) + (16 / 116)

    fx = lab_transform(x)
    fy = lab_transform(y)
    fz = lab_transform(z)

    # Calculate LAB values
    L = max(0, min(100, 116 * fy - 16))  # Clamp L to 0-100 range
    a = 500 * (fx - fy)
    b = 200 * (fy - fz)

    return (L, a, b)


def rgb_to_lab(rgb: Tuple[int, int, int]) -> Tuple[float, float, float]:
    """Convert RGB directly to LAB"""
    xyz = rgb_to_xyz(rgb)
    return xyz_to_lab(xyz)


def rgb_to_oklch_safe(rgb: Tuple[int, int, int]) -> Tuple[float, float, float]:
    """
    Safe RGB to OKLCH conversion with validation and error handling
    """
    try:
        # Validate RGB input
        if not is_valid_rgb(rgb):
            raise ValueError(f"Invalid RGB values: {rgb}")

        oklch = rgb_to_oklch(rgb)

        # Validate OKLCH output
        if not is_valid_oklch(oklch):
            raise ValueError(f"Invalid OKLCH conversion result: {oklch}")

        return oklch

    except Exception as e:
        # Fallback to grayscale conversion if color conversion fails
        r, g, b = rgb
        gray = 0.299 * r + 0.587 * g + 0.114 * b
        gray_normalized = gray / 255.0
        return (gray_normalized, 0.0, 0.0)  # Achromatic color


def oklch_to_rgb_safe(oklch: Tuple[float, float, float]) -> Tuple[int, int, int]:
    """
    Safe OKLCH to RGB conversion with validation and error handling
    """
    try:
        # Validate OKLCH input
        if not is_valid_oklch(oklch):
            raise ValueError(f"Invalid OKLCH values: {oklch}")

        rgb = oklch_to_rgb(oklch)

        # Validate RGB output
        if not is_valid_rgb(rgb):
            raise ValueError(f"Invalid RGB conversion result: {rgb}")

        return rgb

    except Exception as e:
        # Fallback to grayscale if conversion fails
        L, C, H = oklch
        gray_value = max(0, min(255, round(L * 255)))
        return (gray_value, gray_value, gray_value)


def is_valid_rgb(rgb: Tuple[int, int, int]) -> bool:
    """Check if RGB values are valid (0-255)"""
    return all(0 <= value <= 255 for value in rgb)


def is_valid_oklch(oklch: Tuple[float, float, float]) -> bool:
    """
    Check whether an OKLCH color tuple lies within expected component ranges.
    
    Parameters:
        oklch (Tuple[float, float, float]): (L, C, H) where L is lightness, C is chroma, H is hue in degrees.
    
    Returns:
        bool: `True` if L is between 0 and 1 (inclusive), C is greater than or equal to 0, and H is between 0 and 360 (inclusive); `False` otherwise.
    """
    L, C, H = oklch

    # Lightness should be between 0 and 1
    if not (0 <= L <= 1):
        return False

    # Chroma should be non-negative (typically 0 to ~0.4)
    if C < 0:
        return False

    # Hue should be between 0 and 360 degrees
    if not (0 <= H <= 360):
        return False

    return True

# def parse_color_pair(text_color, bg_color):
#     """
#     Parses text and background color inputs, handling RGBA transparency if present.

#     Args:
#         text_color: Color for text (tuple, list, or CSS-style string)
#         bg_color: Color for background (tuple, list, or CSS-style string)

#     Returns:
#         Tuple[Tuple[int, int, int], Tuple[int, int, int]]: (text_rgb, bg_rgb)
#     """
#     # Parse background color to RGB first (for compositing if needed)
#     bg_rgb = parse_color_to_rgb(bg_color)

#     # Check if text_color is RGBA (tuple/list of length 4 or CSS rgba string)
#     is_rgba = False
#     if isinstance(text_color, (tuple, list)) and len(text_color) == 4:
#         is_rgba = True
#     elif isinstance(text_color, str):
#         color_str = text_color.strip().lower()
#         if color_str.startswith("rgba(") and color_str.endswith(")"):
#             is_rgba = True

#     if is_rgba:
#         # Use rgba_to_rgb with background
#         if isinstance(text_color, str):
#             # Parse string to tuple first
#             color_str = text_color.strip().lower()
#             rgba_content = color_str[5:-1]
#             rgba_values = [v.strip() for v in rgba_content.split(",")]
#             if len(rgba_values) != 4:
#                 raise ValueError(
#                     f"RGBA string must have exactly 4 values separated by commas. Got {len(rgba_values)} values in '{text_color}'."
#                 )
#             try:
#                 r = int(rgba_values[0])
#                 g = int(rgba_values[1])
#                 b = int(rgba_values[2])
#                 a = float(rgba_values[3])
#             except Exception:
#                 raise ValueError(f"Invalid RGBA values in '{text_color}'")
#             text_rgb = rgba_to_rgb((r, g, b, a), background=bg_rgb)
#         else:
#             text_rgb = rgba_to_rgb(tuple(text_color), background=bg_rgb)
#     else:
#         text_rgb = parse_color_to_rgb(text_color)

#     return text_rgb, bg_rgb

# def parse_color_to_rgb(color):
#     """Parse a color input (string or tuple) to an RGB tuple.

#     Args:
#         color (str or tuple): Color input, can be a hex string, RGB string, or RGB tuple.

#     Returns:
#         Tuple[int, int, int]: RGB tuple (r, g, b).

#     Raises:
#         ValueError: If the input color format is invalid.
#     """
#         # RGBA tuple/list
#     if isinstance(color, (tuple, list)) and len(color) == 4:
#         return rgba_to_rgb(color)
#     if isinstance(color, tuple) and len(color) == 3:
#         if all(isinstance(x, int) for x in color):
#             # Validate RGB tuple values are in range 0-255
#             for i, value in enumerate(color):
#                 if value < 0:
#                     raise ValueError(
#                         f"RGB values cannot be negative. Got {value} for {'RGB'[i]} component."
#                     )
#                 if value > 255:
#                     raise ValueError(
#                         f"RGB values must be between 0-255. Got {value} for {'RGB'[i]} component."
#                     )
#             return color
#         else:
#             raise ValueError(f"RGB tuple must contain only integers. Got: {color}")
#     elif isinstance(color, list) and len(color) == 3:
#         if all(isinstance(x, int) for x in color):
#             # Validate RGB list values are in range 0-255
#             for i, value in enumerate(color):
#                 if value < 0:
#                     raise ValueError(
#                         f"RGB values cannot be negative. Got {value} for {'RGB'[i]} component."
#                     )
#                 if value > 255:
#                     raise ValueError(
#                         f"RGB values must be between 0-255. Got {value} for {'RGB'[i]} component."
#                     )
#             return tuple(color)
#         else:
#             raise ValueError(f"RGB list must contain only integers. Got: {color}")
#     elif isinstance(color, str):
#         color = color.strip().lower()
#         if color.startswith("#"):
#             try:
#                 return hex_to_rgb(color)
#             except ValueError as e:
#                 # Check for invalid hex characters
#                 hex_part = color[1:] if len(color) > 1 else ""
#                 if len(hex_part) not in [3, 6]:
#                     raise ValueError(
#                         f"Hex color must be 3 or 6 characters after '#'. Got '{color}' with {len(hex_part)} characters."
#                     )
#                 invalid_chars = [c for c in hex_part if c not in "0123456789abcdef"]
#                 if invalid_chars:
#                     raise ValueError(
#                         f"Hex color contains invalid characters: {', '.join(set(invalid_chars))}. Valid characters are 0-9 and A-F."
#                     )
#                 raise ValueError(f"Invalid hex color format: '{color}'")
#         elif color.startswith("rgb(") and color.endswith(")"):
#             # Extract RGB values from rgb() string
#             rgb_content = color[4:-1]
#             rgb_values = rgb_content.split(",")

#             if len(rgb_values) != 3:
#                 raise ValueError(
#                     f"RGB string must have exactly 3 values separated by commas. Got {len(rgb_values)} values in '{color}'."
#                 )

#             try:
#                 parsed_values = []
#                 for i, value_str in enumerate(rgb_values):
#                     value_str = value_str.strip()
#                     try:
#                         value = int(value_str)
#                         if value < 0:
#                             raise ValueError(
#                                 f"RGB values cannot be negative. Got {value} for {'RGB'[i]} component in '{color}'."
#                             )
#                         if value > 255:
#                             raise ValueError(
#                                 f"RGB values must be between 0-255. Got {value} for {'RGB'[i]} component in '{color}'."
#                             )
#                         parsed_values.append(value)
#                     except ValueError as ve:
#                         if "cannot be negative" in str(
#                             ve
#                         ) or "must be between 0-255" in str(ve):
#                             raise ve
#                         raise ValueError(
#                             f"Invalid numeric value '{value_str}' for {'RGB'[i]} component in '{color}'. Must be an integer between 0-255."
#                         )

#                 return tuple(parsed_values)
#             except ValueError as ve:
#                 if "RGB values" in str(ve):
#                     raise ve
#                 raise ValueError(
#                     f"Invalid RGB string format: '{color}'. Expected format: 'rgb(r, g, b)' where r, g, b are integers 0-255."
#                 )
#         else:
#             # Check if it looks like it might be a color name or other format
#             if color.replace(" ", "").replace("-", "").replace("_", "").isalpha():
#                 raise ValueError(
#                     f"Color name '{color}' is not supported. Please use hex format (e.g., '#ff0000') or RGB format (e.g., 'rgb(255, 0, 0)')."
#                 )
#             else:
#                 raise ValueError(
#                     f"Unrecognized color format: '{color}'. Supported formats are hex (e.g., '#ff0000') or RGB (e.g., 'rgb(255, 0, 0)')."
#                 )
#     elif isinstance(color, tuple):
#         if len(color) != 3:
#             raise ValueError(
#                 f"RGB tuple must have exactly 3 values. Got {len(color)} values: {color}"
#             )
#         return parse_color_to_rgb(color)  # Recursive call to handle validation
#     else:
#         raise ValueError(
#             f"Unsupported color input type: {type(color).__name__}. Expected string, tuple, or list."
#         )

def rgba_to_rgb(rgba, background=(255, 255, 255)):
    """
    Convert an RGBA color to an RGB color by alpha blending over a background.

    Args:
        rgba (tuple): (r, g, b, a) where r, g, b are 0–255, and a is 0–1 (float).
        background (tuple): (r_bg, g_bg, b_bg) 0–255, default is white.

    Returns:
        tuple: (r, g, b) after blending.

    Raises:
        ValueError: If inputs are out of expected range.
    """
    if not (isinstance(rgba, (list, tuple)) and len(rgba) == 4):
        raise ValueError("RGBA must be a tuple or list of 4 values.")
    r, g, b, a = rgba
    if not all(isinstance(v, int) and 0 <= v <= 255 for v in (r, g, b)):
        raise ValueError("RGBA r, g, b must be integers in 0–255.")
    if not isinstance(a, (float, int)) or not (0.0 <= a <= 1.0):
        raise ValueError("RGBA a must be a float in 0–1.")
    if not (isinstance(background, (list, tuple)) and len(background) == 3):
        raise ValueError("background must be a tuple or list of 3 values.")
    if not all(isinstance(v, int) and 0 <= v <= 255 for v in background):
        raise ValueError("background r, g, b must be integers in 0–255.")

    r_bg, g_bg, b_bg = background
    r_out = int(round(r * a + r_bg * (1 - a)))
    g_out = int(round(g * a + g_bg * (1 - a)))
    b_out = int(round(b * a + b_bg * (1 - a)))
    return (r_out, g_out, b_out)

def rgbint_to_string(rgb: Tuple[int, int, int]) -> str:
    """Convert an RGB tuple to a CSS rgb() string.

    Args:
        rgb (Tuple[int, int, int]): RGB tuple (r, g, b).

    Returns:
        str: CSS rgb() string, e.g. 'rgb(255, 0, 0)'.
    """
    if not is_valid_rgb(rgb):
        raise ValueError(f"Invalid RGB values: {rgb}")
    return f"rgb({rgb[0]}, {rgb[1]}, {rgb[2]})"

def hsl_to_rgb(hsl_color):
    """
    Convert an HSL color to an RGB tuple.
    
    Args:
        hsl_color: HSL color as either:
            - A tuple/list (h, s, l) where h is in [0, 360), s and l are in [0, 1].
            - A CSS-style string like "hsl(120, 100%, 50%)" or "hsl(120 100% 50%)".
    
    Returns:
        A tuple (r, g, b) where each component is an int in the range 0–255.
    
    Raises:
        ValueError: If the HSL values or string format are invalid or out of range.
        TypeError: If the input type is unsupported.
    """
    if isinstance(hsl_color, str):
        # Parse CSS string
        if hsl_color.startswith("hsl(") and hsl_color.endswith(")"):
            content = hsl_color[4:-1].strip()
            parts = content.replace('%', '').split()
            if len(parts) == 3:
                h = float(parts[0])
                s = float(parts[1]) / 100.0
                l = float(parts[2]) / 100.0
            else:
                raise ValueError("Invalid HSL CSS string format")
        else:
            raise ValueError("Invalid HSL string format")
    elif isinstance(hsl_color, (tuple, list)):
        if len(hsl_color) == 3:
            h, s, l = hsl_color
        else:
            raise ValueError("Invalid HSL tuple/list format")
    else:
        raise TypeError("Unsupported HSL color format")

    if not (0 <= h < 360 and 0 <= s <= 1 and 0 <= l <= 1):
        raise ValueError("HSL values out of range")

    # Algorithm for HSL to RGB conversion
    if s == 0:
        r = g = b = l  # achromatic
    else:
        def hue_to_rgb_component(p, q, t):
            """
            Compute one RGB channel value from HSL interpolation for a given hue fraction.
            
            Parameters:
                p (float): Lower helper value from HSL conversion (typically in 0–1).
                q (float): Upper helper value from HSL conversion (typically in 0–1).
                t (float): Hue fractional offset; values outside 0–1 will be wrapped into that range.
            
            Returns:
                float: The RGB component value in the range 0–1.
            """
            if t < 0: t += 1
            if t > 1: t -= 1
            if t < 1/6: return p + (q - p) * 6 * t
            if t < 1/2: return q
            if t < 2/3: return p + (q - p) * (2/3 - t) * 6
            return p

        q = l * (1 + s) if l < 0.5 else l + s - l * s
        p = 2 * l - q
        
        h /= 360.0 # Normalize hue to [0, 1)

        r = hue_to_rgb_component(p, q, h + 1/3)
        g = hue_to_rgb_component(p, q, h)
        b = hue_to_rgb_component(p, q, h - 1/3)

    return (int(r * 255), int(g * 255), int(b * 255))

def hsl_to_rgb(hsl_color):
    """
    Convert an HSL color to an RGB tuple.
    
    Parameters:
        hsl_color: HSL color as either:
            - a (h, s, l) tuple/list where h is in [0, 360), s and l are in [0, 1], or
            - a CSS-style string "hsl(h, s%, l%)" or "hsl(h s% l%)" (commas or spaces).
    
    Returns:
        tuple: (r, g, b) where each component is an integer in the range 0–255.
    
    Raises:
        ValueError: If the HSL values or string format are invalid or out of range.
        TypeError: If hsl_color is not a supported type.
    """
    if isinstance(hsl_color, str):
        # Parse CSS string
        if hsl_color.startswith("hsl(") and hsl_color.endswith(")"):
            content = hsl_color[4:-1].strip()
            # Handle both comma and space separation
            if ',' in content:
                parts = [p.strip().replace('%', '') for p in content.split(',')]
            else:
                parts = content.replace('%', '').split()
            
            if len(parts) == 3:
                try:
                    h = float(parts[0])
                    s = float(parts[1]) / 100.0
                    l = float(parts[2]) / 100.0
                except ValueError:
                    raise ValueError("Invalid HSL CSS string format")
            else:
                raise ValueError("Invalid HSL CSS string format")
        else:
            raise ValueError("Invalid HSL string format")
    elif isinstance(hsl_color, (tuple, list)):
        if len(hsl_color) == 3:
            h, s, l = hsl_color
        else:
            raise ValueError("Invalid HSL tuple/list format")
    else:
        raise TypeError("Unsupported HSL color format")

    if not (0 <= h < 360 and 0 <= s <= 1 and 0 <= l <= 1):
        raise ValueError("HSL values out of range")

    # Algorithm for HSL to RGB conversion
    if s == 0:
        r = g = b = l  # achromatic
    else:
        def hue_to_rgb_component(p, q, t):
            """
            Compute one RGB channel value from HSL interpolation for a given hue fraction.
            
            Parameters:
                p (float): Lower helper value from HSL conversion (typically in 0–1).
                q (float): Upper helper value from HSL conversion (typically in 0–1).
                t (float): Hue fractional offset; values outside 0–1 will be wrapped into that range.
            
            Returns:
                float: The RGB component value in the range 0–1.
            """
            if t < 0: t += 1
            if t > 1: t -= 1
            if t < 1/6: return p + (q - p) * 6 * t
            if t < 1/2: return q
            if t < 2/3: return p + (q - p) * (2/3 - t) * 6
            return p

        q = l * (1 + s) if l < 0.5 else l + s - l * s
        p = 2 * l - q
        
        h /= 360.0 # Normalize hue to [0, 1)

        r = hue_to_rgb_component(p, q, h + 1/3)
        g = hue_to_rgb_component(p, q, h)
        b = hue_to_rgb_component(p, q, h - 1/3)

    return (int(r * 255), int(g * 255), int(b * 255))

def hsla_to_rgb(hsla_color, background=None):
    """
    Convert an HSLA color to an RGB tuple, optionally compositing the result over a background.
    
    Parameters:
        hsla_color (str | tuple | list): HSLA color in one of the following forms:
            - Tuple/list (h, s, l, a) where h is in degrees (wraps mod 360), s and l are in [0, 1], and a is in [0, 1].
            - CSS string "hsla(h, s%, l%, a)" or space/slash form "hsla(h s% l% / a)".
        background (tuple | list, optional): RGB background (r, g, b) with each component in 0–255 used for alpha compositing.
            If omitted, white (255, 255, 255) is used.
    
    Returns:
        tuple: (r, g, b) with each component as an integer in 0–255 representing the composited RGB color.
    
    Raises:
        TypeError: If hsla_color is not a string, tuple, or list.
        ValueError: If hsla_color or background have an invalid format or values out of the expected ranges.
    """
    if isinstance(hsla_color, str):
        # Parse CSS string
        hsla_color = hsla_color.strip().lower()
        if hsla_color.startswith("hsla(") and hsla_color.endswith(")"):
            content = hsla_color[5:-1].strip()
            # Handle both comma and space separation, and slash for alpha
            content = content.replace('/', ',')  # Convert slash format to comma
            parts = [p.strip().replace('%', '') for p in content.split(',')]
            
            if len(parts) == 4:
                h = float(parts[0]) % 360  # Wrap hue
                s = float(parts[1]) / 100.0 if parts[1] else 0.0
                l = float(parts[2]) / 100.0 if parts[2] else 0.0
                a = float(parts[3]) if float(parts[3]) <= 1.0 else float(parts[3]) / 100.0
            else:
                raise ValueError("Invalid HSLA CSS string format")
        else:
            raise ValueError("Invalid HSLA string format - must start with 'hsla('")
            
    elif isinstance(hsla_color, (tuple, list)):
        if len(hsla_color) == 4:
            h, s, l, a = hsla_color
            h = float(h) % 360
            s = float(s)
            l = float(l)
            a = float(a)
        else:
            raise ValueError("Invalid HSLA tuple/list - must have 4 components")
    else:
        raise TypeError("HSLA color must be string, tuple, or list")
    
    # Validate ranges
    if not (0 <= s <= 1 and 0 <= l <= 1 and 0 <= a <= 1):
        raise ValueError("HSLA values out of range: s, l, a must be in [0, 1]")
    
    # Convert HSL to RGB first
    rgb = hsl_to_rgb((h, s, l))
    
    # If alpha is 1, no compositing needed
    if a >= 1.0:
        return rgb
    
    # Composite with background
    if background is None:
        bg_rgb = (255, 255, 255)  # Default white background
    else:
        # Parse background if it's not already RGB tuple
        if isinstance(background, (tuple, list)) and len(background) == 3:
            bg_rgb = background
        else:
            raise ValueError('Invalid format, please input RGB Tuple (int,int,int)')
    
    # Alpha composite: result = alpha * foreground + (1 - alpha) * background
    r, g, b = rgb
    bg_r, bg_g, bg_b = bg_rgb
    
    final_r = int(a * r + (1 - a) * bg_r)
    final_g = int(a * g + (1 - a) * bg_g)
    final_b = int(a * b + (1 - a) * bg_b)
    
    return (final_r, final_g, final_b)


def rgb_to_hsla(rgb_tuple, alpha=1.0):
    """
    Convert an RGB tuple to an HSLA CSS string.
    
    Parameters:
        rgb_tuple (tuple | list): (r, g, b) with each value 0–255.
        alpha (float): Opacity value in [0, 1]. Defaults to 1.0.
    
    Returns:
        str: HSLA CSS string in the form "hsla(h, s%, l%, a)" where `h` is degrees, `s` and `l` are percentages, and `a` is the given alpha.
    """
    if not isinstance(rgb_tuple, (tuple, list)) or len(rgb_tuple) != 3:
        raise ValueError("RGB must be a tuple/list of 3 values")
    
    r, g, b = rgb_tuple
    if not all(0 <= val <= 255 for val in (r, g, b)):
        raise ValueError("RGB values must be in range [0, 255]")
    
    if not (0 <= alpha <= 1):
        raise ValueError("Alpha must be in range [0, 1]")
    
    hsl_string = rgb_to_hsl(rgb_tuple)
    
    # Extract h, s, l from the HSL string and add alpha
    # hsl_string format: "hsl(120, 100%, 50%)"
    content = hsl_string[4:-1]  # Remove "hsl(" and ")"
    h_part, s_part, l_part = content.split(", ")
    
    return f"hsla({h_part}, {s_part}, {l_part}, {alpha})"