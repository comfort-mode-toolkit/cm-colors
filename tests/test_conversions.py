import pytest
from cm_colors.core.conversions import rgba_to_rgb


def test_rgba_to_rgb_opaque():
    assert rgba_to_rgb((10, 20, 30, 1.0)) == (10, 20, 30)


def test_rgba_to_rgb_transparent_default_bg():
    assert rgba_to_rgb((10, 20, 30, 0.0)) == (255, 255, 255)


def test_rgba_to_rgb_half_alpha_white_bg():
    assert rgba_to_rgb((0, 0, 0, 0.5)) == (128, 128, 128)


def test_rgba_to_rgb_half_alpha_custom_bg():
    assert rgba_to_rgb((0, 0, 255, 0.5), background=(255, 0, 0)) == (
        128,
        0,
        128,
    )


def test_rgba_to_rgb_invalid_alpha():
    with pytest.raises(ValueError):
        rgba_to_rgb((0, 0, 0, 1.5))


def test_rgba_to_rgb_invalid_rgb():
    with pytest.raises(ValueError):
        rgba_to_rgb((256, 0, 0, 0.5))


def test_rgba_to_rgb_invalid_background():
    with pytest.raises(ValueError):
        rgba_to_rgb((0, 0, 0, 0.5), background=(0, 0, 300))
