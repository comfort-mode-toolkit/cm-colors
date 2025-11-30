from typing import Tuple, Optional, List
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
    target_contrast: Optional[float] = None,
    min_contrast: Optional[float] = None,
    delta_e_sequence: Optional[List[float]] = None,
) -> Tuple[int, int, int]:
    """
    Main optimization function: Binary search first, then gradient descent.
    Maintains exact same rigor and quality as brute force with superior performance.
    """
    # Defaults if not provided
    if target_contrast is None:
        target_contrast = 4.5 if large else 7.0
    if min_contrast is None:
        min_contrast = 3.0 if large else 4.5

    # Check if already accessible
    current_contrast = calculate_contrast_ratio(text_rgb, bg_rgb)

    if current_contrast >= target_contrast:
        return text_rgb

    # Progressive DeltaE thresholds (matching brute force sequence)
    if delta_e_sequence is None:
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
        # Only if we are using the default sequence (strict mode)
        if (
            best_candidate
            and best_contrast >= min_contrast
            and max_delta_e <= 2.5
            and delta_e_sequence[-1]
            <= 5.0  # Check if it's the strict sequence
        ):
            return best_candidate

    return best_candidate if best_candidate else text_rgb


def _strategy_strict(
    text_rgb: Tuple[int, int, int],
    bg_rgb: Tuple[int, int, int],
    large: bool,
    target_contrast: float,
    min_contrast: float,
) -> Tuple[Tuple[int, int, int], bool]:
    """
    Mode 0: Ultra Strict
    The current implementation as it is in the py file.
    """
    tuned_rgb = generate_accessible_color(
        text_rgb,
        bg_rgb,
        large=large,
        target_contrast=target_contrast,
        min_contrast=min_contrast,
    )
    final_contrast = calculate_contrast_ratio(tuned_rgb, bg_rgb)
    success = final_contrast >= min_contrast
    return tuned_rgb, success


def _strategy_recursive(
    text_rgb: Tuple[int, int, int],
    bg_rgb: Tuple[int, int, int],
    large: bool,
    target_contrast: float,
    min_contrast: float,
) -> Tuple[Tuple[int, int, int], bool]:
    """
    Mode 1: Default (Recursive)
    Best for all purposes, works on almost all possible pairs with highest success rate.
    """
    current_rgb = text_rgb
    max_iterations = 10

    # Strict sequence for each step
    strict_sequence = [0.8, 1.0, 1.2, 1.4, 1.6, 1.8, 2.0, 2.2, 2.5, 2.8, 3.0]

    for _ in range(max_iterations):
        current_contrast = calculate_contrast_ratio(current_rgb, bg_rgb)
        if current_contrast >= min_contrast:
            return current_rgb, True

        # We use the core function which aims for target_contrast
        # If it returns the same color, it means it couldn't improve within DeltaE limit
        next_rgb = generate_accessible_color(
            current_rgb,
            bg_rgb,
            large=large,
            target_contrast=target_contrast,
            min_contrast=min_contrast,
            delta_e_sequence=strict_sequence,
        )

        if next_rgb == current_rgb:
            # Stuck, can't improve further with strict limit
            # Check if we are at least passing min_contrast
            if calculate_contrast_ratio(next_rgb, bg_rgb) >= min_contrast:
                return next_rgb, True
            else:
                return next_rgb, False

        current_rgb = next_rgb

        # Check if we passed now
        if calculate_contrast_ratio(current_rgb, bg_rgb) >= min_contrast:
            return current_rgb, True

    return current_rgb, False


def _strategy_relaxed(
    text_rgb: Tuple[int, int, int],
    bg_rgb: Tuple[int, int, int],
    large: bool,
    target_contrast: float,
    min_contrast: float,
) -> Tuple[Tuple[int, int, int], bool]:
    """
    Mode 2: Relaxed
    Tries recursive first. If fails, tries increasing iterations OR relaxing Delta E.
    """
    # 1. Try Recursive first
    rec_rgb, rec_success = _strategy_recursive(
        text_rgb, bg_rgb, large, target_contrast, min_contrast
    )
    if rec_success:
        return rec_rgb, True

    # If recursive failed, try two combinations:

    # Option A: Increased iterations (Recursive with 15 iterations)
    # We can just continue from where recursive left off or restart with higher limit.
    # Let's restart with higher limit for simplicity and correctness of the definition "increasing no of iterations by 5"
    # The original recursive used 10, so we use 15.

    opt_a_rgb = text_rgb
    opt_a_success = False
    max_iterations_extended = 15
    strict_sequence = [0.8, 1.0, 1.2, 1.4, 1.6, 1.8, 2.0, 2.2, 2.5, 2.8, 3.0]

    for _ in range(max_iterations_extended):
        if calculate_contrast_ratio(opt_a_rgb, bg_rgb) >= min_contrast:
            opt_a_success = True
            break
        next_rgb = generate_accessible_color(
            opt_a_rgb,
            bg_rgb,
            large=large,
            target_contrast=target_contrast,
            min_contrast=min_contrast,
            delta_e_sequence=strict_sequence,
        )
        if next_rgb == opt_a_rgb:
            if calculate_contrast_ratio(next_rgb, bg_rgb) >= min_contrast:
                opt_a_success = True
            break
        opt_a_rgb = next_rgb
        if calculate_contrast_ratio(opt_a_rgb, bg_rgb) >= min_contrast:
            opt_a_success = True
            break

    # Option B: Delta E relaxation until 15
    relaxed_sequence = [
        0.8,
        1.0,
        1.2,
        1.4,
        1.6,
        1.8,
        2.0,
        2.5,
        3.0,
        3.5,
        4.0,
        5.0,
        6.0,
        7.0,
        8.0,
        9.0,
        10.0,
        12.0,
        15.0,
    ]
    opt_b_rgb = generate_accessible_color(
        text_rgb,
        bg_rgb,
        large=large,
        target_contrast=target_contrast,
        min_contrast=min_contrast,
        delta_e_sequence=relaxed_sequence,
    )
    opt_b_success = calculate_contrast_ratio(opt_b_rgb, bg_rgb) >= min_contrast

    # Decision logic
    if opt_a_success and opt_b_success:
        # Go for the one with minimal delta E
        delta_a = calculate_delta_e_2000(text_rgb, opt_a_rgb)
        delta_b = calculate_delta_e_2000(text_rgb, opt_b_rgb)
        if delta_a <= delta_b:
            return opt_a_rgb, True
        else:
            return opt_b_rgb, True
    elif opt_a_success:
        return opt_a_rgb, True
    elif opt_b_success:
        return opt_b_rgb, True
    else:
        # Return fail (return recursive result as best effort)
        return rec_rgb, False


def check_and_fix_contrast(
    text,
    bg,
    large: bool = False,
    mode: int = 1,
    premium: bool = False,
):
    """
    Verify and, if necessary, adjust a text/background color pair so it meets WCAG contrast requirements.

    Parameters:
        text: Text color in any parseable format.
        bg: Background color in any parseable format.
        large (bool): True to use the large-text WCAG threshold, False to use the normal-text threshold.
        mode (int): Optimization mode.
                    0 = Ultra Strict (original implementation)
                    1 = Default (Recursive)
                    2 = Relaxed (Recursive + fallback)
        premium (bool): If True, aims for AAA compliance regardless of initial state.
                        If False, aims for AA.

    Returns:
        Tuple[str, bool]: (tuned_color, is_accessible)
            tuned_color (str): The resulting text color as an RGB string.
            is_accessible (bool): True if tuned_color meets the requirement.

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

    text_rgb = text_color.rgb
    bg_rgb = bg_color.rgb

    current_contrast = calculate_contrast_ratio(text_rgb, bg_rgb)

    # Determine targets based on premium and large flags
    if premium:
        # Premium always aims for AAA
        if large:
            min_contrast = 4.5
            target_contrast = 4.5   # Aim a bit higher for buffer
        else:
            min_contrast = 7.0
            target_contrast = 7.0
    else:
        # AA Requirements:
        # Normal Text: 4.5
        # Large Text: 3.0

        if large:
            min_contrast = 3.0
            target_contrast = 4.5   # Aim a bit higher for buffer
        else:
            min_contrast = 4.5
            target_contrast = (
                7.0  # Aim a bit higher (AAA) if possible, but AA is the floor
            )

    # Check if already accessible
    # If premium=False, and we already meet AA, return as is.
    # If premium=True, we check against AAA (7.0).

    required_contrast_for_check = min_contrast

    if current_contrast >= required_contrast_for_check:
        # Already passes
        return text, True

    # Dispatch to strategy
    if mode == 0:
        tuned_rgb, success = _strategy_strict(
            text_rgb, bg_rgb, large, target_contrast, min_contrast
        )
    elif mode == 2:
        tuned_rgb, success = _strategy_relaxed(
            text_rgb, bg_rgb, large, target_contrast, min_contrast
        )
    else:
        # Default to mode 1
        tuned_rgb, success = _strategy_recursive(
            text_rgb, bg_rgb, large, target_contrast, min_contrast
        )

    final_contrast = calculate_contrast_ratio(tuned_rgb, bg_rgb)
    wcag_level = get_wcag_level(tuned_rgb, bg_rgb, large)

    improvement_percentage = round(
        (((final_contrast - current_contrast) / current_contrast) * 100), 2
    )
    accessible_text_str = rgbint_to_string(tuned_rgb)

    return accessible_text_str, success
