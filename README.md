# CM-Colors 🎨✨

[![Python Tests](https://github.com/comfort-mode-toolkit/cm-colors/actions/workflows/python-test.yml/badge.svg)](https://github.com/comfort-mode-toolkit/cm-colors/actions/workflows/python-test.yml)
![GitHub stars](https://img.shields.io/github/stars/comfort-mode-toolkit/cm-colors)
![Downloads](https://img.shields.io/pypi/dm/cm-colors)
![License](https://img.shields.io/github/license/comfort-mode-toolkit/cm-colors)

**Automatic color contrast tuning for web accessibility**

CM-Colors adjusts text and background color pairs to meet WCAG accessibility standards while preserving visual aesthetics. Use it as a command-line tool to process CSS files or as a Python library for programmatic color manipulation.

The percentage shows the change in contrast ratio:

<img width="1189" height="1110" alt="an image showing side by side comparision of before and after change of colors" src="https://github.com/user-attachments/assets/4ce92c65-cd27-4bae-8756-bbbe9bf70a91"  />

## Overview

Web content requires sufficient color contrast between text and backgrounds for readability. WCAG defines minimum contrast ratios to ensure accessibility for users with visual impairments. CM-Colors automatically adjusts colors to meet these standards with minimal perceptual changes.

**Key features:**

- Automatic color contrast tuning to WCAG AA/AAA standards
- Command-line tool for batch CSS file processing
- Python API for programmatic color manipulation
- Support for all common color formats (hex, RGB/RGBA, HSL/HSLA, named colors)
- Perceptual color space algorithms for visually minimal adjustments

## Installation

```bash
pip install cm-colors
```

## CLI Usage

The `cm-colors` command processes CSS files and tunes color contrast automatically.

### Basic commands

Process a single CSS file:

```bash
cm-colors style.css
```

Process all CSS files in a directory:

```bash
cm-colors path/to/styles/
```

Process files in the current directory:

```bash
cm-colors .
```

### Options

`--default-bg COLOR`

Specifies the default background color when a CSS rule lacks an explicit background declaration. Accepts any valid color format.

Default: `white`

Example:

```bash
cm-colors styles.css --default-bg "#f5f5f5"
```

### Output

**Modified CSS files:**

The tool creates new files with `_cm` inserted before the extension:

- Input: `style.css`
- Output: `style_cm.css`

Original files remain unchanged. The output preserves formatting, comments, and structure.

**HTML report:**

When colors are tuned, the tool generates `cm_colors_report.html` in the current directory with:

- Visual before/after comparison for each change
- CSS selector and file location
- Original and updated WCAG levels
- Color swatches showing differences

**Console output:**

```
Processing 3 files...

Results:
✓ 12 already accessible
✓ 5 tuned
✗ 2 failed tuning

Could not tune 2 pairs:
  style.css -> .warning-badge
    Reason: Unable to achieve sufficient contrast
  layout.css -> .subtle-text
    Reason: Colors too similar to adjust

Report generated: /path/to/cm_colors_report.html
```

### How it works

1. Discovers all CSS files in the specified path
2. Parses CSS and extracts color declarations
3. Resolves CSS custom properties (variables)
4. Detects text/background color pairs per selector
5. Evaluates each pair against WCAG AA threshold (4.5:1)
6. Tunes colors below threshold using perceptual optimization
7. Generates modified CSS and HTML report

### Limitations

- Some color combinations cannot achieve sufficient contrast while maintaining visual similarity
- Color pair detection requires explicit `color` and `background-color` declarations
- CSS preprocessor syntax (SCSS, LESS) is not supported; process compiled CSS instead

## Python API

### ColorPair class

Check and tune color contrast programmatically:

```python
from cm_colors import ColorPair

# Create a color pair
pair = ColorPair("#5f7887", "rgb(230, 240, 245)")

# Check accessibility
print(f"Contrast ratio: {pair.contrast_ratio:.2f}")  # 3.89
print(f"WCAG level: {pair.wcag_level}")              # FAIL

# Tune colors automatically
tuned_text, is_accessible = pair.tune_colors()
print(f"Tuned color: {tuned_text}")                  # rgb(83, 107, 122)
print(f"Accessible: {is_accessible}")                # True
```

### Color class

Work with individual colors in any format:

```python
from cm_colors import Color

# Create colors from any format
color = Color("#c7483b")
rgba = Color("rgba(255, 0, 0, 0.5)")
hsl = Color("hsl(210, 100%, 50%)")
named = Color("cornflowerblue")

# Convert between formats
if color.is_valid:
    print(color.to_rgb_string())  # 'rgb(199, 72, 59)'
    print(color.to_hex())         # #c7483b
```

### Supported color formats

- **Hex:** `"#ff0000"`, `"#f00"`, `"ff0000"`
- **RGB/RGBA:** `(255, 0, 0)`, `"rgb(255, 0, 0)"`, `"rgba(255, 0, 0, 0.8)"`
- **HSL/HSLA:** `"hsl(120, 100%, 50%)"`, `"hsla(120, 100%, 50%, 0.9)"`
- **Named colors:** `"red"`, `"cornflowerblue"`, `"rebeccapurple"`

### Additional methods

```python
from cm_colors import ColorPair

pair = ColorPair("#646464", "#ffffff")

# Check contrast ratio
print(pair.contrast_ratio)  # 5.92

# Check WCAG compliance level
print(pair.wcag_level)  # AA, AAA, or FAIL

# Calculate perceptual difference (Delta E)
print(f"Delta E: {pair.delta_e:.2f}")

# Use different threshold for large text
pair_large = ColorPair("#767676", "white", large_text=True)
print(pair_large.wcag_level)  # AA (threshold: 3.0)
```

### Legacy API

The v0.1.x API remains supported:

```python
from cm_colors import CMColors

cm = CMColors()
ratio = cm.contrast_ratio("#646464", "white")
level = cm.wcag_level("rgb(100, 100, 100)", "#ffffff")
tuned, success = cm.tune_colors("cornflowerblue", "white")
```

## Documentation

For detailed usage, advanced features, and technical information, see the [full documentation](https://comfort-mode-toolkit.readthedocs.io/en/latest/cm_colors.html).

## Technical details

CM-Colors uses perceptual color space transformations (OKLCH) and Delta E 2000 for color difference calculations. The tuning algorithm employs gradient descent optimization to find accessible colors with minimal perceptual change. See the [Technical README](https://github.com/comfort-mode-toolkit/cm-colors/blob/main/Technical%20README.md) for implementation details.

## License

GNU General Public License v3.0

## Support

Report bugs or request features by [opening an issue](https://github.com/comfort-mode-toolkit/cm-colors/issues).

---

**Making web content accessible through automatic color contrast tuning**