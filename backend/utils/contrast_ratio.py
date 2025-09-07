"""
Contrast ratio calculation utilities specifically for WCAG compliance.
"""

from typing import Tuple, Optional, Dict, Any
from .color_math import RGB, get_contrast_ratio, get_relative_luminance, is_large_text, get_contrast_threshold
from .wcag_constants import CONTRAST_THRESHOLDS, WCAGLevel

class ContrastResult:
    """Result of contrast ratio evaluation."""
    
    def __init__(self, 
                 foreground: RGB, 
                 background: RGB, 
                 ratio: float, 
                 text_size: float, 
                 font_weight: str = "normal",
                 wcag_level: WCAGLevel = WCAGLevel.AA):
        self.foreground = foreground
        self.background = background
        self.ratio = ratio
        self.text_size = text_size
        self.font_weight = font_weight
        self.wcag_level = wcag_level
        
        # Determine if text is large
        self.is_large_text = is_large_text(text_size, font_weight)
        
        # Get appropriate threshold
        if self.is_large_text:
            self.required_ratio = CONTRAST_THRESHOLDS[wcag_level]["large_text"]
        else:
            self.required_ratio = CONTRAST_THRESHOLDS[wcag_level]["normal_text"]
        
        # Check compliance
        self.passes = self.ratio >= self.required_ratio
        self.severity = self._calculate_severity()
    
    def _calculate_severity(self) -> str:
        """Calculate severity based on how far below threshold the ratio is."""
        if self.passes:
            return "pass"
        
        deficit = self.required_ratio - self.ratio
        
        if deficit <= 0.5:
            return "low"
        elif deficit <= 1.0:
            return "medium"
        elif deficit <= 2.0:
            return "high"
        else:
            return "critical"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "foreground": {
                "r": self.foreground.r,
                "g": self.foreground.g,
                "b": self.foreground.b,
                "hex": f"#{self.foreground.r:02x}{self.foreground.g:02x}{self.foreground.b:02x}"
            },
            "background": {
                "r": self.background.r,
                "g": self.background.g,
                "b": self.background.b,
                "hex": f"#{self.background.r:02x}{self.background.g:02x}{self.background.b:02x}"
            },
            "ratio": round(self.ratio, 2),
            "required_ratio": self.required_ratio,
            "text_size": self.text_size,
            "font_weight": self.font_weight,
            "is_large_text": self.is_large_text,
            "wcag_level": self.wcag_level.value,
            "passes": self.passes,
            "severity": self.severity
        }

def evaluate_contrast(foreground: RGB, 
                     background: RGB, 
                     text_size: float = 16, 
                     font_weight: str = "normal",
                     wcag_level: WCAGLevel = WCAGLevel.AA) -> ContrastResult:
    """Evaluate contrast ratio for given colors and text properties."""
    ratio = get_contrast_ratio(foreground, background)
    return ContrastResult(foreground, background, ratio, text_size, font_weight, wcag_level)

def evaluate_non_text_contrast(foreground: RGB, 
                              background: RGB, 
                              wcag_level: WCAGLevel = WCAGLevel.AA) -> ContrastResult:
    """Evaluate contrast ratio for non-text elements (WCAG 1.4.11)."""
    ratio = get_contrast_ratio(foreground, background)
    required_ratio = CONTRAST_THRESHOLDS[wcag_level]["non_text"]
    
    # Create a mock result for non-text elements
    result = ContrastResult(foreground, background, ratio, 16, "normal", wcag_level)
    result.required_ratio = required_ratio
    result.is_large_text = False  # Not applicable for non-text
    result.passes = ratio >= required_ratio
    result.severity = result._calculate_severity()
    
    return result

def find_contrast_issues_in_css(css_content: str, 
                               html_content: str = "", 
                               wcag_level: WCAGLevel = WCAGLevel.AA) -> list[Dict[str, Any]]:
    """Find contrast issues in CSS content."""
    import re
    from .color_math import parse_css_color
    
    issues = []
    
    # Extract color declarations from CSS
    color_pattern = r'(color|background-color|border-color|outline-color)\s*:\s*([^;]+)'
    color_matches = re.finditer(color_pattern, css_content, re.IGNORECASE)
    
    # Simple background color detection (this would be more sophisticated in practice)
    background_colors = []
    bg_pattern = r'background(?:-color)?\s*:\s*([^;]+)'
    bg_matches = re.finditer(bg_pattern, css_content, re.IGNORECASE)
    
    for match in bg_matches:
        try:
            bg_color = parse_css_color(match.group(1).strip())
            background_colors.append(bg_color)
        except:
            continue
    
    # Default background if none found
    if not background_colors:
        background_colors = [RGB(255, 255, 255)]  # White default
    
    # Check each color declaration
    for match in color_matches:
        property_name = match.group(1).lower()
        color_value = match.group(2).strip()
        
        try:
            fg_color = parse_css_color(color_value)
            
            # Check against all background colors
            for bg_color in background_colors:
                if property_name == "color":  # Text color
                    result = evaluate_contrast(fg_color, bg_color, wcag_level=wcag_level)
                else:  # Non-text color
                    result = evaluate_non_text_contrast(fg_color, bg_color, wcag_level=wcag_level)
                
                if not result.passes:
                    issues.append({
                        "property": property_name,
                        "color_value": color_value,
                        "result": result.to_dict(),
                        "line_number": css_content[:match.start()].count('\n') + 1,
                        "column_number": match.start() - css_content.rfind('\n', 0, match.start()) - 1
                    })
        
        except ValueError:
            # Skip invalid color values
            continue
    
    return issues

def get_contrast_suggestions(foreground: RGB, 
                           background: RGB, 
                           target_ratio: float,
                           preserve_hue: bool = True) -> Dict[str, Any]:
    """Get suggestions for improving contrast ratio."""
    from .color_math import suggest_contrast_fix, rgb_to_hsl, hsl_to_rgb
    
    current_ratio = get_contrast_ratio(foreground, background)
    
    suggestions = {
        "current_ratio": round(current_ratio, 2),
        "target_ratio": target_ratio,
        "needs_improvement": current_ratio < target_ratio,
        "suggestions": []
    }
    
    if current_ratio >= target_ratio:
        return suggestions
    
    # Suggestion 1: Darken the foreground
    if preserve_hue:
        suggested_fg = suggest_contrast_fix(foreground, background, target_ratio)
        suggested_ratio = get_contrast_ratio(suggested_fg, background)
        
        suggestions["suggestions"].append({
            "type": "adjust_foreground",
            "description": "Darken the foreground color",
            "original_color": f"#{foreground.r:02x}{foreground.g:02x}{foreground.b:02x}",
            "suggested_color": f"#{suggested_fg.r:02x}{suggested_fg.g:02x}{suggested_fg.b:02x}",
            "new_ratio": round(suggested_ratio, 2),
            "improvement": round(suggested_ratio - current_ratio, 2)
        })
    
    # Suggestion 2: Lighten the background
    fg_luminance = get_relative_luminance(foreground)
    if fg_luminance < 0.5:  # Dark foreground
        # Calculate required background luminance
        required_bg_luminance = (fg_luminance + 0.05) / target_ratio - 0.05
        required_bg_luminance = max(0, min(1, required_bg_luminance))
        
        if required_bg_luminance > get_relative_luminance(background):
            bg_hsl = rgb_to_hsl(background)
            bg_hsl.l = required_bg_luminance
            suggested_bg = hsl_to_rgb(bg_hsl)
            suggested_ratio = get_contrast_ratio(foreground, suggested_bg)
            
            suggestions["suggestions"].append({
                "type": "adjust_background",
                "description": "Lighten the background color",
                "original_color": f"#{background.r:02x}{background.g:02x}{background.b:02x}",
                "suggested_color": f"#{suggested_bg.r:02x}{suggested_bg.g:02x}{suggested_bg.b:02x}",
                "new_ratio": round(suggested_ratio, 2),
                "improvement": round(suggested_ratio - current_ratio, 2)
            })
    
    # Suggestion 3: Add outline or shadow
    suggestions["suggestions"].append({
        "type": "add_outline",
        "description": "Add a contrasting outline or shadow",
        "css_example": f"text-shadow: 1px 1px 2px #{background.r:02x}{background.g:02x}{background.b:02x};",
        "note": "This can help improve contrast without changing colors"
    })
    
    return suggestions

def batch_contrast_evaluation(color_pairs: list[Tuple[RGB, RGB, float, str]], 
                            wcag_level: WCAGLevel = WCAGLevel.AA) -> list[ContrastResult]:
    """Evaluate multiple color pairs for contrast compliance."""
    results = []
    
    for fg, bg, size, weight in color_pairs:
        result = evaluate_contrast(fg, bg, size, weight, wcag_level)
        results.append(result)
    
    return results
