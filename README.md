# CM-Colors 🎨✨

**You do your style, we make it accessible** 
*(Our color wizard can work miracles, but even magic has limits - don't expect us to make neon yellow on white look good!)*

Ever picked perfect colors for your portfolio website, only to have someone tell you they can't read your text? Yeah, that's an accessibility problem, and it's more common than you think.

> ⚠️ **Notice: Upcoming Breaking Changes**  
>  
> We’re currently restructuring `cm-colors`—main APIs are being renamed and improved for clarity and consistency.  
> During this process, contributions may break or need to be updated to match the new structure.  
> If you’re looking to contribute, please hold off for a bit or check in with us about compatibility.  
>
> Please check out the progress [here](https://github.com/comfort-mode-toolkit/cm-colors/issues/14). Please comment on the issue if you want to help or have questions!
> 
> We appreciate your interest and contributions—thanks for helping make `cm-colors` better!



## What's This About?

**The Problem**: You spend hours choosing the perfect shade of dusty rose for your headings and soft lavender for your background. It looks *chef's kiss* aesthetic... but people with visual impairments (or honestly, anyone trying to read it on their phone in sunlight) can't see it properly.

**The Solution**: CM-Colors takes your beautiful color choices and makes tiny, barely-noticeable tweaks so everyone can read your content. We're talking changes so small you won't even notice them, but your accessibility score will love you.

## What Does "Accessible" Even Mean?

Simple version: There needs to be enough contrast between your text and background so people can actually read it. 

- **Good contrast** = Easy to read for everyone
- **Bad contrast** = Squinting, headaches, and people bouncing off your site

The web has official rules called WCAG (don't worry about what it stands for) that say exactly how much contrast you need. Most of the time, you just want to hit "AA" level - that's the sweet spot.

## Installation

```bash
pip install cm-colors
```

## The Magic One-Liner

This is literally all you need:

```python
from cm_colors import CMColors

cm = CMColors()

# Your original colors
text_color = (95, 120, 135)  # dark bluish gray text
bg_color = (230, 240, 245)    # pale blue

# ✨ The magic happens here ✨
accessible_text,_,level,_,_ = cm.ensure_accessible_colors(text_color, bg_color)

print(f"Original: {text_color}")
print(f"Accessible: {accessible_text}")
print(f"Now it passes: {level} level!")
```

That's it. Seriously.

## Real Examples (Because Seeing is Believing)
The % shows the change in contrast ratio

<img width="1189" height="1110" alt="an image showing side by side comparision of before and after change of colors" src="https://github.com/user-attachments/assets/4ce92c65-cd27-4bae-8756-bbbe9bf70a91"  />



<!--```python
# Example 1: Your aesthetic dusty rose
original = (199, 72, 59)    # Pretty dusty rose
fixed, _, level,_,_ = cm.ensure_accessible_colors(original, (255, 255, 255))
print(f"Dusty rose {original} → {fixed} (now {level} compliant!)")

# Example 2: That trendy muted blue
original = (40, 117, 219)   # Trendy blue
fixed, _, level = cm.ensure_accessible_colors(original, (240, 240, 240))
print(f"Trendy blue {original} → {fixed} (still looks trendy, now readable!)")
```-->

## Common Questions

**Q: Will it ruin my carefully chosen aesthetic?**
A: Nope! We make the smallest possible changes. Most of the time you literally can't tell the difference.

**Q: What if my colors are already accessible?**
A: We'll tell you they're perfect and leave them alone.

**Q: What if I picked terrible colors?**
A: We'll try our best, but if you chose neon yellow on white... even wizards have limits. Pick better starting colors! 😅

**Q: Do I need to understand color science?**
A: Not at all! That's why this library exists.

## For Your Portfolio/Project

Here's a simple function you can drop into any project:

```python
def make_my_colors_accessible(text_rgb, background_rgb):
    """
    Takes your color choices and makes them accessible.
    Returns the fixed colors ready to use in CSS.
    """
    from cm_colors import CMColors
    
    cm = CMColors()
    accessible_text, bg, level = cm.ensure_accessible_colors(text_rgb, background_rgb)
    
    # Convert to CSS format
    css_text = f"rgb({accessible_text[0]}, {accessible_text[1]}, {accessible_text[2]})"
    css_bg = f"rgb({bg[0]}, {bg[1]}, {bg[2]})"
    
    return {
        'text_color': css_text,
        'background_color': css_bg,
        'accessibility_level': level,
        'ready_for_css': True
    }

# Use it like this:
result = make_my_colors_accessible((120, 80, 200), (255, 255, 255))
print(f"Use this in your CSS: color: {result['text_color']};")
```

## Other Stuff You Can Do

Want to check if your colors are already good?

```python
# Check contrast ratio (higher = better readability)
ratio = cm.calculate_contrast((100, 100, 100), (255, 255, 255))
print(f"Contrast ratio: {ratio:.2f}")

# Check what level you're hitting
level = cm.get_wcag_level((100, 100, 100), (255, 255, 255))
print(f"Current level: {level}")  # "AA", "AAA", or "FAIL"
```

## Why This Matters

- **Legal stuff**: Many places require accessible websites by law
- **Good human stuff**: 1 in 12 people have some form of visual impairment
- **SEO**: Search engines care about accessibility
- **Professional points**: Shows you actually know what you're doing

## For the Color Science Geeks 🤓

If you want to dive deep into the mathematical wizardry behind this (Delta E 2000, OKLCH color spaces, gradient descent optimization), check out our [full technical documentation](https://github.com/comfort-mode-toolkit/cm-colors/blob/main/Technical%20README.md) where we get very nerdy about color perception and optimization algorithms.

## Installation & Setup

```bash
pip install cm-colors
```

That's it. No complex setup, no configuration files, no PhD in color science required.

## License

GNU v3 - Use it however you want except to put a product label on and sell it - it's free forever!

## Problems?

Found a bug or have questions? [Open an issue](https://github.com/comfort-mode-toolkit/cm-colors/issues) and we'll help you out.

---

**Making the web readable for everyone, one color tweak at a time** 🌈♿

*P.S. Your design professor will be impressed that you actually thought about accessibility*
