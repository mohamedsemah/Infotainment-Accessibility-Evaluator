"""
StateExplorerAgent - Explores UI states for accessibility compliance.
"""

import os
import re
from typing import List, Dict, Any, Optional
from pathlib import Path
from bs4 import BeautifulSoup

from models.schemas import Finding, Evidence, SeverityLevel, ConfidenceLevel, CriterionType
from utils.id_gen import generate_finding_id

class StateExplorerAgent:
    """Agent responsible for exploring UI states and interactions."""
    
    def __init__(self):
        self.findings = []
        self.states = ['default', 'hover', 'focus', 'active', 'disabled', 'selected', 'expanded', 'collapsed']
    
    async def analyze(self, upload_path: str, upload_id: str) -> List[Finding]:
        """Analyze uploaded files for state-related accessibility issues."""
        self.findings = []
        
        # Find all HTML, CSS, and QML files
        html_files = self._find_files(upload_path, ['.html', '.htm', '.xhtml'])
        css_files = self._find_files(upload_path, ['.css', '.scss', '.sass'])
        qml_files = self._find_files(upload_path, ['.qml'])
        
        # Analyze HTML files for interactive elements
        for html_file in html_files:
            await self._analyze_html_file(html_file, upload_path)
        
        # Analyze CSS files for state styles
        for css_file in css_files:
            await self._analyze_css_file(css_file, upload_path)
        
        # Analyze QML files for state properties
        for qml_file in qml_files:
            await self._analyze_qml_file(qml_file, upload_path)
        
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
        """Analyze HTML file for state-related issues."""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            soup = BeautifulSoup(content, 'html.parser')
            relative_path = os.path.relpath(file_path, upload_path)
            
            # Check for interactive elements
            await self._check_interactive_elements(soup, relative_path, file_path)
            
            # Check for focus management
            await self._check_focus_management(soup, relative_path, file_path)
            
            # Check for state indicators
            await self._check_state_indicators(soup, relative_path, file_path)
        
        except Exception as e:
            self._add_error_finding(file_path, upload_path, f"Error analyzing HTML file: {str(e)}")
    
    async def _analyze_css_file(self, file_path: str, upload_path: str):
        """Analyze CSS file for state-related styles."""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            relative_path = os.path.relpath(file_path, upload_path)
            
            # Check for focus styles
            await self._check_focus_styles(content, relative_path, file_path)
            
            # Check for hover styles
            await self._check_hover_styles(content, relative_path, file_path)
            
            # Check for state transitions
            await self._check_state_transitions(content, relative_path, file_path)
        
        except Exception as e:
            self._add_error_finding(file_path, upload_path, f"Error analyzing CSS file: {str(e)}")
    
    async def _analyze_qml_file(self, file_path: str, upload_path: str):
        """Analyze QML file for state-related properties."""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            relative_path = os.path.relpath(file_path, upload_path)
            
            # Check for QML state properties
            await self._check_qml_state_properties(content, relative_path, file_path)
            
            # Check for QML focus handling
            await self._check_qml_focus_handling(content, relative_path, file_path)
        
        except Exception as e:
            self._add_error_finding(file_path, upload_path, f"Error analyzing QML file: {str(e)}")
    
    async def _check_interactive_elements(self, soup: BeautifulSoup, relative_path: str, file_path: str):
        """Check for interactive elements and their states."""
        # Find interactive elements
        interactive_elements = soup.find_all(['button', 'a', 'input', 'select', 'textarea', 'details', 'summary'])
        
        for element in interactive_elements:
            # Check if element has proper focus handling
            if not self._has_focus_handling(element):
                self._add_missing_focus_handling_finding(element, relative_path, file_path)
            
            # Check if element has proper state indicators
            if not self._has_state_indicators(element):
                self._add_missing_state_indicators_finding(element, relative_path, file_path)
    
    async def _check_focus_management(self, soup: BeautifulSoup, relative_path: str, file_path: str):
        """Check for focus management issues."""
        # Check for focus traps
        focus_traps = soup.find_all(attrs={'tabindex': '-1'})
        for trap in focus_traps:
            if not self._has_focus_escape_mechanism(trap):
                self._add_focus_trap_finding(trap, relative_path, file_path)
        
        # Check for focus order
        focusable_elements = soup.find_all(attrs={'tabindex': True})
        if len(focusable_elements) > 1:
            await self._check_focus_order(focusable_elements, relative_path, file_path)
    
    async def _check_state_indicators(self, soup: BeautifulSoup, relative_path: str, file_path: str):
        """Check for state indicators."""
        # Check for disabled elements
        disabled_elements = soup.find_all(attrs={'disabled': True})
        for element in disabled_elements:
            if not self._has_disabled_state_indicator(element):
                self._add_missing_disabled_indicator_finding(element, relative_path, file_path)
        
        # Check for selected elements
        selected_elements = soup.find_all(attrs={'selected': True})
        for element in selected_elements:
            if not self._has_selected_state_indicator(element):
                self._add_missing_selected_indicator_finding(element, relative_path, file_path)
    
    async def _check_focus_styles(self, content: str, relative_path: str, file_path: str):
        """Check for focus styles in CSS."""
        # Look for focus styles
        focus_pattern = r':focus\s*\{[^}]*\}'
        focus_matches = re.finditer(focus_pattern, content, re.IGNORECASE | re.DOTALL)
        
        if not focus_matches:
            self._add_missing_focus_styles_finding(relative_path, file_path)
        else:
            # Check if focus styles are visible
            for match in focus_matches:
                focus_style = match.group(0)
                if not self._has_visible_focus_style(focus_style):
                    self._add_invisible_focus_style_finding(focus_style, relative_path, file_path)
    
    async def _check_hover_styles(self, content: str, relative_path: str, file_path: str):
        """Check for hover styles in CSS."""
        # Look for hover styles
        hover_pattern = r':hover\s*\{[^}]*\}'
        hover_matches = re.finditer(hover_pattern, content, re.IGNORECASE | re.DOTALL)
        
        if not hover_matches:
            self._add_missing_hover_styles_finding(relative_path, file_path)
    
    async def _check_state_transitions(self, content: str, relative_path: str, file_path: str):
        """Check for state transitions in CSS."""
        # Look for transition properties
        transition_pattern = r'transition\s*:\s*[^;]+'
        transition_matches = re.finditer(transition_pattern, content, re.IGNORECASE)
        
        if not transition_matches:
            self._add_missing_transitions_finding(relative_path, file_path)
    
    async def _check_qml_state_properties(self, content: str, relative_path: str, file_path: str):
        """Check for QML state properties."""
        # Look for state properties
        state_pattern = r'(enabled|visible|focus|active|hover|pressed|checked|selected)\s*:\s*[^;]+'
        state_matches = re.finditer(state_pattern, content, re.IGNORECASE)
        
        for match in state_matches:
            state_property = match.group(1)
            if not self._has_qml_state_handling(content, state_property):
                self._add_missing_qml_state_handling_finding(state_property, relative_path, file_path)
    
    async def _check_qml_focus_handling(self, content: str, relative_path: str, file_path: str):
        """Check for QML focus handling."""
        # Look for focus handling
        if 'focus' not in content.lower():
            self._add_missing_qml_focus_handling_finding(relative_path, file_path)
    
    def _has_focus_handling(self, element) -> bool:
        """Check if element has proper focus handling."""
        # Check for tabindex
        if element.get('tabindex'):
            return True
        
        # Check for focus event handlers
        if element.get('onfocus') or element.get('onblur'):
            return True
        
        # Check for ARIA focus attributes
        if element.get('aria-activedescendant') or element.get('aria-expanded'):
            return True
        
        return False
    
    def _has_state_indicators(self, element) -> bool:
        """Check if element has proper state indicators."""
        # Check for ARIA state attributes
        state_attrs = ['aria-expanded', 'aria-selected', 'aria-checked', 'aria-pressed', 'aria-disabled']
        for attr in state_attrs:
            if element.get(attr):
                return True
        
        return False
    
    def _has_focus_escape_mechanism(self, element) -> bool:
        """Check if focus trap has escape mechanism."""
        # Check for escape key handler
        if element.get('onkeydown') and 'escape' in element.get('onkeydown', '').lower():
            return True
        
        # Check for close button
        close_buttons = element.find_all(['button', 'a'], attrs={'aria-label': re.compile(r'close|dismiss', re.IGNORECASE)})
        if close_buttons:
            return True
        
        return False
    
    async def _check_focus_order(self, elements: List, relative_path: str, file_path: str):
        """Check focus order of elements."""
        # Check for proper tabindex values
        tabindex_values = []
        for element in elements:
            tabindex = element.get('tabindex', '0')
            try:
                tabindex_values.append(int(tabindex))
            except ValueError:
                tabindex_values.append(0)
        
        # Check if tabindex values are in order
        if tabindex_values != sorted(tabindex_values):
            self._add_focus_order_finding(elements, relative_path, file_path)
    
    def _has_disabled_state_indicator(self, element) -> bool:
        """Check if disabled element has proper state indicator."""
        # Check for ARIA disabled attribute
        if element.get('aria-disabled') == 'true':
            return True
        
        # Check for visual disabled indicator
        if element.get('class') and 'disabled' in element.get('class', '').lower():
            return True
        
        return False
    
    def _has_selected_state_indicator(self, element) -> bool:
        """Check if selected element has proper state indicator."""
        # Check for ARIA selected attribute
        if element.get('aria-selected') == 'true':
            return True
        
        # Check for visual selected indicator
        if element.get('class') and 'selected' in element.get('class', '').lower():
            return True
        
        return False
    
    def _has_visible_focus_style(self, focus_style: str) -> bool:
        """Check if focus style is visible."""
        # Look for visible focus indicators
        visible_indicators = ['outline', 'border', 'box-shadow', 'background', 'color']
        for indicator in visible_indicators:
            if indicator in focus_style.lower():
                return True
        
        return False
    
    def _has_qml_state_handling(self, content: str, state_property: str) -> bool:
        """Check if QML has proper state handling."""
        # Look for state change handlers
        handler_pattern = f'on{state_property.capitalize()}Changed'
        if re.search(handler_pattern, content, re.IGNORECASE):
            return True
        
        return False
    
    def _add_missing_focus_handling_finding(self, element, relative_path: str, file_path: str):
        """Add finding for missing focus handling."""
        finding_id = generate_finding_id()
        
        evidence = Evidence(
            file_path=relative_path,
            code_snippet=str(element),
            metrics={"issue": "missing_focus_handling"}
        )
        
        finding = Finding(
            id=finding_id,
            criterion=CriterionType.STATE_EXPLORER,
            selector=self._get_element_selector(element),
            details="Interactive element missing focus handling",
            evidence=[evidence],
            severity=SeverityLevel.MEDIUM,
            confidence=ConfidenceLevel.MEDIUM,
            wcag_criterion="2.4.7"
        )
        
        self.findings.append(finding)
    
    def _add_missing_state_indicators_finding(self, element, relative_path: str, file_path: str):
        """Add finding for missing state indicators."""
        finding_id = generate_finding_id()
        
        evidence = Evidence(
            file_path=relative_path,
            code_snippet=str(element),
            metrics={"issue": "missing_state_indicators"}
        )
        
        finding = Finding(
            id=finding_id,
            criterion=CriterionType.STATE_EXPLORER,
            selector=self._get_element_selector(element),
            details="Interactive element missing state indicators",
            evidence=[evidence],
            severity=SeverityLevel.MEDIUM,
            confidence=ConfidenceLevel.MEDIUM,
            wcag_criterion="4.1.2"
        )
        
        self.findings.append(finding)
    
    def _add_focus_trap_finding(self, element, relative_path: str, file_path: str):
        """Add finding for focus trap without escape mechanism."""
        finding_id = generate_finding_id()
        
        evidence = Evidence(
            file_path=relative_path,
            code_snippet=str(element),
            metrics={"issue": "focus_trap_no_escape"}
        )
        
        finding = Finding(
            id=finding_id,
            criterion=CriterionType.STATE_EXPLORER,
            selector=self._get_element_selector(element),
            details="Focus trap without escape mechanism",
            evidence=[evidence],
            severity=SeverityLevel.HIGH,
            confidence=ConfidenceLevel.HIGH,
            wcag_criterion="2.1.2"
        )
        
        self.findings.append(finding)
    
    def _add_focus_order_finding(self, elements: List, relative_path: str, file_path: str):
        """Add finding for focus order issues."""
        finding_id = generate_finding_id()
        
        evidence = Evidence(
            file_path=relative_path,
            code_snippet="",
            metrics={"issue": "focus_order", "element_count": len(elements)}
        )
        
        finding = Finding(
            id=finding_id,
            criterion=CriterionType.STATE_EXPLORER,
            selector="",
            details="Focus order not logical",
            evidence=[evidence],
            severity=SeverityLevel.MEDIUM,
            confidence=ConfidenceLevel.MEDIUM,
            wcag_criterion="2.4.3"
        )
        
        self.findings.append(finding)
    
    def _add_missing_disabled_indicator_finding(self, element, relative_path: str, file_path: str):
        """Add finding for missing disabled state indicator."""
        finding_id = generate_finding_id()
        
        evidence = Evidence(
            file_path=relative_path,
            code_snippet=str(element),
            metrics={"issue": "missing_disabled_indicator"}
        )
        
        finding = Finding(
            id=finding_id,
            criterion=CriterionType.STATE_EXPLORER,
            selector=self._get_element_selector(element),
            details="Disabled element missing state indicator",
            evidence=[evidence],
            severity=SeverityLevel.MEDIUM,
            confidence=ConfidenceLevel.MEDIUM,
            wcag_criterion="4.1.2"
        )
        
        self.findings.append(finding)
    
    def _add_missing_selected_indicator_finding(self, element, relative_path: str, file_path: str):
        """Add finding for missing selected state indicator."""
        finding_id = generate_finding_id()
        
        evidence = Evidence(
            file_path=relative_path,
            code_snippet=str(element),
            metrics={"issue": "missing_selected_indicator"}
        )
        
        finding = Finding(
            id=finding_id,
            criterion=CriterionType.STATE_EXPLORER,
            selector=self._get_element_selector(element),
            details="Selected element missing state indicator",
            evidence=[evidence],
            severity=SeverityLevel.MEDIUM,
            confidence=ConfidenceLevel.MEDIUM,
            wcag_criterion="4.1.2"
        )
        
        self.findings.append(finding)
    
    def _add_missing_focus_styles_finding(self, relative_path: str, file_path: str):
        """Add finding for missing focus styles."""
        finding_id = generate_finding_id()
        
        evidence = Evidence(
            file_path=relative_path,
            code_snippet="",
            metrics={"issue": "missing_focus_styles"}
        )
        
        finding = Finding(
            id=finding_id,
            criterion=CriterionType.STATE_EXPLORER,
            selector="",
            details="Missing focus styles",
            evidence=[evidence],
            severity=SeverityLevel.HIGH,
            confidence=ConfidenceLevel.HIGH,
            wcag_criterion="2.4.7"
        )
        
        self.findings.append(finding)
    
    def _add_invisible_focus_style_finding(self, focus_style: str, relative_path: str, file_path: str):
        """Add finding for invisible focus style."""
        finding_id = generate_finding_id()
        
        evidence = Evidence(
            file_path=relative_path,
            code_snippet=focus_style,
            metrics={"issue": "invisible_focus_style"}
        )
        
        finding = Finding(
            id=finding_id,
            criterion=CriterionType.STATE_EXPLORER,
            selector="",
            details="Focus style not visible",
            evidence=[evidence],
            severity=SeverityLevel.MEDIUM,
            confidence=ConfidenceLevel.MEDIUM,
            wcag_criterion="2.4.7"
        )
        
        self.findings.append(finding)
    
    def _add_missing_hover_styles_finding(self, relative_path: str, file_path: str):
        """Add finding for missing hover styles."""
        finding_id = generate_finding_id()
        
        evidence = Evidence(
            file_path=relative_path,
            code_snippet="",
            metrics={"issue": "missing_hover_styles"}
        )
        
        finding = Finding(
            id=finding_id,
            criterion=CriterionType.STATE_EXPLORER,
            selector="",
            details="Missing hover styles",
            evidence=[evidence],
            severity=SeverityLevel.LOW,
            confidence=ConfidenceLevel.MEDIUM,
            wcag_criterion="1.4.13"
        )
        
        self.findings.append(finding)
    
    def _add_missing_transitions_finding(self, relative_path: str, file_path: str):
        """Add finding for missing transitions."""
        finding_id = generate_finding_id()
        
        evidence = Evidence(
            file_path=relative_path,
            code_snippet="",
            metrics={"issue": "missing_transitions"}
        )
        
        finding = Finding(
            id=finding_id,
            criterion=CriterionType.STATE_EXPLORER,
            selector="",
            details="Missing state transitions",
            evidence=[evidence],
            severity=SeverityLevel.LOW,
            confidence=ConfidenceLevel.MEDIUM,
            wcag_criterion="2.3.3"
        )
        
        self.findings.append(finding)
    
    def _add_missing_qml_state_handling_finding(self, state_property: str, relative_path: str, file_path: str):
        """Add finding for missing QML state handling."""
        finding_id = generate_finding_id()
        
        evidence = Evidence(
            file_path=relative_path,
            code_snippet=f"property: {state_property}",
            metrics={"state_property": state_property, "issue": "missing_qml_state_handling"}
        )
        
        finding = Finding(
            id=finding_id,
            criterion=CriterionType.STATE_EXPLORER,
            selector="",
            details=f"Missing QML state handling for {state_property}",
            evidence=[evidence],
            severity=SeverityLevel.MEDIUM,
            confidence=ConfidenceLevel.MEDIUM,
            wcag_criterion="4.1.2"
        )
        
        self.findings.append(finding)
    
    def _add_missing_qml_focus_handling_finding(self, relative_path: str, file_path: str):
        """Add finding for missing QML focus handling."""
        finding_id = generate_finding_id()
        
        evidence = Evidence(
            file_path=relative_path,
            code_snippet="",
            metrics={"issue": "missing_qml_focus_handling"}
        )
        
        finding = Finding(
            id=finding_id,
            criterion=CriterionType.STATE_EXPLORER,
            selector="",
            details="Missing QML focus handling",
            evidence=[evidence],
            severity=SeverityLevel.MEDIUM,
            confidence=ConfidenceLevel.MEDIUM,
            wcag_criterion="2.4.7"
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
            criterion=CriterionType.STATE_EXPLORER,
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
