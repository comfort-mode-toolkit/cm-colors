# CM-Colors 🎨

**Mathematically Rigorous Accessible Color Science Library**

An open-source Python library for improving color accessibility while preserving brand identity. Built with research-grade mathematical precision and practical accessibility tools.

## ✨ What Makes CM-Colors Different

CM-Colors combines advanced color science with practical accessibility tools to help you improve color contrast while minimizing visual impact on your brand.

### 🔬 **Mathematical Foundation**
- **Delta E 2000**: Complete implementation for accurate perceptual color difference
- **OKLCH Color Space**: Perceptually uniform color adjustments
- **WCAG 2.1 Compliance**: Proper gamma correction and luminance calculations
- **Research-Grade Precision**: Citation-quality implementations of color science standards

### 🎨 **Brand-Conscious Approach**
- **Minimal Visual Impact**: Targets Delta E ≤ 2.0 when possible
- **Hierarchical Optimization**: Binary search + gradient descent for optimal results
- **Perceptual Uniformity**: Changes feel natural to human vision
- **Smart Fallbacks**: Guarantees WCAG compliance when physically possible

## 🚀 Quick Start

### Installation

```bash
pip install cm-colors
```

### Simple Usage

```python
from main import CMColors

# Initialize the library
cm = CMColors()

# Check contrast ratio
ratio = cm.calculate_contrast((100, 100, 100), (255, 255, 255))
print(f"Contrast ratio: {ratio:.2f}")  # 2.65

# Get WCAG compliance level
level = cm.get_wcag_level(ratio)
print(f"WCAG Level: {level}")  # FAIL

# Fix accessibility automatically
accessible_text, bg = cm.ensure_accessible_colors((100, 100, 100), (255, 255, 255))
print(f"Improved text color: {accessible_text}")  # Much darker for better contrast

# Calculate perceptual color difference
delta_e = cm.calculate_delta_e_2000((255, 0, 0), (250, 5, 5))
print(f"Delta E 2000: {delta_e:.2f}")  # Small perceptual difference
```

### Object-Oriented API

```python
from main import CMColors

cm = CMColors()

# Complete contrast analysis
text_rgb = (100, 100, 100)
bg_rgb = (255, 255, 255)

contrast = cm.calculate_contrast(text_rgb, bg_rgb)
level = cm.get_wcag_level(contrast)
print(f"Contrast: {contrast:.2f}, Level: {level}")

# Ensure accessibility with minimal visual change
accessible_text, _ = cm.ensure_accessible_colors(text_rgb, bg_rgb)
print(f"Original: {text_rgb} → Accessible: {accessible_text}")

# Check the improvement
new_contrast = cm.calculate_contrast(accessible_text, bg_rgb)
new_level = cm.get_wcag_level(new_contrast)
print(f"New contrast: {new_contrast:.2f}, Level: {new_level}")
```

## 🔬 Color Space Conversions

### OKLCH - Perceptually Uniform Color Space
```python
cm = CMColors()

# Convert RGB to OKLCH for better manipulation
rgb_color = (123, 45, 200)  # Purple
oklch = cm.rgb_to_oklch(rgb_color)
print(f"OKLCH: L={oklch[0]:.3f}, C={oklch[1]:.3f}, H={oklch[2]:.1f}")

# Convert back to RGB
rgb_back = cm.oklch_to_rgb(oklch)
print(f"RGB back: {rgb_back}")  # Should match original

# OKLCH distance calculation
oklch1 = cm.rgb_to_oklch((255, 100, 0))   # Orange
oklch2 = cm.rgb_to_oklch((255, 150, 50))  # Lighter orange
distance = cm.calculate_oklch_distance(oklch1, oklch2)
print(f"OKLCH distance: {distance:.3f}")
```

### LAB Color Space
```python
# Convert to CIELAB for Delta E calculations
lab = cm.rgb_to_lab((255, 0, 0))
print(f"LAB: L={lab[0]:.3f}, a={lab[1]:.3f}, b={lab[2]:.3f}")
```

## 🎯 Smart Accessibility Improvements

### How We Minimize Brand Impact
CM-Colors uses optimized algorithms to find the smallest acceptable change:

1. **Binary Search on Lightness** - Fast convergence to optimal lightness
2. **Gradient Descent in OKLCH** - Fine-tuning lightness and chroma
3. **Delta E Constraints** - Ensures perceptual similarity when possible

```python
# The library automatically tries different approaches:
# 1. Lightness-only adjustments (minimal impact)
# 2. Lightness + chroma adjustments (moderate impact)  
# 3. Full optimization when necessary

accessible_color = cm.find_accessible_text_color((150, 150, 150), (255, 255, 255))
print(f"Optimized accessible color: {accessible_color}")
```

### WCAG Compliance Levels
```python
# Check compliance for different text sizes
normal_text_ratio = cm.calculate_contrast((75, 75, 75), (255, 255, 255))
large_text_level = cm.get_wcag_level(normal_text_ratio, large_text=True)
normal_text_level = cm.get_wcag_level(normal_text_ratio, large_text=False)

print(f"Large text: {large_text_level}")    # Might pass AA
print(f"Normal text: {normal_text_level}")  # Might fail
```

## 📊 Perceptual Color Difference

### Delta E 2000 - Human Vision Accuracy
```python
# Understanding perceptual differences
colors = [
    (255, 0, 0),    # Red
    (250, 5, 5),    # Slightly different red
    (255, 50, 50),  # Pink-ish red
    (200, 0, 0)     # Dark red
]

for i, color1 in enumerate(colors):
    for color2 in colors[i+1:]:
        delta_e = cm.calculate_delta_e_2000(color1, color2)
        if delta_e < 1.0:
            perception = "Invisible to human eye"
        elif delta_e < 2.3:
            perception = "Barely perceptible"
        elif delta_e < 5.0:
            perception = "Noticeable difference"
        else:
            perception = "Obvious difference"
        
        print(f"{color1} vs {color2}: Δε {delta_e:.2f} ({perception})")
```

## 🔧 API Reference

### Core Methods

| Method | Description | Returns |
|--------|-------------|---------|
| `calculate_contrast(text_rgb, bg_rgb)` | WCAG contrast ratio | `float` (1.0-21.0) |
| `get_wcag_level(ratio, large_text=False)` | WCAG compliance level | `str` ("AAA", "AA", "FAIL") |
| `ensure_accessible_colors(text, bg, large_text=False)` | Fix colors for accessibility | `Tuple[RGB, RGB]` |
| `find_accessible_text_color(text, bg, large_text=False)` | Generate accessible text color | `RGB tuple` |
| `rgb_to_oklch(rgb)` | RGB to OKLCH conversion | `(L, C, H)` tuple |
| `oklch_to_rgb(oklch)` | OKLCH to RGB conversion | `(R, G, B)` tuple |
| `rgb_to_lab(rgb)` | RGB to CIELAB conversion | `(L, a, b)` tuple |
| `calculate_delta_e_2000(rgb1, rgb2)` | Perceptual color difference | `float` |
| `calculate_oklch_distance(oklch1, oklch2)` | OKLCH space distance | `float` |

### Input Validation
All methods validate input parameters:
- **RGB values**: Must be integers 0-255
- **OKLCH values**: L (0-1), C (≥0), H (0-360)
- **Invalid inputs**: Raise `ValueError` with descriptive messages

## 🎯 Real-World Examples

### Design System Audit
```python
def audit_design_system(color_pairs):
    """Audit an entire design system for accessibility."""
    cm = CMColors()
    results = []
    
    for pair in color_pairs:
        text, bg = pair['text'], pair['background']
        contrast = cm.calculate_contrast(text, bg)
        level = cm.get_wcag_level(contrast)
        
        if level == "FAIL":
            accessible_text, _ = cm.ensure_accessible_colors(text, bg)
            delta_e = cm.calculate_delta_e_2000(text, accessible_text)
            
            results.append({
                'original': text,
                'accessible': accessible_text,
                'improvement': f"{contrast:.2f} → {cm.calculate_contrast(accessible_text, bg):.2f}",
                'visual_impact': f"Δε {delta_e:.2f}"
            })
    
    return results
```

### Brand Color Optimization
```python
def optimize_brand_palette(brand_colors, backgrounds):
    """Generate accessible variants of brand colors."""
    cm = CMColors()
    optimized_palette = {}
    
    for color_name, rgb in brand_colors.items():
        variants = {}
        for bg_name, bg_rgb in backgrounds.items():
            accessible = cm.find_accessible_text_color(rgb, bg_rgb)
            delta_e = cm.calculate_delta_e_2000(rgb, accessible)
            
            variants[bg_name] = {
                'color': accessible,
                'contrast': cm.calculate_contrast(accessible, bg_rgb),
                'brand_preservation': f"Δε {delta_e:.2f}"
            }
        
        optimized_palette[color_name] = variants
    
    return optimized_palette
```

## 🔬 Advanced Usage

### Internal Optimization Methods
For advanced users, the library exposes internal optimization methods:

```python
# Direct access to optimization algorithms
cm = CMColors()

# Binary search on lightness only
result = cm._binary_search_lightness(
    text_rgb=(100, 100, 100),
    bg_rgb=(255, 255, 255),
    delta_e_threshold=2.0,
    target_contrast=7.0
)

# Gradient descent optimization
result = cm._gradient_descent_oklch(
    text_rgb=(100, 100, 100),
    bg_rgb=(255, 255, 255),
    delta_e_threshold=2.0,
    target_contrast=7.0,
    max_iter=50
)
```

## 🚀 Installation & Setup

### Requirements
- Python 3.7+
- Dependencies defined in `helper.py` and `accessible_palatte.py`

### Project Structure
```
cm-colors/
├── main.py                 # Main CMColors class
├── helper.py              # Color space conversions, contrast calculations
├── accessible_palatte.py  # Optimization algorithms
└── README.md             # This file
```

### Development Setup
```bash
git clone https://github.com/your-username/cm-colors
cd cm-colors
python -m pip install -e .
```

## 🤝 Contributing

We welcome contributions! Areas where we need help:

- **🧪 Algorithm Optimization**: Improve performance of color space conversions
- **🔌 Integrations**: CLI tools, web APIs, design tool plugins  
- **📚 Documentation**: More examples and tutorials
- **🧪 Testing**: Edge cases and validation
- **🌐 Accessibility**: Making our tools more accessible

## 📜 License

**GNU General Public License v3.0** - This project is open source and will remain free forever.

## 🔗 Resources

- **📖 [Full Documentation](https://github.com/comfort-mode-toolkit/cm-colors#readme)**
- **🐛 [Report Issues](https://github.com/comfort-mode-toolkit/cm-colors/issues)**
- **💻 [Source Code](https://github.com/comfort-mode-toolkit/cm-colors)**

---

**Making the web more accessible, one color at a time.** 🌈♿

*Built with mathematical precision for practical accessibility improvements.*