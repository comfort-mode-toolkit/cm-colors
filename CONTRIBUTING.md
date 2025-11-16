# Contributing to CM-Colors 🌈

*Want to help make the web more accessible? Awesome! Here's how to jump in without breaking things.*

Hey there! So you want to contribute to CM-Colors? Whether you're here to fix a bug, add a feature, improve the docs, or just make the code prettier, we're excited to have you. This project is all about making accessibility easier for everyone, and that includes making it easy to contribute.

## The Vibe

Before we get into the technical stuff, here's what we're going for:
- **Accessibility first**: Every change should make the web more readable for more people
- **Developer-friendly**: If it's hard to use, people won't use it (and accessibility loses)
- **Keep it simple**: Complex APIs scare people away from doing the right thing
- **Preserve aesthetics**: Design and accessibility can coexist

## Codebase Tour ( It's not scary! )
Checkout the tour [here](https://gist.github.com/lalithaar/286ce89bc1d4816b3d6c862380ddc9d6) so you can easily know which file dpes what and where should you edit :>

## Quick Start (I Just Want to Fix Something Small)

For tiny fixes (typos, small bugs, documentation improvements):

1. Fork the repo
2. Make your change
3. Submit a PR with a clear description
4. That's it!

No need to read the rest of this unless you're doing something more involved.

## Setting Up Your Dev Environment

```bash
# Clone your fork
git clone https://github.com/yourusername/cm-colors.git
cd cm-colors

# Install in development mode
pip install -e .

# Install development dependencies
pip install pytest unittest hypothesis black

# Run the tests to make sure everything works
PYTHONPATH=src python -m pytest tests/*.py

# Run a quick smoke test
python -c "from cm_colors import CMColors; cm = CMColors(); print('✨ Everything works!'); print(f'Black on white contrast: {cm.contrast_ratio((0,0,0), (255,255,255)):.1f}')" #Should print 21.0
```

**Requirements**: Python 3.7+ (we try to stay compatible with slightly older versions because not everyone can upgrade immediately)

## What Kind of Contributions We're Looking For

### 🐛 Bug Fixes
Found something broken? Please fix it! Even small bugs can make the library unusable for someone.

### 📚 Documentation
- More examples showing real-world usage
- Better explanations of the color science
- Translations (if you're multilingual and want to help)
- Screenshots/visuals showing before/after results

### ⚡ Performance Improvements
- Our optimization algorithms can always be faster
- Memory usage improvements
- Better edge case handling

### 🎨 New Features
Before adding new features, please open an issue to discuss it. We want to keep the API simple, but there are definitely useful things missing.

**Ideas we'd love help with:**
- Support for color palettes (not just single colors)
- Integration helpers for popular frameworks (React, Vue, etc.)
- Enhanced CLI tool for batch processing CSS files
- Web-based color picker/tester
- More output formats (HSL, named colors, etc.)
- Browser extension for real-time accessibility checking

### 🧪 Better Testing
- More edge cases in our test suite
- Performance benchmarks
- Cross-platform testing
- Real-world color combination testing
- Visual regression tests

## The Technical Stuff

### Code Style
We're not super strict, but:
- **Black** for formatting (run `black .` before submitting)
- **Type hints** where they make sense (especially function signatures)
- **Docstrings** for public functions
- **Comments** for the weird math stuff (help future developers understand the color science)

### Testing Philosophy
- **Test the public API** - users should never get broken behavior
- **Test edge cases** - color math has lots of weird corners
- **Test performance** - accessibility tools need to be fast
- **Test with real colors** - theoretical tests are great, but test with actual hex codes people use


```bash
PYTHONPATH=src python -m pytest tests/*.py 
```

### Directory Structure
```
cm-colors/
├── src/
│   └── cm_colors/           # Main library code
│       ├── __init__.py      # Public API
│       ├── core/            # Core algorithms
│       │   ├── cm_colors.py     # Main CMColors class
│       │   ├── optimisation.py  # Color optimization algorithms
│       │   ├── conversions.py   # Color space conversions
│       │   ├── contrast.py      # WCAG contrast calculations
│       │   └── color_metrics.py # Delta E and color difference
│       └── cli/             # Command-line tools (wip & excluded from package)
│           └── css_parser.py    # CSS color extraction
├── tests/                   # Comprehensive test suite
│   ├── test_unit.py             # Unit tests
│   ├── test_integration.py      # Integration tests
│   ├── test_helperfunc.py       # Core function tests
│   ├── test_properties.py       # Property-based tests
│   ├── test_boundaries.py       # Edge case tests
│   └── test_mocks.py           # Mock/isolation tests
├── setup.py                 # Package configuration
├── MANIFEST.in             # Package file inclusion rules
└── requirements*.txt       # Dependencies
```

## Submitting Changes

### The Process
1. **Fork** the repository
2. **Create a branch** from `main` (name it something descriptive like `fix-gradient-descent-bug` or `add-hsl-support`)
3. **Make your changes** (commit often, write good commit messages)
4. **Test everything** (run the full test suite, try your changes manually)
5. **Submit a PR** with a clear description

### Writing Good PRs

**Good PR title**: "Fix binary search edge case for very dark colors"
**Bad PR title**: "Fix bug"

**Your PR description should answer:**
- What problem are you solving?
- How did you solve it?
- How can we test that it works?
- Are there any breaking changes?

**Example PR description:**
```
## Problem
Binary search was failing when trying to optimize very dark colors (L < 0.1) 
because the search bounds weren't accounting for floating point precision.

## Solution
Added a minimum bound check and increased precision in the binary search 
termination condition in `src/cm_colors/core/optimisation.py`.

## Testing
- Added test case with dark gray (#1a1a1a) on white background
- Verified fix works with other edge cases in test_boundaries.py
- All existing tests still pass
- Performance impact: negligible (< 1ms difference)

## Breaking Changes
None - this is purely a bug fix.
```

### Review Process
- We'll review your PR as quickly as possible (usually within a few days)
- We might suggest changes - don't take it personally! We're all learning
- Once approved, we'll merge and include your changes in the next release
- You'll be added to our contributors list (unless you prefer not to be)

## The Color Science Stuff

If you're working on the core algorithms, here's what you need to know:

### Key Concepts
- **OKLCH color space**: Perceptually uniform (equal math changes = equal visual changes)
- **Delta E 2000**: How we measure color similarity (lower = more similar)
- **WCAG contrast ratios**: Legal/accessibility requirements (4.5:1 minimum, 7:1 preferred)

### When Modifying Algorithms
- **Maintain mathematical rigor**: The color science must be correct
- **Preserve perceptual quality**: Don't break the "minimal change" promise
- **Keep performance**: Accessibility tools must be fast
- **Test extensively**: Color math has lots of edge cases

### Reference Materials
- [OKLCH color space specification](https://bottosson.github.io/posts/oklab/)
- [Delta E 2000 formula](http://www.ece.rochester.edu/~gsharma/ciede2000/)
- [WCAG contrast guidelines](https://www.w3.org/WAI/WCAG21/Understanding/contrast-minimum.html)

## Common Tasks

### Adding a New Color Format

1. Add conversion functions in `src/cm_colors/core/conversions.py`
2. Update the main API in `src/cm_colors/core/cm_colors.py`
3. Add tests for the new format in `tests/test_unit.py`
4. Update documentation and examples

### Fixing Algorithm Issues

1. Write a failing test that reproduces the problem
2. Fix the algorithm (usually in `src/cm_colors/core/optimisation.py`)
3. Verify the test passes
4. Check that existing tests still pass
5. Consider if similar edge cases exist

### Improving Performance

1. Profile the current code to find bottlenecks
2. Implement your optimization
3. Benchmark before/after performance
4. Make sure accuracy isn't compromised
5. Update any relevant documentation

### Working with the Test Suite

Our test suite is comprehensive with different types of tests:

- **Unit tests** (`test_unit.py`): Test individual functions in isolation
- **Integration tests** (`test_integration.py`): Test complete workflows
- **Helper function tests** (`test_helperfunc.py`): Test core mathematical functions
- **Property-based tests** (`test_properties.py`): Test mathematical properties that should always hold
- **Boundary tests** (`test_boundaries.py`): Test edge cases and boundary conditions
- **Mock tests** (`test_mocks.py`): Test component isolation

## Questions? Issues? Ideas?

- **Bug reports**: [Open an issue](https://github.com/comfort-mode-toolkit/cm-colors/issues) with steps to reproduce
- **Feature requests**: [Open an issue](https://github.com/comfort-mode-toolkit/cm-colors/issues) describing what you want and why
- **General questions**: [GitHub Discussions](https://github.com/comfort-mode-toolkit/cm-colors/discussions) or open an issue
- **Security issues**: Email us directly (check the repo for current contact info)

## Recognition

Contributors get:
- Your name in the contributors list (unless you prefer anonymity)
- A mention in release notes for significant contributions
- Our eternal gratitude for making the web more accessible 🙏

## Code of Conduct

**TL;DR**: Be nice to each other. We're all here to make things better.

**Longer version**: This project follows the standard open source code of conduct - be respectful, constructive, and inclusive. We want everyone to feel welcome contributing, regardless of experience level, background, or anything else.

If someone's being a jerk, let us know and we'll handle it.

## Final Notes

### For New Contributors
- Don't be afraid to ask questions
- Start small (documentation improvements, small bug fixes)
- Read existing code to understand the patterns
- Run the test suite early and often
- We're here to help you succeed

### For Experienced Contributors
- Help mentor newcomers
- Review PRs when you can
- Share knowledge about color science/accessibility
- Suggest architectural improvements

### For Everyone
- Test your changes thoroughly - we have a comprehensive test suite for a reason
- Write code that future contributors can understand
- Remember that every contribution makes the web more accessible
- Have fun! This is cool stuff we're working on

---

**Ready to contribute?** Head over to the [issues page](https://github.com/comfort-mode-toolkit/cm-colors/issues) and find something that interests you. Or just fork the repo and start exploring!

*Making the web readable for everyone, one commit at a time* 🌈♿

**P.S.** If you're reading this because you're thinking about contributing but aren't sure where to start, try running the test suite (`pytest tests/ -v`) and see if anything breaks. Or look at the CLI tool in `src/cm_colors/cli/` - that's always a good place to add features!
