from typing import Tuple, Optional
from cm_colors.core.conversions import (
    rgb_to_oklch_safe,
    oklch_to_rgb_safe,
    is_valid_rgb,
    parse_color_to_rgb,
    rgbint_to_string,
    rgba_to_rgb,
)
from cm_colors.core.contrast import calculate_contrast_ratio, get_wcag_level
from cm_colors.core.color_metrics import calculate_delta_e_2000


def binary_search_lightness(
    text_rgb: Tuple[int, int, int],
    bg_rgb: Tuple[int, int, int],
    delta_e_threshold: float = 2.0,
    target_contrast: float = 7.0,
    large_text: bool = False,
) -> Optional[Tuple[int, int, int]]:
    """
    Binary search on lightness component to find minimal change achieving target contrast
    while keeping DeltaE <= threshold. O(log n) complexity vs O(n) brute force.
    """
    try:
        l, c, h = rgb_to_oklch_safe(text_rgb)

        # Determine search direction based on background brightness
        bg_l, _, _ = rgb_to_oklch_safe(bg_rgb)
        search_up = bg_l < 0.5  # Lighten text on dark bg, darken on light bg

        # Binary search bounds
        low = l if search_up else 0.0
        high = 1.0 if search_up else l

        best_rgb = None
        best_delta_e = float("inf")
        best_contrast = 0.0

        # Precision-matched binary search (20 iterations = ~1M precision)
        for _ in range(20):
            mid = (low + high) / 2.0
            candidate_oklch = (mid, c, h)
            candidate_rgb = oklch_to_rgb_safe(candidate_oklch)

            if not is_valid_rgb(candidate_rgb):
                if search_up:
                    high = mid
                else:
                    low = mid
                continue

            delta_e = calculate_delta_e_2000(text_rgb, candidate_rgb)
            contrast = calculate_contrast_ratio(candidate_rgb, bg_rgb)

            # Strict DeltaE enforcement
            if delta_e > delta_e_threshold:
                if search_up:
                    high = mid
                else:
                    low = mid
                continue

            # Track best valid candidate
            if contrast >= target_contrast:
                if delta_e < best_delta_e:
                    best_rgb = candidate_rgb
                    best_delta_e = delta_e
                    best_contrast = contrast
                # Try to minimize DeltaE further
                if search_up:
                    high = mid
                else:
                    low = mid
            else:
                # Need more contrast
                if search_up:
                    low = mid
                else:
                    high = mid
                # Update best if better contrast found
                if contrast > best_contrast:
                    best_contrast = contrast
                    best_rgb = candidate_rgb
                    best_delta_e = delta_e

        return best_rgb

    except Exception:
        return None


def gradient_descent_oklch(
    text_rgb: Tuple[int, int, int],
    bg_rgb: Tuple[int, int, int],
    delta_e_threshold: float = 2.0,
    target_contrast: float = 7.0,
    large_text: bool = False,
    max_iter: int = 50,
) -> Optional[Tuple[int, int, int]]:
    """
    Gradient descent optimization for lightness and chroma simultaneously.
    Maintains mathematical rigor while exploring 2D parameter space efficiently.
    """
    try:
        l, c, h = rgb_to_oklch_safe(text_rgb)

        # Adaptive learning rate based on color space
        learning_rate = 0.02

        # Current parameter vector [lightness, chroma]
        current = [l, c]

        # Cost function with exact penalty structure as brute force
        def cost_function(params):
            new_l, new_c = params
            # Strict bounds enforcement
            new_l = max(0.0, min(1.0, new_l))
            new_c = max(0.0, min(0.5, new_c))  # Gamut constraint

            candidate_oklch = (new_l, new_c, h)
            candidate_rgb = oklch_to_rgb_safe(candidate_oklch)

            if not is_valid_rgb(candidate_rgb):
                return 1e6

            delta_e = calculate_delta_e_2000(text_rgb, candidate_rgb)
            contrast = calculate_contrast_ratio(candidate_rgb, bg_rgb)

            # Penalty structure matching brute force priorities
            contrast_penalty = max(0, target_contrast - contrast) * 1000
            delta_e_penalty = max(0, delta_e - delta_e_threshold) * 10000
            # Minimize perceptual distance (brand preservation)
            distance_penalty = delta_e * 100

            return contrast_penalty + delta_e_penalty + distance_penalty

        # Numerical gradient computation (central difference)
        def compute_gradient(params):
            gradient = [0.0, 0.0]
            epsilon = 1e-4

            for i in range(2):
                params_plus = params.copy()
                params_minus = params.copy()
                params_plus[i] += epsilon
                params_minus[i] -= epsilon

                gradient[i] = (
                    cost_function(params_plus) - cost_function(params_minus)
                ) / (2 * epsilon)

            return gradient

        # Gradient descent with adaptive learning rate
        for iteration in range(max_iter):
            gradient = compute_gradient(current)

            # Adaptive learning rate decay
            adaptive_lr = learning_rate * (0.95 ** (iteration // 10))

            # Update parameters
            next_params = [
                current[0] - adaptive_lr * gradient[0],
                current[1] - adaptive_lr * gradient[1],
            ]

            # Bounds enforcement
            next_params[0] = max(0.0, min(1.0, next_params[0]))
            next_params[1] = max(0.0, min(0.5, next_params[1]))

            # Convergence check
            if abs(cost_function(current) - cost_function(next_params)) < 1e-6:
                break

            current = next_params

        # Validate final result
        final_oklch = (current[0], current[1], h)
        final_rgb = oklch_to_rgb_safe(final_oklch)

        if is_valid_rgb(final_rgb):
            final_delta_e = calculate_delta_e_2000(text_rgb, final_rgb)
            final_contrast = calculate_contrast_ratio(final_rgb, bg_rgb)

            # Strict validation matching brute force standards
            if final_delta_e <= delta_e_threshold and final_contrast >= target_contrast:
                return final_rgb

        return None

    except Exception:
        return None


def generate_accessible_color(
    text_rgb: Tuple[int, int, int], bg_rgb: Tuple[int, int, int], large: bool = False
) -> Tuple[int, int, int]:
    """
    Main optimization function: Binary search first, then gradient descent.
    Maintains exact same rigor and quality as brute force with superior performance.
    """
    # Check if already accessible
    current_contrast = calculate_contrast_ratio(text_rgb, bg_rgb)
    target_contrast = 4.5 if large else 7.0
    min_contrast = 3.0 if large else 4.5

    if current_contrast >= target_contrast:
        return text_rgb

    # Progressive DeltaE thresholds (matching brute force sequence)
    delta_e_sequence = [
        0.8,
        1.0,
        1.2,
        1.4,
        1.6,
        1.8,
        2.0,
        2.1,
        2.2,
        2.3,
        2.4,
        2.5,
        2.7,
        3.0,
        3.5,
        4.0,
        5.0,
    ]

    best_candidate = None
    best_contrast = current_contrast
    best_delta_e = float("inf")

    for max_delta_e in delta_e_sequence:
        # Phase 1: Binary search on lightness (fastest, most effective)
        binary_result = binary_search_lightness(
            text_rgb, bg_rgb, max_delta_e, target_contrast, large
        )

        if binary_result:
            result_contrast = calculate_contrast_ratio(binary_result, bg_rgb)
            result_delta_e = calculate_delta_e_2000(text_rgb, binary_result)

            if result_contrast >= target_contrast:
                return binary_result

            if result_contrast > best_contrast:
                best_contrast = result_contrast
                best_candidate = binary_result
                best_delta_e = result_delta_e

        # Phase 2: Gradient descent for lightness + chroma optimization
        gradient_result = gradient_descent_oklch(
            text_rgb, bg_rgb, max_delta_e, target_contrast, large
        )

        if gradient_result:
            result_contrast = calculate_contrast_ratio(gradient_result, bg_rgb)
            result_delta_e = calculate_delta_e_2000(text_rgb, gradient_result)

            if result_contrast >= target_contrast:
                return gradient_result

            if result_contrast > best_contrast or (
                result_contrast == best_contrast and result_delta_e < best_delta_e
            ):
                best_contrast = result_contrast
                best_candidate = gradient_result
                best_delta_e = result_delta_e

        # Early termination with strict DeltaE (matching brute force logic)
        if best_candidate and best_contrast >= min_contrast and max_delta_e <= 2.5:
            return best_candidate

    return best_candidate if best_candidate else text_rgb


def _is_rgba_input(color) -> bool:
    """Check if the input color is in RGBA format (string or tuple)."""
    if isinstance(color, str):
        return color.startswith("rgba(") and color.endswith(")")
    elif isinstance(color, (tuple, list)):
        return len(color) == 4
    return False


def _convert_rgba_to_rgb(rgba_input, bg_color) -> Tuple[int, int, int]:
    """Convert RGBA input to RGB using alpha blending with background color."""
    # Parse background color to RGB to use as blending background
    if _is_rgba_input(bg_color):
        # If background is also RGBA, convert it to RGB first using white background
        bg_rgb = _convert_rgba_to_rgb(bg_color, (255, 255, 255))
    else:
        bg_rgb = parse_color_to_rgb(bg_color)
    
    if isinstance(rgba_input, str):
        # Parse RGBA string
        rgba_content = rgba_input[5:-1]  # Remove "rgba(" and ")"
        rgba_values = rgba_content.split(",")
        
        if len(rgba_values) != 4:
            raise ValueError(
                f"RGBA string must have exactly 4 values separated by commas. Got {len(rgba_values)} values in '{rgba_input}'."
            )
        
        try:
            parsed_values = []
            # Parse RGB components (first 3 values)
            for i, value_str in enumerate(rgba_values[:3]):
                value_str = value_str.strip()
                try:
                    value = int(value_str)
                    if value < 0:
                        raise ValueError(
                            f"RGB values cannot be negative. Got {value} for {'RGB'[i]} component in '{rgba_input}'."
                        )
                    if value > 255:
                        raise ValueError(
                            f"RGB values must be between 0-255. Got {value} for {'RGB'[i]} component in '{rgba_input}'."
                        )
                    parsed_values.append(value)
                except ValueError as ve:
                    if "cannot be negative" in str(ve) or "must be between 0-255" in str(ve):
                        raise ve
                    raise ValueError(
                        f"Invalid numeric value '{value_str}' for {'RGB'[i]} component in '{rgba_input}'. Must be an integer between 0-255."
                    )
            
            # Parse alpha component (fourth value)
            alpha_str = rgba_values[3].strip()
            try:
                alpha = float(alpha_str)
                if alpha < 0 or alpha > 1:
                    raise ValueError(
                        f"Alpha value must be between 0 and 1. Got {alpha} in '{rgba_input}'."
                    )
                parsed_values.append(alpha)
            except ValueError as ve:
                if "Alpha value must be between" in str(ve):
                    raise ve
                raise ValueError(
                    f"Invalid alpha value '{alpha_str}' in '{rgba_input}'. Must be a number between 0 and 1."
                )
            
            # Convert RGBA to RGB using alpha blending
            rgba_tuple = (parsed_values[0], parsed_values[1], parsed_values[2], parsed_values[3])
            return rgba_to_rgb(rgba_tuple, bg_rgb)
        except ValueError as ve:
            if (
                "RGB values" in str(ve)
                or "Alpha value" in str(ve)
                or "Invalid alpha value" in str(ve)
            ):
                raise ve
            raise ValueError(
                f"Invalid RGBA string format: '{rgba_input}'. Expected format: 'rgba(r, g, b, a)' where r, g, b are integers 0-255 and a is a number 0-1."
            )
    
    elif isinstance(rgba_input, (tuple, list)):
        # Handle RGBA tuple/list
        if len(rgba_input) == 4:
            if all(isinstance(x, (int, float)) for x in rgba_input):
                r, g, b, alpha = rgba_input
                # Validate RGB components
                if not all(isinstance(x, int) and 0 <= x <= 255 for x in [r, g, b]):
                    raise ValueError(f"RGB values in RGBA tuple must be integers 0-255. Got: {rgba_input}")
                # Validate alpha component
                if not isinstance(alpha, (int, float)) or not (0 <= alpha <= 1):
                    raise ValueError(f"Alpha value in RGBA tuple must be between 0 and 1. Got: {rgba_input}")
                # Convert RGBA to RGB using alpha blending
                return rgba_to_rgb((r, g, b, alpha), bg_rgb)
            else:
                raise ValueError(f"RGBA tuple must contain only numbers. Got: {rgba_input}")
        else:
            raise ValueError(f"RGBA tuple must have exactly 4 values. Got {len(rgba_input)} values: {rgba_input}")
    
    raise ValueError(f"Unsupported RGBA input type: {type(rgba_input).__name__}")


def check_and_fix_contrast(text, bg, large: bool = False, details: bool = False):
    """Main function to check and fix contrast using optimized methods.

     Args:
        text: Text color (any valid hex, rgb string, rgba string, rgb tuple, or rgba tuple)
        bg: Background color (any valid hex, rgb string or rgb tuple)
        large: True for large text (18pt+ or 14pt+ bold), False for normal text
        details: If True, returns detailed report, else just (tuned_color, is_accessible)

    Returns:
        details = False: (tuned_color, accessible with atleast 4.5)
        details = True: a dict with detailed report
    """

    # Check if text is RGBA and convert to RGB if necessary
    if _is_rgba_input(text):
        text_rgb = _convert_rgba_to_rgb(text, bg)
    else:
        text_rgb = parse_color_to_rgb(text)
    
    # Check if background is RGBA and convert to RGB if necessary
    if _is_rgba_input(bg):
        bg_rgb = _convert_rgba_to_rgb(bg, (255, 255, 255))  # Use white as default for background conversion
    else:
        bg_rgb = parse_color_to_rgb(bg)

    if not (is_valid_rgb(text_rgb) and is_valid_rgb(bg_rgb)):
        raise ValueError(
            "Invalid RGB values provided. Each component must be between 0 and 255."
        )

    current_contrast = calculate_contrast_ratio(text_rgb, bg_rgb)
    target_contrast = 4.5 if large else 7.0

    if current_contrast >= target_contrast:
        if not details:
            return text, True
        else:
            return {
                "text": text,
                "tuned_text": text,
                "bg": bg,
                "large": large,
                "wcag_level": "AAA",
                "improvement_percentage": 0,
                "status": True,
                "message": "Perfect! Your pair is already accessible with a contrast ratio of {:.2f}.".format(
                    current_contrast
                ),
            }

    accessible_text = generate_accessible_color(text_rgb, bg_rgb, large)
    wcag_level = get_wcag_level(accessible_text, bg_rgb)

    new_contrast = calculate_contrast_ratio(accessible_text, bg_rgb)
    improvement_percentage = round(
        (((new_contrast - current_contrast) / current_contrast) * 100), 2
    )
    accessible_text = rgbint_to_string(accessible_text)

    if not details:
        return accessible_text, True if wcag_level != "FAIL" else False
    else:
        if wcag_level == "FAIL":
            message = f"Please choose a different color, your pair is not accessible with a contrast ratio of {new_contrast:.2f}."
        else:
            message = f"Your pair was not accessible, but now it is {wcag_level} compliant with a contrast ratio of {new_contrast:.2f}."
        return {
            "text": text,
            "tuned_text": accessible_text,
            "bg": bg,
            "large": large,
            "wcag_level": wcag_level,
            "improvement_percentage": improvement_percentage,
            "status": True if wcag_level != "FAIL" else False,
            "message": message,
        }
