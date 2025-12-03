# CM-Colors 🎨✨

[![Python Tests](https://github.com/comfort-mode-toolkit/cm-colors/actions/workflows/python-test.yml/badge.svg)](https://github.com/comfort-mode-toolkit/cm-colors/actions/workflows/python-test.yml)
![PyPI - Version](https://img.shields.io/pypi/v/cm-colors)
![Downloads](https://img.shields.io/pypi/dm/cm-colors)
![License](https://img.shields.io/github/license/comfort-mode-toolkit/cm-colors)

**Color contrast that works for everyone**

CM-Colors automatically fixes your colors so they are easy to read. It finds similar colors that work for everyone, so you don't have to guess.

> "Fortunately, there's a tool that's just come out that's going to change your life: CM-Colors. You give it your colors, and it automatically adjusts them so they're accessible, all while changing the shades as little as possible to keep your design intact."
>
> — [Korben.info](https://korben.info/cm-colors-accessibilite-contraste-couleurs-wcag.html)


The percentage shows how much easier the text is to read:

<img width="1189" height="1110" alt="an image showing side by side comparision of before and after change of colors" src="https://github.com/user-attachments/assets/4ce92c65-cd27-4bae-8756-bbbe9bf70a91"  />

## Overview

Spending too much time adjusting colors? CM-Colors handles it for you. It automatically finds colors that look like your brand but are readable for all your visitors.

**What it does:**

- **Fixes colors automatically**: No more manual tweaking.
- **Works everywhere**: Fix Python code or CSS files.
- **Keeps your style**: Changes colors as little as possible.
- **Saves you time**: Fix your whole project in seconds.

## Installation

```bash
pip install cm-colors
```

## Quick Start

### Fix a single color

```python
from cm_colors import ColorPair

# Your colors
pair = ColorPair("#999999", "#ffffff")

# Fix them and preview in the terminal
fixed_color, success = pair.make_readable(show=True)

print(f"Use {fixed_color} instead of #999999")
# Output: Use #8e8e8e instead of #999999
```

### Fix many colors at once

```python
from cm_colors import make_readable_bulk

my_colors = [
    ("#777", "#fff"),
    ("#888", "#000"),
]

results = make_readable_bulk(my_colors)

for color, status in results:
    print(f"{color} is {status}")
```

### Fix CSS files

Run this in your terminal to fix all colors in a CSS file:

```bash
cm-colors styles.css
```

This creates `styles_cm.css` with readable colors which you can preview before you modify your original css

## Documentation

For more details, see the [full documentation](https://cm-colors.readthedocs.io/en/latest/).

## License

GNU General Public License v3.0

## Support

Found a problem? [Let us know](https://github.com/comfort-mode-toolkit/cm-colors/issues).

---

**Stop guessing, start building.**
