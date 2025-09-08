"""
LanguageAgent - Evaluates language attribute compliance for WCAG 2.2.
"""

import os
import re
from typing import List, Dict, Any, Optional
from pathlib import Path
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET

from models.schemas import Finding, Evidence, SeverityLevel, ConfidenceLevel, CriterionType
from utils.bcp47 import validate_language_tag, canonicalize_language_tag
from utils.id_gen import generate_finding_id
from services.agents.base_agent import BaseAgent

class LanguageAgent(BaseAgent):
    """Agent responsible for evaluating language attribute compliance."""
    
    def __init__(self):
        super().__init__(
            name="LanguageAgent",
            description="Evaluates language attribute compliance for WCAG 2.2",
            criterion=CriterionType.LANGUAGE,
            wcag_criterion="3.1.1"
        )
        self.findings = []
    
    async def analyze(self, upload_path: str) -> List[Finding]:
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
            
            # Check for html element
            html_element = soup.find('html')
            if not html_element:
                self._add_missing_html_element_finding(relative_path, file_path)
                return
            
            # Check for lang attribute on html element
            lang_attr = html_element.get('lang')
            if not lang_attr:
                self._add_missing_lang_attribute_finding(html_element, relative_path, file_path)
            else:
                # Validate the language code
                await self._validate_language_code(html_element, lang_attr, relative_path, file_path)
            
            # Check for elements with different language than the document
            await self._check_language_changes(soup, relative_path, file_path)
            
            # Check for elements that should have language attributes
            await self._check_elements_needing_language(soup, relative_path, file_path)
        
        except Exception as e:
            self._add_error_finding(file_path, relative_path, f"Error analyzing HTML file: {str(e)}")
    
    async def _analyze_qml_file(self, file_path: str, upload_path: str):
        """Analyze QML file for language attribute issues."""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            relative_path = os.path.relpath(file_path, upload_path)
            
            # Check for language-related properties in QML
            await self._check_qml_language_properties(content, relative_path, file_path)
            
            # Check for text elements without language context
            await self._check_qml_text_elements(content, relative_path, file_path)
        
        except Exception as e:
            self._add_error_finding(file_path, relative_path, f"Error analyzing QML file: {str(e)}")
    
    async def _validate_language_code(self, html_element, lang_code: str, relative_path: str, file_path: str):
        """Validate the language code format."""
        try:
            # Check if the language code is valid BCP 47
            validation_result = validate_language_tag(lang_code)
            is_valid = validation_result["valid"]
            normalized_code = validation_result["canonical"]
            
            if not is_valid:
                self._add_invalid_language_code_finding(
                    html_element, lang_code, relative_path, file_path
                )
            elif normalized_code != lang_code:
                self._add_normalization_suggestion_finding(
                    html_element, lang_code, normalized_code, relative_path, file_path
                )
        
        except Exception as e:
            self._add_error_finding(file_path, relative_path, f"Error validating language code: {str(e)}")
    
    async def _check_language_changes(self, soup: BeautifulSoup, relative_path: str, file_path: str):
        """Check for elements with different language than the document."""
        try:
            # Get the document language
            html_element = soup.find('html')
            if not html_element:
                return
            
            doc_lang = html_element.get('lang', '')
            
            # Find elements with lang attributes
            elements_with_lang = soup.find_all(attrs={'lang': True})
            
            for element in elements_with_lang:
                element_lang = element.get('lang', '')
                
                if element_lang != doc_lang:
                    # Validate the element's language code
                    is_valid, normalized_code = validate_language_code(element_lang)
                    
                    if not is_valid:
                        self._add_invalid_language_code_finding(
                            element, element_lang, relative_path, file_path
                        )
                    else:
                        # Check if the language change is appropriate
                        await self._check_language_change_appropriateness(
                            element, element_lang, doc_lang, relative_path, file_path
                        )
        
        except Exception as e:
            self._add_error_finding(file_path, relative_path, f"Error checking language changes: {str(e)}")
    
    async def _check_elements_needing_language(self, soup: BeautifulSoup, relative_path: str, file_path: str):
        """Check for elements that should have language attributes."""
        try:
            # Elements that often need language attributes
            elements_to_check = [
                'blockquote', 'q', 'cite', 'dfn', 'abbr', 'acronym',
                'address', 'ins', 'del', 'samp', 'kbd', 'var', 'code'
            ]
            
            for tag_name in elements_to_check:
                elements = soup.find_all(tag_name)
                
                for element in elements:
                    # Check if element contains text in a different language
                    if self._contains_foreign_language(element):
                        if not element.get('lang'):
                            self._add_missing_language_attribute_finding(
                                element, tag_name, relative_path, file_path
                            )
        
        except Exception as e:
            self._add_error_finding(file_path, relative_path, f"Error checking elements needing language: {str(e)}")
    
    async def _check_qml_language_properties(self, content: str, relative_path: str, file_path: str):
        """Check QML file for language-related properties."""
        try:
            # Look for language-related properties in QML
            language_patterns = [
                r'locale\s*:\s*["\']([^"\']+)["\']',  # locale property
                r'language\s*:\s*["\']([^"\']+)["\']',  # language property
                r'text\s*:\s*["\']([^"\']+)["\']',  # text property
            ]
            
            for pattern in language_patterns:
                matches = re.finditer(pattern, content, re.IGNORECASE)
                for match in matches:
                    if 'locale' in pattern or 'language' in pattern:
                        # Validate language code
                        lang_code = match.group(1)
                        validation_result = validate_language_tag(lang_code)
                        is_valid = validation_result["valid"]
                        normalized_code = validation_result["canonical"]
                        
                        if not is_valid:
                            self._add_invalid_qml_language_finding(
                                match.group(0), lang_code, relative_path, file_path
                            )
        
        except Exception as e:
            self._add_error_finding(file_path, relative_path, f"Error checking QML language properties: {str(e)}")
    
    async def _check_qml_text_elements(self, content: str, relative_path: str, file_path: str):
        """Check QML text elements for language context."""
        try:
            # Look for text elements that might need language context
            text_patterns = [
                r'Text\s*\{[^}]*text\s*:\s*["\']([^"\']+)["\']',  # Text elements
                r'Label\s*\{[^}]*text\s*:\s*["\']([^"\']+)["\']',  # Label elements
            ]
            
            for pattern in text_patterns:
                matches = re.finditer(pattern, content, re.IGNORECASE | re.DOTALL)
                for match in matches:
                    text_content = match.group(1)
                    
                    # Check if text contains foreign language characters
                    if self._contains_foreign_language_text(text_content):
                        self._add_qml_text_language_finding(
                            match.group(0), text_content, relative_path, file_path
                        )
                    
        except Exception as e:
            self._add_error_finding(file_path, relative_path, f"Error checking QML text elements: {str(e)}")
    
    async def _check_language_change_appropriateness(self, element, element_lang: str, doc_lang: str, relative_path: str, file_path: str):
        """Check if a language change is appropriate."""
        try:
            # Check if the element actually contains text in the specified language
            element_text = element.get_text(strip=True)
            
            if not element_text:
                # Element has lang attribute but no text
                self._add_unnecessary_language_attribute_finding(
                    element, element_lang, relative_path, file_path
                )
            elif not self._text_matches_language(element_text, element_lang):
                # Element text doesn't match the specified language
                self._add_mismatched_language_finding(
                    element, element_lang, element_text, relative_path, file_path
                )
        
        except Exception as e:
            self._add_error_finding(file_path, relative_path, f"Error checking language change appropriateness: {str(e)}")
    
    def _contains_foreign_language(self, element) -> bool:
        """Check if element contains text in a foreign language."""
        text = element.get_text(strip=True)
        return self._contains_foreign_language_text(text)
    
    def _contains_foreign_language_text(self, text: str) -> bool:
        """Check if text contains foreign language characters."""
        if not text:
            return False
        
        # Check for non-Latin characters
        non_latin_pattern = r'[^\x00-\x7F\u00A0-\u00FF\u0100-\u017F\u0180-\u024F\u1E00-\u1EFF]'
        return bool(re.search(non_latin_pattern, text))
    
    def _text_matches_language(self, text: str, language_code: str) -> bool:
        """Check if text matches the specified language."""
        # This is a simplified check - in a real implementation, you'd use
        # language detection libraries or more sophisticated heuristics
        
        if not text or not language_code:
            return False
        
        # Check for common language patterns
        language_patterns = {
            'en': r'[a-zA-Z]',  # English
            'es': r'[ñáéíóúü]',  # Spanish
            'fr': r'[àâäéèêëïîôöùûüÿç]',  # French
            'de': r'[äöüß]',  # German
            'zh': r'[\u4e00-\u9fff]',  # Chinese
            'ja': r'[\u3040-\u309f\u30a0-\u30ff]',  # Japanese
            'ko': r'[\uac00-\ud7af]',  # Korean
            'ar': r'[\u0600-\u06ff]',  # Arabic
            'ru': r'[\u0400-\u04ff]',  # Russian
        }
        
        # Get the base language code
        base_lang = language_code.split('-')[0].lower()
        
        if base_lang in language_patterns:
            pattern = language_patterns[base_lang]
            return bool(re.search(pattern, text))
        
        return True  # If we can't determine, assume it's correct
    
    def _add_missing_html_element_finding(self, relative_path: str, file_path: str):
        """Add finding for missing html element."""
        finding_id = generate_finding_id()
        
        evidence = Evidence(
            file_path=relative_path,
            code_snippet="<html>",
            metrics={"issue": "missing_html_element"}
        )
        
        finding = Finding(
            id=finding_id,
            criterion=CriterionType.LANGUAGE,
                    selector="html",
            details="HTML document is missing the root <html> element",
            evidence=[evidence],
                    severity=SeverityLevel.HIGH,
            confidence=ConfidenceLevel.HIGH,
            wcag_criterion="3.1.1"
        )
        
        self.findings.append(finding)
    
    def _add_missing_lang_attribute_finding(self, html_element, relative_path: str, file_path: str):
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
            details="HTML element is missing the lang attribute",
            evidence=[evidence],
            severity=SeverityLevel.HIGH,
            confidence=ConfidenceLevel.HIGH,
            wcag_criterion="3.1.1"
        )
        
        self.findings.append(finding)
    
    def _add_invalid_language_code_finding(self, element, lang_code: str, relative_path: str, file_path: str):
        """Add finding for invalid language code."""
        finding_id = generate_finding_id()
        
        evidence = Evidence(
            file_path=relative_path,
            code_snippet=str(element),
            metrics={"issue": "invalid_language_code", "lang_code": lang_code}
        )
        
        finding = Finding(
            id=finding_id,
            criterion=CriterionType.LANGUAGE,
            selector=self._get_element_selector(element),
            details=f"Invalid language code '{lang_code}' - must be valid BCP 47 format",
            evidence=[evidence],
                        severity=SeverityLevel.MEDIUM,
            confidence=ConfidenceLevel.HIGH,
            wcag_criterion="3.1.1"
        )
        
        self.findings.append(finding)
    
    def _add_normalization_suggestion_finding(self, element, current_code: str, normalized_code: str, relative_path: str, file_path: str):
        """Add finding for language code normalization suggestion."""
        finding_id = generate_finding_id()
        
        evidence = Evidence(
            file_path=relative_path,
            code_snippet=str(element),
            metrics={
                "issue": "language_code_normalization",
                "current_code": current_code,
                "normalized_code": normalized_code
            }
        )
        
        finding = Finding(
            id=finding_id,
            criterion=CriterionType.LANGUAGE,
            selector=self._get_element_selector(element),
            details=f"Language code '{current_code}' should be normalized to '{normalized_code}'",
            evidence=[evidence],
            severity=SeverityLevel.LOW,
            confidence=ConfidenceLevel.MEDIUM,
            wcag_criterion="3.1.1"
        )
        
        self.findings.append(finding)
    
    def _add_missing_language_attribute_finding(self, element, tag_name: str, relative_path: str, file_path: str):
        """Add finding for missing language attribute on element."""
        finding_id = generate_finding_id()
        
        evidence = Evidence(
            file_path=relative_path,
            code_snippet=str(element),
            metrics={"issue": "missing_language_attribute", "tag": tag_name}
        )
        
        finding = Finding(
            id=finding_id,
            criterion=CriterionType.LANGUAGE,
            selector=self._get_element_selector(element),
            details=f"<{tag_name}> element contains foreign language text but lacks lang attribute",
            evidence=[evidence],
            severity=SeverityLevel.MEDIUM,
            confidence=ConfidenceLevel.MEDIUM,
            wcag_criterion="3.1.1"
        )
        
        self.findings.append(finding)
    
    def _add_unnecessary_language_attribute_finding(self, element, lang_code: str, relative_path: str, file_path: str):
        """Add finding for unnecessary language attribute."""
        finding_id = generate_finding_id()
        
        evidence = Evidence(
            file_path=relative_path,
            code_snippet=str(element),
            metrics={"issue": "unnecessary_language_attribute", "lang_code": lang_code}
        )
        
        finding = Finding(
            id=finding_id,
            criterion=CriterionType.LANGUAGE,
            selector=self._get_element_selector(element),
            details=f"Element has lang attribute '{lang_code}' but contains no text",
            evidence=[evidence],
                            severity=SeverityLevel.LOW,
            confidence=ConfidenceLevel.MEDIUM,
            wcag_criterion="3.1.1"
        )
        
        self.findings.append(finding)
    
    def _add_mismatched_language_finding(self, element, lang_code: str, text: str, relative_path: str, file_path: str):
        """Add finding for mismatched language."""
        finding_id = generate_finding_id()
        
        evidence = Evidence(
            file_path=relative_path,
            code_snippet=str(element),
            metrics={"issue": "mismatched_language", "lang_code": lang_code, "text": text[:100]}
        )
        
        finding = Finding(
            id=finding_id,
            criterion=CriterionType.LANGUAGE,
            selector=self._get_element_selector(element),
            details=f"Element text doesn't match specified language '{lang_code}'",
            evidence=[evidence],
            severity=SeverityLevel.MEDIUM,
            confidence=ConfidenceLevel.MEDIUM,
            wcag_criterion="3.1.1"
        )
        
        self.findings.append(finding)
    
    def _add_invalid_qml_language_finding(self, code_snippet: str, lang_code: str, relative_path: str, file_path: str):
        """Add finding for invalid QML language code."""
        finding_id = generate_finding_id()
        
        evidence = Evidence(
            file_path=relative_path,
            code_snippet=code_snippet,
            metrics={"issue": "invalid_qml_language_code", "lang_code": lang_code}
        )
        
        finding = Finding(
            id=finding_id,
            criterion=CriterionType.LANGUAGE,
            selector="qml",
            details=f"Invalid language code '{lang_code}' in QML - must be valid BCP 47 format",
            evidence=[evidence],
            severity=SeverityLevel.MEDIUM,
            confidence=ConfidenceLevel.HIGH,
            wcag_criterion="3.1.1"
        )
        
        self.findings.append(finding)
    
    def _add_qml_text_language_finding(self, code_snippet: str, text: str, relative_path: str, file_path: str):
        """Add finding for QML text without language context."""
        finding_id = generate_finding_id()
        
        evidence = Evidence(
            file_path=relative_path,
            code_snippet=code_snippet,
            metrics={"issue": "qml_text_language_context", "text": text[:100]}
        )
        
        finding = Finding(
            id=finding_id,
            criterion=CriterionType.LANGUAGE,
            selector="qml",
            details="QML text element contains foreign language characters but lacks language context",
            evidence=[evidence],
            severity=SeverityLevel.MEDIUM,
            confidence=ConfidenceLevel.MEDIUM,
            wcag_criterion="3.1.1"
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