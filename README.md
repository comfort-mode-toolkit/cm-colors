# CM-Colors 🎨

**Mathematically Rigorous Accessible Color Science Library**

An open-source library for improving color accessibility while preserving brand identity. Built with research-grade mathematical precision and practical accessibility tools.

## ✨ What Makes CM-Colors Different

CM-Colors combines advanced color science with practical accessibility tools to help you improve color contrast while minimizing visual impact on your brand.

### 🔬 **Mathematical Foundation**
- **Delta E 2000**: Complete implementation for accurate perceptual color difference
- **OKLCH Color Space**: Official OKLab matrices for perceptually uniform adjustments
- **WCAG 2.1 Compliance**: Proper gamma correction and luminance calculations
- **Research-Grade Precision**: Citation-quality implementations of color science standards

### 🎨 **Brand-Conscious Approach**
- **Minimal Visual Impact**: Targets Delta E ≤ 2.0 when possible
- **Hierarchical Optimization**: Tries lightness → chroma → hue adjustments
- **Perceptual Uniformity**: Changes feel natural to human vision
- **Smart Fallbacks**: Guarantees at least WCAG AA compliance when physically possible

## 🚀 Quick Start

### Installation

```bash
pip install cm-colors

# For PDF report generation
pip install cm-colors[pdf]
```

### Simple Usage

```python
import cm_colors as cm

# Color space conversions with mathematical precision
oklch = cm.to_oklch((255, 0, 100))  # RGB to OKLCH
rgb = cm.to_rgb((0.6, 0.15, 350))   # OKLCH to RGB

# Accessibility analysis
ratio = cm.contrast_ratio((33, 33, 33), (255, 255, 255))
print(f"Contrast ratio: {ratio:.2f}")  # 12.63

# Improve colors for accessibility (when possible)
accessible_text, accessible_bg = cm.make_accessible((100, 100, 100), (120, 120, 120))

# Perceptual color difference (Delta E 2000)
difference = cm.color_distance((255, 0, 0), (255, 50, 50))
print(f"Delta E 2000: {difference:.2f}")  # < 2.0 = barely perceptible
```

### Design System Processing

```python
from cm_colors import process_brand_palette

# Define your brand palette
brand_palette = [
    {
        'text': {
            'color': (255, 0, 0),  # Your brand red
            'default': '--text-primary',
            'custom': '--brand-red-text'
        },
        'bg': {
            'color': (255, 255, 255),  # White background
            'default': '--bg-primary',
            'custom': '--brand-white-bg'
        },
        'type': 'normal'  # 'normal' or 'large' for WCAG text size
    }
]

# Process for accessibility - updates CSS and generates PDF report
result = process_brand_palette(brand_palette)
print(f"Improved {result['summary']['improved_pairs']} of {result['summary']['total_pairs']} color pairs")
if result['summary']['avg_delta_e']:
    print(f"Average brand preservation: Δε {result['summary']['avg_delta_e']:.1f}")
```

### Object-Oriented API

```python
from cm_colors import CMColors

cm = CMColors()

# Complete accessibility analysis
analysis = cm.analyze_contrast((33, 33, 33), (200, 200, 200))
print(analysis)
# {
#   'contrast_ratio': 5.74,
#   'wcag_level': 'AA', 
#   'passes_aa': True,
#   'passes_aaa': False,
#   'text_rgb': (33, 33, 33),
#   'bg_rgb': (200, 200, 200)
# }

# Generate accessible color variants
variants = cm.generate_palette_variants((120, 80, 200), 5)
for variant in variants:
    print(f"RGB: {variant['rgb']}, Lightness: {variant['lightness']:.2f}")
```

## 🔬 The Science Behind the Improvements

### OKLCH Color Space - Perceptually Uniform
```python
# Precise gamma correction following sRGB specification (IEC 61966-2-1)
def srgb_to_linear(channel):
    if channel <= 0.04045:
        return channel / 12.92  # Exact threshold from standard
    else:
        return pow((channel + 0.055) / 1.055, 2.4)  # Exact coefficients

# Official OKLab transformation matrices from Björn Ottosson's research
l_cone = 0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b
```

### Delta E 2000 - Human Vision Accuracy
```python
# Complete implementation including all correction factors
# Many libraries omit the complex T factor - we include everything
T = (1 - 0.17 * cos(H_mean_prime - 30) + 
     0.24 * cos(2 * H_mean_prime) + 
     0.32 * cos(3 * H_mean_prime + 6) - 
     0.20 * cos(4 * H_mean_prime - 63))
```

### WCAG Compliance - Exact Standards
```python
# Relative luminance with exact WCAG 2.1 coefficients for photopic vision
luminance = 0.2126 * r_linear + 0.7152 * g_linear + 0.0722 * b_linear
```

## 🎨 Smart Accessibility Improvements

### How We Minimize Brand Impact
CM-Colors uses a hierarchical approach, trying minimal changes first:

1. **Lightness-only adjustments** (minimal visual impact)
2. **Lightness + Chroma adjustments** (moderate impact)  
3. **Full OKLCH adjustments** (when necessary for compliance)

```python
# Ultra-fine increments to find the smallest acceptable change
for step in range(1, 301):
    new_l = l + (direction * step * 0.003)  # 0.3% increments
    if meets_contrast_requirement(new_color) and delta_e <= max_acceptable:
        return new_color  # Found a good balance
```

### What Delta E Values Mean
- **Δε < 1.0**: Changes invisible to human eye
- **Δε 1.0-2.0**: Barely perceptible (our preference when possible)
- **Δε 2.0-4.0**: Noticeable but often acceptable
- **Δε > 4.0**: Significant visual change

**Note**: We aim for minimal Delta E but prioritize accessibility compliance. Some color combinations (like white-on-white) cannot be made accessible while preserving the original colors.

## 📊 What You Get

### 1. **Updated CSS Variables**
Your stylesheets are updated with improved colors:
```css
.color-scheme {
  --brand-red-text: rgb(180, 0, 0);      /* Improved: Δε 1.8, Ratio: 4.52 */
  --brand-white-bg: rgb(255, 255, 255);  /* Already accessible */
}
```

### 2. **Detailed PDF Reports**
Comprehensive accessibility reports including:
- **Executive Summary**: Compliance status and improvement metrics
- **Before/After Analysis**: Visual comparisons with measurements
- **Brand Impact Scores**: Delta E values for each change
- **WCAG Compliance Details**: AA/AAA levels for all text sizes
- **Implementation Guide**: Exact color values and CSS updates
- **Recommendations**: Prioritized suggestions for further improvements

### 3. **Processing Results**
```python
{
    'processed_palette': [...],      # Detailed results for each color pair
    'css_updated': True,            # Success status
    'css_content': '...',           # Generated CSS content
    'report_path': 'reports/accessibility_report_20250105_143022.pdf',
    'summary': {
        'total_pairs': 5,
        'improved_pairs': 3,        # Some may already be accessible
        'failed_pairs': 0,          # Impossible cases (rare)
        'avg_delta_e': 1.8          # Average brand impact
    }
}
```

## 🔧 API Reference

### Core Functions

| Function | Description | Returns |
|----------|-------------|---------|
| `to_oklch(rgb)` | RGB to OKLCH conversion | `(0.627, 0.225, 29.7)` |
| `to_rgb(oklch)` | OKLCH to RGB conversion | `(255, 127, 80)` |
| `contrast_ratio(text, bg)` | WCAG contrast calculation | `4.52` |
| `make_accessible(text, bg)` | Improve colors when possible | `((180, 0, 0), (255, 255, 255))` |
| `color_distance(rgb1, rgb2)` | Delta E 2000 difference | `1.8` |
| `analyze_contrast(text, bg)` | Complete analysis | `{'wcag_level': 'AA', ...}` |

### Input Formats
```python
# RGB tuples
color = (255, 0, 100)

# Hex strings  
color = "#ff0064"

# CSS rgb() strings
color = "rgb(255, 0, 100)"

# OKLCH tuples (lightness, chroma, hue)
oklch = (0.6, 0.15, 350)
```

### Limitations & Considerations
- **Impossible Cases**: Some combinations (like white text on white background) cannot be made accessible while preserving the original intent
- **Subjective Perception**: Delta E 2.0 is "barely perceptible" for most people, but perception varies
- **Color Gamut**: Some OKLCH colors may be outside the sRGB gamut and will be clamped
- **Context Matters**: Accessibility requirements may vary based on your specific use case

## 🎯 Real-World Use Cases

### **Design Systems**
```python
# Audit entire design system
design_tokens = load_design_tokens()
improvements = []
for token in design_tokens:
    result = cm.analyze_contrast(token.text, token.bg)
    if not result['passes_aa']:
        improved = cm.make_accessible(token.text, token.bg)
        improvements.append({
            'token': token.name,
            'original_ratio': result['contrast_ratio'],
            'improved_colors': improved
        })
```

### **Brand Guidelines**
```python
# Generate accessible brand palette variants
brand_red = (205, 0, 50)
variants = cm.generate_palette_variants(brand_red, lightness_steps=9)
# Creates a range of lightness values for different use cases
```

### **Accessibility Auditing**
```python
# Batch process website colors
violations = []
for element in page_elements:
    ratio = cm.contrast_ratio(element.text, element.bg)
    if ratio < 4.5:  # WCAG AA threshold
        try:
            fixed = cm.make_accessible(element.text, element.bg)
            violations.append({'element': element, 'fix': fixed, 'original_ratio': ratio})
        except Exception:
            violations.append({'element': element, 'unfixable': True})
```

### **Educational & Research**
```python
# Study color perception differences
colors = [(255, 0, 0), (255, 20, 20), (255, 40, 40)]
for i, color1 in enumerate(colors):
    for color2 in colors[i+1:]:
        delta_e = cm.color_distance(color1, color2)
        perceptibility = "Imperceptible" if delta_e < 1 else "Barely perceptible" if delta_e < 2 else "Noticeable"
        print(f"Δε {delta_e:.2f}: {perceptibility}")
```

## 🤝 Contributing

We welcome contributions to advance accessible design! This project is **open source and will remain free forever**.

### 🔍 **Areas Where We Need Help**
- **🧪 Color Science**: Algorithm improvements and optimizations
- **🔌 Integrations**: Figma plugins, Sketch extensions, CLI tools
- **📚 Documentation**: Tutorials, examples, translations
- **🧪 Testing**: Edge cases and real-world validation
- **⚡ Performance**: Optimization for large design systems
- **🌐 Accessibility**: Making our tools more accessible

### 🚀 **Getting Started**
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/improvement`)
3. Make your changes with tests
4. Follow our code style (black, flake8)
5. Submit a pull request with clear description

## 📚 Installation & Requirements

### **System Requirements**
- Python 3.7+ (tested up to 3.11)
- Optional: ReportLab for PDF generation

### **Installation Options**
```bash
# Basic installation
pip install cm-colors

# With PDF reports  
pip install cm-colors[pdf]

# Development installation
pip install cm-colors[dev]

# From source
git clone https://github.com/comfort-mode-toolkit/cm-colors
cd cm-colors
pip install -e .
```

## 🙏 Acknowledgments

This project builds upon decades of color science research and accessibility advocacy:

- **Björn Ottosson** for the OKLab color space research
- **CIE Technical Committee** for Delta E 2000 standardization  
- **W3C Accessibility Working Group** for WCAG standards
- **Open source community** for scientific Python libraries
- **Accessibility advocates** worldwide for their tireless work

## 📜 License

**GNU v3 License** - This project is open source and will remain **free forever**. 

## 🔗 Links & Resources

- **📖 [Documentation](https://github.com/comfort-mode-toolkit/cm-colors#readme)**
- **🐛 [Bug Reports](https://github.com/comfort-mode-toolkit/cm-colors/issues)**
- **💻 [Source Code](https://github.com/comfort-mode-toolkit/cm-colors)**


---

**Making the web more accessible, one color at a time.** 🌈♿

*Built with mathematical precision for practical accessibility improvements.*