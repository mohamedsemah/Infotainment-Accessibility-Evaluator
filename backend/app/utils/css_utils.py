"""
CSS parsing utilities for accessibility analysis.
Provides deterministic checks for font sizes, focus indicators, and target sizes.
"""

import re
from typing import Dict, List, Optional, Tuple, Union


def parse_css_rules(css_content: str) -> Dict[str, Dict[str, str]]:
    """
    Parse CSS content into a dictionary of selectors and their properties.
    
    Args:
        css_content: Raw CSS content
        
    Returns:
        Dictionary mapping selectors to property dictionaries
    """
    rules = {}
    
    # Remove comments
    css_content = re.sub(r'/\*.*?\*/', '', css_content, flags=re.DOTALL)
    
    # Find CSS rules
    rule_pattern = r'([^{]+)\{([^}]+)\}'
    matches = re.findall(rule_pattern, css_content, re.DOTALL)
    
    for selector, properties in matches:
        selector = selector.strip()
        props = {}
        
        # Parse properties
        prop_pattern = r'([^:]+):\s*([^;]+);?'
        prop_matches = re.findall(prop_pattern, properties)
        
        for prop, value in prop_matches:
            prop = prop.strip().lower()
            value = value.strip()
            props[prop] = value
        
        if props:
            rules[selector] = props
    
    return rules


def extract_font_size(properties: Dict[str, str]) -> Optional[float]:
    """
    Extract font size in pixels from CSS properties.
    
    Args:
        properties: Dictionary of CSS properties
        
    Returns:
        Font size in pixels or None if not found/parseable
    """
    font_size = properties.get('font-size')
    if not font_size:
        return None
    
    # Remove units and convert to float
    size_str = re.sub(r'[^\d.]', '', font_size)
    try:
        return float(size_str)
    except ValueError:
        return None


def extract_font_weight(properties: Dict[str, str]) -> str:
    """
    Extract font weight from CSS properties.
    
    Args:
        properties: Dictionary of CSS properties
        
    Returns:
        Font weight string (defaults to "normal")
    """
    return properties.get('font-weight', 'normal').lower()


def extract_dimensions(properties: Dict[str, str]) -> Tuple[Optional[float], Optional[float]]:
    """
    Extract width and height from CSS properties.
    
    Args:
        properties: Dictionary of CSS properties
        
    Returns:
        Tuple of (width, height) in pixels, or (None, None) if not found
    """
    def parse_dimension(dim_str: str) -> Optional[float]:
        if not dim_str:
            return None
        size_str = re.sub(r'[^\d.]', '', dim_str)
        try:
            return float(size_str)
        except ValueError:
            return None
    
    width = parse_dimension(properties.get('width', ''))
    height = parse_dimension(properties.get('height', ''))
    
    return width, height


def has_focus_indicator(properties: Dict[str, str]) -> bool:
    """
    Check if CSS properties include focus indicators.
    
    Args:
        properties: Dictionary of CSS properties
        
    Returns:
        True if focus indicators are present
    """
    # Check for explicit focus styles
    focus_props = [
        'outline', 'outline-color', 'outline-style', 'outline-width',
        'box-shadow', 'border', 'border-color'
    ]
    
    for prop in focus_props:
        if prop in properties and properties[prop].strip() and properties[prop] != 'none':
            return True
    
    # Check for :focus pseudo-class (would need more complex parsing)
    return False


def get_target_size(properties: Dict[str, str]) -> Optional[float]:
    """
    Get the minimum target size from CSS properties.
    
    Args:
        properties: Dictionary of CSS properties
        
    Returns:
        Minimum dimension in pixels or None if not determinable
    """
    width, height = extract_dimensions(properties)
    
    if width is not None and height is not None:
        return min(width, height)
    elif width is not None:
        return width
    elif height is not None:
        return height
    
    return None


def find_css_rules_for_selector(css_rules: Dict[str, Dict[str, str]], 
                               selector: str) -> List[Dict[str, str]]:
    """
    Find CSS rules that match a given selector.
    
    Args:
        css_rules: Parsed CSS rules
        selector: CSS selector to match
        
    Returns:
        List of matching rule properties
    """
    matching_rules = []
    
    for rule_selector, properties in css_rules.items():
        # Simple selector matching (could be enhanced for complex selectors)
        if selector in rule_selector or rule_selector in selector:
            matching_rules.append(properties)
    
    return matching_rules


def extract_color_properties(properties: Dict[str, str]) -> Tuple[Optional[str], Optional[str]]:
    """
    Extract foreground and background colors from CSS properties.
    
    Args:
        properties: Dictionary of CSS properties
        
    Returns:
        Tuple of (foreground_color, background_color)
    """
    foreground = properties.get('color')
    background = properties.get('background-color') or properties.get('background')
    
    return foreground, background


def is_keyboard_accessible(properties: Dict[str, str]) -> bool:
    """
    Check if element appears to be keyboard accessible based on CSS.
    
    Args:
        properties: Dictionary of CSS properties
        
    Returns:
        True if element appears keyboard accessible
    """
    # Check for pointer-events: none (would make element not accessible)
    pointer_events = properties.get('pointer-events', '').lower()
    if pointer_events == 'none':
        return False
    
    # Check for display: none or visibility: hidden
    display = properties.get('display', '').lower()
    visibility = properties.get('visibility', '').lower()
    
    if display == 'none' or visibility == 'hidden':
        return False
    
    return True


def parse_css_file(file_content: str) -> Dict[str, Dict[str, str]]:
    """
    Parse a CSS file and return structured rules.
    
    Args:
        file_content: Raw CSS file content
        
    Returns:
        Dictionary of parsed CSS rules
    """
    return parse_css_rules(file_content)
