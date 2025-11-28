# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.4.2] - 2025-11-28

### Added

- **CLI Modes**: You can now use the `--mode` option in the CLI to choose your optimization strategy (0, 1, or 2).
- **CLI Premium**: Added the `--premium` flag to the CLI to target AAA compliance.

## [0.4.1] - 2025-11-28

### Fixed

- **Bug Fix**: `ColorPair.tune_colors()` now correctly accepts `mode` and `premium` arguments.
- **Contrast Target**: Fixed an issue where the contrast target didn't adjust correctly for large text when using the premium option.

## [0.4.0] - 2025-11-27

### Added

- **Smarter Color Fixing**: We've improved how we find readable colors. The default mode is now much better at fixing difficult color pairs.
- **Strictness Modes**: You can now choose how much we're allowed to change your colors:
  - **Mode 0 (Ultra Strict)**: Changes colors very little (best for strict brand guidelines).
  - **Mode 1 (Default)**: The best balance of readability and style.
  - **Mode 2 (Relaxed)**: Allows more change to ensure your text is readable.
- **Premium Standard**: Added a `premium` option to aim for the highest readability standard (AAA) instead of the standard (AA).


## [0.3.0] - 2025-11-27

### Added

- **Command-Line Interface (CLI) Tool**: New `cm-colors` command for processing CSS files
  - Automatically scans CSS files for color pairs and checks contrast against WCAG standards
  - Tunes inaccessible colors while preserving visual similarity
  - Generates modified CSS files with `_cm` suffix
  - Supports nested CSS rules (`@media`, `@supports`)
  - Configurable default background color via `--default-bg` option
- **HTML Report Generation**: Visual before/after comparison report for tuned color pairs
  - Clean, minimal design using Yeseva One and Atkinson Hyperlegible fonts
  - Shows original and tuned colors with sample text
  - Displays WCAG level improvements (FAIL to AA, FAIL to AAA)
  - Saved as `cm_colors_report.html` in the working directory
- **Colorized CLI Output**: Terminal-friendly color-coded status messages
  - Green for successfully tuned pairs
  - Cyan for already-accessible pairs
  - Red for failed tuning attempts with detailed failure information
- **Comprehensive Test Suite**: Production-ready tests for CLI functionality
  - Input validation and argument parsing tests
  - CSS processing and color tuning logic tests
  - Console output and HTML report generation tests
  - 13 tests covering all major CLI scenarios

### Changed

- CLI terminology: Uses "tuned" instead of "fixed" for color adjustments
- CLI output structure: Summary statistics moved to top for better visibility
- Failure messages: More user-friendly explanations ("Could not tune without too much changes")

### Documentation

- Added comprehensive CLI usage guide (`docs/cm_colors/cli.rst`)
- Added Color class API reference (`docs/cm_colors/color.rst`)
- Added ColorPair class API reference (`docs/cm_colors/colorpair.rst`)
- Updated CMColors API documentation for v0.3.0
- All documentation follows Google Developer Documentation Style Guide

## [0.2.0] - Previous Release

### Added

- Universal color format support (hex, RGB/RGBA, HSL/HSLA, named colors)
- RGBA and HSLA transparency handling with automatic compositing
- Color and ColorPair classes for intuitive API
- Enhanced color validation and error reporting

[0.3.0]: https://github.com/comfort-mode-toolkit/cm-colors/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/comfort-mode-toolkit/cm-colors/releases/tag/v0.2.0
