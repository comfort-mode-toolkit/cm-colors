# CM-Colors Tone and Messaging Guide

## Core Principles

### Voice
- **Helpful neighbor** - You've been there, we've been there, here's the solution
- **Practical first** - Focus on what works, not how it works
- **Clear over clever** - Simple words always win

### Tone
- **Encouraging** - "You can do this" not "You should do this"
- **Direct** - Say what it does, simply
- **Confident** - We've solved this problem so you don't have to

## Messaging Framework

### Primary Value Proposition
"CM-Colors automatically fixes color contrast so your website is readable for everyone."

### Key Messages

**For the problem:**
- "Tired of guessing which colors work together?"
- "Spending too much time adjusting colors for readability?"
- "Want to make sure your website works for all visitors?"

**For the solution:**
- "Automatically find colors that look good and read well"
- "Fix all your colors at once, not one by one"
- "Get back to building features instead of adjusting colors"

**For the result:**
- "Colors that work for all your visitors"
- "More time for your actual work"
- "Confidence that your colors are readable"

## Documentation Language

### Do Use
- "readable" / "easy to read"
- "color contrast" 
- "fix colors" / "adjust colors"
- "works for everyone"
- "process multiple colors"
- "check readability"

### Don't Use
- WCAG, AA, AAA, compliance
- Contrast ratios, 4.5:1, 3:1
- Perceptual uniformity, Delta E, OKLCH
- Accessibility standards, guidelines
- Algorithms, optimization, color spaces

## API Documentation Examples

### Before (Technical)
```python
# Calculate WCAG contrast ratio and return compliance level
# Args: text_color, bg_color, large_text for AA/AAA thresholds
# Returns: "AAA", "AA", or "FAIL" based on 4.5:1 ratio
```

### After (Plain Language)
```python
# Check how readable text is on a background
# Args: text_color, bg_color, large_text for larger font sizes
# Returns: "premium", "standard", or "not_readable"
```

### Before (Technical)
```python
# Tune colors using OKLCH color space and Delta E optimization
# to achieve WCAG AA compliance with minimal perceptual difference
```

### After (Plain Language)  
```python
# Find a similar color that's easier to read
# Returns the adjusted color and whether it's now readable
```

## User Journey Messaging

### First Encounter
"CM-Colors fixes color contrast automatically. Process your entire website's colors in one go."

### During Use
"Checking your colors... found 12 that need adjustment. Fixing them now."

### After Processing  
"Fixed 12 colors. Your website is now more readable for all visitors."

### When Colors Can't Be Fixed
"Some colors couldn't be adjusted while keeping the same look. Consider using different colors for these."

## Error Messages

### Instead of:
"Unable to achieve sufficient contrast ratio while maintaining Delta E below 2.3"

### Use:
"Couldn't find a similar color that's easy to read. Try starting with different colors."

## Marketing Language

### Headlines
- "Color contrast that works for everyone"
- "Stop guessing, start building"
- "Automatically readable colors"

### Body Copy
"Spend less time adjusting colors and more time building features. CM-Colors automatically finds colors that look good and read well, so your website works for all visitors."

## Implementation Notes

### Always:
- Focus on the user's goal (readable website) not the method (color science)
- Use active voice ("fix colors" not "colors are fixed")
- Keep sentences under 25 words
- Explain what things do, not how they work

### Never:
- Assume knowledge of accessibility standards
- Use technical terms without plain language explanation
- Focus on implementation details over user benefits

## Example Scenarios

### CLI Output
```
Processing your colors...
✓ 15 colors already readable
✓ 8 colors adjusted for better readability
○ 2 colors need your attention

Your website colors are now more readable for everyone.
```

### Python Usage
```python
from cm_colors import CMColors

cm = CMColors()

# Check if colors are readable
readability = cm.check_readability("#666", "white")
print(readability)  # "not_readable"

# Fix colors automatically  
fixed_color, new_readability = cm.fix_color("#666", "white")
print(new_readability)  # "standard"

# Process many colors at once
color_pairs = [("#111", "#fff"), ("#666", "#f0f0f0")]
results = cm.fix_many_colors(color_pairs)
```

This guide ensures every piece of communication focuses on solving the user's problem in the simplest language possible, following Google's principle of "clear, accurate, and concise" documentation.