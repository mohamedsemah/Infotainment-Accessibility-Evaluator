"""
ErrorPreventionAgent - Detects error prevention and recovery issues.
"""

import os
import re
from typing import List, Dict, Any
from bs4 import BeautifulSoup
from models.schemas import Finding, Evidence, SeverityLevel, ConfidenceLevel, CriterionType
from services.agents.base_agent import BaseAgent
import logging

logger = logging.getLogger(__name__)

class ErrorPreventionAgent(BaseAgent):
    """Agent for detecting error prevention and recovery issues."""
    
    def __init__(self):
        super().__init__(
            name="ErrorPreventionAgent",
            description="Detects error prevention and recovery issues",
            criterion=CriterionType.ARIA,
            wcag_criterion="3.3.4"
        )
    
    async def analyze(self, upload_path: str) -> List[Finding]:
        """Analyze files for error prevention issues."""
        findings = []
        
        try:
            html_files = self._find_files(upload_path, ['.html', '.htm', '.xhtml'])
            
            for file_path in html_files:
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    
                    soup = BeautifulSoup(content, 'html.parser')
                    file_findings = await self._analyze_html_content(soup, file_path)
                    findings.extend(file_findings)
                    
                except Exception as e:
                    logger.error(f"Error analyzing {file_path}: {str(e)}")
                    findings.append(self._create_error_finding(file_path, str(e)))
        
        except Exception as e:
            logger.error(f"ErrorPreventionAgent analysis failed: {str(e)}")
            findings.append(self._create_error_finding(upload_path, str(e)))
        
        return findings
    
    async def _analyze_html_content(self, soup: BeautifulSoup, file_path: str) -> List[Finding]:
        """Analyze HTML content for error prevention issues."""
        findings = []
        
        # Check form validation
        validation_findings = await self._check_form_validation(soup, file_path)
        findings.extend(validation_findings)
        
        # Check error messages
        error_message_findings = await self._check_error_messages(soup, file_path)
        findings.extend(error_message_findings)
        
        # Check confirmation dialogs
        confirmation_findings = await self._check_confirmation_dialogs(soup, file_path)
        findings.extend(confirmation_findings)
        
        return findings
    
    async def _check_form_validation(self, soup: BeautifulSoup, file_path: str) -> List[Finding]:
        """Check form validation for error prevention."""
        findings = []
        
        forms = soup.find_all('form')
        for form in forms:
            try:
                line_number = form.sourceline if hasattr(form, 'sourceline') else None
                
                # Check for required fields
                required_inputs = form.find_all('input', attrs={'required': True})
                for input_elem in required_inputs:
                    input_line = input_elem.sourceline if hasattr(input_elem, 'sourceline') else None
                    
                    # Check if required field has proper validation
                    if not self._has_proper_validation(input_elem):
                        findings.append(self._create_finding(
                            file_path=file_path,
                            line_number=input_line,
                            selector=self._get_selector(input_elem),
                            details="Required input missing proper validation",
                            severity=SeverityLevel.MEDIUM,
                            evidence=self._create_evidence(file_path, input_line, str(input_elem))
                        ))
                
                # Check for email validation
                email_inputs = form.find_all('input', attrs={'type': 'email'})
                for input_elem in email_inputs:
                    input_line = input_elem.sourceline if hasattr(input_elem, 'sourceline') else None
                    
                    if not self._has_email_validation(input_elem):
                        findings.append(self._create_finding(
                            file_path=file_path,
                            line_number=input_line,
                            selector=self._get_selector(input_elem),
                            details="Email input missing proper validation",
                            severity=SeverityLevel.MEDIUM,
                            evidence=self._create_evidence(file_path, input_line, str(input_elem))
                        ))
                
            except Exception as e:
                logger.error(f"Error checking form validation: {str(e)}")
        
        return findings
    
    async def _check_error_messages(self, soup: BeautifulSoup, file_path: str) -> List[Finding]:
        """Check for proper error message handling."""
        findings = []
        
        # Check for error message elements
        error_elements = soup.find_all(attrs={'role': 'alert'})
        error_elements.extend(soup.find_all(attrs={'aria-live': 'assertive'}))
        error_elements.extend(soup.find_all(class_=re.compile(r'error|invalid', re.IGNORECASE)))
        
        for element in error_elements:
            try:
                line_number = element.sourceline if hasattr(element, 'sourceline') else None
                text = element.get_text().strip()
                
                if not text:
                    findings.append(self._create_finding(
                        file_path=file_path,
                        line_number=line_number,
                        selector=self._get_selector(element),
                        details="Error message element is empty",
                        severity=SeverityLevel.MEDIUM,
                        evidence=self._create_evidence(file_path, line_number, str(element))
                    ))
                elif len(text) < 5:
                    findings.append(self._create_finding(
                        file_path=file_path,
                        line_number=line_number,
                        selector=self._get_selector(element),
                        details="Error message is too short to be helpful",
                        severity=SeverityLevel.LOW,
                        evidence=self._create_evidence(file_path, line_number, str(element))
                    ))
                
            except Exception as e:
                logger.error(f"Error checking error messages: {str(e)}")
        
        return findings
    
    async def _check_confirmation_dialogs(self, soup: BeautifulSoup, file_path: str) -> List[Finding]:
        """Check for confirmation dialogs for destructive actions."""
        findings = []
        
        # Check for delete buttons
        delete_buttons = soup.find_all('button', string=re.compile(r'delete|remove|clear', re.IGNORECASE))
        for button in delete_buttons:
            try:
                line_number = button.sourceline if hasattr(button, 'sourceline') else None
                
                # Check if button has confirmation
                if not self._has_confirmation(button):
                    findings.append(self._create_finding(
                        file_path=file_path,
                        line_number=line_number,
                        selector=self._get_selector(button),
                        details="Destructive action button missing confirmation",
                        severity=SeverityLevel.MEDIUM,
                        evidence=self._create_evidence(file_path, line_number, str(button))
                    ))
                
            except Exception as e:
                logger.error(f"Error checking delete buttons: {str(e)}")
        
        # Check for form submissions
        forms = soup.find_all('form')
        for form in forms:
            try:
                line_number = form.sourceline if hasattr(form, 'sourceline') else None
                
                # Check if form has confirmation for important actions
                if self._is_important_form(form) and not self._has_confirmation(form):
                    findings.append(self._create_finding(
                        file_path=file_path,
                        line_number=line_number,
                        selector=self._get_selector(form),
                        details="Important form missing confirmation",
                        severity=SeverityLevel.LOW,
                        evidence=self._create_evidence(file_path, line_number, str(form))
                    ))
                
            except Exception as e:
                logger.error(f"Error checking form confirmations: {str(e)}")
        
        return findings
    
    def _has_proper_validation(self, input_elem) -> bool:
        """Check if input has proper validation."""
        # Check for validation attributes
        validation_attrs = ['pattern', 'min', 'max', 'minlength', 'maxlength']
        if any(attr in input_elem.attrs for attr in validation_attrs):
            return True
        
        # Check for ARIA validation
        if input_elem.get('aria-invalid') is not None:
            return True
        
        return False
    
    def _has_email_validation(self, input_elem) -> bool:
        """Check if email input has proper validation."""
        # Check for email pattern
        if input_elem.get('pattern'):
            return True
        
        # Check for type="email" (basic validation)
        if input_elem.get('type') == 'email':
            return True
        
        return False
    
    def _has_confirmation(self, element) -> bool:
        """Check if element has confirmation."""
        # Check for onclick confirmation
        onclick = element.get('onclick', '')
        if 'confirm(' in onclick.lower():
            return True
        
        # Check for data attributes
        if element.get('data-confirm'):
            return True
        
        return False
    
    def _is_important_form(self, form) -> bool:
        """Check if form is important (needs confirmation)."""
        # Look for important form indicators
        form_text = form.get_text().lower()
        important_indicators = ['delete', 'remove', 'clear', 'reset', 'submit', 'save']
        
        return any(indicator in form_text for indicator in important_indicators)
    
    def _get_selector(self, element) -> str:
        """Generate CSS selector for element."""
        try:
            if element.get('id'):
                return f"#{element.get('id')}"
            elif element.get('class'):
                return f".{'.'.join(element.get('class'))}"
            else:
                return element.name
        except:
            return element.name if hasattr(element, 'name') else 'unknown'
