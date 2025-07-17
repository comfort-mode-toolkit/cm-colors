from typing import Tuple, Optional
from helper import rgb_to_oklch_safe, oklch_to_rgb_safe, calculate_delta_e_2000, is_valid_rgb, calculate_contrast_ratio

def binary_search_lightness(text_rgb: Tuple[int, int, int], bg_rgb: Tuple[int, int, int], 
                           delta_e_threshold: float = 2.0, target_contrast: float = 7.0, 
                           large_text: bool = False) -> Optional[Tuple[int, int, int]]:
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


def gradient_descent_oklch(text_rgb: Tuple[int, int, int], bg_rgb: Tuple[int, int, int],
                          delta_e_threshold: float = 2.0, target_contrast: float = 7.0,
                          large_text: bool = False, max_iter: int = 50) -> Optional[Tuple[int, int, int]]:
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
                
                gradient[i] = (cost_function(params_plus) - cost_function(params_minus)) / (2 * epsilon)
            
            return gradient
        
        # Gradient descent with adaptive learning rate
        for iteration in range(max_iter):
            gradient = compute_gradient(current)
            
            # Adaptive learning rate decay
            adaptive_lr = learning_rate * (0.95 ** (iteration // 10))
            
            # Update parameters
            next_params = [
                current[0] - adaptive_lr * gradient[0],
                current[1] - adaptive_lr * gradient[1]
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


def generate_accessible_color_optimized(text_rgb: Tuple[int, int, int], bg_rgb: Tuple[int, int, int], 
                                       large: bool = False) -> Tuple[int, int, int]:
    """
    Main optimization function: Binary search first, then gradient descent.
    Maintains exact same rigor and quality as brute force with superior performance.
    """
    # Check if already accessible
    current_contrast = calculate_contrast_ratio(text_rgb, bg_rgb)
    target_contrast = 7.0
    min_contrast = 4.5 if not large else 3.0
    
    if current_contrast >= target_contrast:
        return text_rgb
    
    # Progressive DeltaE thresholds (matching brute force sequence)
    delta_e_sequence = [0.8, 1.0, 1.2, 1.4, 1.6, 1.8, 2.0, 2.1, 2.2, 2.3, 2.4, 2.5, 2.7, 3.0, 3.5, 4.0, 5.0]
    
    best_candidate = None
    best_contrast = current_contrast
    best_delta_e = float('inf')
    
    for max_delta_e in delta_e_sequence:
        # Phase 1: Binary search on lightness (fastest, most effective)
        binary_result = binary_search_lightness(text_rgb, bg_rgb, max_delta_e, target_contrast, large)
        
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
        gradient_result = gradient_descent_oklch(text_rgb, bg_rgb, max_delta_e, target_contrast, large)
        
        if gradient_result:
            result_contrast = calculate_contrast_ratio(gradient_result, bg_rgb)
            result_delta_e = calculate_delta_e_2000(text_rgb, gradient_result)
            
            if result_contrast >= target_contrast:
                return gradient_result
            
            if result_contrast > best_contrast or (result_contrast == best_contrast and result_delta_e < best_delta_e):
                best_contrast = result_contrast
                best_candidate = gradient_result
                best_delta_e = result_delta_e
        
        # Early termination with strict DeltaE (matching brute force logic)
        if best_candidate and best_contrast >= min_contrast and max_delta_e <= 2.5:
            return best_candidate
    
    return best_candidate if best_candidate else text_rgb


def check_and_fix_contrast_optimized(text_rgb: Tuple[int, int, int], bg_rgb: Tuple[int, int, int], 
                                    large: bool = False) -> Tuple[Tuple[int, int, int], Tuple[int, int, int]]:
    """
    Main function maintaining exact same interface and guarantees as original.
    """
    current_contrast = calculate_contrast_ratio(text_rgb, bg_rgb)
    target_contrast = 7.0
    
    if current_contrast >= target_contrast:
        return (text_rgb, bg_rgb)
    
    accessible_text = generate_accessible_color_optimized(text_rgb, bg_rgb, large)
    return (accessible_text, bg_rgb)
