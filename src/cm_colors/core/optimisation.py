from typing import Tuple, Optional
from cm_colors.core.conversions import (
    rgb_to_oklch_safe,
    oklch_to_rgb_safe,
    is_valid_rgb,
    rgbint_to_string,
)
from cm_colors.core.color_parser import parse_color_to_rgb

from cm_colors.core.contrast import calculate_contrast_ratio, get_wcag_level
from cm_colors.core.color_metrics import calculate_delta_e_2000

from cm_colors.core.colors import Color


def binary_search_lightness(
    text_rgb: Tuple[int, int, int],
    bg_rgb: Tuple[int, int, int],
    delta_e_threshold: float = 2.0,
    target_contrast: float = 7.0,
    large_text: bool = False,
) -> Optional[Tuple[int, int, int]]:
    """
    Search the Oklch lightness of a text color to find a candidate RGB that meets a contrast target while keeping perceptual change within a DeltaE threshold.

    Parameters:
        text_rgb (Tuple[int, int, int]): Original text color as an (R, G, B) tuple with 0–255 components.
        bg_rgb (Tuple[int, int, int]): Background color as an (R, G, B) tuple with 0–255 components.
        delta_e_threshold (float): Maximum allowed CIEDE2000 distance between the original text color and a candidate (default 2.0).
        target_contrast (float): Desired contrast ratio between candidate text and background (default 7.0).
        large_text (bool): Ignored by this routine but kept for API compatibility; no effect on search behavior (default False).

    Returns:
        Optional[Tuple[int, int, int]]: An (R, G, B) tuple for a candidate text color that meets the constraints, or `None` if no suitable candidate is found or an error occurs.
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
        best_delta_e = float('inf')
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

            # Strict validation only checks DeltaE. The calling function 
            # (generate_accessible_color) will handle the overall contrast requirement 
            # and track the best candidate found. (FIX APPLIED HERE)
            if final_delta_e <= delta_e_threshold:
                return final_rgb

        return None

    except Exception:
        return None


def generate_accessible_color(
    text_rgb: Tuple[int, int, int],
    bg_rgb: Tuple[int, int, int],
    large: bool = False,
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
    best_delta_e = float('inf')

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
                result_contrast == best_contrast
                and result_delta_e < best_delta_e
            ):
                best_contrast = result_contrast
                best_candidate = gradient_result
                best_delta_e = result_delta_e

        # Early termination with strict DeltaE (matching brute force logic)
        if (
            best_candidate
            and best_contrast >= min_contrast
            and max_delta_e <= 2.5
        ):
            return best_candidate

    return best_candidate if best_candidate else text_rgb


def check_and_fix_contrast(
    text, bg, large: bool = False, details: bool = False
):
    """
    Verify and, if necessary, adjust a text/background color pair so it meets WCAG contrast requirements.

    Parameters:
        text: Text color in any parseable format.
        bg: Background color in any parseable format.
        large (bool): True to use the large-text WCAG threshold, False to use the normal-text threshold.
        details (bool): If False, return a simple result tuple; if True, return a detailed report dictionary.

    Returns:
        If details is False: (tuned_color, is_accessible)
            tuned_color (str): The resulting text color as an RGB string (may be the original input if already acceptable).
            is_accessible (bool): True if tuned_color meets the WCAG contrast requirement for the given `large` flag, False otherwise.
        If details is True: dict containing:
            - text: original text color input
            - tuned_text: resulting text color as an RGB string
            - bg: original background color input
            - large: the `large` flag value used
            - wcag_level: resulting WCAG level string (e.g., "AAA", "AA", "FAIL")
            - improvement_percentage: percent improvement in contrast relative to the original color
            - status: True if tuned_text meets at least the minimum WCAG level, False otherwise
            - message: human-readable outcome message

    Raises:
        ValueError: if `text` or `bg` cannot be parsed as valid colors.
    """
    # SHOULD NEVER BE CALLED STANDALONE. CALL ONLY THROUGH ColorPair Class
    # Assumes the inputs are passed through ColorPair's _rgb method only after parsing
    # Validaton just to double check - the function is only called through ColorPair which already validates

    text_color = Color(text)
    bg_color = Color(bg)

    if not text_color.is_valid:
        raise ValueError(f'Invalid text color: {text_color.error}')
    if not bg_color.is_valid:
        raise ValueError(f'Invalid background color: {bg_color.error}')

    current_contrast = calculate_contrast_ratio(text, bg)
    target_contrast = 4.5 if large else 7.0

    if current_contrast >= target_contrast:
        if not details:
            return text, True
        else:
            return {
                'text': text,
                'tuned_text': text,
                'bg': bg,
                'large': large,
                'wcag_level': 'AAA' if current_contrast >= 7.0 else 'AA',
                'improvement_percentage': 0,
                'status': True,
                'message': 'Perfect! Your pair is already accessible with a contrast ratio of {:.2f}.'.format(
                    current_contrast
                ),
            }

    accessible_text = generate_accessible_color(text, bg, large)
    final_contrast = calculate_contrast_ratio(accessible_text, bg)
                
    aa_target = 3.0 if large else 4.5

    # is_wcag_aa = final_contrast >= aa_target
    success = final_contrast >= aa_target
    wcag_level = get_wcag_level(accessible_text, bg,large)



    improvement_percentage = round(
        (((final_contrast - current_contrast) / current_contrast) * 100), 2
    )
    accessible_text = rgbint_to_string(accessible_text)


    if not details:
        return accessible_text, success
    else:
        if wcag_level == 'FAIL':
            message = f'Please choose a different color, your pair is not accessible with a contrast ratio of {final_contrast:.2f}.'
        else:
            message = f'Your pair was not accessible, but now it is {wcag_level} compliant with a contrast ratio of {final_contrast:.2f}.'
        return {
            'text': text,
            'tuned_text': accessible_text,
            'bg': bg,
            'large': large,
            'wcag_level': wcag_level,
            'improvement_percentage': improvement_percentage,
            'status': success,
            'message': message,
        }