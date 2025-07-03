# CM-Colors 🎨

**Accessible Color Management for Design Systems**

A powerful, mathematically rigorous library for generating accessible color palettes while preserving brand identity. Part of the CM-Hub ecosystem for comprehensive design system management.

## ✨ What It Does

CM-Colors helps you automatically fix color accessibility issues in your design system without compromising your brand. It uses advanced color science (Delta E 2000, OKLCH color space) to make minimal, perceptually-guided adjustments that ensure WCAG compliance while keeping your colors recognizably yours.

## 🎯 Key Features

- **🔬 Mathematically Rigorous**: Full Delta E 2000 implementation with perfect OKLCH color space conversions
- **🎨 Brand-First Approach**: Ultra-strict Delta E ≤ 2.0 targeting to minimize visual impact
- **♿ WCAG Compliance**: Automatic AA/AAA level accessibility improvements
- **🔄 Smart Processing**: Hierarchical optimization (lightness → chroma → hue) for natural-looking results
- **📊 Comprehensive Reports**: Professional PDF reports with detailed analysis
- **🔧 CSS Integration**: Surgical updates to your existing stylesheets
- **⚡ Batch Processing**: Handle entire design systems efficiently

## 🚀 Quick Start

```bash
pip install cm-colors
```

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
        'type': 'normal'
    }
]

# Process for accessibility
result = process_brand_palette(brand_palette)

# Your cm-vars.css is automatically updated with accessible colors
# A detailed PDF report is generated in ./reports/
```

## 📋 Comparison with Existing Tools

| Feature | CM-Colors | Stark | Colour Contrast Analyser | Adobe Color | colour-science | colorjs.io |
|---------|-----------|-------|---------------------------|-------------|----------------|-------------|
| **Automated Color Fixing** | ✅ Yes | ❌ No | ❌ No | ❌ No | ❌ No | ❌ No |
| **Brand Preservation** | ✅ Delta E ≤ 2.0 | ❌ No | ❌ No | ❌ No | ❌ No | ❌ No |
| **WCAG Compliance** | ✅ AA/AAA | ✅ Basic | ✅ Basic | ✅ Basic | ❌ No | ❌ No |
| **Batch Processing** | ✅ Yes | ❌ Manual | ❌ Manual | ❌ Manual | ❌ No | ❌ No |
| **Delta E 2000** | ✅ Full | ❌ No | ❌ No | ❌ Basic | ✅ Yes | ✅ Yes |
| **OKLCH Color Space** | ✅ Perfect | ❌ No | ❌ No | ❌ No | ✅ Yes | ✅ Yes |
| **CSS Integration** | ✅ Surgical | ❌ No | ❌ No | ❌ No | ❌ No | ❌ No |
| **Professional Reports** | ✅ PDF | ❌ Basic | ❌ Basic | ❌ No | ❌ No | ❌ No |
| **Open Source** | ✅ Free | ❌ Paid | ✅ Free | ❌ Paid | ✅ Free | ✅ Free |
| **Design System Focus** | ✅ Yes | ❌ No | ❌ No | ❌ No | ❌ No | ❌ No |

## 🔧 Installation & Setup

### Requirements
```bash
pip install reportlab>=3.6.0
```

### Basic Usage
```python
from cm_colors import AccessibleColorProcessor

# Initialize processor
processor = AccessibleColorProcessor(
    css_file_path="your-styles.css",
    report_dir="accessibility-reports"
)

# Process your colors
results = processor.process_brand_palette(your_palette)
```

## 📁 Input Format

```python
brand_palette = [
    {
        'text': {
            'color': (255, 0, 0),  # RGB tuple, hex string, or "rgb(r,g,b)"
            'default': '--text-primary',    # Default CSS variable name
            'custom': '--brand-red-text'    # Custom CSS variable (optional)
        },
        'bg': {
            'color': (255, 255, 255),
            'default': '--bg-primary',
            'custom': '--brand-white-bg'
        },
        'type': 'normal'  # 'normal' or 'large' for WCAG text size
    }
]
```

## 📊 What You Get

### 1. **Updated CSS**
Your `cm-vars.css` file is surgically updated with accessible colors:
```css
.color-scheme {
  --brand-red-text: rgb(180, 0, 0);      /* Accessible version */
  --brand-white-bg: rgb(255, 255, 255);  /* Unchanged */
}
```

### 2. **Detailed PDF Report**
Professional accessibility report with:
- Executive summary with key metrics
- Before/after color analysis
- WCAG compliance levels
- Brand preservation scores (Delta E)
- Technical implementation details
- Actionable recommendations

### 3. **Processing Results**
```python
{
    'processed_palette': [...],      # Detailed results
    'css_updated': True,            # Success status
    'report_path': 'reports/...',   # PDF location
    'summary': {
        'total_pairs': 5,
        'improved_pairs': 3,
        'avg_delta_e': 1.8          # Excellent brand preservation
    }
}
```

## 🎯 Part of CM-Hub Ecosystem

CM-Colors is designed to integrate seamlessly with the CM-Hub central design system management platform. While it works perfectly as a standalone tool, it becomes even more powerful when used as part of the complete CM-Hub ecosystem for:

- **Centralized Design Tokens**: Manage colors across all brand touchpoints
- **Automated Workflows**: Integrate accessibility checks into your design process
- **Team Collaboration**: Share accessible color palettes across design and development teams
- **Brand Governance**: Ensure consistent, accessible color usage organization-wide

## 🤝 Contributing

We welcome contributions! This project aims to make accessibility tools available to everyone, regardless of budget or technical expertise.

### Areas where we'd love help:
- **Color Science**: Improvements to our algorithms
- **Integrations**: Figma plugins, Sketch extensions, CLI tools
- **Documentation**: Tutorials, examples, translations
- **Testing**: More comprehensive test coverage
- **Performance**: Optimization for large design systems

### Getting Started
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📚 How It Works

### The Science Behind It
1. **Color Analysis**: Convert colors to perceptually uniform OKLCH space
2. **Accessibility Check**: Calculate WCAG contrast ratios
3. **Smart Optimization**: Use hierarchical adjustments (lightness → chroma → hue)
4. **Brand Preservation**: Minimize perceptual difference using Delta E 2000
5. **Quality Control**: Validate all results meet accessibility standards

### Why It's Different
- **Perceptually Accurate**: Uses the most advanced color difference formulas
- **Brand-Aware**: Designed specifically to preserve brand identity
- **Practical**: Generates production-ready CSS and comprehensive reports
- **Accessible**: Free and open source for everyone

## 🌟 Use Cases

- **Design Systems**: Ensure your entire color palette is accessible
- **Brand Compliance**: Maintain brand colors while meeting accessibility standards
- **Agency Work**: Deliver accessible designs without compromising creative vision
- **Educational**: Learn about color accessibility with real-world examples
- **Auditing**: Analyze existing websites for accessibility improvements

## 📄 License

This project is open source and will remain free forever. Forking for commercialization is prohibited. All contributions are welcome under our [Code of Conduct](https://github.com/comfort-mode-toolkit/cm-hub?tab=coc-ov-file)

## 🙏 Acknowledgments

This project builds upon decades of color science research and the incredible work of accessibility advocates worldwide. Special thanks to the contributors of color science libraries and WCAG standards that make this possible.

Special Thanks to Mr.Krishna

---

**Making the web more accessible, one color at a time.** 🌈♿

*For support, questions, or just to say hi, feel free to open an issue or start a discussion!*