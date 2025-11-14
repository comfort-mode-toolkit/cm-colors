from cm_colors.core.named_colors import CSS_NAMED_COLORS
from cm_colors.core.conversions import (
    is_valid_rgb,
    hex_to_rgb,
    rgba_to_rgb,
    hsla_to_rgb,
    hsl_to_rgb,
)

import re
from typing import Tuple, Union,Optional

NumberLike = Union[int, float, str]
ColorInput = Union[str, Tuple, list]

_NUM_RE = re.compile(r'[-+]?\d*\.?\d+%?')


def _parse_number_token(tok: str, component: bool = True) -> float:
    """
    Parse a numeric token representing an RGB component or alpha and convert it to the appropriate numeric scale.

    Parameters:
        tok (str): Numeric token to parse; may include a trailing '%' to denote a percentage.
        component (bool): If True, interpret the token as an RGB component and return a value on the 0–255 scale. If False, interpret as an alpha value on the 0–1 scale.

    Returns:
        float: For RGB components (`component=True`), a value in the range 0.0–255.0. For alpha (`component=False`), a value in the range 0.0–1.0.

    Raises:
        ValueError: If the token is not a valid number/percentage or if the parsed value falls outside the allowed range for the selected mode.
    """
    tok = tok.strip()
    if tok.endswith('%'):
        # percentage
        try:
            v = float(tok[:-1])
        except Exception:
            raise ValueError(f"Invalid percentage value: '{tok}'")
        if component:
            return max(0.0, min(255.0, v * 255.0 / 100.0))
        else:
            return max(0.0, min(1.0, v / 100.0))
    # not percentage
    try:
        # Use float() for all parsing - handles int, float, and scientific notation
        v = float(tok)
    except Exception:
        raise ValueError(f"Invalid numeric value: '{tok}'")

    if component:
        # allow 0..255, or 0..1 style floats
        if 0.0 <= v <= 1.0:
            # treat as fraction of 255
            return v * 255.0
        if 0.0 <= v <= 255.0:
            return float(v)
        raise ValueError(f'RGB component out of range: {v}')
    else:
        # alpha: prefer 0..1, but if given >1 and <=100 maybe user intended percent
        if 0.0 <= v <= 1.0:
            return float(v)
        if 1.0 < v <= 100.0:
            # interpret as percent (e.g., "50" -> 50% -> 0.5)
            return max(0.0, min(1.0, v / 100.0))
        raise ValueError(f'Alpha value out of range: {v}')


def _extract_number_tokens(s: str) -> list:
    """
    Extract numeric tokens from a string, preserving trailing percent signs.

    Parameters:
        s (str): Input string to search for numeric tokens.

    Returns:
        list[str]: Matched numeric tokens as strings (e.g., '10', '50%', '-3.5').
    """
    return _NUM_RE.findall(s)


def parse_color_to_rgb(
    color: ColorInput, background: ColorInput | None = None
) -> Tuple[int, int, int]:
    """
    Parse a color specification and return its RGB representation.

    Accepts CSS named colors, hex strings (with or without '#'), "rgb(...)" / "rgba(...)" and informal "r, g, b" or "(r,g,b)" formats, "hsl(...)" / "hsla(...)", and 3- or 4-element tuple/list forms (interpreting 3-element lists as RGB or HSL by heuristic, and 4-element lists as RGBA or HSLA by heuristic). Percentage and fractional component values are supported; when an alpha is present the color is composited over `background` (defaults to white).

    Parameters:
        color: The color to parse (string, tuple, or list). See accepted formats above.
        background: Optional background color used when compositing an alpha channel; may be any input accepted by this function. If omitted and compositing is required, white (255, 255, 255) is used.

    Returns:
        Tuple[int, int, int]: The composited RGB color as integers in the range 0–255.

    Raises:
        ValueError: If the input format, component values, or types are unrecognized or out of range.
    """
    # 1. Normalise tuple/list inputs first
    if isinstance(color, (tuple, list)):
        ln = len(color)
        if ln == 3:
            # 3-component tuple/list - DEFAULT TO RGB (most common case)
            # Only treat as HSL if explicitly float values in 0-1 range for s,l AND h <= 360
            r_raw, g_raw, b_raw = color

            # Check if this looks like HSL: h <= 360, s and l are floats in [0,1]
            if (
                isinstance(r_raw, (int, float))
                and 1 < float(r_raw) <= 360
                and isinstance(g_raw, float)
                and 0.0 <= float(g_raw) <= 1.0
                and isinstance(b_raw, float)
                and 0.0 <= float(b_raw) <= 1.0
                and not isinstance(g_raw, int)
                and not isinstance(b_raw, int)
            ):
                # This looks like HSL: (hue, saturation_float, lightness_float)
                return hsl_to_rgb(color)
            else:
                # Default to RGB processing
                comps = []
                for c in color:
                    if isinstance(c, (int, float)):
                        if isinstance(c, float) and 0.0 <= c <= 1.0:
                            comps.append(int(round(c * 255.0)))
                        elif isinstance(c, int) and 0 <= c <= 255:
                            comps.append(int(c))
                        elif isinstance(c, float) and 0.0 <= c <= 255.0:
                            comps.append(int(round(c)))
                        else:
                            raise ValueError(
                                f'RGB component out of range or invalid: {c}'
                            )
                    elif isinstance(c, str):
                        comps.append(
                            int(round(_parse_number_token(c, component=True)))
                        )
                    else:
                        raise ValueError(
                            f'Unsupported RGB component type: {type(c).__name__}'
                        )

                rgb = tuple(max(0, min(255, int(round(x)))) for x in comps)
                if not is_valid_rgb(rgb):
                    raise ValueError(f'Invalid RGB tuple after parsing: {rgb}')
                return rgb

        elif ln == 4:
            # 4-component tuple: RGBA or HSLA
            # Heuristic: if any of first 3 values are > 1 or integers, treat as RGBA
            r_raw, g_raw, b_raw, a_raw = color

            looks_like_rgb = (
                isinstance(r_raw, int)
                or isinstance(g_raw, int)
                or isinstance(b_raw, int)
                or (isinstance(r_raw, (int, float)) and float(r_raw) > 1.0)
                or (isinstance(g_raw, (int, float)) and float(g_raw) > 1.0)
                or (isinstance(b_raw, (int, float)) and float(b_raw) > 1.0)
            )

            if looks_like_rgb:
                # Treat as RGBA
                r = int(round(_parse_number_token(str(r_raw), component=True)))
                g = int(round(_parse_number_token(str(g_raw), component=True)))
                b = int(round(_parse_number_token(str(b_raw), component=True)))
                a = _parse_number_token(str(a_raw), component=False)

                # resolve background
                if background is None:
                    bg_rgb = (255, 255, 255)
                else:
                    bg_rgb = parse_color_to_rgb(background)
                return rgba_to_rgb((r, g, b, a), background=bg_rgb)
            else:
                bg_rgb = None
                if background is not None:
                    if isinstance(background, (tuple, list)) and len(background) == 3:
                        bg_rgb = tuple(background)
                    else:
                        bg_rgb = parse_color_to_rgb(background)
                return hsla_to_rgb(color, bg_rgb)
        else:
            raise ValueError(
                f'Tuple/list color must have length 3 (RGB/HSL) or 4 (RGBA/HSLA). Got length {ln}'
            )

    # 2. Strings (named, hex, rgb(), rgba(), hsl(), hsla(), informal)
    if isinstance(color, str):
        s = color.strip()
        s_lower = s.lower()

        # CSS named color lookup
        if s_lower in CSS_NAMED_COLORS:
            hex_val = CSS_NAMED_COLORS[s_lower]
            return hex_to_rgb(hex_val)

        # hex with or without '#'
        if s_lower.startswith('#') or re.fullmatch(
            r'[0-9a-fA-F]{3}|[0-9a-fA-F]{6}', s_lower
        ):
            if not s_lower.startswith('#'):
                s = '#' + s
                s_lower = s.lower()
            return hex_to_rgb(s)

        # HSL/HSLA functional notation
        if s_lower.startswith('hsl(') or s_lower.startswith('hsla('):
            if s_lower.startswith('hsla('):
                bg_rgb = None
                if background is not None:
                    if isinstance(background, (tuple, list)) and len(background) == 3:
                        bg_rgb = tuple(background)
                    else:
                        bg_rgb = parse_color_to_rgb(background)
                return hsla_to_rgb(s, bg_rgb)
            else:
                # HSL without alpha
                return hsl_to_rgb(s)

        # RGB/RGBA functional notation and informal formats
        if (
            s_lower.startswith('rgb(')
            or s_lower.startswith('rgba(')
            or s_lower.startswith('rgb ')
            or s_lower.startswith('(')
            or ',' in s
            or ' ' in s
        ):

            tokens = _extract_number_tokens(s_lower)
            if not tokens:
                raise ValueError(
                    f"Could not parse numeric components from '{s}'"
                )

            if len(tokens) >= 4:
                # RGBA
                try:
                    r = int(
                        round(_parse_number_token(tokens[0], component=True))
                    )
                    g = int(
                        round(_parse_number_token(tokens[1], component=True))
                    )
                    b = int(
                        round(_parse_number_token(tokens[2], component=True))
                    )
                    a = _parse_number_token(tokens[3], component=False)
                except ValueError as e:
                    raise ValueError(f"Invalid RGBA components in '{s}': {e}")
                if background is None:
                    bg_rgb = (255, 255, 255)
                else:
                    bg_rgb = parse_color_to_rgb(background)
                return rgba_to_rgb((r, g, b, a), background=bg_rgb)
            elif len(tokens) == 3:
                # RGB
                try:
                    r = int(
                        round(_parse_number_token(tokens[0], component=True))
                    )
                    g = int(
                        round(_parse_number_token(tokens[1], component=True))
                    )
                    b = int(
                        round(_parse_number_token(tokens[2], component=True))
                    )
                except ValueError as e:
                    raise ValueError(f"Invalid RGB components in '{s}': {e}")
                rgb = (
                    max(0, min(255, r)),
                    max(0, min(255, g)),
                    max(0, min(255, b)),
                )
                if not is_valid_rgb(rgb):
                    raise ValueError(
                        f"Invalid RGB values parsed from '{s}': {rgb}"
                    )
                return rgb
            else:
                raise ValueError(f"Unrecognized color format: '{s}'")

        # fallback: unrecognized string
        raise ValueError(f"Unrecognized color string format: '{s}'")

    # unsupported types
    raise ValueError(
        f'Unsupported color input type: {type(color).__name__}. Expected string, tuple, or list.'
    )
