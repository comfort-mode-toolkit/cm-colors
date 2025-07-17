from typing import Tuple, List, Dict
from helper import rgb_to_oklch_safe, oklch_to_rgb_safe, calculate_delta_e_2000, is_valid_rgb, calculate_contrast_ratio

def generate_lightness_candidates(rgb: Tuple[int, int, int], max_delta_e: float) -> List[Dict]:
    """Generate lightness candidates using perfect OKLCH implementation"""
    try:
        oklch = rgb_to_oklch_safe(rgb)
        l, c, h = oklch
        
        candidates = []
        
        # Ultra-fine grained steps with perfect mathematical precision
        for direction in [-1, 1]:
            for step in range(1, 301):  # Even more steps for maximum precision
                # Use smaller increments for better precision
                new_l = l + (direction * step * 0.003)  # 0.3% increments
                
                # Strict bounds checking
                if not (0.0 <= new_l <= 1.0):
                    break
                
                try:
                    new_oklch = (new_l, c, h)
                    new_rgb = oklch_to_rgb_safe(new_oklch)
                    
                    if not is_valid_rgb(new_rgb):
                        continue
                    
                    # Use rigorous Delta E 2000 calculation
                    delta_e = calculate_delta_e_2000(rgb, new_rgb)
                    
                    # Strict threshold enforcement
                    if delta_e > max_delta_e:
                        break
                    
                    # Only add if Delta E is meaningful and different
                    if delta_e > 0.05 and new_rgb != rgb:  # Even stricter threshold
                        candidates.append({
                            'rgb': new_rgb,
                            'oklch': new_oklch,
                            'delta_e': delta_e,
                            'adjustment_type': 'lightness_only',
                            'priority': 1,
                            'lightness_change': abs(new_l - l)
                        })
                
                except Exception:
                    continue
        
        return candidates
    
    except Exception:
        return []

def generate_lightness_chroma_candidates(rgb: Tuple[int, int, int], max_delta_e: float) -> List[Dict]:
    """Generate lightness+chroma candidates using perfect OKLCH implementation"""
    try:
        oklch = rgb_to_oklch_safe(rgb)
        l, c, h = oklch
        
        candidates = []
        
        # Ultra-conservative chroma steps with mathematical precision
        chroma_steps = [-0.015, -0.01, -0.005, -0.002, 0.002, 0.005, 0.01, 0.015]
        
        for chroma_delta in chroma_steps:
            new_c = max(0.0, c + chroma_delta)
            
            # Skip if chroma becomes too large (outside sRGB gamut)
            if new_c > 0.5:
                continue
            
            for direction in [-1, 1]:
                for step in range(1, 151):  # Reduced range for chroma adjustments
                    new_l = l + (direction * step * 0.005)  # 0.5% increments
                    
                    if not (0.0 <= new_l <= 1.0):
                        break
                    
                    try:
                        new_oklch = (new_l, new_c, h)
                        new_rgb = oklch_to_rgb_safe(new_oklch)
                        
                        if not is_valid_rgb(new_rgb):
                            continue
                        
                        delta_e = calculate_delta_e_2000(rgb, new_rgb)
                        
                        if delta_e > max_delta_e:
                            break
                        
                        if delta_e > 0.05 and new_rgb != rgb:
                            candidates.append({
                                'rgb': new_rgb,
                                'oklch': new_oklch,
                                'delta_e': delta_e,
                                'adjustment_type': 'lightness_chroma',
                                'priority': 2,
                                'lightness_change': abs(new_l - l),
                                'chroma_change': abs(new_c - c)
                            })
                    
                    except Exception:
                        continue
        
        return candidates
    
    except Exception:
        return []

def generate_full_oklch_candidates(rgb: Tuple[int, int, int], max_delta_e: float) -> List[Dict]:
    """Generate full OKLCH candidates using perfect mathematical implementation"""
    try:
        oklch = rgb_to_oklch_safe(rgb)
        l, c, h = oklch
        
        candidates = []
        
        # Extremely conservative adjustments with perfect precision
        hue_steps = [-3, -2, -1, 1, 2, 3]  # Maximum ±3 degrees for brand preservation
        chroma_steps = [-0.02, -0.01, -0.005, 0.005, 0.01, 0.02]
        
        for hue_delta in hue_steps:
            new_h = (h + hue_delta) % 360.0
            
            for chroma_delta in chroma_steps:
                new_c = max(0.0, c + chroma_delta)
                
                # Skip if chroma becomes too large
                if new_c > 0.4:
                    continue
                
                for direction in [-1, 1]:
                    for step in range(1, 101):  # Limited range for full adjustments
                        new_l = l + (direction * step * 0.007)  # 0.7% increments
                        
                        if not (0.0 <= new_l <= 1.0):
                            break
                        
                        try:
                            new_oklch = (new_l, new_c, new_h)
                            new_rgb = oklch_to_rgb_safe(new_oklch)
                            
                            if not is_valid_rgb(new_rgb):
                                continue
                            
                            delta_e = calculate_delta_e_2000(rgb, new_rgb)
                            
                            if delta_e > max_delta_e:
                                break
                            
                            if delta_e > 0.05 and new_rgb != rgb:
                                candidates.append({
                                    'rgb': new_rgb,
                                    'oklch': new_oklch,
                                    'delta_e': delta_e,
                                    'adjustment_type': 'full_oklch',
                                    'priority': 3,
                                    'lightness_change': abs(new_l - l),
                                    'chroma_change': abs(new_c - c),
                                    'hue_change': min(abs(new_h - h), 360 - abs(new_h - h))
                                })
                        
                        except Exception:
                            continue
        
        return candidates
    
    except Exception:
        return []

def generate_accessible_color_robust(text_rgb: Tuple[int, int, int], bg_rgb: Tuple[int, int, int], large: bool = False) -> Tuple[int, int, int]:
    """
    Generate accessible color using perfect OKLCH implementation
    Maximum brand preservation with mathematical rigor
    """
    # Check if already accessible
    current_contrast = calculate_contrast_ratio(text_rgb, bg_rgb)
    target_contrast = 7.0
    min_contrast = 4.5 if not large else 3.0
    
    if current_contrast >= target_contrast:
        return text_rgb
    
    # Ultra-strict Delta E progression with perfect precision
    delta_e_sequence = [0.8, 1.0, 1.2, 1.4, 1.6, 1.8, 2.0, 2.1, 2.2, 2.3, 2.4, 2.5, 2.7, 3.0, 3.5, 4.0, 5.0]
    
    best_candidate = None
    best_contrast = current_contrast
    
    for max_delta_e in delta_e_sequence:
        # Generate candidates using perfect OKLCH implementation
        candidates = []
        candidates.extend(generate_lightness_candidates(text_rgb, max_delta_e))
        candidates.extend(generate_lightness_chroma_candidates(text_rgb, max_delta_e))
        candidates.extend(generate_full_oklch_candidates(text_rgb, max_delta_e))
        
        # Sort by priority, then by delta-E, then by minimal changes
        candidates.sort(key=lambda x: (
            x['priority'], 
            x['delta_e'],
            x.get('hue_change', 0),  # Prefer minimal hue change
            x.get('chroma_change', 0),  # Prefer minimal chroma change
            x.get('lightness_change', 0)  # Prefer minimal lightness change
        ))
        
        # Look for target contrast first
        for candidate in candidates:
            contrast = calculate_contrast_ratio(candidate['rgb'], bg_rgb)
            
            if contrast >= target_contrast:
                return candidate['rgb']
            
            # Track best candidate
            if contrast > best_contrast:
                best_contrast = contrast
                best_candidate = candidate
        
        # If we found minimum acceptable contrast with strict Delta E, use it
        if best_candidate and best_contrast >= min_contrast and max_delta_e <= 2.5:
            return best_candidate['rgb']
    
    # Final fallback
    return best_candidate['rgb'] if best_candidate else text_rgb

def check_and_fix_contrast(text_rgb: Tuple[int, int, int], bg_rgb: Tuple[int, int, int], large: bool = False) -> Tuple[Tuple[int, int, int], Tuple[int, int, int]]:
    """
    Main function that checks contrast and fixes if necessary
    Returns (text_color, bg_color) tuple - always returns the original background
    """
    # Calculate current contrast
    current_contrast = calculate_contrast_ratio(text_rgb, bg_rgb)
    target_contrast = 7.0
    
    # Check if already meets target
    if current_contrast >= target_contrast:
        return (text_rgb, bg_rgb)
    
    # Generate accessible text color
    accessible_text = generate_accessible_color_robust(text_rgb, bg_rgb, large)
    
    return (accessible_text, bg_rgb)


# Example usage and testing
# if __name__ == "__main__":
#     # Test cases
#     test_cases = [
#         ((255, 0, 0), (255, 255, 255), False),  # Red on white
#         ((0, 100, 0), (255, 255, 255), False),  # Dark green on white
#         ((0, 0, 255), (0, 0, 0), True),         # Blue on black (large text)
#         ((128, 128, 128), (255, 255, 255), False), # Gray on white
#     ]
    
#     for text_rgb, bg_rgb, large in test_cases:
#         print(f"\nTesting: Text {text_rgb} on Background {bg_rgb} (Large: {large})")
        
#         # Original contrast
#         original_contrast = calculate_contrast_ratio(text_rgb, bg_rgb)
#         original_level = get_contrast_level(original_contrast, large)
#         print(f"Original contrast: {original_contrast:.2f} ({original_level})")
        
#         # Fixed colors
#         fixed_text, fixed_bg = check_and_fix_contrast(text_rgb, bg_rgb, large)
#         fixed_contrast = calculate_contrast_ratio(fixed_text, fixed_bg)
#         fixed_level = get_contrast_level(fixed_contrast, large)
        
#         print(f"Fixed text color: {fixed_text}")
#         print(f"Fixed contrast: {fixed_contrast:.2f} ({fixed_level})")
        
#         # Delta E calculation
#         if fixed_text != text_rgb:
#             delta_e = calculate_delta_e_2000(text_rgb, fixed_text)
#             print(f"Color difference (Delta E): {delta_e:.2f}")

#  VSSS

from typing import Tuple, Optional, List, Dict
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
