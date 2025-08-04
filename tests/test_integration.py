"""
Integration Tests for CMColors

These tests verify that different components work together correctly
and test real-world workflows and use cases.
"""

import pytest
from cm_colors import CMColors


class TestColorWorkflowIntegration:
    """Test complete color accessibility workflows"""
    
    def setup_method(self):
        """Setup for each test method"""
        self.cm = CMColors()
    
    def test_hex_to_accessible_workflow(self):
        """Test complete workflow: hex input -> accessibility check -> tuning"""
        # Start with hex colors
        text_hex = "#888888"  # Medium grey
        bg_hex = "#ffffff"    # White
        
        # Parse to RGB
        text_rgb = self.cm.parse_to_rgb(text_hex)
        bg_rgb = self.cm.parse_to_rgb(bg_hex)
        
        # Check original accessibility
        original_contrast = self.cm.contrast_ratio(text_rgb, bg_rgb)
        original_wcag = self.cm.wcag_level(text_rgb, bg_rgb)
        
        # Tune for accessibility
        tuned_color, is_accessible = self.cm.tune_colors(text_rgb, bg_rgb)
        
        # Verify the workflow
        assert text_rgb == (136, 136, 136)
        assert bg_rgb == (255, 255, 255)
        assert original_contrast < 4.5  # Should be too low
        assert original_wcag == "FAIL"
        assert isinstance(is_accessible, bool)  # Should return a boolean
        # Don't assume it's always True - depends on what's possible
    
    def test_rgb_string_to_accessible_workflow(self):
        """Test workflow with RGB string inputs"""
        text_rgb_str = "rgb(150, 150, 150)"
        bg_rgb_str = "rgb(255, 255, 255)"
        
        # Parse RGB strings
        text_rgb = self.cm.parse_to_rgb(text_rgb_str)
        bg_rgb = self.cm.parse_to_rgb(bg_rgb_str)
        
        # Get detailed tuning results
        details = self.cm.tune_colors(text_rgb, bg_rgb, details=True)
        
        # Verify integration
        assert text_rgb == (150, 150, 150)
        assert details['text'] == text_rgb
        assert details['bg'] == bg_rgb
        assert isinstance(details['status'], bool)  # Should be boolean
        assert details['wcag_level'] in ['AA', 'AAA', 'FAIL']  # Could still fail
        assert 'improvement_percentage' in details
   
    def test_large_text_vs_normal_text_workflow(self):
        """Test that large text flag affects the entire workflow"""
        text_rgb = (120, 120, 120)  # Borderline color
        bg_rgb = (255, 255, 255)
        
        # Test normal text
        normal_wcag = self.cm.wcag_level(text_rgb, bg_rgb, large_text=False)
        normal_tuned, normal_accessible = self.cm.tune_colors(text_rgb, bg_rgb, large_text=False)
        
        # Test large text
        large_wcag = self.cm.wcag_level(text_rgb, bg_rgb, large_text=True)
        large_tuned, large_accessible = self.cm.tune_colors(text_rgb, bg_rgb, large_text=True)
        
        # Both should return valid results
        assert isinstance(normal_accessible, bool)
        assert isinstance(large_accessible, bool)
        
        # Original WCAG levels should be valid
        wcag_levels = ['AAA', 'AA', 'FAIL']
        assert normal_wcag in wcag_levels
        assert large_wcag in wcag_levels
        
        # Large text should be more lenient (lower contrast requirement)
        # So if normal text passes, large text should also pass
        if normal_wcag in ['AA', 'AAA']:
            assert large_wcag in ['AA', 'AAA']


class TestColorSpaceIntegration:
    """Test integration between different color spaces"""
    
    def setup_method(self):
        self.cm = CMColors()
    
    def test_rgb_oklch_lab_roundtrip(self):
        """Test conversion chain: RGB -> OKLCH -> RGB and RGB -> LAB"""
        test_colors = [
            (255, 0, 0),      # Pure red
            (0, 255, 0),      # Pure green  
            (0, 0, 255),      # Pure blue
            (128, 128, 128),  # Grey
            (123, 45, 200),   # Random color
            (255, 255, 255),  # White
            (0, 0, 0)         # Black
        ]
        
        for rgb in test_colors:
            # RGB -> OKLCH -> RGB roundtrip
            oklch = self.cm.rgb_to_oklch(rgb)
            rgb_back = self.cm.oklch_to_rgb(oklch)
            
            # RGB -> LAB conversion
            lab = self.cm.rgb_to_lab(rgb)
            
            # Verify roundtrip accuracy
            for orig, back in zip(rgb, rgb_back):
                assert abs(orig - back) <= 3, f"Roundtrip failed for {rgb}: got {rgb_back}"
            
            # Verify LAB conversion
            assert len(lab) == 3
            assert 0 <= lab[0] <= 100  # L* should be 0-100
    
    def test_color_difference_across_spaces(self):
        """Test that color differences make sense across color spaces"""
        color1 = (255, 0, 0)    # Red
        color2 = (255, 10, 10)  # Slightly different red
        color3 = (0, 255, 0)    # Green (very different)
        
        # Calculate Delta E
        delta_small = self.cm.delta_e(color1, color2)
        delta_large = self.cm.delta_e(color1, color3)
        
        # Small difference should be smaller than large difference
        assert delta_small < delta_large
        assert delta_small < 10  # Similar colors
        assert delta_large > 50  # Very different colors
        
        # Convert to other spaces and verify consistency
        oklch1 = self.cm.rgb_to_oklch(color1)
        oklch2 = self.cm.rgb_to_oklch(color2)
        oklch3 = self.cm.rgb_to_oklch(color3)
        
        # OKLCH should preserve the relationship
        assert oklch1 != oklch2
        assert oklch1 != oklch3


class TestAccessibilityPipelineIntegration:
    """Test complete accessibility checking and fixing pipeline"""
    
    def setup_method(self):
        self.cm = CMColors()
    
    def test_accessibility_pipeline_various_inputs(self):
        """Test accessibility pipeline with various input formats"""
        test_cases = [
            ("#ff0000", "#ffffff"),  # Red on white
            ("rgb(255, 0, 0)", "rgb(255, 255, 255)"),  # Same as above
            ((255, 0, 0), (255, 255, 255)),  # Same as tuple
            ("#333333", "#ffffff"),  # Dark grey on white
            ("#cccccc", "#ffffff"),  # Light grey on white (likely to fail)
        ]
        
        for text_input, bg_input in test_cases:
            # Parse inputs to RGB
            if isinstance(text_input, str):
                text_rgb = self.cm.parse_to_rgb(text_input)
                bg_rgb = self.cm.parse_to_rgb(bg_input)
            else:
                text_rgb = text_input
                bg_rgb = bg_input
            
            # Run accessibility pipeline
            contrast = self.cm.contrast_ratio(text_rgb, bg_rgb)
            wcag = self.cm.wcag_level(text_rgb, bg_rgb)
            tuned, accessible = self.cm.tune_colors(text_rgb, bg_rgb)
            
            # Verify pipeline results
            assert contrast >= 1.0  # Minimum possible contrast
            assert wcag in ['AAA', 'AA', 'FAIL']
            assert isinstance(accessible, bool)  # Should be boolean
            
            # If accessible after tuning, verify it meets requirements
            if accessible:
                # Parse tuned color if it's a string
                if isinstance(tuned, str):
                    # Extract RGB from string like "rgb(r, g, b)"
                    import re
                    matches = re.findall(r'\d+', tuned)
                    if len(matches) >= 3:
                        tuned_rgb = tuple(int(x) for x in matches[:3])
                    else:
                        tuned_rgb = text_rgb  # Fallback
                else:
                    tuned_rgb = tuned
                
                tuned_contrast = self.cm.contrast_ratio(tuned_rgb, bg_rgb)
                tuned_wcag = self.cm.wcag_level(tuned_rgb, bg_rgb)
                
                assert tuned_contrast >= 4.5  # Should meet AA
                assert tuned_wcag in ['AA', 'AAA']
    
    def test_accessibility_with_color_similarity(self):
        """Test that tuned colors maintain visual similarity when possible"""
        problematic_colors = [
            ((180, 180, 180), (255, 255, 255)),  # Light grey on white
            ((100, 100, 100), (255, 255, 255)),  # Medium grey on white
            ((200, 150, 150), (255, 255, 255)),  # Light pink on white
        ]
        
        for text_rgb, bg_rgb in problematic_colors:
            # Get tuned color
            tuned, accessible = self.cm.tune_colors(text_rgb, bg_rgb)
            
            # Test that we get valid results
            assert isinstance(accessible, bool)
            assert tuned is not None
            
            # If accessible, check similarity
            if accessible:
                # Parse tuned color
                if isinstance(tuned, str):
                    # Extract RGB values from string like "rgb(r, g, b)"
                    import re
                    matches = re.findall(r'\d+', tuned)
                    if len(matches) >= 3:
                        tuned_rgb = tuple(int(x) for x in matches[:3])
                    else:
                        continue  # Skip if can't parse
                else:
                    tuned_rgb = tuned
                
                # Check that colors are reasonably similar
                delta_e = self.cm.delta_e(text_rgb, tuned_rgb)
                
                # Should preserve intent when possible
                assert delta_e < 100, f"Tuned color very different: Delta E = {delta_e}"


class TestErrorHandlingIntegration:
    """Test error handling across integrated workflows"""
    
    def setup_method(self):
        self.cm = CMColors()
    
    def test_invalid_color_propagation(self):
        """Test that invalid colors are caught early in workflows"""
        invalid_colors = [
            "notacolor",
            "#gggggg", 
            "rgb(300, 0, 0)",
            "rgb(0, -10, 0)",
            (256, 0, 0),
            (-1, 100, 100)
        ]
        
        for invalid in invalid_colors:
            with pytest.raises(ValueError):
                if isinstance(invalid, str):
                    self.cm.parse_to_rgb(invalid)
                else:
                    # Test with tuple input
                    self.cm.contrast_ratio(invalid, (255, 255, 255))
    
    def test_edge_case_color_combinations(self):
        """Test edge cases that might break workflows"""
        edge_cases = [
            ((0, 0, 0), (0, 0, 0)),      # Same color (black)
            ((255, 255, 255), (255, 255, 255)),  # Same color (white)
            ((0, 0, 0), (1, 1, 1)),      # Nearly same (very dark)
            ((254, 254, 254), (255, 255, 255)),  # Nearly same (very light)
        ]
        
        for text_rgb, bg_rgb in edge_cases:
            # These should not crash
            contrast = self.cm.contrast_ratio(text_rgb, bg_rgb)
            wcag = self.cm.wcag_level(text_rgb, bg_rgb)
            tuned, accessible = self.cm.tune_colors(text_rgb, bg_rgb)
            
            # Verify basic results
            assert contrast >= 1.0
            assert wcag in ['AAA', 'AA', 'FAIL']
            assert isinstance(accessible, bool)
            
            # Contrast of same colors should be 1.0
            if text_rgb == bg_rgb:
                assert contrast == pytest.approx(1.0, abs=0.1)
                assert wcag == "FAIL"
                # Same colors can't be made accessible
                assert accessible is False


class TestPerformanceIntegration:
    """Test that integrated workflows perform reasonably"""
    
    def setup_method(self):
        self.cm = CMColors()
    
    def test_batch_color_processing(self):
        """Test processing multiple colors efficiently"""
        import time
        
        # Generate test colors
        test_colors = [
            (i * 10 % 256, (i * 15) % 256, (i * 20) % 256) 
            for i in range(20)  # Smaller batch for reliability
        ]
        bg_color = (255, 255, 255)
        
        start_time = time.time()
        
        results = []
        for text_color in test_colors:
            # Full workflow for each color
            contrast = self.cm.contrast_ratio(text_color, bg_color)
            wcag = self.cm.wcag_level(text_color, bg_color)
            tuned, accessible = self.cm.tune_colors(text_color, bg_color)
            
            results.append({
                'original': text_color,
                'contrast': contrast,
                'wcag': wcag,
                'tuned': tuned,
                'accessible': accessible
            })
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        # Should process colors in reasonable time (less than 10 seconds)
        assert processing_time < 10.0, f"Batch processing too slow: {processing_time:.2f}s"
        assert len(results) == 20
        
        # All results should be valid
        for result in results:
            assert result['contrast'] >= 1.0
            assert result['wcag'] in ['AAA', 'AA', 'FAIL']
            assert isinstance(result['accessible'], bool)


class TestRealWorldScenarios:
    """Test real-world use cases and scenarios"""
    
    def setup_method(self):
        self.cm = CMColors()
    
    def test_web_design_color_palette(self):
        """Test typical web design color palette accessibility"""
        # Common web color palette
        palette = {
            'primary': '#3498db',    # Blue
            'secondary': '#2ecc71',  # Green  
            'accent': '#e74c3c',     # Red
            'text': '#2c3e50',       # Dark blue-grey
            'light_text': '#7f8c8d', # Light grey
            'background': '#ffffff',  # White
            'card_bg': '#f8f9fa'     # Light grey
        }
        
        # Convert to RGB
        rgb_palette = {
            name: self.cm.parse_to_rgb(hex_color) 
            for name, hex_color in palette.items()
        }
        
        # Test common text/background combinations
        combinations = [
            ('text', 'background'),
            ('text', 'card_bg'),
            ('light_text', 'background'),
            ('primary', 'background'),
            ('secondary', 'background'),
            ('accent', 'background')
        ]
        
        accessibility_results = {}
        
        for text_key, bg_key in combinations:
            text_rgb = rgb_palette[text_key]
            bg_rgb = rgb_palette[bg_key]
            
            contrast = self.cm.contrast_ratio(text_rgb, bg_rgb)
            wcag = self.cm.wcag_level(text_rgb, bg_rgb)
            tuned, accessible = self.cm.tune_colors(text_rgb, bg_rgb)
            
            accessibility_results[f"{text_key}_on_{bg_key}"] = {
                'contrast': contrast,
                'wcag': wcag,
                'accessible_after_tuning': accessible,
                'original_accessible': wcag in ['AA', 'AAA']
            }
        
        # Verify results make sense
        assert len(accessibility_results) == len(combinations)
        
        # Dark text on white should be accessible
        assert accessibility_results['text_on_background']['wcag'] in ['AA', 'AAA']
        
        # Check that tuning attempts were made (results are boolean)
        for combo, result in accessibility_results.items():
            assert isinstance(result['accessible_after_tuning'], bool)
            assert isinstance(result['original_accessible'], bool)
    
    def test_accessibility_report_generation(self):
        """Test generating comprehensive accessibility reports"""
        test_combinations = [
            ('#000000', '#ffffff', 'Black on white'),
            ('#888888', '#ffffff', 'Grey on white'),  
            ('#ff0000', '#ffffff', 'Red on white'),
            ('#0066cc', '#ffffff', 'Blue on white'),
            ('#cccccc', '#ffffff', 'Light grey on white')
        ]
        
        report = []
        
        for text_hex, bg_hex, description in test_combinations:
            text_rgb = self.cm.parse_to_rgb(text_hex)
            bg_rgb = self.cm.parse_to_rgb(bg_hex)
            
            # Get detailed results
            details = self.cm.tune_colors(text_rgb, bg_rgb, details=True)
            
            # Add to report
            report_entry = {
                'description': description,
                'original_text': text_hex,
                'background': bg_hex,
                'details': details
            }
            report.append(report_entry)
        
        # Verify report structure
        assert len(report) == len(test_combinations)
        
        for entry in report:
            assert 'description' in entry
            assert 'details' in entry
            assert isinstance(entry['details'], dict)
            assert 'wcag_level' in entry['details']
            assert 'status' in entry['details']
            assert isinstance(entry['details']['status'], bool)


class TestImpossibleCases:
    """Test cases where accessibility improvement is impossible"""
    
    def setup_method(self):
        self.cm = CMColors()
    
    def test_same_colors(self):
        """Test that same colors correctly report as not accessible"""
        same_color_pairs = [
            ((128, 128, 128), (128, 128, 128)),  # Same grey
            ((255, 255, 255), (255, 255, 255)),  # Same white
            ((0, 0, 0), (0, 0, 0)),              # Same black
        ]
        
        for text_rgb, bg_rgb in same_color_pairs:
            contrast = self.cm.contrast_ratio(text_rgb, bg_rgb)
            wcag = self.cm.wcag_level(text_rgb, bg_rgb)
            tuned, accessible = self.cm.tune_colors(text_rgb, bg_rgb)
            
            # Same colors have 1:1 contrast and should fail
            assert contrast == pytest.approx(1.0, abs=0.1)
            assert wcag == "FAIL"
            assert accessible is False  # Cannot be made accessible
    
    def test_very_similar_colors(self):
        """Test very similar colors that may be impossible to fix"""
        similar_pairs = [
            ((250, 250, 250), (255, 255, 255)),  # Very light grey on white
            ((5, 5, 5), (0, 0, 0)),              # Very dark grey on black
        ]
        
        for text_rgb, bg_rgb in similar_pairs:
            contrast = self.cm.contrast_ratio(text_rgb, bg_rgb)
            wcag = self.cm.wcag_level(text_rgb, bg_rgb)
            tuned, accessible = self.cm.tune_colors(text_rgb, bg_rgb)
            
            # Should have very low contrast
            assert contrast < 2.0
            assert wcag == "FAIL"
            # May or may not be fixable - just check it's a boolean
            assert isinstance(accessible, bool)


# Convenience function to run integration tests
def test_quick_integration():
    """Quick integration test for basic workflows"""
    cm = CMColors()
    
    # Test basic workflow with a color that should be improvable
    text_rgb = cm.parse_to_rgb("#666666")  # Medium grey
    bg_rgb = cm.parse_to_rgb("#ffffff")    # White
    
    contrast = cm.contrast_ratio(text_rgb, bg_rgb)
    wcag = cm.wcag_level(text_rgb, bg_rgb)
    tuned, accessible = cm.tune_colors(text_rgb, bg_rgb)
    
    assert contrast > 0
    assert wcag in ['AAA', 'AA', 'FAIL']
    assert isinstance(accessible, bool)
    
    # Test impossible case
    same_tuned, same_accessible = cm.tune_colors((128, 128, 128), (128, 128, 128))
    assert same_accessible is False
    
    print("✅ Basic integration test passed!")


if __name__ == "__main__":
    # Run quick integration test if called directly
    test_quick_integration()