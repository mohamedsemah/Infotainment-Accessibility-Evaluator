"""
CSS computation helper for calculating computed styles and resolving values.
"""

import re
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import tinycss2
from tinycss2 import parse_stylesheet, parse_component_value_list
from utils.color_math import parse_css_color, RGB
from utils.contrast_ratio import calculate_contrast_ratio

@dataclass
class ComputedStyle:
    """Represents computed CSS styles for an element."""
    color: Optional[str] = None
    background_color: Optional[str] = None
    border_color: Optional[str] = None
    outline_color: Optional[str] = None
    font_size: Optional[str] = None
    font_weight: Optional[str] = None
    font_family: Optional[str] = None
    line_height: Optional[str] = None
    text_decoration: Optional[str] = None
    text_transform: Optional[str] = None
    opacity: Optional[str] = None
    display: Optional[str] = None
    visibility: Optional[str] = None
    position: Optional[str] = None
    z_index: Optional[str] = None
    width: Optional[str] = None
    height: Optional[str] = None
    margin: Optional[str] = None
    padding: Optional[str] = None
    border: Optional[str] = None
    border_radius: Optional[str] = None
    box_shadow: Optional[str] = None
    text_shadow: Optional[str] = None
    animation: Optional[str] = None
    transition: Optional[str] = None
    transform: Optional[str] = None
    filter: Optional[str] = None
    backdrop_filter: Optional[str] = None

class CSSComputeHelper:
    """Helper for computing CSS styles and resolving values."""
    
    def __init__(self):
        self.default_styles = {
            'color': '#000000',
            'background-color': 'transparent',
            'font-size': '16px',
            'font-weight': 'normal',
            'opacity': '1',
            'display': 'inline',
            'visibility': 'visible'
        }
        
        # CSS property inheritance rules
        self.inherited_properties = {
            'color', 'font-family', 'font-size', 'font-weight', 'font-style',
            'line-height', 'text-align', 'text-decoration', 'text-transform',
            'letter-spacing', 'word-spacing', 'white-space', 'direction',
            'unicode-bidi', 'visibility'
        }
        
        # CSS property reset rules
        self.reset_properties = {
            'margin', 'padding', 'border', 'background', 'color', 'font',
            'line-height', 'text-decoration', 'text-transform', 'letter-spacing',
            'word-spacing', 'white-space', 'direction', 'unicode-bidi'
        }
    
    async def compute_styles(self, element, css_files: List[str]) -> ComputedStyle:
        """Compute styles for an element from CSS files."""
        computed = ComputedStyle()
        
        # Parse all CSS files
        stylesheets = []
        for css_file in css_files:
            try:
                with open(css_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    stylesheet = parse_stylesheet(content)
                    stylesheets.append(stylesheet)
            except Exception as e:
                print(f"Error parsing CSS file {css_file}: {e}")
                continue
        
        # Get element's inline styles
        inline_styles = self._get_inline_styles(element)
        
        # Get element's class and ID
        element_classes = self._get_element_classes(element)
        element_id = self._get_element_id(element)
        element_tag = self._get_element_tag(element)
        
        # Find matching CSS rules
        matching_rules = self._find_matching_rules(
            element_tag, element_classes, element_id, stylesheets
        )
        
        # Apply styles in order of specificity
        for rule in matching_rules:
            self._apply_rule_to_computed(rule, computed)
        
        # Apply inline styles (highest specificity)
        self._apply_inline_styles(inline_styles, computed)
        
        # Resolve computed values
        self._resolve_computed_values(computed)
        
        return computed
    
    def _get_inline_styles(self, element) -> Dict[str, str]:
        """Get inline styles from element."""
        if hasattr(element, 'get') and element.get('style'):
            styles = {}
            for style in element['style'].split(';'):
                if ':' in style:
                    prop, value = style.split(':', 1)
                    styles[prop.strip()] = value.strip()
            return styles
        return {}
    
    def _get_element_classes(self, element) -> List[str]:
        """Get element classes."""
        if hasattr(element, 'get') and element.get('class'):
            classes = element['class']
            if isinstance(classes, list):
                return classes
            return classes.split()
        return []
    
    def _get_element_id(self, element) -> Optional[str]:
        """Get element ID."""
        if hasattr(element, 'get'):
            return element.get('id')
        return None
    
    def _get_element_tag(self, element) -> str:
        """Get element tag name."""
        if hasattr(element, 'name'):
            return element.name
        return 'unknown'
    
    def _find_matching_rules(self, tag: str, classes: List[str], element_id: Optional[str], stylesheets: List) -> List[Dict]:
        """Find CSS rules that match the element."""
        matching_rules = []
        
        for stylesheet in stylesheets:
            for rule in stylesheet:
                if hasattr(rule, 'prelude') and hasattr(rule, 'content'):
                    selectors = self._extract_selectors(rule.prelude)
                    
                    for selector in selectors:
                        if self._selector_matches(selector, tag, classes, element_id):
                            specificity = self._calculate_specificity(selector)
                            matching_rules.append({
                                'selector': selector,
                                'properties': self._extract_properties(rule.content),
                                'specificity': specificity
                            })
        
        # Sort by specificity (highest first)
        matching_rules.sort(key=lambda x: x['specificity'], reverse=True)
        
        return matching_rules
    
    def _extract_selectors(self, prelude) -> List[str]:
        """Extract CSS selectors from rule prelude."""
        selectors = []
        
        if isinstance(prelude, list):
            current_selector = ""
            for token in prelude:
                if hasattr(token, 'type'):
                    if token.type == 'ident':
                        if current_selector:
                            current_selector += " " + token.value
                        else:
                            current_selector = token.value
                    elif token.type == 'literal' and token.value == ',':
                        if current_selector:
                            selectors.append(current_selector.strip())
                            current_selector = ""
                    elif token.type == 'whitespace':
                        if current_selector:
                            current_selector += " "
            
            if current_selector:
                selectors.append(current_selector.strip())
        
        return selectors
    
    def _selector_matches(self, selector: str, tag: str, classes: List[str], element_id: Optional[str]) -> bool:
        """Check if a CSS selector matches the element."""
        # Simple selector matching implementation
        # This is a simplified version - a full implementation would be much more complex
        
        # Tag selector
        if selector == tag:
            return True
        
        # ID selector
        if selector.startswith('#') and element_id:
            return selector[1:] == element_id
        
        # Class selector
        if selector.startswith('.') and classes:
            class_name = selector[1:]
            return class_name in classes
        
        # Combined selectors (simplified)
        if ' ' in selector:
            parts = selector.split()
            # For now, just check if any part matches
            for part in parts:
                if self._selector_matches(part, tag, classes, element_id):
                    return True
        
        return False
    
    def _calculate_specificity(self, selector: str) -> Tuple[int, int, int]:
        """Calculate CSS specificity (inline, IDs, classes/elements)."""
        inline = 0
        ids = 0
        classes = 0
        
        # Count IDs
        ids = selector.count('#')
        
        # Count classes and attributes
        classes = selector.count('.') + selector.count('[') + selector.count(':')
        
        # Count elements (simplified)
        elements = len(re.findall(r'[a-zA-Z][a-zA-Z0-9]*', selector)) - ids - classes
        
        return (inline, ids, classes + elements)
    
    def _extract_properties(self, content) -> Dict[str, str]:
        """Extract CSS properties from rule content."""
        properties = {}
        
        if isinstance(content, list):
            i = 0
            while i < len(content):
                token = content[i]
                
                if hasattr(token, 'type') and token.type == 'ident':
                    prop_name = token.value
                    
                    # Look for colon
                    i += 1
                    while i < len(content) and hasattr(content[i], 'type') and content[i].type in ['whitespace', 'literal']:
                        if hasattr(content[i], 'type') and content[i].type == 'literal' and content[i].value == ':':
                            break
                        i += 1
                    
                    # Skip whitespace after colon
                    i += 1
                    while i < len(content) and hasattr(content[i], 'type') and content[i].type == 'whitespace':
                        i += 1
                    
                    # Extract value
                    value_tokens = []
                    while i < len(content) and not (hasattr(content[i], 'type') and content[i].type == 'literal' and content[i].value == ';'):
                        value_tokens.append(content[i])
                        i += 1
                    
                    if value_tokens:
                        value = self._tokens_to_string(value_tokens)
                        properties[prop_name] = value
                
                i += 1
        
        return properties
    
    def _tokens_to_string(self, tokens) -> str:
        """Convert tokens to string value."""
        result = ""
        for token in tokens:
            if hasattr(token, 'value'):
                result += str(token.value)
            elif hasattr(token, 'type'):
                if token.type == 'whitespace':
                    result += " "
                elif token.type == 'literal':
                    result += token.value
        return result.strip()
    
    def _apply_rule_to_computed(self, rule: Dict, computed: ComputedStyle):
        """Apply CSS rule properties to computed styles."""
        for prop, value in rule['properties'].items():
            if hasattr(computed, prop.replace('-', '_')):
                setattr(computed, prop.replace('-', '_'), value)
    
    def _apply_inline_styles(self, inline_styles: Dict[str, str], computed: ComputedStyle):
        """Apply inline styles to computed styles."""
        for prop, value in inline_styles.items():
            if hasattr(computed, prop.replace('-', '_')):
                setattr(computed, prop.replace('-', '_'), value)
    
    def _resolve_computed_values(self, computed: ComputedStyle):
        """Resolve computed values to final values."""
        # Resolve color values
        if computed.color:
            computed.color = self._resolve_color(computed.color)
        if computed.background_color:
            computed.background_color = self._resolve_color(computed.background_color)
        if computed.border_color:
            computed.border_color = self._resolve_color(computed.border_color)
        if computed.outline_color:
            computed.outline_color = self._resolve_color(computed.outline_color)
        
        # Resolve font size
        if computed.font_size:
            computed.font_size = self._resolve_font_size(computed.font_size)
        
        # Resolve opacity
        if computed.opacity:
            computed.opacity = self._resolve_opacity(computed.opacity)
    
    def _resolve_color(self, color_value: str) -> str:
        """Resolve color value to final color."""
        try:
            # Parse color value
            color = parse_css_color(color_value)
            if color:
                return color.to_hex()
        except Exception:
            pass
        
        return color_value
    
    def _resolve_font_size(self, font_size: str) -> str:
        """Resolve font size to pixels."""
        try:
            if font_size.endswith('px'):
                return font_size
            elif font_size.endswith('pt'):
                # Convert pt to px (1pt = 1.33px)
                pt_value = float(font_size[:-2])
                px_value = pt_value * 1.33
                return f"{px_value:.1f}px"
            elif font_size.endswith('em'):
                # Convert em to px (assume 16px base)
                em_value = float(font_size[:-2])
                px_value = em_value * 16
                return f"{px_value:.1f}px"
            elif font_size.endswith('%'):
                # Convert % to px (assume 16px base)
                percent_value = float(font_size[:-1])
                px_value = (percent_value / 100) * 16
                return f"{px_value:.1f}px"
        except Exception:
            pass
        
        return font_size
    
    def _resolve_opacity(self, opacity: str) -> str:
        """Resolve opacity value."""
        try:
            opacity_value = float(opacity)
            return str(max(0, min(1, opacity_value)))
        except Exception:
            pass
        
        return opacity
    
    def get_contrast_ratio(self, computed: ComputedStyle) -> Optional[float]:
        """Calculate contrast ratio between foreground and background colors."""
        if not computed.color or not computed.background_color:
            return None
        
        try:
            fg_color = parse_css_color(computed.color)
            bg_color = parse_css_color(computed.background_color)
            
            if fg_color and bg_color:
                return calculate_contrast_ratio(fg_color, bg_color)
        except Exception:
            pass
        
        return None
    
    def is_high_contrast(self, computed: ComputedStyle) -> bool:
        """Check if element has high contrast."""
        contrast_ratio = self.get_contrast_ratio(computed)
        if contrast_ratio is None:
            return False
        
        # WCAG AA requires 4.5:1 for normal text, 3:1 for large text
        return contrast_ratio >= 4.5
    
    def get_font_size_pixels(self, computed: ComputedStyle) -> float:
        """Get font size in pixels."""
        if not computed.font_size:
            return 16.0
        
        try:
            if computed.font_size.endswith('px'):
                return float(computed.font_size[:-2])
            elif computed.font_size.endswith('pt'):
                return float(computed.font_size[:-2]) * 1.33
            elif computed.font_size.endswith('em'):
                return float(computed.font_size[:-2]) * 16
            elif computed.font_size.endswith('%'):
                return (float(computed.font_size[:-1]) / 100) * 16
        except Exception:
            pass
        
        return 16.0
    
    def is_large_text(self, computed: ComputedStyle) -> bool:
        """Check if text is considered large (18px+ or 14px+ bold)."""
        font_size = self.get_font_size_pixels(computed)
        font_weight = computed.font_weight or 'normal'
        
        # Large text is 18px+ or 14px+ bold
        if font_size >= 18:
            return True
        
        if font_size >= 14 and font_weight in ['bold', 'bolder', '700', '800', '900']:
            return True
        
        return False

