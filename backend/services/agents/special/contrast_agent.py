"""
ContrastAgent - Evaluates color contrast compliance for WCAG 2.2.
"""

import os
import re
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
from bs4 import BeautifulSoup
import tinycss2
from tinycss2 import parse_stylesheet, parse_component_value_list

from models.schemas import Finding, Evidence, SeverityLevel, ConfidenceLevel, CriterionType
from utils.contrast_ratio import evaluate_contrast, evaluate_non_text_contrast, ContrastResult
from utils.color_math import parse_css_color, RGB, get_contrast_suggestions
from utils.wcag_constants import CONTRAST_THRESHOLDS, WCAGLevel
from utils.id_gen import generate_finding_id

class ContrastAgent:
    """Agent responsible for evaluating color contrast compliance."""
    
    def __init__(self, wcag_level: WCAGLevel = WCAGLevel.AA):
        self.wcag_level = wcag_level
        self.thresholds = CONTRAST_THRESHOLDS[wcag_level]
        self.findings = []
    
    async def analyze(self, upload_path: str, upload_id: str) -> List[Finding]:
        """Analyze uploaded files for contrast issues."""
        self.findings = []
        
        # Find all HTML and CSS files
        html_files = self._find_files(upload_path, ['.html', '.htm', '.xhtml'])
        css_files = self._find_files(upload_path, ['.css', '.scss', '.sass'])
        qml_files = self._find_files(upload_path, ['.qml'])
        
        print(f"DEBUG: ContrastAgent found {len(html_files)} HTML, {len(css_files)} CSS, {len(qml_files)} QML files")
        
        # Analyze HTML files for text elements
        for html_file in html_files:
            print(f"DEBUG: ContrastAgent analyzing HTML: {html_file}")
            await self._analyze_html_file(html_file, upload_path)
        
        # Analyze CSS files for color declarations
        for css_file in css_files:
            print(f"DEBUG: ContrastAgent analyzing CSS: {css_file}")
            await self._analyze_css_file(css_file, upload_path)
        
        # Analyze QML files for color properties
        for qml_file in qml_files:
            print(f"DEBUG: ContrastAgent analyzing QML: {qml_file}")
            await self._analyze_qml_file(qml_file, upload_path)
        
        print(f"DEBUG: ContrastAgent found {len(self.findings)} contrast issues")
        return self.findings
    
    def _find_files(self, upload_path: str, extensions: List[str]) -> List[str]:
        """Find files with specific extensions."""
        files = []
        for root, dirs, filenames in os.walk(upload_path):
            for filename in filenames:
                if Path(filename).suffix.lower() in extensions:
                    files.append(os.path.join(root, filename))
        return files
    
    async def _analyze_html_file(self, file_path: str, upload_path: str):
        """Analyze HTML file for text elements and their computed styles."""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            soup = BeautifulSoup(content, 'html.parser')
            relative_path = os.path.relpath(file_path, upload_path)
            
            # Find all text elements
            text_elements = soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'span', 'div', 'a', 'button', 'label', 'li', 'td', 'th'])
            
            for element in text_elements:
                # Skip empty elements
                if not element.get_text(strip=True):
                    continue
                
                # Get element's computed styles (simplified)
                styles = self._get_element_styles(element, file_path)
                
                # Check contrast for text elements
                if styles.get('color') and styles.get('background-color'):
                    await self._check_text_contrast(element, styles, relative_path, file_path)
                
                # Check contrast for non-text elements (borders, outlines)
                if styles.get('border-color') and styles.get('background-color'):
                    await self._check_non_text_contrast(element, styles, relative_path, file_path, 'border')
                
                if styles.get('outline-color') and styles.get('background-color'):
                    await self._check_non_text_contrast(element, styles, relative_path, file_path, 'outline')
        
        except Exception as e:
            self._add_error_finding(file_path, upload_path, f"Error analyzing HTML file: {str(e)}")
    
    async def _analyze_css_file(self, file_path: str, upload_path: str):
        """Analyze CSS file for color declarations."""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            relative_path = os.path.relpath(file_path, upload_path)
            
            # Parse CSS
            stylesheet = parse_stylesheet(content)
            print(f"DEBUG: ContrastAgent parsed {len(stylesheet)} CSS rules")
            
            for i, rule in enumerate(stylesheet):
                if hasattr(rule, 'prelude') and hasattr(rule, 'content'):
                    # Extract selectors
                    selectors = self._extract_selectors(rule.prelude)
                    
                    # Extract color properties
                    color_props = self._extract_color_properties(rule.content)
                    print(f"DEBUG: Rule {i+1}: {len(selectors)} selectors, {len(color_props)} color properties")
                    
                    # Check contrast for each color combination
                    for selector in selectors:
                        await self._check_css_contrast(selector, color_props, relative_path, file_path)
        
        except Exception as e:
            self._add_error_finding(file_path, upload_path, f"Error analyzing CSS file: {str(e)}")
    
    async def _analyze_qml_file(self, file_path: str, upload_path: str):
        """Analyze QML file for color properties."""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            relative_path = os.path.relpath(file_path, upload_path)
            
            # Find color properties in QML
            color_pattern = r'(color|border\.color|outline\.color)\s*:\s*["\']([^"\']+)["\']'
            matches = re.finditer(color_pattern, content, re.IGNORECASE)
            
            for match in matches:
                property_name = match.group(1)
                color_value = match.group(2)
                
                # Find background color
                bg_match = re.search(r'background\.color\s*:\s*["\']([^"\']+)["\']', content, re.IGNORECASE)
                if bg_match:
                    bg_color = bg_match.group(1)
                    await self._check_qml_contrast(property_name, color_value, bg_color, relative_path, file_path)
        
        except Exception as e:
            self._add_error_finding(file_path, upload_path, f"Error analyzing QML file: {str(e)}")
    
    def _get_element_styles(self, element, file_path: str) -> Dict[str, str]:
        """Get computed styles for an element (simplified)."""
        styles = {}
        
        # Get inline styles
        if element.get('style'):
            inline_styles = element['style'].split(';')
            for style in inline_styles:
                if ':' in style:
                    prop, value = style.split(':', 1)
                    styles[prop.strip()] = value.strip()
        
        # Get class-based styles (simplified)
        if element.get('class'):
            classes = element['class']
            if isinstance(classes, list):
                classes = ' '.join(classes)
            
            # This would need to parse CSS files to get actual computed styles
            # For now, we'll use a simplified approach
        
        return styles
    
    def _extract_selectors(self, prelude) -> List[str]:
        """Extract CSS selectors from rule prelude."""
        selectors = []
        print(f"DEBUG: Extracting selectors from prelude: {type(prelude)}")
        
        if isinstance(prelude, list):
            print(f"DEBUG: Prelude is a list with {len(prelude)} items")
            current_selector = ""
            for i, token in enumerate(prelude):
                print(f"DEBUG: Token {i}: {type(token)} - {token}")
                if hasattr(token, 'type'):
                    if token.type == 'ident':
                        if current_selector:
                            current_selector += " " + token.value
                        else:
                            current_selector = token.value
                    elif token.type == 'literal' and token.value == ',':
                        # End of current selector, start new one
                        if current_selector:
                            selectors.append(current_selector.strip())
                            current_selector = ""
                    elif token.type == 'whitespace':
                        # Add space to current selector
                        if current_selector:
                            current_selector += " "
            
            # Add the last selector
            if current_selector:
                selectors.append(current_selector.strip())
        
        print(f"DEBUG: Extracted selectors: {selectors}")
        return selectors
    
    def _extract_color_properties(self, content) -> Dict[str, str]:
        """Extract color-related properties from CSS rule content."""
        color_props = {}
        print(f"DEBUG: Extracting color properties from content: {type(content)}")
        
        if isinstance(content, list):
            i = 0
            while i < len(content):
                token = content[i]
                print(f"DEBUG: Content token {i}: {type(token)} - {token}")
                
                # Look for property name (ident token)
                if hasattr(token, 'type') and token.type == 'ident':
                    prop_name = token.value
                    print(f"DEBUG: Found property name: {prop_name}")
                    
                    # Check if it's a color-related property
                    if prop_name in ['color', 'background-color', 'border-color', 'outline-color']:
                        # Look for the colon
                        i += 1
                        while i < len(content) and hasattr(content[i], 'type') and content[i].type in ['whitespace', 'literal']:
                            if hasattr(content[i], 'type') and content[i].type == 'literal' and content[i].value == ':':
                                break
                            i += 1
                        
                        # Skip whitespace after colon
                        i += 1
                        while i < len(content) and hasattr(content[i], 'type') and content[i].type == 'whitespace':
                            i += 1
                        
                        # Extract the color value
                        if i < len(content):
                            value_token = content[i]
                            if hasattr(value_token, 'type'):
                                if value_token.type == 'hash':
                                    # Hex color like #f0f0f0
                                    color_value = '#' + value_token.value
                                elif value_token.type == 'ident':
                                    # Named color like red, blue
                                    color_value = value_token.value
                                elif value_token.type == 'function':
                                    # Function like rgb(255, 0, 0)
                                    color_value = value_token.value + '('
                                    # This is simplified - would need to handle function arguments
                                else:
                                    color_value = str(value_token.value) if hasattr(value_token, 'value') else str(value_token)
                                
                                color_props[prop_name] = color_value
                                print(f"DEBUG: Found color property: {prop_name} = {color_value}")
                
                i += 1
        
        print(f"DEBUG: Extracted color properties: {color_props}")
        return color_props
    
    async def _check_text_contrast(self, element, styles: Dict[str, str], relative_path: str, file_path: str):
        """Check contrast for text elements."""
        try:
            fg_color = parse_css_color(styles['color'])
            bg_color = parse_css_color(styles['background-color'])
            
            # Get font size (simplified)
            font_size = self._extract_font_size(styles)
            font_weight = styles.get('font-weight', 'normal')
            
            # Evaluate contrast
            result = evaluate_contrast(fg_color, bg_color, font_size, font_weight, self.wcag_level)
            
            if not result.passes:
                self._add_contrast_finding(
                    element, result, relative_path, file_path, 'text'
                )
        
        except Exception as e:
            self._add_error_finding(file_path, relative_path, f"Error checking text contrast: {str(e)}")
    
    async def _check_non_text_contrast(self, element, styles: Dict[str, str], relative_path: str, file_path: str, element_type: str):
        """Check contrast for non-text elements."""
        try:
            if element_type == 'border':
                fg_color = parse_css_color(styles['border-color'])
            elif element_type == 'outline':
                fg_color = parse_css_color(styles['outline-color'])
            else:
                return
            
            bg_color = parse_css_color(styles['background-color'])
            
            # Evaluate non-text contrast
            result = evaluate_non_text_contrast(fg_color, bg_color, self.wcag_level)
            
            if not result.passes:
                self._add_contrast_finding(
                    element, result, relative_path, file_path, element_type
                )
        
        except Exception as e:
            self._add_error_finding(file_path, relative_path, f"Error checking non-text contrast: {str(e)}")
    
    async def _check_css_contrast(self, selector: str, color_props: Dict[str, str], relative_path: str, file_path: str):
        """Check contrast for CSS color combinations."""
        try:
            if 'color' in color_props and 'background-color' in color_props:
                fg_color = parse_css_color(color_props['color'])
                bg_color = parse_css_color(color_props['background-color'])
                
                # Evaluate contrast
                result = evaluate_contrast(fg_color, bg_color, 16, 'normal', self.wcag_level)
                
                if not result.passes:
                    self._add_css_contrast_finding(
                        selector, result, relative_path, file_path
                    )
        
        except Exception as e:
            self._add_error_finding(file_path, relative_path, f"Error checking CSS contrast: {str(e)}")
    
    async def _check_qml_contrast(self, property_name: str, color_value: str, bg_color: str, relative_path: str, file_path: str):
        """Check contrast for QML color combinations."""
        try:
            fg_color = parse_css_color(color_value)
            bg_color = parse_css_color(bg_color)
            
            # Determine if it's text or non-text
            if property_name == 'color':
                result = evaluate_contrast(fg_color, bg_color, 16, 'normal', self.wcag_level)
                element_type = 'text'
            else:
                result = evaluate_non_text_contrast(fg_color, bg_color, self.wcag_level)
                element_type = 'non-text'
            
            if not result.passes:
                self._add_qml_contrast_finding(
                    property_name, result, relative_path, file_path, element_type
                )
        
        except Exception as e:
            self._add_error_finding(file_path, relative_path, f"Error checking QML contrast: {str(e)}")
    
    def _extract_font_size(self, styles: Dict[str, str]) -> float:
        """Extract font size from styles."""
        font_size = styles.get('font-size', '16px')
        
        # Parse font size
        if font_size.endswith('px'):
            return float(font_size[:-2])
        elif font_size.endswith('pt'):
            return float(font_size[:-2]) * 1.33  # Convert pt to px
        elif font_size.endswith('em'):
            return float(font_size[:-2]) * 16  # Assume 16px base
        else:
            return 16.0  # Default
    
    def _add_contrast_finding(self, element, result: ContrastResult, relative_path: str, file_path: str, element_type: str):
        """Add a contrast finding."""
        finding_id = generate_finding_id()
        
        # Determine severity
        if result.severity == "critical":
            severity = SeverityLevel.CRITICAL
        elif result.severity == "high":
            severity = SeverityLevel.HIGH
        elif result.severity == "medium":
            severity = SeverityLevel.MEDIUM
        else:
            severity = SeverityLevel.LOW
        
        # Create evidence
        evidence = Evidence(
            file_path=relative_path,
            code_snippet=str(element),
            metrics=result.to_dict()
        )
        
        # Create finding
        finding = Finding(
            id=finding_id,
            criterion=CriterionType.CONTRAST,
            selector=self._get_element_selector(element),
            component_id=element.get('id', ''),
            details=f"Contrast ratio {result.ratio:.1f} below required {result.required_ratio:.1f} for {element_type}",
            evidence=[evidence],
            severity=severity,
            confidence=ConfidenceLevel.HIGH,
            wcag_criterion="1.4.3" if element_type == "text" else "1.4.11"
        )
        
        self.findings.append(finding)
    
    def _add_css_contrast_finding(self, selector: str, result: ContrastResult, relative_path: str, file_path: str):
        """Add a CSS contrast finding."""
        finding_id = generate_finding_id()
        
        # Determine severity
        if result.severity == "critical":
            severity = SeverityLevel.CRITICAL
        elif result.severity == "high":
            severity = SeverityLevel.HIGH
        elif result.severity == "medium":
            severity = SeverityLevel.MEDIUM
        else:
            severity = SeverityLevel.LOW
        
        # Create evidence
        evidence = Evidence(
            file_path=relative_path,
            code_snippet=f"selector: {selector}",
            metrics=result.to_dict()
        )
        
        # Create finding
        finding = Finding(
            id=finding_id,
            criterion=CriterionType.CONTRAST,
            selector=selector,
            details=f"Contrast ratio {result.ratio:.1f} below required {result.required_ratio:.1f} in CSS",
            evidence=[evidence],
            severity=severity,
            confidence=ConfidenceLevel.HIGH,
            wcag_criterion="1.4.3"
        )
        
        self.findings.append(finding)
    
    def _add_qml_contrast_finding(self, property_name: str, result: ContrastResult, relative_path: str, file_path: str, element_type: str):
        """Add a QML contrast finding."""
        finding_id = generate_finding_id()
        
        # Determine severity
        if result.severity == "critical":
            severity = SeverityLevel.CRITICAL
        elif result.severity == "high":
            severity = SeverityLevel.HIGH
        elif result.severity == "medium":
            severity = SeverityLevel.MEDIUM
        else:
            severity = SeverityLevel.LOW
        
        # Create evidence
        evidence = Evidence(
            file_path=relative_path,
            code_snippet=f"property: {property_name}",
            metrics=result.to_dict()
        )
        
        # Create finding
        finding = Finding(
            id=finding_id,
            criterion=CriterionType.CONTRAST,
            selector=property_name,
            details=f"Contrast ratio {result.ratio:.1f} below required {result.required_ratio:.1f} for {element_type} in QML",
            evidence=[evidence],
            severity=severity,
            confidence=ConfidenceLevel.HIGH,
            wcag_criterion="1.4.3" if element_type == "text" else "1.4.11"
        )
        
        self.findings.append(finding)
    
    def _add_error_finding(self, file_path: str, relative_path: str, error_message: str):
        """Add an error finding."""
        finding_id = generate_finding_id()
        
        evidence = Evidence(
            file_path=relative_path,
            code_snippet="",
            metrics={"error": error_message}
        )
        
        finding = Finding(
            id=finding_id,
            criterion=CriterionType.CONTRAST,
            selector="",
            details=f"Error analyzing file: {error_message}",
            evidence=[evidence],
            severity=SeverityLevel.LOW,
            confidence=ConfidenceLevel.LOW,
            wcag_criterion="N/A"
        )
        
        self.findings.append(finding)
    
    def _get_element_selector(self, element) -> str:
        """Get a CSS selector for an element."""
        if element.get('id'):
            return f"#{element['id']}"
        elif element.get('class'):
            classes = element['class']
            if isinstance(classes, list):
                classes = ' '.join(classes)
            return f".{classes.replace(' ', '.')}"
        else:
            return element.name
