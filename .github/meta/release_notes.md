# Release Notes

## [0.5.0] - 2025-11-30

### Focused
**We made the tool do one thing really well.**

We simplified everything to focus on the main goal: fixing colors to make them readable. We removed complicated options that got in the way.

- **New Simple API**: Just use `make_readable()` or `make_readable_bulk()`.
- **Clearer Names**: Changed `tune_colors` to `make_readable` because that's what it does.
- **Better Defaults**: The tool now makes smart decisions for you, so you don't need to tweak settings.

### Changed
- **Renamed**: `ColorPair.tune_colors()` is now `ColorPair.make_readable()`.
- **Renamed**: `extra_readable` is now `very_readable` to be clearer.
- **Renamed**: `large` is now `large_text` so you know exactly what it means.
- **Removed**: The `CMColors` class. You don't need it anymore. Just import the functions you need.
- **Removed**: `details` parameter. We now always give you the fixed color and whether it worked.

### Added
- **Bulk Fixing**: New `make_readable_bulk()` function to fix lists of colors easily.
- **Reports**: Built-in HTML reporting to see exactly what changed.