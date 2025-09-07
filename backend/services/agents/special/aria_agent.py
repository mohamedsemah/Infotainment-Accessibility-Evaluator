"""
ARIAAgent - Evaluates ARIA attribute compliance for WCAG 2.2.
"""

import os
import re
from typing import List, Dict, Any, Optional
from pathlib import Path
from bs4 import BeautifulSoup

from models.schemas import Finding, Evidence, SeverityLevel, ConfidenceLevel, CriterionType
from utils.aria_maps import (
    get_role, get_attribute, validate_role_attribute_combination,
    validate_attribute_value, get_required_attributes_for_role,
    get_optional_attributes_for_role, get_prohibited_attributes_for_role
)
from utils.id_gen import generate_finding_id

class ARIAAgent:
    """Agent responsible for evaluating ARIA attribute compliance."""
    
    def __init__(self):
        self.findings = []
    
    async def analyze(self, upload_path: str, upload_id: str) -> List[Finding]:
        """Analyze uploaded files for ARIA attribute issues."""
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
        """Analyze HTML file for ARIA attribute issues."""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            soup = BeautifulSoup(content, 'html.parser')
            relative_path = os.path.relpath(file_path, upload_path)
            
            # Find all elements with ARIA attributes
            aria_elements = soup.find_all(attrs=lambda x: x and any(attr.startswith('aria-') for attr in x.keys()))
            
            for element in aria_elements:
                await self._analyze_element_aria(element, relative_path, file_path)
            
            # Check for missing ARIA attributes on interactive elements
            await self._check_missing_aria_attributes(soup, relative_path, file_path)
            
            # Check for ARIA landmarks
            await self._check_aria_landmarks(soup, relative_path, file_path)
        
        except Exception as e:
            self._add_error_finding(file_path, upload_path, f"Error analyzing HTML file: {str(e)}")
    
    async def _analyze_qml_file(self, file_path: str, upload_path: str):
        """Analyze QML file for ARIA attribute issues."""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            relative_path = os.path.relpath(file_path, upload_path)
            
            # Check for QML accessibility properties
            await self._check_qml_accessibility_properties(content, relative_path, file_path)
            
            # Check for QML interactive elements
            await self._check_qml_interactive_elements(content, relative_path, file_path)
        
        except Exception as e:
            self._add_error_finding(file_path, upload_path, f"Error analyzing QML file: {str(e)}")
    
    async def _analyze_element_aria(self, element, relative_path: str, file_path: str):
        """Analyze ARIA attributes on a specific element."""
        # Get role attribute
        role = element.get('role')
        
        if role:
            # Validate role
            role_info = get_role(role)
            if not role_info:
                self._add_invalid_role_finding(element, role, relative_path, file_path)
                return
            
            # Check required attributes
            required_attrs = get_required_attributes_for_role(role)
            for attr in required_attrs:
                if not element.get(attr):
                    self._add_missing_required_attr_finding(element, role, attr, relative_path, file_path)
            
            # Check prohibited attributes
            prohibited_attrs = get_prohibited_attributes_for_role(role)
            for attr in prohibited_attrs:
                if element.get(attr):
                    self._add_prohibited_attr_finding(element, role, attr, relative_path, file_path)
        
        # Check all ARIA attributes on the element
        for attr_name, attr_value in element.attrs.items():
            if attr_name.startswith('aria-'):
                await self._validate_aria_attribute(element, attr_name, attr_value, role, relative_path, file_path)
    
    async def _check_missing_aria_attributes(self, soup: BeautifulSoup, relative_path: str, file_path: str):
        """Check for missing ARIA attributes on interactive elements."""
        # Check for buttons without proper ARIA
        buttons = soup.find_all('button')
        for button in buttons:
            if not button.get('aria-label') and not button.get('aria-labelledby') and not button.get_text(strip=True):
                self._add_missing_aria_label_finding(button, 'button', relative_path, file_path)
        
        # Check for links without proper ARIA
        links = soup.find_all('a')
        for link in links:
            if not link.get('aria-label') and not link.get('aria-labelledby') and not link.get_text(strip=True):
                self._add_missing_aria_label_finding(link, 'link', relative_path, file_path)
        
        # Check for form inputs without proper ARIA
        inputs = soup.find_all('input')
        for input_elem in inputs:
            input_type = input_elem.get('type', 'text')
            if input_type in ['text', 'email', 'password', 'search', 'tel', 'url']:
                if not input_elem.get('aria-label') and not input_elem.get('aria-labelledby') and not input_elem.get('placeholder'):
                    self._add_missing_aria_label_finding(input_elem, 'input', relative_path, file_path)
        
        # Check for images without alt text
        images = soup.find_all('img')
        for img in images:
            if not img.get('alt') and not img.get('aria-label'):
                self._add_missing_alt_text_finding(img, relative_path, file_path)
    
    async def _check_aria_landmarks(self, soup: BeautifulSoup, relative_path: str, file_path: str):
        """Check for ARIA landmarks."""
        # Check for main landmark
        main_elements = soup.find_all(['main', 'div'], attrs={'role': 'main'})
        if not main_elements:
            self._add_missing_landmark_finding('main', relative_path, file_path)
        
        # Check for navigation landmarks
        nav_elements = soup.find_all(['nav', 'div'], attrs={'role': 'navigation'})
        if not nav_elements:
            self._add_missing_landmark_finding('navigation', relative_path, file_path)
        
        # Check for banner landmark
        banner_elements = soup.find_all(['header', 'div'], attrs={'role': 'banner'})
        if not banner_elements:
            self._add_missing_landmark_finding('banner', relative_path, file_path)
        
        # Check for contentinfo landmark
        contentinfo_elements = soup.find_all(['footer', 'div'], attrs={'role': 'contentinfo'})
        if not contentinfo_elements:
            self._add_missing_landmark_finding('contentinfo', relative_path, file_path)
    
    async def _check_qml_accessibility_properties(self, content: str, relative_path: str, file_path: str):
        """Check for QML accessibility properties."""
        # Find QML elements with accessibility properties
        accessibility_pattern = r'Accessible\s*\{[^}]*\}'
        matches = re.finditer(accessibility_pattern, content, re.IGNORECASE | re.DOTALL)
        
        for match in matches:
            accessible_block = match.group(0)
            
            # Check for required accessibility properties
            if 'name:' not in accessible_block.lower():
                self._add_missing_qml_accessibility_finding('name', accessible_block, relative_path, file_path)
            
            if 'role:' not in accessible_block.lower():
                self._add_missing_qml_accessibility_finding('role', accessible_block, relative_path, file_path)
    
    async def _check_qml_interactive_elements(self, content: str, relative_path: str, file_path: str):
        """Check for QML interactive elements without accessibility."""
        # Find QML interactive elements
        interactive_patterns = [
            r'<Button[^>]*>',
            r'<MouseArea[^>]*>',
            r'<Flickable[^>]*>',
            r'<ScrollView[^>]*>',
            r'<Slider[^>]*>',
            r'<Switch[^>]*>',
            r'<CheckBox[^>]*>',
            r'<RadioButton[^>]*>'
        ]
        
        for pattern in interactive_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            
            for match in matches:
                element = match.group(0)
                
                # Check if element has accessibility properties
                if 'Accessible' not in element and 'accessible' not in element:
                    self._add_missing_qml_accessibility_finding('Accessible', element, relative_path, file_path)
    
    async def _validate_aria_attribute(self, element, attr_name: str, attr_value: str, role: str, relative_path: str, file_path: str):
        """Validate a specific ARIA attribute."""
        # Check if attribute is valid for the role
        if role:
            validation = validate_role_attribute_combination(role, attr_name)
            
            if not validation["valid"]:
                if validation["prohibited"]:
                    self._add_prohibited_attr_finding(element, role, attr_name, relative_path, file_path)
                else:
                    self._add_invalid_attr_for_role_finding(element, role, attr_name, relative_path, file_path)
        
        # Validate attribute value
        value_validation = validate_attribute_value(attr_name, attr_value)
        
        if not value_validation["valid"]:
            self._add_invalid_attr_value_finding(element, attr_name, attr_value, value_validation, relative_path, file_path)
    
    def _add_invalid_role_finding(self, element, role: str, relative_path: str, file_path: str):
        """Add finding for invalid ARIA role."""
        finding_id = generate_finding_id()
        
        evidence = Evidence(
            file_path=relative_path,
            code_snippet=str(element),
            metrics={"role": role, "issue": "invalid_role"}
        )
        
        finding = Finding(
            id=finding_id,
            criterion=CriterionType.ARIA,
            selector=self._get_element_selector(element),
            details=f"Invalid ARIA role: {role}",
            evidence=[evidence],
            severity=SeverityLevel.HIGH,
            confidence=ConfidenceLevel.HIGH,
            wcag_criterion="4.1.2"
        )
        
        self.findings.append(finding)
    
    def _add_missing_required_attr_finding(self, element, role: str, attr: str, relative_path: str, file_path: str):
        """Add finding for missing required ARIA attribute."""
        finding_id = generate_finding_id()
        
        evidence = Evidence(
            file_path=relative_path,
            code_snippet=str(element),
            metrics={"role": role, "missing_attribute": attr, "issue": "missing_required_attribute"}
        )
        
        finding = Finding(
            id=finding_id,
            criterion=CriterionType.ARIA,
            selector=self._get_element_selector(element),
            details=f"Missing required ARIA attribute '{attr}' for role '{role}'",
            evidence=[evidence],
            severity=SeverityLevel.HIGH,
            confidence=ConfidenceLevel.HIGH,
            wcag_criterion="4.1.2"
        )
        
        self.findings.append(finding)
    
    def _add_prohibited_attr_finding(self, element, role: str, attr: str, relative_path: str, file_path: str):
        """Add finding for prohibited ARIA attribute."""
        finding_id = generate_finding_id()
        
        evidence = Evidence(
            file_path=relative_path,
            code_snippet=str(element),
            metrics={"role": role, "prohibited_attribute": attr, "issue": "prohibited_attribute"}
        )
        
        finding = Finding(
            id=finding_id,
            criterion=CriterionType.ARIA,
            selector=self._get_element_selector(element),
            details=f"Prohibited ARIA attribute '{attr}' for role '{role}'",
            evidence=[evidence],
            severity=SeverityLevel.MEDIUM,
            confidence=ConfidenceLevel.HIGH,
            wcag_criterion="4.1.2"
        )
        
        self.findings.append(finding)
    
    def _add_invalid_attr_for_role_finding(self, element, role: str, attr: str, relative_path: str, file_path: str):
        """Add finding for invalid ARIA attribute for role."""
        finding_id = generate_finding_id()
        
        evidence = Evidence(
            file_path=relative_path,
            code_snippet=str(element),
            metrics={"role": role, "attribute": attr, "issue": "invalid_attribute_for_role"}
        )
        
        finding = Finding(
            id=finding_id,
            criterion=CriterionType.ARIA,
            selector=self._get_element_selector(element),
            details=f"Invalid ARIA attribute '{attr}' for role '{role}'",
            evidence=[evidence],
            severity=SeverityLevel.MEDIUM,
            confidence=ConfidenceLevel.HIGH,
            wcag_criterion="4.1.2"
        )
        
        self.findings.append(finding)
    
    def _add_invalid_attr_value_finding(self, element, attr: str, value: str, validation: Dict[str, Any], relative_path: str, file_path: str):
        """Add finding for invalid ARIA attribute value."""
        finding_id = generate_finding_id()
        
        evidence = Evidence(
            file_path=relative_path,
            code_snippet=str(element),
            metrics={
                "attribute": attr,
                "value": value,
                "validation": validation,
                "issue": "invalid_attribute_value"
            }
        )
        
        finding = Finding(
            id=finding_id,
            criterion=CriterionType.ARIA,
            selector=self._get_element_selector(element),
            details=f"Invalid ARIA attribute value '{value}' for '{attr}'",
            evidence=[evidence],
            severity=SeverityLevel.MEDIUM,
            confidence=ConfidenceLevel.HIGH,
            wcag_criterion="4.1.2"
        )
        
        self.findings.append(finding)
    
    def _add_missing_aria_label_finding(self, element, element_type: str, relative_path: str, file_path: str):
        """Add finding for missing ARIA label."""
        finding_id = generate_finding_id()
        
        evidence = Evidence(
            file_path=relative_path,
            code_snippet=str(element),
            metrics={"element_type": element_type, "issue": "missing_aria_label"}
        )
        
        finding = Finding(
            id=finding_id,
            criterion=CriterionType.ARIA,
            selector=self._get_element_selector(element),
            details=f"Missing ARIA label for {element_type} element",
            evidence=[evidence],
            severity=SeverityLevel.HIGH,
            confidence=ConfidenceLevel.HIGH,
            wcag_criterion="4.1.2"
        )
        
        self.findings.append(finding)
    
    def _add_missing_alt_text_finding(self, element, relative_path: str, file_path: str):
        """Add finding for missing alt text."""
        finding_id = generate_finding_id()
        
        evidence = Evidence(
            file_path=relative_path,
            code_snippet=str(element),
            metrics={"issue": "missing_alt_text"}
        )
        
        finding = Finding(
            id=finding_id,
            criterion=CriterionType.ARIA,
            selector=self._get_element_selector(element),
            details="Missing alt text for image element",
            evidence=[evidence],
            severity=SeverityLevel.HIGH,
            confidence=ConfidenceLevel.HIGH,
            wcag_criterion="1.1.1"
        )
        
        self.findings.append(finding)
    
    def _add_missing_landmark_finding(self, landmark_type: str, relative_path: str, file_path: str):
        """Add finding for missing ARIA landmark."""
        finding_id = generate_finding_id()
        
        evidence = Evidence(
            file_path=relative_path,
            code_snippet="",
            metrics={"landmark_type": landmark_type, "issue": "missing_landmark"}
        )
        
        finding = Finding(
            id=finding_id,
            criterion=CriterionType.ARIA,
            selector="",
            details=f"Missing {landmark_type} landmark",
            evidence=[evidence],
            severity=SeverityLevel.MEDIUM,
            confidence=ConfidenceLevel.MEDIUM,
            wcag_criterion="1.3.1"
        )
        
        self.findings.append(finding)
    
    def _add_missing_qml_accessibility_finding(self, property_name: str, element: str, relative_path: str, file_path: str):
        """Add finding for missing QML accessibility property."""
        finding_id = generate_finding_id()
        
        evidence = Evidence(
            file_path=relative_path,
            code_snippet=element,
            metrics={"property_name": property_name, "issue": "missing_qml_accessibility"}
        )
        
        finding = Finding(
            id=finding_id,
            criterion=CriterionType.ARIA,
            selector="Accessible",
            details=f"Missing QML accessibility property: {property_name}",
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
