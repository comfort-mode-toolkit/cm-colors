import math
from typing import Tuple


def hex_to_rgb(
    hex_str: str, string: bool = False
) -> Tuple[int, int, int] | str:
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
    hex_str = hex_str.strip().lstrip('#')
    if len(hex_str) == 3:
        hex_str = ''.join([c * 2 for c in hex_str])
    if len(hex_str) != 6 or not all(
        c in '0123456789abcdefABCDEF' for c in hex_str
    ):
        raise ValueError(f'Invalid hex color: {hex_str}')
    r = int(hex_str[0:2], 16)
    g = int(hex_str[2:4], 16)
    b = int(hex_str[4:6], 16)
    if string:
        return f'rgb({r}, {g}, {b})'
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
            r'rgb\(\s*(\d{1,3})\s*,\s*(\d{1,3})\s*,\s*(\d{1,3})\s*\)',
            rgb.strip(),
        )
        if not match:
            raise ValueError(f'Invalid CSS rgb() string: {rgb}')
        r, g, b = map(int, match.groups())
    elif isinstance(rgb, tuple) and len(rgb) == 3:
        r, g, b = rgb
    else:
        raise ValueError(f'Invalid RGB input: {rgb}')
    if not all(isinstance(x, int) and 0 <= x <= 255 for x in (r, g, b)):
        raise ValueError(f'RGB values must be integers in 0-255: {rgb}')
    return '#{:02x}{:02x}{:02x}'.format(r, g, b)


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
    l_cone = (
        0.4122214708 * r_linear
        + 0.5363325363 * g_linear
        + 0.0514459929 * b_linear
    )
    m_cone = (
        0.2119034982 * r_linear
        + 0.6806995451 * g_linear
        + 0.1073969566 * b_linear
    )
    s_cone = (
        0.0883024619 * r_linear
        + 0.2817188376 * g_linear
        + 0.6299787005 * b_linear
    )

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
    L = (
        0.2104542553 * l_prime
        + 0.7936177850 * m_prime
        - 0.0040720468 * s_prime
    )
    a = (
        1.9779984951 * l_prime
        - 2.4285922050 * m_prime
        + 0.4505937099 * s_prime
    )
    b = (
        0.0259040371 * l_prime
        + 0.7827717662 * m_prime
        - 0.8086757660 * s_prime
    )

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
    r_linear = (
        +4.0767416621 * l_cone - 3.3077115913 * m_cone + 0.2309699292 * s_cone
    )
    g_linear = (
        -1.2684380046 * l_cone + 2.6097574011 * m_cone - 0.3413193965 * s_cone
    )
    b_linear = (
        -0.0041960863 * l_cone - 0.7034186147 * m_cone + 1.7076147010 * s_cone
    )

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
            raise ValueError(f'Invalid RGB values: {rgb}')

        oklch = rgb_to_oklch(rgb)

        # Validate OKLCH output
        if not is_valid_oklch(oklch):
            raise ValueError(f'Invalid OKLCH conversion result: {oklch}')

        return oklch

    except Exception as e:
        # Fallback to grayscale conversion if color conversion fails
        r, g, b = rgb
        gray = 0.299 * r + 0.587 * g + 0.114 * b
        gray_normalized = gray / 255.0
        return (gray_normalized, 0.0, 0.0)  # Achromatic color


def oklch_to_rgb_safe(
    oklch: Tuple[float, float, float]
) -> Tuple[int, int, int]:
    """
    Safe OKLCH to RGB conversion with validation and error handling
    """
    try:
        # Validate OKLCH input
        if not is_valid_oklch(oklch):
            raise ValueError(f'Invalid OKLCH values: {oklch}')

        rgb = oklch_to_rgb(oklch)

        # Validate RGB output
        if not is_valid_rgb(rgb):
            raise ValueError(f'Invalid RGB conversion result: {rgb}')

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
    Return whether an OKLCH color tuple has components within expected ranges.

    Parameters:
        oklch (Tuple[float, float, float]): (L, C, H) where L is lightness in [0,1], C is chroma (>= 0), and H is hue in degrees [0,360].

    Returns:
        bool: `True` if L is between 0 and 1 inclusive, C is greater than or equal to 0, and H is between 0 and 360 inclusive; `False` otherwise.
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


def rgba_to_rgb(rgba, background=(255, 255, 255)):
    """
    Alpha-blend an RGBA color over a background to produce an RGB tuple.

    Parameters:
        rgba (tuple|list): Four values (r, g, b, a) where r, g, b are integers 0–255 and a is a float 0–1.
        background (tuple|list, optional): Three integers (r_bg, g_bg, b_bg) 0–255 to composite against. Defaults to (255, 255, 255).

    Returns:
        tuple: Three integers (r, g, b) in 0–255 representing the blended color.

    Raises:
        ValueError: If `rgba` or `background` have incorrect lengths or values outside their allowed ranges.
    """
    if not (isinstance(rgba, (list, tuple)) and len(rgba) == 4):
        raise ValueError('RGBA must be a tuple or list of 4 values.')
    r, g, b, a = rgba
    if not all(isinstance(v, int) and 0 <= v <= 255 for v in (r, g, b)):
        raise ValueError('RGBA r, g, b must be integers in 0–255.')
    if not isinstance(a, (float, int)) or not (0.0 <= a <= 1.0):
        raise ValueError('RGBA a must be a float in 0–1.')
    if not (isinstance(background, (list, tuple)) and len(background) == 3):
        raise ValueError('background must be a tuple or list of 3 values.')
    if not all(isinstance(v, int) and 0 <= v <= 255 for v in background):
        raise ValueError('background r, g, b must be integers in 0–255.')

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
        raise ValueError(f'Invalid RGB values: {rgb}')
    return f'rgb({rgb[0]}, {rgb[1]}, {rgb[2]})'


import re

# -------------------------
# Utility parsers
# -------------------------


def _parse_rgb_component(v):
    """
    Parse an RGB component string into a numeric value on the 0–255 scale.

    Parameters:
        v (str): String containing a numeric component or a percentage (may include surrounding whitespace,
            e.g. "128", "50%", " 75.5% ").

    Returns:
        float: Component value scaled to the 0–255 range (percentages are converted so "100%" → 255.0).
    """
    v = v.strip()
    if v.endswith('%'):
        return float(v[:-1]) * 2.55  # 100% → 255
    return float(v)


def _parse_hsl_percentage_or_decimal(v):
    """
    Parse an HSL saturation or lightness component into a decimal in the range 0–1.

    Accepts percentage strings (e.g., "50%") or decimal strings (e.g., "0.5" or "1.0") and returns the corresponding float.

    Parameters:
        v (str): The S or L value as a string, optionally ending with '%' for percentages.

    Returns:
        float: The parsed value as a decimal between 0 and 1.

    Raises:
        ValueError: If the input is not a percentage or a decimal in the range 0–1.
    """
    v = v.strip()
    if v.endswith('%'):
        return float(v[:-1]) / 100.0
    x = float(v)
    if 0 <= x <= 1:
        return x
    raise ValueError(f'S/L must be either percentage or decimal 0–1: {v}')


def _parse_hue(v):
    """
    Normalize a hue value to degrees in the range [0, 360).

    Parameters:
        v (str | int | float): Hue value as a number or string (may include surrounding whitespace or represent a float).

    Returns:
        float: Hue in degrees normalized to the interval [0, 360).
    """
    return float(v.strip()) % 360


# -------------------------
# RGB → HSL
# -------------------------


def rgb_to_hsl(rgb_color):
    """
    Convert an RGB color to a CSS HSL string.

    Parameters:
        rgb_color (tuple | list | str): An RGB color as a 3- or 4-element tuple/list (r, g, b[, a]) with 0–255 components,
            or a CSS `rgb()` / `rgba()` string. Strings may use commas or spaces, components may be percentages,
            and alpha may be provided after a slash or as a fourth component.

    Returns:
        str: A CSS HSL string in the form `hsl(H, S%, L%)` where `H` is hue in degrees [0, 360), and `S%` and `L%`
            are saturation and lightness as percentages (0%–100%).

    Raises:
        ValueError: If the input string is malformed or any RGB component is out of the 0–255 range.
        TypeError: If `rgb_color` is not a supported type.
    """

    # ---- Parse CSS string ----
    if isinstance(rgb_color, str):
        text = rgb_color.strip().lower()

        if not (text.startswith('rgb(') or text.startswith('rgba(')):
            raise ValueError(f'Invalid RGB/RGBA string: {rgb_color}')

        inside = text[text.find('(') + 1 : text.rfind(')')].strip()
        inside = inside.replace(',', ' ')

        # strip alpha if present
        if '/' in inside:
            inside, _alpha = inside.split('/', 1)
            inside = inside.strip()

        parts = re.split(r'\s+', inside)
        if len(parts) < 3:
            raise ValueError(f'Invalid RGB (missing components): {rgb_color}')

        r = _parse_rgb_component(parts[0])
        g = _parse_rgb_component(parts[1])
        b = _parse_rgb_component(parts[2])

    # ---- Parse tuple/list ----
    elif isinstance(rgb_color, (tuple, list)):
        if len(rgb_color) < 3:
            raise ValueError('RGB tuple must have ≥ 3 components')
        r, g, b = rgb_color[:3]
    else:
        raise TypeError('Unsupported RGB format')

    # validate range
    for c in (r, g, b):
        if not (0 <= c <= 255):
            raise ValueError(f'RGB component out of range: {c}')

    # normalize
    r /= 255
    g /= 255
    b /= 255

    # ---- Convert to HSL ----
    mx = max(r, g, b)
    mn = min(r, g, b)
    diff = mx - mn

    l = (mx + mn) / 2

    if diff == 0:
        h = 0
        s = 0
    else:
        s = diff / (1 - abs(2 * l - 1))

        if mx == r:
            h = (g - b) / diff % 6
        elif mx == g:
            h = (b - r) / diff + 2
        else:
            h = (r - g) / diff + 4

        h *= 60

    # return CSS string form
    return f'hsl({h}, {s*100}%, {l*100}%)'


# -------------------------
# HSL → RGB
# -------------------------


def hsl_to_rgb(hsl_color):
    """
    Convert an HSL color representation to an RGB color.

    Parameters:
        hsl_color (str | tuple | list): An HSL color specified as a CSS-like string (e.g. "hsl(120, 50%, 25%)" or "hsl(120 50% 25%)")
            or a 3-element tuple/list (h, s, l). Hue may be any numeric value (wrapped into [0,360)); saturation and lightness
            may be percentages (e.g. "50%") or decimals in [0,1].

    Returns:
        tuple: A 3-tuple of integers (r, g, b) with each component in 0–255.

    Raises:
        ValueError: If the input string is malformed, the tuple length is not 3, or parsed S/L are outside 0–1.
        TypeError: If hsl_color is not a supported type.
    """

    # ---- Parse CSS string ----
    if isinstance(hsl_color, str):
        text = hsl_color.strip().lower()
        if not text.startswith('hsl(') or not text.endswith(')'):
            raise ValueError(f'Invalid HSL string: {hsl_color}')

        inside = text[4:-1].strip()
        inside = inside.replace(',', ' ')
        inside = inside.replace('%', '% ')  # so split doesn't glue them

        parts = re.split(r'\s+', inside)
        parts = [p for p in parts if p]  # trim empties

        if len(parts) < 3:
            raise ValueError(f'Invalid HSL string components: {hsl_color}')

        h = _parse_hue(parts[0])
        s = _parse_hsl_percentage_or_decimal(parts[1])
        l = _parse_hsl_percentage_or_decimal(parts[2])

    # ---- Parse tuple/list ----
    elif isinstance(hsl_color, (tuple, list)):
        if len(hsl_color) != 3:
            raise ValueError('HSL tuple must be length 3')

        raw_h, raw_s, raw_l = hsl_color

        h = _parse_hue(str(raw_h))

        # raw_s, raw_l may be decimals or percentages
        s = _parse_hsl_percentage_or_decimal(str(raw_s))
        l = _parse_hsl_percentage_or_decimal(str(raw_l))

    else:
        raise TypeError('Unsupported HSL format')

    # ---- Validate ----
    if not (0 <= s <= 1 and 0 <= l <= 1):
        raise ValueError('S and L must be in [0, 1] after parsing')

    # ---- Convert to RGB ----
    if s == 0:
        r = g = b = l
    else:

        def f(p, q, t):
            """
            Compute a single RGB channel value from HSL interpolation parameters.

            Parameters:
                p (float): Lower intermediate value, typically in the 0–1 range.
                q (float): Upper intermediate value, typically in the 0–1 range.
                t (float): Hue-derived offset; values outside 0–1 are wrapped into that interval.

            Returns:
                float: The computed channel value (typically in the 0–1 range).
            """
            if t < 0:
                t += 1
            if t > 1:
                t -= 1
            if t < 1 / 6:
                return p + (q - p) * 6 * t
            if t < 1 / 2:
                return q
            if t < 2 / 3:
                return p + (q - p) * (2 / 3 - t) * 6
            return p

        q = l * (1 + s) if l < 0.5 else (l + s - l * s)
        p = 2 * l - q

        h_norm = h / 360

        r = f(p, q, h_norm + 1 / 3)
        g = f(p, q, h_norm)
        b = f(p, q, h_norm - 1 / 3)

    return (int(round(r * 255)), int(round(g * 255)), int(round(b * 255)))


def hsla_to_rgb(hsla_color, background=None):
    """
    Convert an HSLA color to an RGB tuple, compositing over a background when alpha < 1.

    Parameters:
        hsla_color (str | tuple | list): HSLA color. Accepted formats:
            - Tuple/list: (h, s, l, a) where h is in degrees (will be wrapped into [0,360)), s and l are decimals in [0,1], and a is in [0,1].
            - CSS string: "hsla(120, 100%, 50%, 0.8)" or "hsla(120 100% 50% / 0.8)" (percent signs allowed for s and l; alpha may be a decimal or percent).
        background (tuple | list, optional): RGB background to composite against when alpha < 1, as (r, g, b) with each in 0–255. Defaults to white (255, 255, 255).

    Returns:
        tuple: (r, g, b) with each component as an integer in 0–255.

    Raises:
        TypeError: If hsla_color is not a string, tuple, or list.
        ValueError: If hsla_color or background formats or numeric ranges are invalid.
    """
    if isinstance(hsla_color, str):
        # Parse CSS string
        hsla_color = hsla_color.strip().lower()
        if hsla_color.startswith('hsla(') and hsla_color.endswith(')'):
            content = hsla_color[5:-1].strip()
            # Handle both comma and space separation, and slash for alpha
            content = content.replace(
                '/', ','
            )  # Convert slash format to comma
            parts = [p.strip().replace('%', '') for p in content.split(',')]

            if len(parts) == 4:
                h = float(parts[0]) % 360  # Wrap hue
                s = float(parts[1]) / 100.0 if parts[1] else 0.0
                l = float(parts[2]) / 100.0 if parts[2] else 0.0
                a = (
                    float(parts[3])
                    if float(parts[3]) <= 1.0
                    else float(parts[3]) / 100.0
                )
            else:
                raise ValueError('Invalid HSLA CSS string format')
        else:
            raise ValueError(
                "Invalid HSLA string format - must start with 'hsla('"
            )

    elif isinstance(hsla_color, (tuple, list)):
        if len(hsla_color) == 4:
            h, s, l, a = hsla_color
            h = float(h) % 360
            s = float(s)
            l = float(l)
            a = float(a)
        else:
            raise ValueError(
                'Invalid HSLA tuple/list - must have 4 components'
            )
    else:
        raise TypeError('HSLA color must be string, tuple, or list')

    # Validate ranges
    if not (0 <= s <= 1 and 0 <= l <= 1 and 0 <= a <= 1):
        raise ValueError('HSLA values out of range: s, l, a must be in [0, 1]')

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
            raise ValueError(
                'Invalid format, please input RGB Tuple (int,int,int)'
            )

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
        rgb_tuple (tuple[int, int, int]): RGB color as (r, g, b) with each value in 0–255.
        alpha (float): Alpha value in 0–1 (defaults to 1.0).

    Returns:
        str: HSLA CSS string in the form "hsla(h, s%, l%, a)" where h is degrees, s and l are percentages, and a is the provided alpha.
    """
    if not isinstance(rgb_tuple, (tuple, list)) or len(rgb_tuple) != 3:
        raise ValueError('RGB must be a tuple/list of 3 values')

    r, g, b = rgb_tuple
    if not all(0 <= val <= 255 for val in (r, g, b)):
        raise ValueError('RGB values must be in range [0, 255]')

    if not (0 <= alpha <= 1):
        raise ValueError('Alpha must be in range [0, 1]')

    hsl_string = rgb_to_hsl(rgb_tuple)

    # Extract h, s, l from the HSL string and add alpha
    # hsl_string format: "hsl(120, 100%, 50%)"
    content = hsl_string[4:-1]  # Remove "hsl(" and ")"
    h_part, s_part, l_part = content.split(', ')

    return f'hsla({h_part}, {s_part}, {l_part}, {alpha})'
