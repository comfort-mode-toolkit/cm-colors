# CM-Colors 🎨✨

[![Python Tests](https://github.com/comfort-mode-toolkit/cm-colors/actions/workflows/python-test.yml/badge.svg)](https://github.com/comfort-mode-toolkit/cm-colors/actions/workflows/python-test.yml)
![PyPI - Version](https://img.shields.io/pypi/v/cm-colors)
![GitHub stars](https://img.shields.io/github/stars/comfort-mode-toolkit/cm-colors)
![Downloads](https://img.shields.io/pypi/dm/cm-colors)
![License](https://img.shields.io/github/license/comfort-mode-toolkit/cm-colors)

**Color contrast that works for everyone**

CM-Colors automatically finds colors that look good and read well, so your website works for all visitors. Use it to fix your CSS files or as a Python tool to adjust colors in your code.

The percentage shows how much easier the text is to read:

<img width="1189" height="1110" alt="an image showing side by side comparision of before and after change of colors" src="https://github.com/user-attachments/assets/4ce92c65-cd27-4bae-8756-bbbe9bf70a91"  />

## Overview

Tired of guessing which colors work together? CM-Colors fixes color contrast automatically. It finds similar colors that are easy to read, so you can get back to building features instead of adjusting colors.

**What it does:**

- Automatically makes your colors readable for everyone
- Fixes all your CSS files in one go
- Works with any color format you use (hex, RGB, named colors)
- Keeps your design looking great while making it accessible

## Installation

```bash
pip install cm-colors
```

## CLI Usage

The `cm-colors` command checks your CSS files and fixes colors that are hard to read.

### Basic commands

Fix a single CSS file:

```bash
cm-colors style.css
```

Fix all CSS files in a folder:

```bash
cm-colors path/to/styles/
```

Fix files in the current folder:

```bash
cm-colors .
```

### Options

`--default-bg COLOR`

Sets the background color to use if one isn't specified.

Default: `white`

Example:

```bash
cm-colors styles.css --default-bg "#f5f5f5"
```

### Output

**Updated CSS files:**

We create new files with `_cm` added to the name, so your original files stay safe.

- Input: `style.css`
- Output: `style_cm.css`

**HTML report:**

If we change any colors, we'll create a `cm_colors_report.html` file showing you exactly what changed and why.

**Console output:**

```
Processing 3 files...

Results:
✓ 12 colors already readable
✓ 5 colors adjusted for better readability
✗ 2 colors need your attention

Could not tune 2 pairs:
  style.css -> .warning-badge
    Reason: Couldn't find a similar color that's easy to read
  layout.css -> .subtle-text
    Reason: Try starting with different colors

Report generated: /path/to/cm_colors_report.html
```

## Python API

### ColorPair class

Check and fix colors in your Python code:

```python
from cm_colors import ColorPair

# Create a color pair
pair = ColorPair("#5f7887", "rgb(230, 240, 245)")

# Check if it's readable
print(f"Readable: {pair.is_readable}")  # False

# Fix colors automatically
tuned_text, success = pair.tune_colors()
print(f"New color: {tuned_text}")       # rgb(83, 107, 122)
print(f"Fixed: {success}")              # True
```

### Advanced Options

You can control how we fix your colors:

```python
# Use 'premium' mode to aim for the highest readability standard (AAA)
tuned_text, success = pair.tune_colors(premium=True)

# Choose how strict we should be about changing the color shade
# mode=0: Ultra Strict (changes color very little)
# mode=1: Default (best balance of readability and style)
# mode=2: Relaxed (allows more change to ensure readability)
tuned_text, success = pair.tune_colors(mode=2)
```

### Color class

Work with individual colors easily:

```python
from cm_colors import Color

# Create colors from any format
color = Color("#c7483b")

# Convert to other formats
if color.is_valid:
    print(color.to_rgb_string())  # 'rgb(199, 72, 59)'
    print(color.to_hex())         # #c7483b
```

## Documentation

For more details, see the [full documentation](https://comfort-mode-toolkit.readthedocs.io/en/latest/cm_colors/index.html).

## License

GNU General Public License v3.0

## Support

Found a problem? [Let us know](https://github.com/comfort-mode-toolkit/cm-colors/issues).

---

**Stop guessing, start building.**