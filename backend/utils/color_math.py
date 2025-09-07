"""
Color mathematics utilities for contrast ratio calculations and color space conversions.
"""

import math
from typing import Tuple, Union
from dataclasses import dataclass

@dataclass
class RGB:
    """RGB color representation."""
    r: int
    g: int
    b: int
    
    def __post_init__(self):
        self.r = max(0, min(255, self.r))
        self.g = max(0, min(255, self.g))
        self.b = max(0, min(255, self.b))

@dataclass
class HSL:
    """HSL color representation."""
    h: float  # 0-360
    s: float  # 0-1
    l: float  # 0-1

def hex_to_rgb(hex_color: str) -> RGB:
    """Convert hex color to RGB."""
    hex_color = hex_color.lstrip('#')
    if len(hex_color) == 3:
        hex_color = ''.join([c*2 for c in hex_color])
    
    try:
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        return RGB(r, g, b)
    except ValueError:
        raise ValueError(f"Invalid hex color: {hex_color}")

def rgb_to_hex(rgb: RGB) -> str:
    """Convert RGB to hex color."""
    return f"#{rgb.r:02x}{rgb.g:02x}{rgb.b:02x}"

def rgb_to_hsl(rgb: RGB) -> HSL:
    """Convert RGB to HSL."""
    r, g, b = rgb.r / 255.0, rgb.g / 255.0, rgb.b / 255.0
    
    max_val = max(r, g, b)
    min_val = min(r, g, b)
    diff = max_val - min_val
    
    # Lightness
    l = (max_val + min_val) / 2.0
    
    if diff == 0:
        # Achromatic
        h = s = 0
    else:
        # Saturation
        s = diff / (2 - max_val - min_val) if l < 0.5 else diff / (max_val + min_val)
        
        # Hue
        if max_val == r:
            h = (g - b) / diff + (6 if g < b else 0)
        elif max_val == g:
            h = (b - r) / diff + 2
        else:
            h = (r - g) / diff + 4
        h /= 6
    
    return HSL(h * 360, s, l)

def hsl_to_rgb(hsl: HSL) -> RGB:
    """Convert HSL to RGB."""
    h = hsl.h / 360.0
    s = hsl.s
    l = hsl.l
    
    if s == 0:
        # Achromatic
        r = g = b = l
    else:
        def hue_to_rgb(p, q, t):
            if t < 0:
                t += 1
            if t > 1:
                t -= 1
            if t < 1/6:
                return p + (q - p) * 6 * t
            if t < 1/2:
                return q
            if t < 2/3:
                return p + (q - p) * (2/3 - t) * 6
            return p
        
        q = l * (1 + s) if l < 0.5 else l + s - l * s
        p = 2 * l - q
        r = hue_to_rgb(p, q, h + 1/3)
        g = hue_to_rgb(p, q, h)
        b = hue_to_rgb(p, q, h - 1/3)
    
    return RGB(int(r * 255), int(g * 255), int(b * 255))

def get_relative_luminance(rgb: RGB) -> float:
    """Calculate relative luminance according to WCAG 2.1."""
    def linearize(value):
        value = value / 255.0
        return value / 12.92 if value <= 0.03928 else ((value + 0.055) / 1.055) ** 2.4
    
    r_linear = linearize(rgb.r)
    g_linear = linearize(rgb.g)
    b_linear = linearize(rgb.b)
    
    return 0.2126 * r_linear + 0.7152 * g_linear + 0.0722 * b_linear

def get_contrast_ratio(color1: RGB, color2: RGB) -> float:
    """Calculate contrast ratio between two colors."""
    l1 = get_relative_luminance(color1)
    l2 = get_relative_luminance(color2)
    
    lighter = max(l1, l2)
    darker = min(l1, l2)
    
    return (lighter + 0.05) / (darker + 0.05)

def parse_css_color(color_str: str) -> RGB:
    """Parse CSS color string to RGB."""
    color_str = color_str.strip().lower()
    
    # Hex colors
    if color_str.startswith('#'):
        return hex_to_rgb(color_str)
    
    # RGB/RGBA colors
    if color_str.startswith('rgb'):
        # Extract numbers from rgb(r,g,b) or rgba(r,g,b,a)
        import re
        numbers = re.findall(r'\d+', color_str)
        if len(numbers) >= 3:
            return RGB(int(numbers[0]), int(numbers[1]), int(numbers[2]))
    
    # Named colors (basic set)
    named_colors = {
        'black': RGB(0, 0, 0),
        'white': RGB(255, 255, 255),
        'red': RGB(255, 0, 0),
        'green': RGB(0, 128, 0),
        'blue': RGB(0, 0, 255),
        'yellow': RGB(255, 255, 0),
        'cyan': RGB(0, 255, 255),
        'magenta': RGB(255, 0, 255),
        'gray': RGB(128, 128, 128),
        'grey': RGB(128, 128, 128),
        'silver': RGB(192, 192, 192),
        'maroon': RGB(128, 0, 0),
        'olive': RGB(128, 128, 0),
        'lime': RGB(0, 255, 0),
        'aqua': RGB(0, 255, 255),
        'teal': RGB(0, 128, 128),
        'navy': RGB(0, 0, 128),
        'fuchsia': RGB(255, 0, 255),
        'purple': RGB(128, 0, 128),
        'orange': RGB(255, 165, 0),
        'pink': RGB(255, 192, 203),
        'brown': RGB(165, 42, 42),
        'transparent': RGB(0, 0, 0)  # Will be handled by opacity
    }
    
    if color_str in named_colors:
        return named_colors[color_str]
    
    # Default to black if parsing fails
    return RGB(0, 0, 0)

def apply_opacity(foreground: RGB, background: RGB, opacity: float) -> RGB:
    """Apply opacity to foreground color over background."""
    alpha = max(0, min(1, opacity))
    
    r = int(foreground.r * alpha + background.r * (1 - alpha))
    g = int(foreground.g * alpha + background.g * (1 - alpha))
    b = int(foreground.b * alpha + background.b * (1 - alpha))
    
    return RGB(r, g, b)

def is_large_text(font_size: Union[int, float], font_weight: str = "normal") -> bool:
    """Determine if text is considered large according to WCAG."""
    size = float(font_size)
    weight = font_weight.lower()
    
    # Large text: 18pt+ or 14pt+ bold
    if weight in ['bold', 'bolder', '700', '800', '900']:
        return size >= 14
    else:
        return size >= 18

def get_contrast_threshold(text_size: Union[int, float], font_weight: str = "normal") -> float:
    """Get the appropriate contrast threshold for text size and weight."""
    if is_large_text(text_size, font_weight):
        return 3.0  # AA level for large text
    else:
        return 4.5  # AA level for normal text

def suggest_contrast_fix(foreground: RGB, background: RGB, target_ratio: float) -> RGB:
    """Suggest a new foreground color to meet the target contrast ratio."""
    current_ratio = get_contrast_ratio(foreground, background)
    
    if current_ratio >= target_ratio:
        return foreground
    
    # Convert to HSL for easier manipulation
    fg_hsl = rgb_to_hsl(foreground)
    bg_luminance = get_relative_luminance(background)
    
    # Calculate required luminance for target ratio
    if bg_luminance > 0.5:  # Light background
        required_luminance = (bg_luminance + 0.05) / target_ratio - 0.05
    else:  # Dark background
        required_luminance = (bg_luminance + 0.05) * target_ratio - 0.05
    
    required_luminance = max(0, min(1, required_luminance))
    
    # Adjust lightness to meet requirement
    fg_hsl.l = required_luminance
    
    return hsl_to_rgb(fg_hsl)

def get_color_distance(color1: RGB, color2: RGB) -> float:
    """Calculate perceptual color distance using Euclidean distance in RGB space."""
    return math.sqrt(
        (color1.r - color2.r) ** 2 +
        (color1.g - color2.g) ** 2 +
        (color1.b - color2.b) ** 2
    )

def get_accessible_color_palette(base_color: RGB, background: RGB, target_ratio: float = 4.5) -> list[RGB]:
    """Generate a palette of accessible colors based on a base color."""
    palette = []
    base_hsl = rgb_to_hsl(base_color)
    
    # Generate variations by adjusting lightness
    for lightness in [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]:
        test_hsl = HSL(base_hsl.h, base_hsl.s, lightness)
        test_rgb = hsl_to_rgb(test_hsl)
        
        if get_contrast_ratio(test_rgb, background) >= target_ratio:
            palette.append(test_rgb)
    
    return palette

def get_contrast_suggestions(foreground: RGB, background: RGB, target_ratio: float = 4.5) -> list[dict]:
    """Get multiple contrast improvement suggestions for a color pair."""
    suggestions = []
    current_ratio = get_contrast_ratio(foreground, background)
    
    if current_ratio >= target_ratio:
        return [{
            "type": "current",
            "color": foreground,
            "ratio": current_ratio,
            "description": "Current color already meets contrast requirements"
        }]
    
    # Suggestion 1: Darken the foreground
    darker_fg = suggest_contrast_fix(foreground, background, target_ratio)
    darker_ratio = get_contrast_ratio(darker_fg, background)
    suggestions.append({
        "type": "darken_foreground",
        "color": darker_fg,
        "ratio": darker_ratio,
        "description": f"Darken foreground to achieve {darker_ratio:.1f}:1 contrast"
    })
    
    # Suggestion 2: Lighten the background
    bg_hsl = rgb_to_hsl(background)
    if bg_hsl.l > 0.5:  # Light background - make it lighter
        lighter_bg_hsl = HSL(bg_hsl.h, bg_hsl.s, min(0.95, bg_hsl.l + 0.2))
    else:  # Dark background - make it darker
        lighter_bg_hsl = HSL(bg_hsl.h, bg_hsl.s, max(0.05, bg_hsl.l - 0.2))
    
    lighter_bg = hsl_to_rgb(lighter_bg_hsl)
    lighter_ratio = get_contrast_ratio(foreground, lighter_bg)
    suggestions.append({
        "type": "adjust_background",
        "color": lighter_bg,
        "ratio": lighter_ratio,
        "description": f"Adjust background to achieve {lighter_ratio:.1f}:1 contrast"
    })
    
    # Suggestion 3: High contrast alternatives
    high_contrast_colors = [
        RGB(0, 0, 0),      # Black
        RGB(255, 255, 255), # White
        RGB(0, 0, 139),    # Dark blue
        RGB(139, 0, 0),    # Dark red
        RGB(0, 100, 0),    # Dark green
    ]
    
    for hc_color in high_contrast_colors:
        hc_ratio = get_contrast_ratio(hc_color, background)
        if hc_ratio >= target_ratio:
            suggestions.append({
                "type": "high_contrast",
                "color": hc_color,
                "ratio": hc_ratio,
                "description": f"Use high contrast color for {hc_ratio:.1f}:1 contrast"
            })
    
    # Sort by contrast ratio (highest first)
    suggestions.sort(key=lambda x: x["ratio"], reverse=True)
    
    return suggestions
