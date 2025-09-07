"""
AssistiveTechSimulationAgent - Simulates assistive technology behavior.
"""

import os
import re
from typing import List, Dict, Any
from bs4 import BeautifulSoup
from models.schemas import Finding, Evidence, SeverityLevel, ConfidenceLevel, CriterionType
from services.agents.base_agent import BaseAgent
import logging

logger = logging.getLogger(__name__)

class AssistiveTechSimulationAgent(BaseAgent):
    """Agent for simulating assistive technology behavior."""
    
    def __init__(self):
        super().__init__(
            name="AssistiveTechSimulationAgent",
            description="Simulates assistive technology behavior",
            criterion=CriterionType.ARIA,
            wcag_criterion="4.1.3"
        )
    
    async def analyze(self, upload_path: str) -> List[Finding]:
        """Analyze files for assistive technology compatibility."""
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
            logger.error(f"AssistiveTechSimulationAgent analysis failed: {str(e)}")
            findings.append(self._create_error_finding(upload_path, str(e)))
        
        return findings
    
    async def _analyze_html_content(self, soup: BeautifulSoup, file_path: str) -> List[Finding]:
        """Analyze HTML content for assistive technology compatibility."""
        findings = []
        
        # Check screen reader compatibility
        screen_reader_findings = await self._check_screen_reader_compatibility(soup, file_path)
        findings.extend(screen_reader_findings)
        
        # Check keyboard navigation
        keyboard_findings = await self._check_keyboard_navigation(soup, file_path)
        findings.extend(keyboard_findings)
        
        # Check focus management
        focus_findings = await self._check_focus_management(soup, file_path)
        findings.extend(focus_findings)
        
        return findings
    
    async def _check_screen_reader_compatibility(self, soup: BeautifulSoup, file_path: str) -> List[Finding]:
        """Check screen reader compatibility."""
        findings = []
        
        # Check for missing alt text on images
        images = soup.find_all('img')
        for img in images:
            try:
                line_number = img.sourceline if hasattr(img, 'sourceline') else None
                alt_text = img.get('alt', '')
                
                if not alt_text:
                    findings.append(self._create_finding(
                        file_path=file_path,
                        line_number=line_number,
                        selector=self._get_selector(img),
                        details="Image missing alt text for screen readers",
                        severity=SeverityLevel.HIGH,
                        evidence=self._create_evidence(file_path, line_number, str(img))
                    ))
                
            except Exception as e:
                logger.error(f"Error checking image alt text: {str(e)}")
        
        # Check for missing labels on form controls
        form_controls = soup.find_all(['input', 'select', 'textarea'])
        for control in form_controls:
            try:
                line_number = control.sourceline if hasattr(control, 'sourceline') else None
                
                # Skip hidden inputs
                if control.get('type') == 'hidden':
                    continue
                
                # Check for label association
                control_id = control.get('id')
                if control_id:
                    label = soup.find('label', {'for': control_id})
                    if not label:
                        findings.append(self._create_finding(
                            file_path=file_path,
                            line_number=line_number,
                            selector=self._get_selector(control),
                            details="Form control missing associated label for screen readers",
                            severity=SeverityLevel.HIGH,
                            evidence=self._create_evidence(file_path, line_number, str(control))
                        ))
                
            except Exception as e:
                logger.error(f"Error checking form control labels: {str(e)}")
        
        # Check for proper heading structure
        headings = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
        if headings:
            # Check for missing h1
            h1_count = len(soup.find_all('h1'))
            if h1_count == 0:
                findings.append(self._create_finding(
                    file_path=file_path,
                    line_number=1,
                    selector="body",
                    details="Page missing h1 heading - screen readers need clear page structure",
                    severity=SeverityLevel.HIGH,
                    evidence=self._create_evidence(file_path, 1, "No h1 element found")
                ))
            
            # Check for proper heading hierarchy
            prev_level = 0
            for heading in headings:
                try:
                    level = int(heading.name[1])
                    line_number = heading.sourceline if hasattr(heading, 'sourceline') else None
                    
                    if level > prev_level + 1:
                        findings.append(self._create_finding(
                            file_path=file_path,
                            line_number=line_number,
                            selector=self._get_selector(heading),
                            details=f"Heading level skipped from h{prev_level} to h{level} - screen readers may be confused",
                            severity=SeverityLevel.MEDIUM,
                            evidence=self._create_evidence(file_path, line_number, str(heading))
                        ))
                    
                    prev_level = level
                    
                except Exception as e:
                    logger.error(f"Error checking heading hierarchy: {str(e)}")
        
        return findings
    
    async def _check_keyboard_navigation(self, soup: BeautifulSoup, file_path: str) -> List[Finding]:
        """Check keyboard navigation compatibility."""
        findings = []
        
        # Check for focusable elements
        focusable_elements = soup.find_all([
            'a', 'button', 'input', 'select', 'textarea', 'details', 'summary'
        ])
        
        for element in focusable_elements:
            try:
                line_number = element.sourceline if hasattr(element, 'sourceline') else None
                
                # Skip disabled elements
                if element.get('disabled'):
                    continue
                
                # Check if element is properly focusable
                if not self._is_properly_focusable(element):
                    findings.append(self._create_finding(
                        file_path=file_path,
                        line_number=line_number,
                        selector=self._get_selector(element),
                        details="Element may not be properly focusable with keyboard",
                        severity=SeverityLevel.MEDIUM,
                        evidence=self._create_evidence(file_path, line_number, str(element))
                    ))
                
            except Exception as e:
                logger.error(f"Error checking keyboard navigation: {str(e)}")
        
        return findings
    
    async def _check_focus_management(self, soup: BeautifulSoup, file_path: str) -> List[Finding]:
        """Check focus management for assistive technology."""
        findings = []
        
        # Check for focus traps
        modal_elements = soup.find_all(attrs={'role': 'dialog'})
        modal_elements.extend(soup.find_all(attrs={'aria-modal': 'true'}))
        
        for modal in modal_elements:
            try:
                line_number = modal.sourceline if hasattr(modal, 'sourceline') else None
                
                # Check if modal has proper focus management
                if not self._modal_has_focus_management(modal):
                    findings.append(self._create_finding(
                        file_path=file_path,
                        line_number=line_number,
                        selector=self._get_selector(modal),
                        details="Modal dialog missing proper focus management for assistive technology",
                        severity=SeverityLevel.HIGH,
                        evidence=self._create_evidence(file_path, line_number, str(modal))
                    ))
                
            except Exception as e:
                logger.error(f"Error checking focus management: {str(e)}")
        
        return findings
    
    def _is_properly_focusable(self, element) -> bool:
        """Check if element is properly focusable."""
        # Check if element has proper role
        role = element.get('role')
        if role in ['button', 'link', 'menuitem', 'tab']:
            return True
        
        # Check if element is naturally focusable
        if element.name in ['a', 'button', 'input', 'select', 'textarea']:
            return True
        
        # Check if element has tabindex
        if element.get('tabindex') is not None:
            return True
        
        return False
    
    def _modal_has_focus_management(self, modal) -> bool:
        """Check if modal has proper focus management."""
        # Check for focusable elements
        focusable_elements = modal.find_all([
            'a', 'button', 'input', 'select', 'textarea'
        ])
        
        if not focusable_elements:
            return False
        
        # Check for close button
        close_buttons = modal.find_all('button', string=re.compile(r'close|cancel|escape', re.IGNORECASE))
        if not close_buttons:
            return False
        
        return True
    
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
