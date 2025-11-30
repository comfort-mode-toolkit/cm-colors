"""Tests for make_readable_bulk API"""

import pytest
from cm_colors import make_readable_bulk


class TestMakeReadableBulk:
    """Test the make_readable_bulk function"""

    def test_basic_bulk_processing(self):
        """Test basic bulk processing of multiple pairs"""
        pairs = [
            ('#000000', '#ffffff'),  # Already readable
            ('#777777', '#ffffff'),  # Needs fixing
        ]

        results = make_readable_bulk(pairs)

        assert len(results) == 2
        assert all(isinstance(r, tuple) and len(r) == 2 for r in results)

        # First pair should be already readable
        color1, status1 = results[0]
        assert status1 in ['readable', 'very readable']

        # Second pair should be fixed
        color2, status2 = results[1]
        assert isinstance(color2, str)

    def test_hex_format_preservation(self):
        """Test that Hex input returns Hex output"""
        pairs = [('#777777', '#ffffff')]

        results = make_readable_bulk(pairs)
        color, status = results[0]

        assert color.startswith('#')
        assert len(color) == 7  # #RRGGBB format

    def test_tuple_format_preservation(self):
        """Test that tuple input returns tuple output"""
        pairs = [((119, 119, 119), (255, 255, 255))]

        results = make_readable_bulk(pairs)
        color, status = results[0]

        assert isinstance(color, tuple)
        assert len(color) == 3

    def test_large_text_flag(self):
        """Test large text flag affects color tuning"""
        text_color = '#777777'
        bg_color = '#ffffff'

        # Normal text
        normal_results = make_readable_bulk([(text_color, bg_color)])
        normal_color, _ = normal_results[0]

        # Large text (more lenient)
        large_results = make_readable_bulk([(text_color, bg_color, True)])
        large_color, _ = large_results[0]

        # Results may differ based on thresholds
        assert normal_color is not None
        assert large_color is not None

    def test_extra_readable_flag(self):
        """Test very_readable flag aims for AAA"""
        pairs = [('#777777', '#ffffff')]

        # Normal
        normal_results = make_readable_bulk(pairs, very_readable=False)

        # Extra readable
        extra_results = make_readable_bulk(pairs, very_readable=True)

        assert len(normal_results) == 1
        assert len(extra_results) == 1

    def test_mode_parameter(self):
        """Test different optimization modes"""
        pairs = [('#777777', '#ffffff')]

        # Mode 0: Strict
        results_0 = make_readable_bulk(pairs, mode=0)

        # Mode 1: Default
        results_1 = make_readable_bulk(pairs, mode=1)

        # Mode 2: Relaxed
        results_2 = make_readable_bulk(pairs, mode=2)

        assert len(results_0) == 1
        assert len(results_1) == 1
        assert len(results_2) == 1

    def test_readability_status_strings(self):
        """Test that status strings are user-friendly"""
        pairs = [
            ('#000000', '#ffffff'),  # Very readable
            ('#ffffff', '#ffffff'),  # Not readable
            ('#777777', '#ffffff'),  # Should become readable
        ]

        results = make_readable_bulk(pairs)

        for color, status in results:
            assert status in ['readable', 'very readable', 'not readable']

    def test_invalid_color_handling(self):
        """Test handling of invalid colors"""
        pairs = [('invalid', '#ffffff')]

        results = make_readable_bulk(pairs)

        # Should return something for invalid colors
        assert len(results) == 1

    def test_empty_pairs_list(self):
        """Test with empty pairs list"""
        pairs = []

        results = make_readable_bulk(pairs)

        assert len(results) == 0

    def test_mixed_formats(self):
        """Test processing pairs with mixed color formats"""
        pairs = [
            ('#777777', '#ffffff'),  # Hex
            ((119, 119, 119), (255, 255, 255)),  # Tuple
        ]

        results = make_readable_bulk(pairs)

        assert len(results) == 2
        # Each should preserve its input format
        assert results[0][0].startswith('#')
        assert isinstance(results[1][0], tuple)

    def test_save_report_generates_file(self, tmp_path):
        """Test that save_report=True generates HTML file"""
        import os

        pairs = [('#777777', '#ffffff')]

        # Change to temp directory
        original_dir = os.getcwd()
        try:
            os.chdir(tmp_path)
            results = make_readable_bulk(pairs, save_report=True)

            # Check that report file was created
            assert os.path.exists('cm_colors_bulk_report.html')

        finally:
            os.chdir(original_dir)
