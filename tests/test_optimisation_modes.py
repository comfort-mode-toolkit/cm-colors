import pytest
from cm_colors.core.optimisation import check_and_fix_contrast
from cm_colors.core.contrast import calculate_contrast_ratio
from cm_colors.core.color_parser import parse_color_to_rgb

# Test Data
# A pair that is already accessible (AA)
ACCESSIBLE_PAIR = ("#000000", "#FFFFFF")  # 21:1
# A pair that is close but fails AA
CLOSE_FAIL_PAIR = ("#777777", "#000000")  # ~4.48:1 (needs 4.5)
# A pair that is hard to fix strictly
HARD_PAIR = ("#888888", "#FFFFFF")


def parse_result(color_str):
    return parse_color_to_rgb(color_str)


def test_already_accessible_no_change():
    """If already accessible, should return as is (default mode)."""
    text, bg = ACCESSIBLE_PAIR
    result, success = check_and_fix_contrast(text, bg, mode=1, premium=False)
    assert success
    assert result == text


def test_premium_upgrade():
    """If premium is True, should try to upgrade AA to AAA."""
    # #767676 on white is 4.54:1 (AA pass, AAA fail)
    text = "#767676"
    bg = "#FFFFFF"

    # Standard mode: should return as is because it passes AA
    res_std, success_std = check_and_fix_contrast(text, bg, mode=1, premium=False)
    assert success_std
    assert res_std == text

    # Premium mode: should tune it to reach AAA (7.0)
    res_prem, success_prem = check_and_fix_contrast(text, bg, mode=1, premium=True)
    assert success_prem
    assert res_prem != text

    res_rgb = parse_result(res_prem)
    bg_rgb = parse_result(bg)
    ratio = calculate_contrast_ratio(res_rgb, bg_rgb)
    assert ratio >= 7.0


def test_mode_0_strict():
    """Mode 0 should work for simple cases."""
    text = "#777777"  # Fails 4.5
    bg = "#000000"
    res, success = check_and_fix_contrast(text, bg, mode=0)
    assert success

    res_rgb = parse_result(res)
    bg_rgb = parse_result(bg)
    assert calculate_contrast_ratio(res_rgb, bg_rgb) >= 4.5


def test_mode_1_recursive_effectiveness():
    """Mode 1 should find solutions."""
    # Use a pair that might need some work
    text = "#999999"
    bg = "#FFFFFF"
    res, success = check_and_fix_contrast(text, bg, mode=1)
    assert success

    res_rgb = parse_result(res)
    bg_rgb = parse_result(bg)
    assert calculate_contrast_ratio(res_rgb, bg_rgb) >= 4.5


def test_mode_2_relaxed_fallback():
    """Mode 2 should work and potentially use fallback."""
    # It's hard to deterministically trigger the fallback without a very specific pair
    # that fails recursive but passes relaxed.
    # But we can at least verify it runs and returns a valid result.
    text = "#ABCDEF"
    bg = "#FEDCBA"
    res, success = check_and_fix_contrast(text, bg, mode=2)
    # Even if it fails, it should return a result
    if success:
        res_rgb = parse_result(res)
        bg_rgb = parse_result(bg)
        assert calculate_contrast_ratio(res_rgb, bg_rgb) >= 4.5


def test_large_text_handling():
    """Verify large text threshold (3.0) is respected."""
    # #959595 on white is ~3.0:1
    text = "#949494"  # Just below 3.0
    bg = "#FFFFFF"
    bg_rgb = parse_result(bg)

    # Normal text (needs 4.5)
    res_norm, success_norm = check_and_fix_contrast(text, bg, large=False, mode=1)
    res_norm_rgb = parse_result(res_norm)
    assert calculate_contrast_ratio(res_norm_rgb, bg_rgb) >= 4.5

    # Large text (needs 3.0)
    res_large, success_large = check_and_fix_contrast(text, bg, large=True, mode=1)
    res_large_rgb = parse_result(res_large)
    assert calculate_contrast_ratio(res_large_rgb, bg_rgb) >= 3.0


def test_invalid_inputs():
    with pytest.raises(ValueError):
        check_and_fix_contrast("invalid", "#FFFFFF")
