import math
from typing import Tuple, List, Dict, Optional

def rgb_to_linear(rgb_value: float) -> float:
    """Convert RGB value to linear RGB for contrast calculation"""
    normalized = rgb_value / 255.0
    if normalized <= 0.03928:
        return normalized / 12.92
    else:
        return pow((normalized + 0.055) / 1.055, 2.4)

def calculate_relative_luminance(rgb: Tuple[int, int, int]) -> float:
    """Calculate relative luminance according to WCAG"""
    r, g, b = rgb
    r_linear = rgb_to_linear(r)
    g_linear = rgb_to_linear(g)
    b_linear = rgb_to_linear(b)
    
    return 0.2126 * r_linear + 0.7152 * g_linear + 0.0722 * b_linear

def calculate_contrast_ratio(text_rgb: Tuple[int, int, int], bg_rgb: Tuple[int, int, int]) -> float:
    """Calculate WCAG contrast ratio between text and background colors"""
    text_luminance = calculate_relative_luminance(text_rgb)
    bg_luminance = calculate_relative_luminance(bg_rgb)
    
    lighter = max(text_luminance, bg_luminance)
    darker = min(text_luminance, bg_luminance)
    
    return (lighter + 0.05) / (darker + 0.05)

def get_contrast_level(contrast_ratio: float, large: bool = False) -> str:
    """Return WCAG contrast level based on ratio and text size"""
    if large:
        if contrast_ratio >= 4.5:
            return "AAA"
        elif contrast_ratio >= 3.0:
            return "AA"
        else:
            return "FAIL"
    else:
        if contrast_ratio >= 7.0:
            return "AAA"
        elif contrast_ratio >= 4.5:
            return "AA"
        else:
            return "FAIL"

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
            return pow(x, 1/3)
        else:
            return -pow(-x, 1/3)
    
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
            return 1.055 * pow(channel, 1.0/2.4) - 0.055
    
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

# REPLACE THE EXISTING calculate_delta_e_2000 FUNCTION WITH THIS RIGOROUS VERSION
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
            return pow(t, 1/3)
        else:
            return (7.787 * t) + (16/116)
    
    fx = lab_transform(x)
    fy = lab_transform(y)
    fz = lab_transform(z)
    
    # Calculate LAB values
    L = 116 * fy - 16
    a = 500 * (fx - fy)
    b = 200 * (fy - fz)
    
    return (L, a, b)

def rgb_to_lab(rgb: Tuple[int, int, int]) -> Tuple[float, float, float]:
    """Convert RGB directly to LAB"""
    xyz = rgb_to_xyz(rgb)
    return xyz_to_lab(xyz)

def calculate_delta_e_2000(rgb1: Tuple[int, int, int], rgb2: Tuple[int, int, int]) -> float:
    """
    Calculate Delta E 2000 color difference with full mathematical rigor
    Most perceptually accurate color difference formula
    """
    # Convert RGB to LAB
    L1, a1, b1 = rgb_to_lab(rgb1)
    L2, a2, b2 = rgb_to_lab(rgb2)
    
    # Calculate differences
    delta_L = L2 - L1
    delta_a = a2 - a1
    delta_b = b2 - b1
    
    # Calculate mean values
    L_mean = (L1 + L2) / 2
    
    # Calculate C (chroma) values
    C1 = math.sqrt(a1 * a1 + b1 * b1)
    C2 = math.sqrt(a2 * a2 + b2 * b2)
    C_mean = (C1 + C2) / 2
    
    # Calculate a' (adjusted a values)
    G = 0.5 * (1 - math.sqrt(pow(C_mean, 7) / (pow(C_mean, 7) + pow(25, 7))))
    a1_prime = a1 * (1 + G)
    a2_prime = a2 * (1 + G)
    
    # Calculate C' (adjusted chroma values)
    C1_prime = math.sqrt(a1_prime * a1_prime + b1 * b1)
    C2_prime = math.sqrt(a2_prime * a2_prime + b2 * b2)
    C_mean_prime = (C1_prime + C2_prime) / 2
    
    # Calculate h' (adjusted hue values)
    def calculate_hue_angle(a_prime, b):
        if a_prime == 0 and b == 0:
            return 0
        hue = math.atan2(b, a_prime) * 180 / math.pi
        return hue + 360 if hue < 0 else hue
    
    h1_prime = calculate_hue_angle(a1_prime, b1)
    h2_prime = calculate_hue_angle(a2_prime, b2)
    
    # Calculate delta h'
    delta_h_prime = 0
    if C1_prime == 0 or C2_prime == 0:
        delta_h_prime = 0
    elif abs(h2_prime - h1_prime) <= 180:
        delta_h_prime = h2_prime - h1_prime
    elif h2_prime - h1_prime > 180:
        delta_h_prime = h2_prime - h1_prime - 360
    else:
        delta_h_prime = h2_prime - h1_prime + 360
    
    # Calculate delta H' (capital H)
    delta_H_prime = 2 * math.sqrt(C1_prime * C2_prime) * math.sin(math.radians(delta_h_prime / 2))
    
    # Calculate delta C'
    delta_C_prime = C2_prime - C1_prime
    
    # Calculate H' mean
    H_mean_prime = 0
    if C1_prime == 0 or C2_prime == 0:
        H_mean_prime = h1_prime + h2_prime
    elif abs(h1_prime - h2_prime) <= 180:
        H_mean_prime = (h1_prime + h2_prime) / 2
    elif abs(h1_prime - h2_prime) > 180 and (h1_prime + h2_prime) < 360:
        H_mean_prime = (h1_prime + h2_prime + 360) / 2
    else:
        H_mean_prime = (h1_prime + h2_prime - 360) / 2
    
    # Calculate T (hue-dependent factor)
    T = (1 - 0.17 * math.cos(math.radians(H_mean_prime - 30)) +
         0.24 * math.cos(math.radians(2 * H_mean_prime)) +
         0.32 * math.cos(math.radians(3 * H_mean_prime + 6)) -
         0.20 * math.cos(math.radians(4 * H_mean_prime - 63)))
    
    # Calculate delta theta
    delta_theta = 30 * math.exp(-pow((H_mean_prime - 275) / 25, 2))
    
    # Calculate RC (rotation factor)
    RC = 2 * math.sqrt(pow(C_mean_prime, 7) / (pow(C_mean_prime, 7) + pow(25, 7)))
    
    # Calculate SL, SC, SH (weighting functions)
    SL = 1 + ((0.015 * pow(L_mean - 50, 2)) / math.sqrt(20 + pow(L_mean - 50, 2)))
    SC = 1 + 0.045 * C_mean_prime
    SH = 1 + 0.015 * C_mean_prime * T
    
    # Calculate RT (rotation term)
    RT = -math.sin(math.radians(2 * delta_theta)) * RC
    
    # Calculate final Delta E 2000
    # Using standard weighting factors (kL=1, kC=1, kH=1)
    kL = kC = kH = 1.0
    
    delta_E_2000 = math.sqrt(
        pow(delta_L / (kL * SL), 2) +
        pow(delta_C_prime / (kC * SC), 2) +
        pow(delta_H_prime / (kH * SH), 2) +
        RT * (delta_C_prime / (kC * SC)) * (delta_H_prime / (kH * SH))
    )
    
    return delta_E_2000

def is_valid_rgb(rgb: Tuple[int, int, int]) -> bool:
    """Check if RGB values are valid (0-255)"""
    return all(0 <= value <= 255 for value in rgb)

# REPLACE THE EXISTING CANDIDATE GENERATION FUNCTIONS WITH THESE ULTRA-STRICT VERSIONS
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

# REPLACE THE EXISTING generate_accessible_color_robust FUNCTION WITH THIS PERFECT VERSION
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


def oklch_color_distance(oklch1: Tuple[float, float, float], oklch2: Tuple[float, float, float]) -> float:
    """
    Calculate perceptual distance between two OKLCH colors
    More accurate than RGB distance for perceptual uniformity
    """
    L1, C1, H1 = oklch1
    L2, C2, H2 = oklch2
    
    # Convert to Cartesian coordinates for proper distance calculation
    a1 = C1 * math.cos(H1 * math.pi / 180)
    b1 = C1 * math.sin(H1 * math.pi / 180)
    a2 = C2 * math.cos(H2 * math.pi / 180)
    b2 = C2 * math.sin(H2 * math.pi / 180)
    
    # Euclidean distance in OKLab space
    delta_L = L2 - L1
    delta_a = a2 - a1
    delta_b = b2 - b1
    
    return math.sqrt(delta_L * delta_L + delta_a * delta_a + delta_b * delta_b)

def validate_oklch(oklch: Tuple[float, float, float]) -> bool:
    """
    Validate OKLCH values are within acceptable ranges
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
        if not validate_oklch(oklch):
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
        if not validate_oklch(oklch):
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

# Example usage and testing
if __name__ == "__main__":
    # Test cases
    test_cases = [
        ((255, 0, 0), (255, 255, 255), False),  # Red on white
        ((0, 100, 0), (255, 255, 255), False),  # Dark green on white
        ((0, 0, 255), (0, 0, 0), True),         # Blue on black (large text)
        ((128, 128, 128), (255, 255, 255), False), # Gray on white
    ]
    
    for text_rgb, bg_rgb, large in test_cases:
        print(f"\nTesting: Text {text_rgb} on Background {bg_rgb} (Large: {large})")
        
        # Original contrast
        original_contrast = calculate_contrast_ratio(text_rgb, bg_rgb)
        original_level = get_contrast_level(original_contrast, large)
        print(f"Original contrast: {original_contrast:.2f} ({original_level})")
        
        # Fixed colors
        fixed_text, fixed_bg = check_and_fix_contrast(text_rgb, bg_rgb, large)
        fixed_contrast = calculate_contrast_ratio(fixed_text, fixed_bg)
        fixed_level = get_contrast_level(fixed_contrast, large)
        
        print(f"Fixed text color: {fixed_text}")
        print(f"Fixed contrast: {fixed_contrast:.2f} ({fixed_level})")
        
        # Delta E calculation
        if fixed_text != text_rgb:
            delta_e = calculate_delta_e_2000(text_rgb, fixed_text)
            print(f"Color difference (Delta E): {delta_e:.2f}")
