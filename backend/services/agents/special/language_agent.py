"""
LanguageAgent - Evaluates language attribute compliance for WCAG 2.2.
"""

import os
import re
from typing import List, Dict, Any, Optional
from pathlib import Path
from bs4 import BeautifulSoup

from models.schemas import Finding, Evidence, SeverityLevel, ConfidenceLevel, CriterionType
from utils.bcp47 import validate_language_tag, canonicalize_language_tag, get_language_name
from utils.id_gen import generate_finding_id

class LanguageAgent:
    """Agent responsible for evaluating language attribute compliance."""
    
    def __init__(self):
        self.findings = []
    
    async def analyze(self, upload_path: str, upload_id: str) -> List[Finding]:
        """Analyze uploaded files for language attribute issues."""
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
        """Analyze HTML file for language attribute issues."""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            soup = BeautifulSoup(content, 'html.parser')
            relative_path = os.path.relpath(file_path, upload_path)
            
            # Check for html lang attribute
            await self._check_html_lang_attribute(soup, relative_path, file_path)
            
            # Check for inline language changes
            await self._check_inline_language_changes(soup, relative_path, file_path)
            
            # Check for meta language declarations
            await self._check_meta_language(soup, relative_path, file_path)
        
        except Exception as e:
            self._add_error_finding(file_path, upload_path, f"Error analyzing HTML file: {str(e)}")
    
    async def _analyze_qml_file(self, file_path: str, upload_path: str):
        """Analyze QML file for language attribute issues."""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            relative_path = os.path.relpath(file_path, upload_path)
            
            # Check for QML language properties
            await self._check_qml_language_properties(content, relative_path, file_path)
            
            # Check for QML text elements without language context
            await self._check_qml_text_elements(content, relative_path, file_path)
        
        except Exception as e:
            self._add_error_finding(file_path, upload_path, f"Error analyzing QML file: {str(e)}")
    
    async def _check_html_lang_attribute(self, soup: BeautifulSoup, relative_path: str, file_path: str):
        """Check for html lang attribute."""
        html_element = soup.find('html')
        
        if not html_element:
            self._add_missing_html_finding(relative_path, file_path)
            return
        
        lang_value = html_element.get('lang')
        
        if not lang_value:
            self._add_missing_lang_finding(html_element, relative_path, file_path)
        else:
            # Validate language tag
            validation = validate_language_tag(lang_value)
            
            if not validation["valid"]:
                self._add_invalid_lang_finding(html_element, lang_value, validation, relative_path, file_path)
            else:
                # Check for canonicalization
                canonical = canonicalize_language_tag(lang_value)
                if canonical and canonical != lang_value:
                    self._add_canonicalization_finding(html_element, lang_value, canonical, relative_path, file_path)
    
    async def _check_inline_language_changes(self, soup: BeautifulSoup, relative_path: str, file_path: str):
        """Check for inline language changes."""
        # Find elements with lang attributes
        elements_with_lang = soup.find_all(attrs={'lang': True})
        
        for element in elements_with_lang:
            lang_value = element.get('lang')
            
            # Validate language tag
            validation = validate_language_tag(lang_value)
            
            if not validation["valid"]:
                self._add_invalid_inline_lang_finding(element, lang_value, validation, relative_path, file_path)
            else:
                # Check for canonicalization
                canonical = canonicalize_language_tag(lang_value)
                if canonical and canonical != lang_value:
                    self._add_inline_canonicalization_finding(element, lang_value, canonical, relative_path, file_path)
    
    async def _check_meta_language(self, soup: BeautifulSoup, relative_path: str, file_path: str):
        """Check for meta language declarations."""
        meta_lang = soup.find('meta', attrs={'http-equiv': 'content-language'})
        
        if meta_lang:
            content = meta_lang.get('content', '')
            
            if content:
                # Validate language tag
                validation = validate_language_tag(content)
                
                if not validation["valid"]:
                    self._add_invalid_meta_lang_finding(meta_lang, content, validation, relative_path, file_path)
    
    async def _check_qml_language_properties(self, content: str, relative_path: str, file_path: str):
        """Check for QML language properties."""
        # Find QML language properties
        lang_pattern = r'language\s*:\s*["\']([^"\']+)["\']'
        matches = re.finditer(lang_pattern, content, re.IGNORECASE)
        
        for match in matches:
            lang_value = match.group(1)
            
            # Validate language tag
            validation = validate_language_tag(lang_value)
            
            if not validation["valid"]:
                self._add_invalid_qml_lang_finding(lang_value, validation, relative_path, file_path)
            else:
                # Check for canonicalization
                canonical = canonicalize_language_tag(lang_value)
                if canonical and canonical != lang_value:
                    self._add_qml_canonicalization_finding(lang_value, canonical, relative_path, file_path)
    
    async def _check_qml_text_elements(self, content: str, relative_path: str, file_path: str):
        """Check for QML text elements without language context."""
        # Find QML text elements
        text_pattern = r'<Text[^>]*>([^<]+)</Text>'
        matches = re.finditer(text_pattern, content, re.IGNORECASE)
        
        for match in matches:
            text_content = match.group(1).strip()
            
            if text_content and len(text_content) > 10:  # Only check substantial text
                # Check if there's a language property nearby
                text_start = match.start()
                text_end = match.end()
                
                # Look for language property in the surrounding context
                context_start = max(0, text_start - 200)
                context_end = min(len(content), text_end + 200)
                context = content[context_start:context_end]
                
                if 'language:' not in context.lower():
                    self._add_qml_text_without_lang_finding(text_content, relative_path, file_path)
    
    def _add_missing_html_finding(self, relative_path: str, file_path: str):
        """Add finding for missing html element."""
        finding_id = generate_finding_id()
        
        evidence = Evidence(
            file_path=relative_path,
            code_snippet="",
            metrics={"issue": "missing_html_element"}
        )
        
        finding = Finding(
            id=finding_id,
            criterion=CriterionType.LANGUAGE,
            selector="html",
            details="Missing html element",
            evidence=[evidence],
            severity=SeverityLevel.HIGH,
            confidence=ConfidenceLevel.HIGH,
            wcag_criterion="3.1.1"
        )
        
        self.findings.append(finding)
    
    def _add_missing_lang_finding(self, html_element, relative_path: str, file_path: str):
        """Add finding for missing lang attribute."""
        finding_id = generate_finding_id()
        
        evidence = Evidence(
            file_path=relative_path,
            code_snippet=str(html_element),
            metrics={"issue": "missing_lang_attribute"}
        )
        
        finding = Finding(
            id=finding_id,
            criterion=CriterionType.LANGUAGE,
            selector="html",
            details="Missing lang attribute on html element",
            evidence=[evidence],
            severity=SeverityLevel.HIGH,
            confidence=ConfidenceLevel.HIGH,
            wcag_criterion="3.1.1"
        )
        
        self.findings.append(finding)
    
    def _add_invalid_lang_finding(self, html_element, lang_value: str, validation: Dict[str, Any], relative_path: str, file_path: str):
        """Add finding for invalid lang attribute."""
        finding_id = generate_finding_id()
        
        evidence = Evidence(
            file_path=relative_path,
            code_snippet=str(html_element),
            metrics={
                "lang_value": lang_value,
                "validation": validation,
                "issue": "invalid_lang_attribute"
            }
        )
        
        finding = Finding(
            id=finding_id,
            criterion=CriterionType.LANGUAGE,
            selector="html",
            details=f"Invalid lang attribute value: {lang_value}",
            evidence=[evidence],
            severity=SeverityLevel.MEDIUM,
            confidence=ConfidenceLevel.HIGH,
            wcag_criterion="3.1.1"
        )
        
        self.findings.append(finding)
    
    def _add_canonicalization_finding(self, html_element, lang_value: str, canonical: str, relative_path: str, file_path: str):
        """Add finding for lang attribute canonicalization."""
        finding_id = generate_finding_id()
        
        evidence = Evidence(
            file_path=relative_path,
            code_snippet=str(html_element),
            metrics={
                "lang_value": lang_value,
                "canonical": canonical,
                "issue": "lang_canonicalization"
            }
        )
        
        finding = Finding(
            id=finding_id,
            criterion=CriterionType.LANGUAGE,
            selector="html",
            details=f"Lang attribute should be canonicalized: {lang_value} → {canonical}",
            evidence=[evidence],
            severity=SeverityLevel.LOW,
            confidence=ConfidenceLevel.MEDIUM,
            wcag_criterion="3.1.1"
        )
        
        self.findings.append(finding)
    
    def _add_invalid_inline_lang_finding(self, element, lang_value: str, validation: Dict[str, Any], relative_path: str, file_path: str):
        """Add finding for invalid inline lang attribute."""
        finding_id = generate_finding_id()
        
        evidence = Evidence(
            file_path=relative_path,
            code_snippet=str(element),
            metrics={
                "lang_value": lang_value,
                "validation": validation,
                "issue": "invalid_inline_lang_attribute"
            }
        )
        
        finding = Finding(
            id=finding_id,
            criterion=CriterionType.LANGUAGE,
            selector=self._get_element_selector(element),
            details=f"Invalid inline lang attribute value: {lang_value}",
            evidence=[evidence],
            severity=SeverityLevel.MEDIUM,
            confidence=ConfidenceLevel.HIGH,
            wcag_criterion="3.1.2"
        )
        
        self.findings.append(finding)
    
    def _add_inline_canonicalization_finding(self, element, lang_value: str, canonical: str, relative_path: str, file_path: str):
        """Add finding for inline lang attribute canonicalization."""
        finding_id = generate_finding_id()
        
        evidence = Evidence(
            file_path=relative_path,
            code_snippet=str(element),
            metrics={
                "lang_value": lang_value,
                "canonical": canonical,
                "issue": "inline_lang_canonicalization"
            }
        )
        
        finding = Finding(
            id=finding_id,
            criterion=CriterionType.LANGUAGE,
            selector=self._get_element_selector(element),
            details=f"Inline lang attribute should be canonicalized: {lang_value} → {canonical}",
            evidence=[evidence],
            severity=SeverityLevel.LOW,
            confidence=ConfidenceLevel.MEDIUM,
            wcag_criterion="3.1.2"
        )
        
        self.findings.append(finding)
    
    def _add_invalid_meta_lang_finding(self, meta_element, content: str, validation: Dict[str, Any], relative_path: str, file_path: str):
        """Add finding for invalid meta language declaration."""
        finding_id = generate_finding_id()
        
        evidence = Evidence(
            file_path=relative_path,
            code_snippet=str(meta_element),
            metrics={
                "content": content,
                "validation": validation,
                "issue": "invalid_meta_lang"
            }
        )
        
        finding = Finding(
            id=finding_id,
            criterion=CriterionType.LANGUAGE,
            selector="meta",
            details=f"Invalid meta language declaration: {content}",
            evidence=[evidence],
            severity=SeverityLevel.MEDIUM,
            confidence=ConfidenceLevel.HIGH,
            wcag_criterion="3.1.1"
        )
        
        self.findings.append(finding)
    
    def _add_invalid_qml_lang_finding(self, lang_value: str, validation: Dict[str, Any], relative_path: str, file_path: str):
        """Add finding for invalid QML language property."""
        finding_id = generate_finding_id()
        
        evidence = Evidence(
            file_path=relative_path,
            code_snippet=f"language: {lang_value}",
            metrics={
                "lang_value": lang_value,
                "validation": validation,
                "issue": "invalid_qml_lang"
            }
        )
        
        finding = Finding(
            id=finding_id,
            criterion=CriterionType.LANGUAGE,
            selector="language",
            details=f"Invalid QML language property: {lang_value}",
            evidence=[evidence],
            severity=SeverityLevel.MEDIUM,
            confidence=ConfidenceLevel.HIGH,
            wcag_criterion="3.1.1"
        )
        
        self.findings.append(finding)
    
    def _add_qml_canonicalization_finding(self, lang_value: str, canonical: str, relative_path: str, file_path: str):
        """Add finding for QML language property canonicalization."""
        finding_id = generate_finding_id()
        
        evidence = Evidence(
            file_path=relative_path,
            code_snippet=f"language: {lang_value}",
            metrics={
                "lang_value": lang_value,
                "canonical": canonical,
                "issue": "qml_lang_canonicalization"
            }
        )
        
        finding = Finding(
            id=finding_id,
            criterion=CriterionType.LANGUAGE,
            selector="language",
            details=f"QML language property should be canonicalized: {lang_value} → {canonical}",
            evidence=[evidence],
            severity=SeverityLevel.LOW,
            confidence=ConfidenceLevel.MEDIUM,
            wcag_criterion="3.1.1"
        )
        
        self.findings.append(finding)
    
    def _add_qml_text_without_lang_finding(self, text_content: str, relative_path: str, file_path: str):
        """Add finding for QML text without language context."""
        finding_id = generate_finding_id()
        
        evidence = Evidence(
            file_path=relative_path,
            code_snippet=f"<Text>{text_content[:50]}...</Text>",
            metrics={
                "text_content": text_content[:100],
                "issue": "qml_text_without_lang"
            }
        )
        
        finding = Finding(
            id=finding_id,
            criterion=CriterionType.LANGUAGE,
            selector="Text",
            details="QML text element without language context",
            evidence=[evidence],
            severity=SeverityLevel.LOW,
            confidence=ConfidenceLevel.MEDIUM,
            wcag_criterion="3.1.2"
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
            criterion=CriterionType.LANGUAGE,
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
