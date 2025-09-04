"""
Deterministic color contrast calculations for WCAG compliance.
Implements the WCAG 2.2 contrast ratio formula.
"""

import re
from typing import Optional, Tuple, Union


def hex_to_rgb(hex_color: str) -> Optional[Tuple[int, int, int]]:
    """Convert hex color to RGB tuple."""
    hex_color = hex_color.lstrip('#')
    
    if len(hex_color) == 3:
        # Short form: #RGB -> #RRGGBB
        hex_color = ''.join([c*2 for c in hex_color])
    elif len(hex_color) != 6:
        return None
    
    try:
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    except ValueError:
        return None


def rgb_to_rgb(rgb_str: str) -> Optional[Tuple[int, int, int]]:
    """Parse RGB/RGBA string to RGB tuple."""
    # Match rgb(r, g, b) or rgba(r, g, b, a)
    match = re.match(r'rgba?\((\d+),\s*(\d+),\s*(\d+)(?:,\s*[\d.]+)?\)', rgb_str)
    if match:
        return tuple(int(x) for x in match.groups())
    return None


def parse_color(color: str) -> Optional[Tuple[int, int, int]]:
    """Parse various color formats to RGB tuple."""
    color = color.strip().lower()
    
    # Handle hex colors
    if color.startswith('#'):
        return hex_to_rgb(color)
    
    # Handle rgb/rgba
    if color.startswith('rgb'):
        return rgb_to_rgb(color)
    
    # Handle named colors (basic set)
    named_colors = {
        'black': (0, 0, 0),
        'white': (255, 255, 255),
        'red': (255, 0, 0),
        'green': (0, 128, 0),
        'blue': (0, 0, 255),
        'yellow': (255, 255, 0),
        'cyan': (0, 255, 255),
        'magenta': (255, 0, 255),
        'gray': (128, 128, 128),
        'grey': (128, 128, 128),
        'silver': (192, 192, 192),
        'maroon': (128, 0, 0),
        'olive': (128, 128, 0),
        'lime': (0, 255, 0),
        'aqua': (0, 255, 255),
        'teal': (0, 128, 128),
        'navy': (0, 0, 128),
        'fuchsia': (255, 0, 255),
        'purple': (128, 0, 128),
    }
    
    return named_colors.get(color)


def relative_luminance(rgb: Tuple[int, int, int]) -> float:
    """
    Calculate relative luminance according to WCAG 2.2.
    
    Args:
        rgb: RGB tuple with values 0-255
        
    Returns:
        Relative luminance value between 0 and 1
    """
    def linearize_component(c: int) -> float:
        """Linearize RGB component for luminance calculation."""
        c_norm = c / 255.0
        if c_norm <= 0.03928:
            return c_norm / 12.92
        else:
            return ((c_norm + 0.055) / 1.055) ** 2.4
    
    r, g, b = rgb
    return 0.2126 * linearize_component(r) + 0.7152 * linearize_component(g) + 0.0722 * linearize_component(b)


def contrast_ratio(color1: Union[str, Tuple[int, int, int]], 
                  color2: Union[str, Tuple[int, int, int]]) -> Optional[float]:
    """
    Calculate contrast ratio between two colors.
    
    Args:
        color1: First color (hex string, rgb string, or RGB tuple)
        color2: Second color (hex string, rgb string, or RGB tuple)
        
    Returns:
        Contrast ratio (1-21) or None if colors cannot be parsed
    """
    # Parse colors to RGB tuples
    if isinstance(color1, str):
        rgb1 = parse_color(color1)
    else:
        rgb1 = color1
        
    if isinstance(color2, str):
        rgb2 = parse_color(color2)
    else:
        rgb2 = color2
    
    if rgb1 is None or rgb2 is None:
        return None
    
    # Calculate relative luminances
    l1 = relative_luminance(rgb1)
    l2 = relative_luminance(rgb2)
    
    # Ensure l1 is the lighter color
    if l1 < l2:
        l1, l2 = l2, l1
    
    # Calculate contrast ratio
    return (l1 + 0.05) / (l2 + 0.05)


def is_large_text(font_size: Union[str, int, float], font_weight: str = "normal") -> bool:
    """
    Determine if text qualifies as "large text" for WCAG contrast requirements.
    
    Args:
        font_size: Font size in pixels or CSS units
        font_weight: Font weight (normal, bold, etc.)
        
    Returns:
        True if text qualifies as large text
    """
    # Parse font size
    if isinstance(font_size, str):
        # Remove units and convert to float
        size_str = re.sub(r'[^\d.]', '', font_size)
        try:
            size_px = float(size_str)
        except ValueError:
            return False
    else:
        size_px = float(font_size)
    
    # Check if bold
    is_bold = font_weight.lower() in ['bold', 'bolder', '700', '800', '900']
    
    # Large text criteria:
    # - ≥18pt (≈24px) normal weight
    # - ≥14pt (≈18.67px) bold weight
    if is_bold:
        return size_px >= 18.67
    else:
        return size_px >= 24.0


def get_contrast_threshold(is_large_text: bool, level: str = "AA") -> float:
    """
    Get the required contrast threshold for WCAG compliance.
    
    Args:
        is_large_text: Whether the text qualifies as large text
        level: WCAG level ("AA" or "AAA")
        
    Returns:
        Required contrast ratio
    """
    if level == "AAA":
        return 7.0 if not is_large_text else 4.5
    else:  # AA level
        return 4.5 if not is_large_text else 3.0
