# """
# CM Colors - Mathematically Rigorous Accessible Color Science Library

# A comprehensive library for accessible color manipulation, WCAG compliance,
# and perceptually uniform color space transformations.

# Key Features:
# - OKLCH color space conversions with mathematical precision
# - Delta E 2000 perceptual color difference calculations
# - WCAG 2.1 contrast ratio compliance
# - Brand-preserving accessibility improvements
# - Comprehensive color palette processing
# """

# from .main import (
#     # Object-oriented interface
#     CMColors,
    
#     # Functional API
#     to_oklch,
#     to_rgb,
#     contrast_ratio,
#     make_accessible,
#     contrast_level,
#     color_distance,
#     is_valid_rgb,
#     relative_luminance,
#     analyze_contrast,
#     generate_palette_variants,
#     process_palette,
    
#     # Module info
#     __version__,
#     __author__,
#     __description__,
# )

# from .helper import (
#     rgb_to_oklch,
#     oklch_to_rgb,
#     calculate_contrast_ratio,
#     calculate_delta_e_2000,
#     get_contrast_level,
#     check_and_fix_contrast,
#     rgb_to_linear,
#     calculate_relative_luminance,
#     is_valid_rgb,
# )

# from .color_scheme import (
#     AccessibleColorProcessor,
#     process_brand_palette,
# )

# # Version info
# __version__ = "1.0.0"
# __author__ = "Lalitha A R"
# __description__ = "Mathematically rigorous accessible color science library"

# # All exports
# __all__ = [
#     # Main class
#     "CMColors",
    
#     # Functional API
#     "to_oklch",
#     "to_rgb", 
#     "contrast_ratio",
#     "make_accessible",
#     "contrast_level",
#     "color_distance",
#     "is_valid_rgb",
#     "relative_luminance",
#     "analyze_contrast",
#     "generate_palette_variants",
#     "process_palette",
    
#     # Core functions
#     "rgb_to_oklch",
#     "oklch_to_rgb",
#     "calculate_contrast_ratio", 
#     "calculate_delta_e_2000",
#     "get_contrast_level",
#     "check_and_fix_contrast",
#     "rgb_to_linear",
#     "calculate_relative_luminance",
    
#     # Advanced processing
#     "AccessibleColorProcessor",
#     "process_brand_palette",
# ]