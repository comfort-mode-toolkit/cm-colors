# CM-Colors 🎨✨

**You do your style, we make it accessible**
_(Our color wizard can work miracles, but even magic has limits - don't expect us to make neon yellow on white look good!)_

Ever picked perfect colors for your portfolio website, only to have someone tell you they can't read your text? Yeah, that's an accessibility problem, and it's more common than you think.
 
## What's This About?

**The Problem**: You spend hours choosing the perfect shade of dusty rose for your headings and soft lavender for your background. It looks _chef's kiss_ aesthetic... but people with visual impairments (or honestly, anyone trying to read it on their phone in sunlight) can't see it properly.

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

That's it. No complex setup, no configuration files, no PhD in color science required.

## The Magic One-Liner

This is literally all you need:

```python
from cm_colors import CMColors

cm = CMColors()

# Your original colors
text_color = 'rgb(95, 120, 135)'  # dark bluish gray text
bg_color = 'rgb(230, 240, 245)'    # pale blue

# ✨ The magic happens here ✨
tuned_text,is_accessible = cm.tune_colors(text_color, bg_color)

print(f"Original: {text_color}")
print(f"Tuned: {tuned_text}") #Output:- Tuned: rgb(83, 107, 122)
print(f"Is it accessible now?: {is_accessible}") #Always check to ensure it is true
```

That's it. Seriously.

## Real Examples (Because Seeing is Believing)

The % shows the change in contrast ratio

<img width="1189" height="1110" alt="an image showing side by side comparision of before and after change of colors" src="https://github.com/user-attachments/assets/4ce92c65-cd27-4bae-8756-bbbe9bf70a91"  />

<!--```python
# Example 1: Your aesthetic dusty rose
original = (199, 72, 59)    # Pretty dusty rose
fixed, _, level,_,_ = cm.tune_colors(original, (255, 255, 255))
print(f"Dusty rose {original} → {fixed} (now {level} compliant!)")

# Example 2: That trendy muted blue
original = (40, 117, 219)   # Trendy blue
fixed, _, level = cm.tune_colors(original, (240, 240, 240))
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

## Other Stuff You Can Do

Want to check if your colors are already good?

```python
# Check contrast ratio (higher = better readability)
ratio = cm.contrast_ratio((100, 100, 100), (255, 255, 255))
print(f"Contrast ratio: {ratio:.2f}")   #Output:- Contrast ratio: 5.92

# Check what level you're hitting
level = cm.wcag_level((100, 100, 100), (255, 255, 255))
print(f"Current level: {level}")  # "AA", "AAA", or "FAIL"  #Output:- Current level: AA
```

## Why This Matters

- **Legal stuff**: Many places require accessible websites by law
- **Good human stuff**: 1 in 12 people have some form of visual impairment
- **SEO**: Search engines care about accessibility
- **Professional points**: Shows you actually know what you're doing

## For the Color Science Geeks 🤓

If you want to dive deep into the mathematical wizardry behind this (Delta E 2000, OKLCH color spaces, gradient descent optimization), check out our [full technical documentation](https://github.com/comfort-mode-toolkit/cm-colors/blob/main/Technical%20README.md) where we get very nerdy about color perception and optimization algorithms.

## License

This project is licensed under GNU General Public License v3.0 — meaning it's free to use and modify, but you can't sell it as a closed-source product.

## Problems?

Found a bug or have questions? [Open an issue](https://github.com/comfort-mode-toolkit/cm-colors/issues) and we'll help you out.

---

**Making the web readable for everyone, one color tweak at a time** 🌈♿

_P.S. Your design professor will be impressed that you actually thought about accessibility_
