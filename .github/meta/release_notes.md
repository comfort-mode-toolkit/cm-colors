# CM-Colors v0.4.1 Release Notes

### Fixing the details
We smoothed out a few edges in our Python tools. The advanced options for tuning colors now work exactly as expected, and we improved how we handle large text when you're aiming for the highest standards.

# CM-Colors v0.4.2 Release Notes

### More control at your fingertips
You can now choose exactly how you want your colors to be tuned, right from the command line.

- **Choose your mode**: Use `--mode` to decide if you want us to be strict or relaxed when adjusting your colors.
- **Go Premium**: Use `--premium` to aim for the very highest readability standards.

# CM-Colors v0.4.3 Release Notes

### See your changes right away

- **Preview in your terminal**: Add `show=True` when tuning colors to see a before-and-after comparison right in your terminal.
- **Save detailed reports**: Use `html=True` to generate a visual report showing exactly what changed and why.

We also made some improvements under the hood. Now when we fix your colors, we keep them in the same format you gave us—if you use hex codes, you get hex codes back. If you use RGB, you get RGB back. This makes it easier to work with the output and keeps your code consistent.

# CM-Colors v0.5.0 Release Notes

<!-- All breaking changes, removed any function that someone who wants to fix color contrast wouldn't use
     + All tests updated to match the API changes
     + All docstrings and function names on the public facing API's and outputs alone are refactored to strictly          follow tone_guide.md + Google Docstring style + Google Documentation Style Guide
     -->

# CM-Colors v0.5.1 Release Notes
<!-- Updated Sphinx Documentation to reflect latest changes + strictly follow tone_guide.md + Google Documentation        Style Guide, optimised for SEO + gsearchconsole + ganalytics +
     not 'Here are all functions we have and all our API's dumped together for reference' but rather 'How to fix          color contrast issue?' 'How to make the colors more readable without changing the theme?' 'How to fix all color      contrast issues in website in 5 minutes' basically things people would actually search for - relevant and short      scripts and guides to guide people - Diataxis
     -->

# CM-Colors v0.6.0 Release Notes
<!-- Include the cdp scanner with optional install `pip install cm-colors[scan]`- now it visually checks the site         and gives back a css file with element specific color changes written into it
     -->