"""
ARIAAgent - Evaluates ARIA compliance for WCAG 2.2.
"""

import os
import re
from typing import List, Dict, Any, Optional
from pathlib import Path
from bs4 import BeautifulSoup

from models.schemas import Finding, Evidence, SeverityLevel, ConfidenceLevel, CriterionType
from utils.aria_maps import ARIA_ROLES, ARIA_ATTRIBUTES
from utils.id_gen import generate_finding_id
from services.agents.base_agent import BaseAgent

class ARIAAgent(BaseAgent):
    """Agent responsible for evaluating ARIA compliance."""
    
    def __init__(self):
        super().__init__(
            name="ARIAAgent",
            description="Evaluates ARIA compliance for WCAG 2.2",
            criterion=CriterionType.ARIA,
            wcag_criterion="4.1.2"
        )
        self.findings = []
        self.aria_roles = ARIA_ROLES
        self.aria_attributes = ARIA_ATTRIBUTES
    
    async def analyze(self, upload_path: str) -> List[Finding]:
        """Analyze uploaded files for ARIA compliance issues."""
        self.findings = []
        
        # Find all HTML and QML files
        html_files = self._find_files(upload_path, ['.html', '.htm', '.xhtml'])
        qml_files = self._find_files(upload_path, ['.qml'])
        
        # Analyze HTML files
        for html_file in html_files:
            await self._analyze_html_file(html_file, upload_path)
        
        # Analyze QML files
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
        """Analyze HTML file for ARIA compliance issues."""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            soup = BeautifulSoup(content, 'html.parser')
            relative_path = os.path.relpath(file_path, upload_path)
            
            # Check all elements for ARIA issues
            all_elements = soup.find_all()
            
            for element in all_elements:
                await self._check_element_aria_compliance(element, relative_path, file_path)
            
            # Check for missing ARIA landmarks
            await self._check_aria_landmarks(soup, relative_path, file_path)
            
            # Check for ARIA relationships
            await self._check_aria_relationships(soup, relative_path, file_path)
        
        except Exception as e:
            self._add_error_finding(file_path, relative_path, f"Error analyzing HTML file: {str(e)}")
    
    async def _analyze_qml_file(self, file_path: str, upload_path: str):
        """Analyze QML file for ARIA compliance issues."""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            relative_path = os.path.relpath(file_path, upload_path)
            
            # Check for QML accessibility properties
            await self._check_qml_accessibility_properties(content, relative_path, file_path)
            
            # Check for QML interactive elements
            await self._check_qml_interactive_elements(content, relative_path, file_path)
        
        except Exception as e:
            self._add_error_finding(file_path, relative_path, f"Error analyzing QML file: {str(e)}")
    
    async def _check_element_aria_compliance(self, element, relative_path: str, file_path: str):
        """Check individual element for ARIA compliance."""
        try:
            # Check for invalid ARIA roles
            await self._check_aria_role(element, relative_path, file_path)
            
            # Check for invalid ARIA attributes
            await self._check_aria_attributes(element, relative_path, file_path)
            
            # Check for ARIA states and properties
            await self._check_aria_states_properties(element, relative_path, file_path)
            
            # Check for required ARIA attributes
            await self._check_required_aria_attributes(element, relative_path, file_path)
            
            # Check for ARIA naming
            await self._check_aria_naming(element, relative_path, file_path)
        
        except Exception as e:
            self._add_error_finding(file_path, relative_path, f"Error checking element ARIA compliance: {str(e)}")
    
    async def _check_aria_role(self, element, relative_path: str, file_path: str):
        """Check ARIA role validity."""
        role = element.get('role')
        if not role:
            return
        
        # Check if role is valid
        if role not in self.aria_roles:
            self._add_invalid_aria_role_finding(element, role, relative_path, file_path)
        
        # Check for role conflicts with native HTML elements
        if self._has_role_conflict(element, role):
            self._add_aria_role_conflict_finding(element, role, relative_path, file_path)
    
    async def _check_aria_attributes(self, element, relative_path: str, file_path: str):
        """Check ARIA attributes validity."""
        for attr_name, attr_value in element.attrs.items():
            if attr_name.startswith('aria-'):
                # Check if attribute is valid
                if attr_name not in self.aria_attributes:
                    self._add_invalid_aria_attribute_finding(element, attr_name, relative_path, file_path)
                
                # Check attribute value validity
                if not self._is_valid_aria_attribute_value(attr_name, attr_value):
                    self._add_invalid_aria_attribute_value_finding(element, attr_name, attr_value, relative_path, file_path)
    
    async def _check_aria_states_properties(self, element, relative_path: str, file_path: str):
        """Check ARIA states and properties."""
        for attr_name, attr_value in element.attrs.items():
            if attr_name.startswith('aria-'):
                # Check if it's a state or property
                if attr_name in self.aria_states:
                    if not self._is_valid_aria_state_value(attr_name, attr_value):
                        self._add_invalid_aria_state_finding(element, attr_name, attr_value, relative_path, file_path)
                elif attr_name in self.aria_properties:
                    if not self._is_valid_aria_property_value(attr_name, attr_value):
                        self._add_invalid_aria_property_finding(element, attr_name, attr_value, relative_path, file_path)
    
    async def _check_required_aria_attributes(self, element, relative_path: str, file_path: str):
        """Check for required ARIA attributes."""
        role = element.get('role')
        if not role:
            return
        
        # Check for required attributes based on role
        required_attrs = self._get_required_aria_attributes(role)
        
        for required_attr in required_attrs:
            if not element.get(required_attr):
                self._add_missing_required_aria_attribute_finding(element, role, required_attr, relative_path, file_path)
    
    async def _check_aria_naming(self, element, relative_path: str, file_path: str):
        """Check ARIA naming requirements."""
        # Check if element needs accessible name
        if self._needs_accessible_name(element):
            accessible_name = self._get_accessible_name(element)
            
            if not accessible_name:
                self._add_missing_accessible_name_finding(element, relative_path, file_path)
            elif len(accessible_name) < 2:
                self._add_insufficient_accessible_name_finding(element, accessible_name, relative_path, file_path)
    
    async def _check_aria_landmarks(self, soup: BeautifulSoup, relative_path: str, file_path: str):
        """Check for ARIA landmarks."""
        try:
            # Check for main landmark
            main_landmark = soup.find('main') or soup.find(attrs={'role': 'main'})
            if not main_landmark:
                self._add_missing_main_landmark_finding(relative_path, file_path)
            
            # Check for navigation landmarks
            nav_landmarks = soup.find_all('nav') + soup.find_all(attrs={'role': 'navigation'})
            if not nav_landmarks:
                self._add_missing_navigation_landmark_finding(relative_path, file_path)
            
            # Check for heading structure
            await self._check_heading_structure(soup, relative_path, file_path)
        
        except Exception as e:
            self._add_error_finding(file_path, relative_path, f"Error checking ARIA landmarks: {str(e)}")
    
    async def _check_aria_relationships(self, soup: BeautifulSoup, relative_path: str, file_path: str):
        """Check ARIA relationships."""
        try:
            # Check for aria-labelledby relationships
            labelledby_elements = soup.find_all(attrs={'aria-labelledby': True})
            for element in labelledby_elements:
                await self._check_labelledby_relationship(element, soup, relative_path, file_path)
            
            # Check for aria-describedby relationships
            describedby_elements = soup.find_all(attrs={'aria-describedby': True})
            for element in describedby_elements:
                await self._check_describedby_relationship(element, soup, relative_path, file_path)
            
            # Check for aria-controls relationships
            controls_elements = soup.find_all(attrs={'aria-controls': True})
            for element in controls_elements:
                await self._check_controls_relationship(element, soup, relative_path, file_path)
        
        except Exception as e:
            self._add_error_finding(file_path, relative_path, f"Error checking ARIA relationships: {str(e)}")
    
    async def _check_qml_accessibility_properties(self, content: str, relative_path: str, file_path: str):
        """Check QML accessibility properties."""
        try:
            # Look for accessibility-related properties
            accessibility_patterns = [
                r'Accessible\.name\s*:\s*["\']([^"\']*)["\']',  # Accessible name
                r'Accessible\.description\s*:\s*["\']([^"\']*)["\']',  # Accessible description
                r'Accessible\.role\s*:\s*["\']([^"\']*)["\']',  # Accessible role
            ]
            
            for pattern in accessibility_patterns:
                matches = re.finditer(pattern, content, re.IGNORECASE)
                for match in matches:
                    if 'role' in pattern:
                        role = match.group(1)
                        if role not in self.aria_roles:
                            self._add_invalid_qml_aria_role_finding(match.group(0), role, relative_path, file_path)
                    elif 'name' in pattern:
                        name = match.group(1)
                        if not name or len(name) < 2:
                            self._add_insufficient_qml_accessible_name_finding(match.group(0), name, relative_path, file_path)
        
        except Exception as e:
            self._add_error_finding(file_path, relative_path, f"Error checking QML accessibility properties: {str(e)}")
    
    async def _check_qml_interactive_elements(self, content: str, relative_path: str, file_path: str):
        """Check QML interactive elements for accessibility."""
        try:
            # Look for interactive QML elements
            interactive_patterns = [
                r'Button\s*\{',  # Button elements
                r'MouseArea\s*\{',  # MouseArea elements
                r'TextInput\s*\{',  # TextInput elements
                r'Slider\s*\{',  # Slider elements
            ]
            
            for pattern in interactive_patterns:
                matches = re.finditer(pattern, content, re.IGNORECASE)
                for match in matches:
                    # Check if the element has accessibility properties
                    element_start = match.start()
                    element_end = self._find_qml_element_end(content, element_start)
                    element_content = content[element_start:element_end]
                    
                    if not self._has_qml_accessibility_properties(element_content):
                        self._add_missing_qml_accessibility_finding(match.group(0), relative_path, file_path)
        
        except Exception as e:
            self._add_error_finding(file_path, relative_path, f"Error checking QML interactive elements: {str(e)}")
    
    def _has_role_conflict(self, element, role: str) -> bool:
        """Check if element has role conflict with native HTML element."""
        tag_name = element.name.lower()
        
        # Define role conflicts
        role_conflicts = {
            'button': ['button', 'input[type="button"]', 'input[type="submit"]', 'input[type="reset"]'],
            'link': ['a'],
            'textbox': ['input[type="text"]', 'input[type="email"]', 'input[type="password"]', 'textarea'],
            'checkbox': ['input[type="checkbox"]'],
            'radio': ['input[type="radio"]'],
            'slider': ['input[type="range"]'],
            'progressbar': ['progress'],
            'tab': ['button[role="tab"]'],
            'tabpanel': ['div[role="tabpanel"]'],
        }
        
        if role in role_conflicts:
            conflicting_elements = role_conflicts[role]
            for conflicting in conflicting_elements:
                if conflicting == tag_name or conflicting.startswith(tag_name + '['):
                    return True
        
        return False
    
    def _is_valid_aria_attribute_value(self, attr_name: str, attr_value: str) -> bool:
        """Check if ARIA attribute value is valid."""
        # Define valid values for specific attributes
        valid_values = {
            'aria-expanded': ['true', 'false'],
            'aria-selected': ['true', 'false'],
            'aria-checked': ['true', 'false', 'mixed'],
            'aria-pressed': ['true', 'false', 'mixed'],
            'aria-sort': ['ascending', 'descending', 'none', 'other'],
            'aria-orientation': ['horizontal', 'vertical'],
            'aria-autocomplete': ['inline', 'list', 'both', 'none'],
            'aria-invalid': ['true', 'false', 'grammar', 'spelling'],
            'aria-live': ['off', 'polite', 'assertive'],
            'aria-relevant': ['additions', 'removals', 'text', 'all'],
            'aria-busy': ['true', 'false'],
        }
        
        if attr_name in valid_values:
            return attr_value in valid_values[attr_name]
        
        return True  # If no specific validation, assume valid
    
    def _is_valid_aria_state_value(self, state_name: str, state_value: str) -> bool:
        """Check if ARIA state value is valid."""
        # ARIA states typically have boolean values
        if state_name in ['aria-expanded', 'aria-selected', 'aria-checked', 'aria-pressed', 'aria-busy']:
            return state_value in ['true', 'false']
        
        return True
    
    def _is_valid_aria_property_value(self, property_name: str, property_value: str) -> bool:
        """Check if ARIA property value is valid."""
        # ARIA properties can have various value types
        return True  # Simplified validation
    
    def _get_required_aria_attributes(self, role: str) -> List[str]:
        """Get required ARIA attributes for a role."""
        required_attrs = {
            'combobox': ['aria-expanded'],
            'dialog': ['aria-labelledby'],
            'grid': ['aria-rowcount', 'aria-colcount'],
            'listbox': ['aria-multiselectable'],
            'menu': ['aria-orientation'],
            'menubar': ['aria-orientation'],
            'radiogroup': ['aria-required'],
            'slider': ['aria-valuemin', 'aria-valuemax', 'aria-valuenow'],
            'spinbutton': ['aria-valuemin', 'aria-valuemax', 'aria-valuenow'],
            'tablist': ['aria-orientation'],
            'textbox': ['aria-multiline'],
            'tree': ['aria-multiselectable'],
        }
        
        return required_attrs.get(role, [])
    
    def _needs_accessible_name(self, element) -> bool:
        """Check if element needs an accessible name."""
        # Elements that need accessible names
        elements_needing_names = [
            'button', 'input', 'select', 'textarea', 'a', 'img', 'iframe',
            'object', 'embed', 'area', 'label'
        ]
        
        tag_name = element.name.lower()
        
        # Check native HTML elements
        if tag_name in elements_needing_names:
            return True
        
        # Check ARIA roles that need names
        role = element.get('role')
        if role:
            roles_needing_names = [
                'button', 'link', 'textbox', 'checkbox', 'radio', 'slider',
                'progressbar', 'tab', 'menuitem', 'option', 'treeitem'
            ]
            if role in roles_needing_names:
                return True
        
        return False
    
    def _get_accessible_name(self, element) -> str:
        """Get the accessible name of an element."""
        # Check aria-label
        aria_label = element.get('aria-label')
        if aria_label:
            return aria_label
        
        # Check aria-labelledby
        aria_labelledby = element.get('aria-labelledby')
        if aria_labelledby:
            # In a real implementation, you'd resolve the referenced element
            return f"Referenced by: {aria_labelledby}"
        
        # Check for text content
        text_content = element.get_text(strip=True)
        if text_content:
            return text_content
        
        # Check for alt text on images
        if element.name == 'img':
            alt_text = element.get('alt')
            if alt_text:
                return alt_text
        
        # Check for title attribute
        title = element.get('title')
        if title:
            return title
        
        return ""
    
    def _find_qml_element_end(self, content: str, start_pos: int) -> int:
        """Find the end of a QML element."""
        brace_count = 0
        in_string = False
        escape_next = False
        
        for i in range(start_pos, len(content)):
            char = content[i]
            
            if escape_next:
                escape_next = False
                continue
            
            if char == '\\':
                escape_next = True
                continue
            
            if char == '"' and not escape_next:
                in_string = not in_string
                continue
            
            if not in_string:
                if char == '{':
                    brace_count += 1
                elif char == '}':
                    brace_count -= 1
                    if brace_count == 0:
                        return i + 1
        
        return len(content)
    
    def _has_qml_accessibility_properties(self, element_content: str) -> bool:
        """Check if QML element has accessibility properties."""
        accessibility_props = [
            'Accessible.name', 'Accessible.description', 'Accessible.role',
            'Accessible.help', 'Accessible.focusable'
        ]
        
        for prop in accessibility_props:
            if prop in element_content:
                return True
        
        return False
    
    # Finding creation methods
    def _add_invalid_aria_role_finding(self, element, role: str, relative_path: str, file_path: str):
        """Add finding for invalid ARIA role."""
        finding_id = generate_finding_id()
        
        evidence = Evidence(
            file_path=relative_path,
            code_snippet=str(element),
            metrics={"issue": "invalid_aria_role", "role": role}
        )
        
        finding = Finding(
            id=finding_id,
            criterion=CriterionType.ARIA,
            selector=self._get_element_selector(element),
            details=f"Invalid ARIA role '{role}' - not a valid ARIA role",
            evidence=[evidence],
            severity=SeverityLevel.MEDIUM,
            confidence=ConfidenceLevel.HIGH,
            wcag_criterion="4.1.2"
        )
        
        self.findings.append(finding)
    
    def _add_aria_role_conflict_finding(self, element, role: str, relative_path: str, file_path: str):
        """Add finding for ARIA role conflict."""
        finding_id = generate_finding_id()
        
        evidence = Evidence(
            file_path=relative_path,
            code_snippet=str(element),
            metrics={"issue": "aria_role_conflict", "role": role}
        )
        
        finding = Finding(
            id=finding_id,
            criterion=CriterionType.ARIA,
            selector=self._get_element_selector(element),
            details=f"ARIA role '{role}' conflicts with native HTML element",
            evidence=[evidence],
            severity=SeverityLevel.MEDIUM,
            confidence=ConfidenceLevel.HIGH,
            wcag_criterion="4.1.2"
        )
        
        self.findings.append(finding)
    
    def _add_invalid_aria_attribute_finding(self, element, attr_name: str, relative_path: str, file_path: str):
        """Add finding for invalid ARIA attribute."""
        finding_id = generate_finding_id()
        
        evidence = Evidence(
            file_path=relative_path,
            code_snippet=str(element),
            metrics={"issue": "invalid_aria_attribute", "attribute": attr_name}
        )
        
        finding = Finding(
            id=finding_id,
            criterion=CriterionType.ARIA,
            selector=self._get_element_selector(element),
            details=f"Invalid ARIA attribute '{attr_name}' - not a valid ARIA attribute",
            evidence=[evidence],
            severity=SeverityLevel.MEDIUM,
            confidence=ConfidenceLevel.HIGH,
            wcag_criterion="4.1.2"
        )
        
        self.findings.append(finding)
    
    def _add_invalid_aria_attribute_value_finding(self, element, attr_name: str, attr_value: str, relative_path: str, file_path: str):
        """Add finding for invalid ARIA attribute value."""
        finding_id = generate_finding_id()
        
        evidence = Evidence(
            file_path=relative_path,
            code_snippet=str(element),
            metrics={"issue": "invalid_aria_attribute_value", "attribute": attr_name, "value": attr_value}
        )
        
        finding = Finding(
            id=finding_id,
            criterion=CriterionType.ARIA,
            selector=self._get_element_selector(element),
            details=f"Invalid ARIA attribute value '{attr_value}' for '{attr_name}'",
            evidence=[evidence],
            severity=SeverityLevel.MEDIUM,
            confidence=ConfidenceLevel.HIGH,
            wcag_criterion="4.1.2"
        )
        
        self.findings.append(finding)
    
    def _add_missing_required_aria_attribute_finding(self, element, role: str, required_attr: str, relative_path: str, file_path: str):
        """Add finding for missing required ARIA attribute."""
        finding_id = generate_finding_id()
        
        evidence = Evidence(
            file_path=relative_path,
            code_snippet=str(element),
            metrics={"issue": "missing_required_aria_attribute", "role": role, "attribute": required_attr}
        )
        
        finding = Finding(
            id=finding_id,
            criterion=CriterionType.ARIA,
            selector=self._get_element_selector(element),
            details=f"Missing required ARIA attribute '{required_attr}' for role '{role}'",
            evidence=[evidence],
            severity=SeverityLevel.HIGH,
            confidence=ConfidenceLevel.HIGH,
            wcag_criterion="4.1.2"
        )
        
        self.findings.append(finding)
    
    def _add_missing_accessible_name_finding(self, element, relative_path: str, file_path: str):
        """Add finding for missing accessible name."""
        finding_id = generate_finding_id()
        
        evidence = Evidence(
            file_path=relative_path,
            code_snippet=str(element),
            metrics={"issue": "missing_accessible_name"}
        )
        
        finding = Finding(
            id=finding_id,
            criterion=CriterionType.ARIA,
            selector=self._get_element_selector(element),
            details="Element lacks accessible name - add aria-label, aria-labelledby, or text content",
            evidence=[evidence],
            severity=SeverityLevel.HIGH,
            confidence=ConfidenceLevel.HIGH,
            wcag_criterion="4.1.2"
        )
        
        self.findings.append(finding)
    
    def _add_insufficient_accessible_name_finding(self, element, name: str, relative_path: str, file_path: str):
        """Add finding for insufficient accessible name."""
        finding_id = generate_finding_id()
        
        evidence = Evidence(
            file_path=relative_path,
            code_snippet=str(element),
            metrics={"issue": "insufficient_accessible_name", "name": name}
        )
        
        finding = Finding(
            id=finding_id,
            criterion=CriterionType.ARIA,
            selector=self._get_element_selector(element),
            details=f"Accessible name '{name}' is too short - provide more descriptive text",
            evidence=[evidence],
            severity=SeverityLevel.MEDIUM,
            confidence=ConfidenceLevel.MEDIUM,
            wcag_criterion="4.1.2"
        )
        
        self.findings.append(finding)
    
    def _add_missing_main_landmark_finding(self, relative_path: str, file_path: str):
        """Add finding for missing main landmark."""
        finding_id = generate_finding_id()
        
        evidence = Evidence(
            file_path=relative_path,
            code_snippet="<main> or <div role=\"main\">",
            metrics={"issue": "missing_main_landmark"}
        )
        
        finding = Finding(
            id=finding_id,
            criterion=CriterionType.ARIA,
            selector="main",
            details="Document lacks main landmark - add <main> element or role=\"main\"",
            evidence=[evidence],
            severity=SeverityLevel.HIGH,
            confidence=ConfidenceLevel.HIGH,
            wcag_criterion="4.1.2"
        )
        
        self.findings.append(finding)
    
    def _add_missing_navigation_landmark_finding(self, relative_path: str, file_path: str):
        """Add finding for missing navigation landmark."""
        finding_id = generate_finding_id()
        
        evidence = Evidence(
            file_path=relative_path,
            code_snippet="<nav> or <div role=\"navigation\">",
            metrics={"issue": "missing_navigation_landmark"}
        )
        
        finding = Finding(
            id=finding_id,
            criterion=CriterionType.ARIA,
            selector="nav",
            details="Document lacks navigation landmark - add <nav> element or role=\"navigation\"",
            evidence=[evidence],
            severity=SeverityLevel.MEDIUM,
            confidence=ConfidenceLevel.MEDIUM,
            wcag_criterion="4.1.2"
        )
        
        self.findings.append(finding)
    
    def _add_invalid_qml_aria_role_finding(self, code_snippet: str, role: str, relative_path: str, file_path: str):
        """Add finding for invalid QML ARIA role."""
        finding_id = generate_finding_id()
        
        evidence = Evidence(
            file_path=relative_path,
            code_snippet=code_snippet,
            metrics={"issue": "invalid_qml_aria_role", "role": role}
        )
        
        finding = Finding(
            id=finding_id,
            criterion=CriterionType.ARIA,
            selector="qml",
            details=f"Invalid ARIA role '{role}' in QML - not a valid ARIA role",
            evidence=[evidence],
            severity=SeverityLevel.MEDIUM,
            confidence=ConfidenceLevel.HIGH,
            wcag_criterion="4.1.2"
        )
        
        self.findings.append(finding)
    
    def _add_insufficient_qml_accessible_name_finding(self, code_snippet: str, name: str, relative_path: str, file_path: str):
        """Add finding for insufficient QML accessible name."""
        finding_id = generate_finding_id()
        
        evidence = Evidence(
            file_path=relative_path,
            code_snippet=code_snippet,
            metrics={"issue": "insufficient_qml_accessible_name", "name": name}
        )
        
        finding = Finding(
            id=finding_id,
            criterion=CriterionType.ARIA,
            selector="qml",
            details=f"QML accessible name '{name}' is too short - provide more descriptive text",
            evidence=[evidence],
            severity=SeverityLevel.MEDIUM,
            confidence=ConfidenceLevel.MEDIUM,
            wcag_criterion="4.1.2"
        )
        
        self.findings.append(finding)
    
    def _add_missing_qml_accessibility_finding(self, code_snippet: str, relative_path: str, file_path: str):
        """Add finding for missing QML accessibility properties."""
        finding_id = generate_finding_id()
        
        evidence = Evidence(
            file_path=relative_path,
            code_snippet=code_snippet,
            metrics={"issue": "missing_qml_accessibility"}
        )
        
        finding = Finding(
            id=finding_id,
            criterion=CriterionType.ARIA,
            selector="qml",
            details="QML interactive element lacks accessibility properties - add Accessible.name, Accessible.description, or Accessible.role",
            evidence=[evidence],
            severity=SeverityLevel.HIGH,
            confidence=ConfidenceLevel.HIGH,
            wcag_criterion="4.1.2"
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
            criterion=CriterionType.ARIA,
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

    async def _check_heading_structure(self, soup: BeautifulSoup, relative_path: str, file_path: str):
        """Check heading structure for accessibility."""
        try:
            headings = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
            
            if not headings:
                self._add_missing_headings_finding(relative_path, file_path)
                return
            
            # Check for proper heading hierarchy
            previous_level = 0
            for heading in headings:
                level = int(heading.name[1])
                
                if level > previous_level + 1:
                    self._add_heading_skip_finding(heading, previous_level, level, relative_path, file_path)
                
                previous_level = level
        
        except Exception as e:
            self._add_error_finding(file_path, relative_path, f"Error checking heading structure: {str(e)}")
    
    def _add_missing_headings_finding(self, relative_path: str, file_path: str):
        """Add finding for missing headings."""
        finding_id = generate_finding_id()
        
        evidence = Evidence(
            file_path=relative_path,
            code_snippet="<h1>, <h2>, <h3>, etc.",
            metrics={"issue": "missing_headings"}
        )
        
        finding = Finding(
            id=finding_id,
            criterion=CriterionType.ARIA,
            selector="headings",
            details="Document lacks proper heading structure - add heading elements (h1, h2, h3, etc.)",
            evidence=[evidence],
            severity=SeverityLevel.MEDIUM,
            confidence=ConfidenceLevel.MEDIUM,
            wcag_criterion="4.1.2"
        )
        
        self.findings.append(finding)
    
    def _add_heading_skip_finding(self, heading, previous_level: int, current_level: int, relative_path: str, file_path: str):
        """Add finding for heading level skip."""
        finding_id = generate_finding_id()
        
        evidence = Evidence(
            file_path=relative_path,
            code_snippet=str(heading),
            metrics={"issue": "heading_level_skip", "previous_level": previous_level, "current_level": current_level}
        )
        
        finding = Finding(
            id=finding_id,
            criterion=CriterionType.ARIA,
            selector=self._get_element_selector(heading),
            details=f"Heading level {current_level} skips from level {previous_level} - maintain proper heading hierarchy",
            evidence=[evidence],
            severity=SeverityLevel.MEDIUM,
            confidence=ConfidenceLevel.MEDIUM,
            wcag_criterion="4.1.2"
        )
        
        self.findings.append(finding)
    
    async def _check_labelledby_relationship(self, element, soup: BeautifulSoup, relative_path: str, file_path: str):
        """Check aria-labelledby relationship."""
        try:
            labelledby_ids = element.get('aria-labelledby', '').split()
            
            for label_id in labelledby_ids:
                label_element = soup.find(id=label_id)
                if not label_element:
                    self._add_broken_labelledby_relationship_finding(element, label_id, relative_path, file_path)
        
        except Exception as e:
            self._add_error_finding(file_path, relative_path, f"Error checking labelledby relationship: {str(e)}")
    
    async def _check_describedby_relationship(self, element, soup: BeautifulSoup, relative_path: str, file_path: str):
        """Check aria-describedby relationship."""
        try:
            describedby_ids = element.get('aria-describedby', '').split()
            
            for desc_id in describedby_ids:
                desc_element = soup.find(id=desc_id)
                if not desc_element:
                    self._add_broken_describedby_relationship_finding(element, desc_id, relative_path, file_path)
        
        except Exception as e:
            self._add_error_finding(file_path, relative_path, f"Error checking describedby relationship: {str(e)}")
    
    async def _check_controls_relationship(self, element, soup: BeautifulSoup, relative_path: str, file_path: str):
        """Check aria-controls relationship."""
        try:
            controls_ids = element.get('aria-controls', '').split()
            
            for control_id in controls_ids:
                control_element = soup.find(id=control_id)
                if not control_element:
                    self._add_broken_controls_relationship_finding(element, control_id, relative_path, file_path)
        
        except Exception as e:
            self._add_error_finding(file_path, relative_path, f"Error checking controls relationship: {str(e)}")
    
    def _add_broken_labelledby_relationship_finding(self, element, label_id: str, relative_path: str, file_path: str):
        """Add finding for broken aria-labelledby relationship."""
        finding_id = generate_finding_id()
        
        evidence = Evidence(
            file_path=relative_path,
            code_snippet=str(element),
            metrics={"issue": "broken_labelledby_relationship", "label_id": label_id}
        )
        
        finding = Finding(
            id=finding_id,
            criterion=CriterionType.ARIA,
            selector=self._get_element_selector(element),
            details=f"aria-labelledby references non-existent element with id '{label_id}'",
            evidence=[evidence],
            severity=SeverityLevel.HIGH,
            confidence=ConfidenceLevel.HIGH,
            wcag_criterion="4.1.2"
        )
        
        self.findings.append(finding)
    
    def _add_broken_describedby_relationship_finding(self, element, desc_id: str, relative_path: str, file_path: str):
        """Add finding for broken aria-describedby relationship."""
        finding_id = generate_finding_id()
        
        evidence = Evidence(
            file_path=relative_path,
            code_snippet=str(element),
            metrics={"issue": "broken_describedby_relationship", "desc_id": desc_id}
        )
        
        finding = Finding(
            id=finding_id,
            criterion=CriterionType.ARIA,
            selector=self._get_element_selector(element),
            details=f"aria-describedby references non-existent element with id '{desc_id}'",
            evidence=[evidence],
            severity=SeverityLevel.HIGH,
            confidence=ConfidenceLevel.HIGH,
            wcag_criterion="4.1.2"
        )
        
        self.findings.append(finding)
    
    def _add_broken_controls_relationship_finding(self, element, control_id: str, relative_path: str, file_path: str):
        """Add finding for broken aria-controls relationship."""
        finding_id = generate_finding_id()
        
        evidence = Evidence(
            file_path=relative_path,
            code_snippet=str(element),
            metrics={"issue": "broken_controls_relationship", "control_id": control_id}
        )
        
        finding = Finding(
            id=finding_id,
            criterion=CriterionType.ARIA,
            selector=self._get_element_selector(element),
            details=f"aria-controls references non-existent element with id '{control_id}'",
            evidence=[evidence],
            severity=SeverityLevel.HIGH,
            confidence=ConfidenceLevel.HIGH,
            wcag_criterion="4.1.2"
        )
        
        self.findings.append(finding)