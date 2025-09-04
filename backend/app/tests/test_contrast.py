"""
Tests for color contrast calculations.
"""

import pytest
from app.utils.color_contrast import (
    contrast_ratio, relative_luminance, is_large_text, 
    get_contrast_threshold, hex_to_rgb, parse_color
)


class TestColorContrast:
    """Test color contrast calculations."""
    
    def test_hex_to_rgb(self):
        """Test hex color parsing."""
        assert hex_to_rgb("#000000") == (0, 0, 0)
        assert hex_to_rgb("#ffffff") == (255, 255, 255)
        assert hex_to_rgb("#ff0000") == (255, 0, 0)
        assert hex_to_rgb("#00ff00") == (0, 255, 0)
        assert hex_to_rgb("#0000ff") == (0, 0, 255)
        
        # Short form
        assert hex_to_rgb("#000") == (0, 0, 0)
        assert hex_to_rgb("#fff") == (255, 255, 255)
        
        # Invalid formats
        assert hex_to_rgb("invalid") is None
        assert hex_to_rgb("#gggggg") is None
    
    def test_parse_color(self):
        """Test color parsing from various formats."""
        # Hex colors
        assert parse_color("#000000") == (0, 0, 0)
        assert parse_color("#ffffff") == (255, 255, 255)
        
        # RGB colors
        assert parse_color("rgb(255, 0, 0)") == (255, 0, 0)
        assert parse_color("rgba(0, 255, 0, 0.5)") == (0, 255, 0)
        
        # Named colors
        assert parse_color("black") == (0, 0, 0)
        assert parse_color("white") == (255, 255, 255)
        assert parse_color("red") == (255, 0, 0)
        
        # Invalid colors
        assert parse_color("invalid") is None
    
    def test_relative_luminance(self):
        """Test relative luminance calculations."""
        # Black should have luminance 0
        assert relative_luminance((0, 0, 0)) == 0.0
        
        # White should have luminance 1
        assert relative_luminance((255, 255, 255)) == 1.0
        
        # Red should have some luminance
        red_luminance = relative_luminance((255, 0, 0))
        assert 0 < red_luminance < 1
        
        # Green should have higher luminance than red
        green_luminance = relative_luminance((0, 255, 0))
        assert green_luminance > red_luminance
    
    def test_contrast_ratio(self):
        """Test contrast ratio calculations."""
        # Black on white should have maximum contrast
        black_white_ratio = contrast_ratio("#000000", "#ffffff")
        assert black_white_ratio == 21.0
        
        # White on black should have maximum contrast
        white_black_ratio = contrast_ratio("#ffffff", "#000000")
        assert white_black_ratio == 21.0
        
        # Same colors should have ratio 1
        same_color_ratio = contrast_ratio("#000000", "#000000")
        assert same_color_ratio == 1.0
        
        # Test with RGB tuples
        rgb_ratio = contrast_ratio((0, 0, 0), (255, 255, 255))
        assert rgb_ratio == 21.0
        
        # Test invalid colors
        assert contrast_ratio("invalid", "#ffffff") is None
        assert contrast_ratio("#000000", "invalid") is None
    
    def test_is_large_text(self):
        """Test large text detection."""
        # Normal text sizes
        assert not is_large_text(12)  # 12px normal
        assert not is_large_text(16)  # 16px normal
        assert not is_large_text(18)  # 18px normal
        
        # Large text sizes
        assert is_large_text(24)  # 24px normal (large)
        assert is_large_text(30)  # 30px normal (large)
        
        # Bold text with lower threshold
        assert not is_large_text(14, "normal")  # 14px normal
        assert is_large_text(14, "bold")  # 14px bold (large)
        assert is_large_text(18, "bold")  # 18px bold (large)
        
        # String inputs
        assert not is_large_text("16px")
        assert is_large_text("24px")
        assert is_large_text("18px", "bold")
    
    def test_get_contrast_threshold(self):
        """Test WCAG contrast threshold retrieval."""
        # AA level thresholds
        assert get_contrast_threshold(False, "AA") == 4.5  # Normal text
        assert get_contrast_threshold(True, "AA") == 3.0   # Large text
        
        # AAA level thresholds
        assert get_contrast_threshold(False, "AAA") == 7.0  # Normal text
        assert get_contrast_threshold(True, "AAA") == 4.5   # Large text
        
        # Default to AA level
        assert get_contrast_threshold(False) == 4.5
        assert get_contrast_threshold(True) == 3.0
    
    def test_known_contrast_ratios(self):
        """Test contrast ratios for known color pairs."""
        # These are well-known contrast ratios
        test_cases = [
            ("#000000", "#ffffff", 21.0),  # Black on white
            ("#ffffff", "#000000", 21.0),  # White on black
            ("#000000", "#808080", 5.0),   # Black on gray
            ("#ffffff", "#808080", 5.0),   # White on gray
        ]
        
        for color1, color2, expected_ratio in test_cases:
            actual_ratio = contrast_ratio(color1, color2)
            assert abs(actual_ratio - expected_ratio) < 0.1, \
                f"Expected {expected_ratio}, got {actual_ratio} for {color1} on {color2}"
