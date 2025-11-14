"""
Mock and Stub Tests for CMColors

Tests components in isolation using mocks for dependencies.
"""

import pytest
from unittest.mock import patch, MagicMock

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from cm_colors import CMColors


class TestWithMocks:
    
    def setup_method(self):
        """
        Create a fresh CMColors instance for use by each test method.
        
        Called by pytest before each test; assigns the new CMColors instance to self.cm.
        """
        self.cm = CMColors()
    
    # @patch('cm_colors.core.cm_colors.check_and_fix_contrast')  # Patch where it's imported
    # def test_tune_colors_calls_optimization(self, mock_optimize):
    #     """Test that tune_colors calls the optimization function correctly
    #     # TODO - Rewrite or delete this test to match lates api
    #     # """
    #     mock_optimize.return_value = ("rgb(0, 0, 0)", True)
        
    #     result = self.cm.tune_colors((128, 128, 128), (255, 255, 255))
        
    #     mock_optimize.assert_called_once_with((128, 128, 128), (255, 255, 255), False, False)
    #     assert result == ("rgb(0, 0, 0)", True)
    
    # @patch('cm_colors.core.cm_colors.calculate_contrast_ratio')  # Patch where it's imported
    # def test_contrast_ratio_delegation(self, mock_calc):
    #     """
    #     Test that contrast_ratio delegates to core function
    #     TODO: remove or rewrite
    #     Not relevant from v0.2
    #     """
    #     mock_calc.return_value = 4.5
        
    #     result = self.cm.contrast_ratio((0, 0, 0), (255, 255, 255))
        
    #     mock_calc.assert_called_once_with((0, 0, 0), (255, 255, 255))
    #     assert result == 4.5
    
    @patch('cm_colors.core.cm_colors.parse_color_to_rgb')  # Patch where it's imported
    def test_error_handling_propagation(self, mock_parse):
        """Test that errors from core functions are properly propagated"""
        mock_parse.side_effect = ValueError("Invalid color")
        
        with pytest.raises(ValueError, match="Invalid color"):
            self.cm.parse_to_rgb("invalid")
    
    # @patch('cm_colors.core.cm_colors.get_wcag_level')
    # def test_wcag_level_delegation(self, mock_wcag):
    #     """Test that wcag_level delegates to core function
    #     #TODO: remove or rewrite Additional test - Not relevant from v0.2 since ColorPair class handles this, 
    #     and doesn't directly call core get_wcag level ( handled through ColorPair(color1,color2).wcag_level)
    # """
    #     mock_wcag.return_value = "AA"
        
    #     result = self.cm.wcag_level((100, 100, 100), (255, 255, 255), large_text=True)
        
    #     mock_wcag.assert_called_once_with((100, 100, 100), (255, 255, 255), True)  
    #     assert result == "AA"
    
    @patch('cm_colors.core.cm_colors.rgb_to_oklch_safe')
    def test_rgb_to_oklch_delegation(self, mock_convert):
        """Test that rgb_to_oklch delegates to core function"""
        mock_convert.return_value = (0.5, 0.1, 180.0)
        
        result = self.cm.rgb_to_oklch((255, 0, 0))
        
        mock_convert.assert_called_once_with((255, 0, 0))
        assert result == (0.5, 0.1, 180.0)
    
    @patch('cm_colors.core.cm_colors.oklch_to_rgb_safe')
    def test_oklch_to_rgb_delegation(self, mock_convert):
        """Test that oklch_to_rgb delegates to core function"""
        mock_convert.return_value = (255, 0, 0)
        
        result = self.cm.oklch_to_rgb((0.5, 0.1, 180.0))
        
        mock_convert.assert_called_once_with((0.5, 0.1, 180.0))
        assert result == (255, 0, 0)
    
    @patch('cm_colors.core.cm_colors.rgb_to_lab')
    def test_rgb_to_lab_delegation(self, mock_convert):
        """Test that rgb_to_lab delegates to core function"""
        mock_convert.return_value = (50.0, 0.0, 0.0)
        
        result = self.cm.rgb_to_lab((128, 128, 128))
        
        mock_convert.assert_called_once_with((128, 128, 128))
        assert result == (50.0, 0.0, 0.0)
    
    # @patch('src.cm_colors.core.color_metrics.calculate_delta_e_2000')
    # def test_delta_e_delegation(self, mock_delta):
    #     """Test that delta_e delegates to core function
    # TODO: remove or rewrite
    #     Not relevant from v0.2"""
    #     mock_delta.return_value = 2.5
        
    #     result = self.cm.delta_e((255, 0, 0), (250, 5, 5))
        
    #     mock_delta.assert_called_once_with((255, 0, 0), (250, 5, 5))
    #     assert result == 2.5
    
    # def test_validation_error_handling(self):
    #     """Test that validation errors are properly raised
    #     # TODO: we now use dynamic error handling, not just hardcoded, so regex doesn't match - rewrite regex
    #     """
    #     # Test invalid RGB for contrast_ratio
    #     with pytest.raises(ValueError, match="Invalid color input(s)"):
    #         self.cm.contrast_ratio((256, 0, 0), (255, 255, 255))
        
    #     # Test invalid RGB for rgb_to_oklch
    #     with pytest.raises(ValueError, match="Invalid RGB values"):
    #         self.cm.rgb_to_oklch((-1, 0, 0))
        
    #     # Test invalid OKLCH for oklch_to_rgb
    #     with pytest.raises(ValueError, match="Invalid OKLCH values"):
    #         self.cm.oklch_to_rgb((2.0, 0.1, 180.0))  # L > 1
    

    # @patch('cm_colors.core.cm_colors.check_and_fix_contrast')
    # def test_tune_colors_with_all_parameters(self, mock_optimize):
    #     """Test tune_colors with all parameter combinations
    #     # TODO - Rewrite or delete this test to match lates api""""
    #     # Test with large_text=True, details=True
    #     mock_optimize.return_value = {
    #         'text': (128, 128, 128),
    #         'tuned_text': 'rgb(0, 0, 0)',
    #         'bg': (255, 255, 255),
    #         'large': True,
    #         'wcag_level': 'AA',
    #         'improvement_percentage': 50.0,
    #         'status': True,
    #         'message': 'Improved'
    #     }
        
    #     result = self.cm.tune_colors((128, 128, 128), (255, 255, 255), large_text=True, details=True)
        
    #     mock_optimize.assert_called_once_with((128, 128, 128), (255, 255, 255), True, True)
    #     assert isinstance(result, dict)
    #     assert result['wcag_level'] == 'AA'
    
    def test_integration_without_mocks(self):
        """Test that methods work together without mocks (integration)"""
        # This ensures the real functions still work when not mocked
        contrast = self.cm.contrast_ratio((0, 0, 0), (255, 255, 255))
        assert contrast > 20  # Should be ~21
        
        wcag = self.cm.wcag_level((0, 0, 0), (255, 255, 255))
        assert wcag == "AAA"
        
        rgb = self.cm.parse_to_rgb("#ffffff")
        assert rgb == (255, 255, 255)


class TestMockEdgeCases:
    """Test edge cases with mocks"""
    
    def setup_method(self):
        self.cm = CMColors()
    
    @patch('cm_colors.core.cm_colors.check_and_fix_contrast')
    def test_tune_colors_failure_case(self, mock_optimize):
        """Test tune_colors when optimization fails"""
        mock_optimize.return_value = ("rgb(128, 128, 128)", False)  # Failed to optimize
        
        result = self.cm.tune_colors((200, 200, 200), (255, 255, 255))
        
        tuned_color, is_accessible = result
        assert is_accessible is False
        assert tuned_color is not None
    
    # @patch('cm_colors.core.cm_colors.check_and_fix_contrast')
    # def test_tune_colors_exception_handling(self, mock_optimize):
    #     """Test tune_colors when optimization raises exception
    #       # TODO - Rewrite or delete this test to match lates api"""
    #     mock_optimize.side_effect = ValueError("Optimization failed")
        
    #     with pytest.raises(ValueError, match="Optimization failed"):
    #         self.cm.tune_colors((128, 128, 128), (255, 255, 255))
    
    
    @patch('cm_colors.core.colors.calculate_contrast_ratio')
    def test_contrast_ratio_edge_values(self, mock_calc):
        """Test contrast ratio with edge return values"""
        # Test minimum contrast
        mock_calc.return_value = 1.0
        result = self.cm.contrast_ratio((128, 128, 128), (128, 128, 128))
        assert result == 1.0
        
        # Test maximum contrast  
        mock_calc.return_value = 21.0
        result = self.cm.contrast_ratio((0, 0, 0), (255, 255, 255))
        assert result == 21.0


# Convenience function for quick mock testing
# def test_quick_mock():
#     """Quick test to verify mocking works"""
#     cm = CMColors()
    
#     with patch('cm_colors.core.contrast.calculate_contrast_ratio') as mock_calc:
#         mock_calc.return_value = 10.0
#         result = cm.contrast_ratio((0, 0, 0), (255, 255, 255))
#         assert result == 10.0  # Should return mocked value, not real ~21 # TODO: Check why because it returns 21 not 10.0
        
#     print("✅ Basic mock test passed!")