"""
InputAssistanceAgent - Detects input assistance and help issues.
"""

import os
import re
from typing import List, Dict, Any
from bs4 import BeautifulSoup
from models.schemas import Finding, Evidence, SeverityLevel, ConfidenceLevel, CriterionType
from services.agents.base_agent import BaseAgent
import logging

logger = logging.getLogger(__name__)

class InputAssistanceAgent(BaseAgent):
    """Agent for detecting input assistance and help issues."""
    
    def __init__(self):
        super().__init__(
            name="InputAssistanceAgent",
            description="Detects input assistance and help issues",
            criterion=CriterionType.ARIA,
            wcag_criterion="3.3.5"
        )
    
    async def analyze(self, upload_path: str) -> List[Finding]:
        """Analyze files for input assistance issues."""
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
            logger.error(f"InputAssistanceAgent analysis failed: {str(e)}")
            findings.append(self._create_error_finding(upload_path, str(e)))
        
        return findings
    
    async def _analyze_html_content(self, soup: BeautifulSoup, file_path: str) -> List[Finding]:
        """Analyze HTML content for input assistance issues."""
        findings = []
        
        # Check form help
        help_findings = await self._check_form_help(soup, file_path)
        findings.extend(help_findings)
        
        # Check error recovery
        recovery_findings = await self._check_error_recovery(soup, file_path)
        findings.extend(recovery_findings)
        
        # Check input instructions
        instruction_findings = await self._check_input_instructions(soup, file_path)
        findings.extend(instruction_findings)
        
        return findings
    
    async def _check_form_help(self, soup: BeautifulSoup, file_path: str) -> List[Finding]:
        """Check form help and assistance."""
        findings = []
        
        forms = soup.find_all('form')
        for form in forms:
            try:
                line_number = form.sourceline if hasattr(form, 'sourceline') else None
                
                # Check for help text
                help_elements = form.find_all(attrs={'aria-describedby': True})
                help_elements.extend(form.find_all(class_=re.compile(r'help|hint|instruction', re.IGNORECASE)))
                
                if not help_elements:
                    findings.append(self._create_finding(
                        file_path=file_path,
                        line_number=line_number,
                        selector=self._get_selector(form),
                        details="Form missing help text or instructions",
                        severity=SeverityLevel.LOW,
                        evidence=self._create_evidence(file_path, line_number, str(form))
                    ))
                
                # Check for required field indicators
                required_inputs = form.find_all('input', attrs={'required': True})
                for input_elem in required_inputs:
                    input_line = input_elem.sourceline if hasattr(input_elem, 'sourceline') else None
                    
                    # Check if required field has clear indication
                    if not self._has_required_indication(input_elem):
                        findings.append(self._create_finding(
                            file_path=file_path,
                            line_number=input_line,
                            selector=self._get_selector(input_elem),
                            details="Required field missing clear indication",
                            severity=SeverityLevel.MEDIUM,
                            evidence=self._create_evidence(file_path, input_line, str(input_elem))
                        ))
                
            except Exception as e:
                logger.error(f"Error checking form help: {str(e)}")
        
        return findings
    
    async def _check_error_recovery(self, soup: BeautifulSoup, file_path: str) -> List[Finding]:
        """Check error recovery mechanisms."""
        findings = []
        
        # Check for error recovery links
        error_elements = soup.find_all(attrs={'role': 'alert'})
        error_elements.extend(soup.find_all(class_=re.compile(r'error|invalid', re.IGNORECASE)))
        
        for element in error_elements:
            try:
                line_number = element.sourceline if hasattr(element, 'sourceline') else None
                text = element.get_text().strip()
                
                # Check if error message provides recovery options
                if not self._has_recovery_options(text):
                    findings.append(self._create_finding(
                        file_path=file_path,
                        line_number=line_number,
                        selector=self._get_selector(element),
                        details="Error message missing recovery options or suggestions",
                        severity=SeverityLevel.LOW,
                        evidence=self._create_evidence(file_path, line_number, str(element))
                    ))
                
            except Exception as e:
                logger.error(f"Error checking error recovery: {str(e)}")
        
        return findings
    
    async def _check_input_instructions(self, soup: BeautifulSoup, file_path: str) -> List[Finding]:
        """Check input instructions and guidance."""
        findings = []
        
        # Check for input instructions
        inputs = soup.find_all(['input', 'select', 'textarea'])
        for input_elem in inputs:
            try:
                line_number = input_elem.sourceline if hasattr(input_elem, 'sourceline') else None
                
                # Check if input has instructions
                if not self._has_input_instructions(input_elem):
                    findings.append(self._create_finding(
                        file_path=file_path,
                        line_number=line_number,
                        selector=self._get_selector(input_elem),
                        details="Input missing instructions or guidance",
                        severity=SeverityLevel.LOW,
                        evidence=self._create_evidence(file_path, line_number, str(input_elem))
                    ))
                
                # Check for placeholder text
                if input_elem.get('placeholder'):
                    placeholder = input_elem.get('placeholder', '')
                    if len(placeholder) < 3:
                        findings.append(self._create_finding(
                            file_path=file_path,
                            line_number=line_number,
                            selector=self._get_selector(input_elem),
                            details="Placeholder text too short to be helpful",
                            severity=SeverityLevel.LOW,
                            evidence=self._create_evidence(file_path, line_number, str(input_elem))
                        ))
                
            except Exception as e:
                logger.error(f"Error checking input instructions: {str(e)}")
        
        return findings
    
    def _has_required_indication(self, input_elem) -> bool:
        """Check if input has clear required indication."""
        # Check for asterisk in label
        label = input_elem.find_parent('label')
        if label and '*' in label.get_text():
            return True
        
        # Check for aria-required
        if input_elem.get('aria-required') == 'true':
            return True
        
        # Check for required attribute
        if input_elem.get('required'):
            return True
        
        return False
    
    def _has_recovery_options(self, text: str) -> bool:
        """Check if error text provides recovery options."""
        recovery_indicators = [
            'try', 'retry', 'again', 'correct', 'fix', 'change',
            'update', 'modify', 'adjust', 'resubmit'
        ]
        
        text_lower = text.lower()
        return any(indicator in text_lower for indicator in recovery_indicators)
    
    def _has_input_instructions(self, input_elem) -> bool:
        """Check if input has instructions."""
        # Check for aria-describedby
        if input_elem.get('aria-describedby'):
            return True
        
        # Check for placeholder
        if input_elem.get('placeholder'):
            return True
        
        # Check for associated help text
        input_id = input_elem.get('id')
        if input_id:
            # Look for help text with matching id
            help_text = input_elem.find_next(string=re.compile(r'help|hint|instruction', re.IGNORECASE))
            if help_text:
                return True
        
        return False
    
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
