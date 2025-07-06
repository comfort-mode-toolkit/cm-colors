from processor import process_config
from color_scheme import process_brand_palette
from helper import (
    rgb_to_oklch, oklch_to_rgb,
    calculate_contrast_ratio, calculate_delta_e_2000,
    get_contrast_level, check_and_fix_contrast,
    is_valid_rgb, rgb_to_linear, calculate_relative_luminance
)

def main(config, cm=False):
    """
    Main entry point - switches between CM integration and standalone mode
    
    Args:
        config: Configuration for CM integration as a part of cm-core library, or None for standalone
        cm: Boolean flag for CM integration mode
        
    Returns:
        bool: Success status for CM mode
        dict: Standalone API exports for standalone mode
    """
    if cm:
        # CM integration mode - existing functionality
        brand_palette = process_brand_palette(config, "cm-vars.css", 'reports')
        return True if brand_palette else False
    else:
        # Standalone mode - export core functions
        return get_standalone_api()

def get_standalone_api():
    """
    Returns the standalone API dictionary with all core functions
    """
    return {
        # Core color space conversions
        'to_oklch': rgb_to_oklch,
        'to_rgb': oklch_to_rgb,
        
        # Accessibility functions
        'contrast_ratio': calculate_contrast_ratio,
        'make_accessible': check_and_fix_contrast,
        'contrast_level': get_contrast_level,
        
        # Perceptual color difference
        'color_distance': calculate_delta_e_2000,
        
        # Utility functions
        'is_valid_rgb': is_valid_rgb,
        'relative_luminance': calculate_relative_luminance,
        'linear_rgb': rgb_to_linear,
        
        # Advanced processing
        'process_palette': process_brand_palette,
        
        # Version and info
        'version': '1.0.0',
        'description': 'Mathematically rigorous accessible color science library'
    }

# Standalone usage examples and API
class CMColors:
    """
    Clean object-oriented interface for standalone usage
    """
    
    def __init__(self):
        self.version = "1.0.0"
        self.description = "Mathematically rigorous accessible color science library"
    
    # Color space conversions
    def to_oklch(self, rgb):
        """Convert RGB to OKLCH color space"""
        return rgb_to_oklch(rgb)
    
    def to_rgb(self, oklch):
        """Convert OKLCH to RGB color space"""
        return oklch_to_rgb(oklch)
    
    # Accessibility functions
    def contrast_ratio(self, text_rgb, bg_rgb):
        """Calculate WCAG contrast ratio between text and background"""
        return calculate_contrast_ratio(text_rgb, bg_rgb)
    
    def make_accessible(self, text_rgb, bg_rgb, large=False):
        """Generate accessible color variants with minimal brand impact"""
        return check_and_fix_contrast(text_rgb, bg_rgb, large)
    
    def contrast_level(self, contrast_ratio, large=False):
        """Get WCAG compliance level (AA, AAA, or FAIL)"""
        return get_contrast_level(contrast_ratio, large)
    
    # Perceptual color difference
    def color_distance(self, rgb1, rgb2):
        """Calculate perceptual color difference using Delta E 2000"""
        return calculate_delta_e_2000(rgb1, rgb2)
    
    # Utility functions
    def is_valid_rgb(self, rgb):
        """Validate RGB color tuple"""
        return is_valid_rgb(rgb)
    
    def relative_luminance(self, rgb):
        """Calculate relative luminance for WCAG calculations"""
        return calculate_relative_luminance(rgb)
    
    # Batch processing
    def process_palette(self, config, css_file=None, report_dir=None):
        """Process entire brand palette for accessibility"""
        css_file = css_file or "cm-vars.css"
        report_dir = report_dir or "reports"
        return process_brand_palette(config, css_file, report_dir)
    
    # Convenience methods
    def analyze_contrast(self, text_rgb, bg_rgb, large=False):
        """Complete contrast analysis with recommendations"""
        ratio = self.contrast_ratio(text_rgb, bg_rgb)
        level = self.contrast_level(ratio, large)
        
        result = {
            'contrast_ratio': ratio,
            'wcag_level': level,
            'passes_aa': ratio >= (3.0 if large else 4.5),
            'passes_aaa': ratio >= (4.5 if large else 7.0),
            'text_rgb': text_rgb,
            'bg_rgb': bg_rgb
        }
        
        if result['wcag_level'] == 'FAIL':
            accessible_text, accessible_bg = self.make_accessible(text_rgb, bg_rgb, large)
            result['suggestions'] = {
                'accessible_text': accessible_text,
                'accessible_bg': accessible_bg,
                'new_ratio': self.contrast_ratio(accessible_text, accessible_bg)
            }
        
        return result
    
    def generate_palette_variants(self, base_rgb, lightness_steps=5):
        """Generate accessible lightness variants of a base color"""
        oklch = self.to_oklch(base_rgb)
        variants = []
        
        for i in range(lightness_steps):
            # Generate evenly distributed lightness values
            lightness = 0.1 + (0.8 * i / (lightness_steps - 1))  # 0.1 to 0.9
            variant_oklch = (lightness, oklch[1], oklch[2])
            variant_rgb = self.to_rgb(variant_oklch)
            
            variants.append({
                'rgb': variant_rgb,
                'oklch': variant_oklch,
                'lightness': lightness,
                'hex': f"#{variant_rgb[0]:02x}{variant_rgb[1]:02x}{variant_rgb[2]:02x}"
            })
        
        return variants

# Create default instance for functional API
_cm_colors = CMColors()

# Functional API exports (for simple imports)
to_oklch = _cm_colors.to_oklch
to_rgb = _cm_colors.to_rgb
contrast_ratio = _cm_colors.contrast_ratio
make_accessible = _cm_colors.make_accessible
contrast_level = _cm_colors.contrast_level
color_distance = _cm_colors.color_distance
is_valid_rgb = _cm_colors.is_valid_rgb
relative_luminance = _cm_colors.relative_luminance
analyze_contrast = _cm_colors.analyze_contrast
generate_palette_variants = _cm_colors.generate_palette_variants
process_palette = _cm_colors.process_palette

# Module info
__version__ = "1.0.0"
__author__ = "CM Colors"
__description__ = "Mathematically rigorous accessible color science library"

# ...existing code...

# Add this at the bottom for package testing
if __name__ == "__main__":
    print("=== CM Colors Standalone Demo ===\n")
    
    # Example 1: Basic color space conversion
    print("1. Color Space Conversion:")
    brand_red = (255, 0, 100)
    oklch = to_oklch(brand_red)
    back_to_rgb = to_rgb(oklch)
    print(f"   RGB {brand_red} → OKLCH {oklch}")
    print(f"   OKLCH → RGB {back_to_rgb} (round-trip test)")
    
    # Example 2: Accessibility analysis
    print("\n2. Accessibility Analysis:")
    text_color = (33, 33, 33)  # Dark gray
    bg_color = (200, 200, 200)  # Light gray
    
    analysis = analyze_contrast(text_color, bg_color)
    print(f"   Text: {text_color}, Background: {bg_color}")
    print(f"   Contrast Ratio: {analysis['contrast_ratio']:.2f}")
    print(f"   WCAG Level: {analysis['wcag_level']}")
    print(f"   Passes AA: {analysis['passes_aa']}")
    
    if 'suggestions' in analysis:
        print(f"   Suggested accessible text: {analysis['suggestions']['accessible_text']}")
        print(f"   New contrast ratio: {analysis['suggestions']['new_ratio']:.2f}")
    
    # Example 3: Color distance
    print("\n3. Perceptual Color Distance:")
    color1 = (255, 0, 0)    # Red
    color2 = (255, 50, 50)  # Slightly different red
    distance = color_distance(color1, color2)
    print(f"   Color 1: {color1}")
    print(f"   Color 2: {color2}")
    print(f"   Delta E 2000: {distance:.2f} (< 2.0 = barely perceptible)")
    
    print("\n=== Demo Complete ===")
    print("\nTry: pip install cm-colors")
    print("Then: import cm_colors as cm")