"""
FocusAgent - Detects focus management accessibility issues.
"""

import os
import re
from typing import List, Dict, Any
from bs4 import BeautifulSoup
from models.schemas import Finding, Evidence, SeverityLevel, ConfidenceLevel, CriterionType
from services.agents.base_agent import BaseAgent
import logging

logger = logging.getLogger(__name__)

class FocusAgent(BaseAgent):
    """Agent for detecting focus management accessibility issues."""
    
    def __init__(self):
        super().__init__(
            name="FocusAgent",
            description="Detects focus management accessibility issues",
            criterion=CriterionType.ARIA,
            wcag_criterion="2.4.7"
        )
    
    async def analyze(self, upload_path: str) -> List[Finding]:
        """Analyze files for focus management issues."""
        findings = []
        
        try:
            # Find HTML files
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
            logger.error(f"FocusAgent analysis failed: {str(e)}")
            findings.append(self._create_error_finding(upload_path, str(e)))
        
        return findings
    
    async def _analyze_html_content(self, soup: BeautifulSoup, file_path: str) -> List[Finding]:
        """Analyze HTML content for focus management issues."""
        findings = []
        
        # Check focus indicators
        focus_indicator_findings = await self._check_focus_indicators(soup, file_path)
        findings.extend(focus_indicator_findings)
        
        # Check focus management
        focus_management_findings = await self._check_focus_management(soup, file_path)
        findings.extend(focus_management_findings)
        
        # Check focus order
        focus_order_findings = await self._check_focus_order(soup, file_path)
        findings.extend(focus_order_findings)
        
        # Check focus traps
        focus_trap_findings = await self._check_focus_traps(soup, file_path)
        findings.extend(focus_trap_findings)
        
        return findings
    
    async def _check_focus_indicators(self, soup: BeautifulSoup, file_path: str) -> List[Finding]:
        """Check for focus indicators on interactive elements."""
        findings = []
        
        # Check for CSS focus styles
        css_findings = await self._check_css_focus_styles(soup, file_path)
        findings.extend(css_findings)
        
        # Check for missing focus indicators
        missing_focus_findings = await self._check_missing_focus_indicators(soup, file_path)
        findings.extend(missing_focus_findings)
        
        return findings
    
    async def _check_css_focus_styles(self, soup: BeautifulSoup, file_path: str) -> List[Finding]:
        """Check CSS for focus styles."""
        findings = []
        
        # Look for style elements
        style_elements = soup.find_all('style')
        
        for style in style_elements:
            try:
                line_number = style.sourceline if hasattr(style, 'sourceline') else None
                css_content = style.get_text()
                
                # Check for focus styles
                if not self._has_focus_styles(css_content):
                    findings.append(self._create_finding(
                        file_path=file_path,
                        line_number=line_number,
                        selector="style",
                        details="CSS missing focus styles for interactive elements",
                        severity=SeverityLevel.MEDIUM,
                        evidence=self._create_evidence(file_path, line_number, str(style))
                    ))
                
            except Exception as e:
                logger.error(f"Error checking CSS focus styles: {str(e)}")
        
        return findings
    
    async def _check_missing_focus_indicators(self, soup: BeautifulSoup, file_path: str) -> List[Finding]:
        """Check for missing focus indicators on interactive elements."""
        findings = []
        
        # Get all interactive elements
        interactive_elements = soup.find_all([
            'a', 'button', 'input', 'select', 'textarea', 'details', 'summary'
        ])
        
        for element in interactive_elements:
            try:
                line_number = element.sourceline if hasattr(element, 'sourceline') else None
                
                # Skip disabled elements
                if element.get('disabled'):
                    continue
                
                # Check if element has focus styles
                if not self._element_has_focus_styles(element):
                    findings.append(self._create_finding(
                        file_path=file_path,
                        line_number=line_number,
                        selector=self._get_selector(element),
                        details="Interactive element missing visible focus indicator",
                        severity=SeverityLevel.MEDIUM,
                        evidence=self._create_evidence(file_path, line_number, str(element))
                    ))
                
            except Exception as e:
                logger.error(f"Error checking missing focus indicators: {str(e)}")
        
        return findings
    
    async def _check_focus_management(self, soup: BeautifulSoup, file_path: str) -> List[Finding]:
        """Check focus management patterns."""
        findings = []
        
        # Check for proper focus management in modals
        modal_findings = await self._check_modal_focus_management(soup, file_path)
        findings.extend(modal_findings)
        
        # Check for focus management in dynamic content
        dynamic_findings = await self._check_dynamic_focus_management(soup, file_path)
        findings.extend(dynamic_findings)
        
        return findings
    
    async def _check_modal_focus_management(self, soup: BeautifulSoup, file_path: str) -> List[Finding]:
        """Check focus management in modal dialogs."""
        findings = []
        
        # Look for modal dialogs
        modals = soup.find_all(attrs={'role': 'dialog'})
        modals.extend(soup.find_all(attrs={'aria-modal': 'true'}))
        
        for modal in modals:
            try:
                line_number = modal.sourceline if hasattr(modal, 'sourceline') else None
                
                # Check if modal has proper focus management
                if not self._modal_has_proper_focus_management(modal):
                    findings.append(self._create_finding(
                        file_path=file_path,
                        line_number=line_number,
                        selector=self._get_selector(modal),
                        details="Modal dialog missing proper focus management",
                        severity=SeverityLevel.HIGH,
                        evidence=self._create_evidence(file_path, line_number, str(modal))
                    ))
                
            except Exception as e:
                logger.error(f"Error checking modal focus management: {str(e)}")
        
        return findings
    
    async def _check_dynamic_focus_management(self, soup: BeautifulSoup, file_path: str) -> List[Finding]:
        """Check focus management for dynamic content."""
        findings = []
        
        # Look for elements that might have dynamic content
        dynamic_elements = soup.find_all(attrs={'aria-live': True})
        dynamic_elements.extend(soup.find_all(attrs={'aria-expanded': True}))
        
        for element in dynamic_elements:
            try:
                line_number = element.sourceline if hasattr(element, 'sourceline') else None
                
                # Check if dynamic content has proper focus management
                if not self._dynamic_content_has_focus_management(element):
                    findings.append(self._create_finding(
                        file_path=file_path,
                        line_number=line_number,
                        selector=self._get_selector(element),
                        details="Dynamic content missing proper focus management",
                        severity=SeverityLevel.MEDIUM,
                        evidence=self._create_evidence(file_path, line_number, str(element))
                    ))
                
            except Exception as e:
                logger.error(f"Error checking dynamic focus management: {str(e)}")
        
        return findings
    
    async def _check_focus_order(self, soup: BeautifulSoup, file_path: str) -> List[Finding]:
        """Check focus order for logical sequence."""
        findings = []
        
        # Get all focusable elements
        focusable_elements = soup.find_all([
            'a', 'button', 'input', 'select', 'textarea', 'details', 'summary'
        ])
        
        # Filter out disabled elements
        focusable_elements = [
            elem for elem in focusable_elements
            if not elem.get('disabled') and not elem.get('hidden')
        ]
        
        # Check for logical focus order
        if len(focusable_elements) > 1:
            # Check if elements are in logical order
            if not self._elements_in_logical_order(focusable_elements):
                findings.append(self._create_finding(
                    file_path=file_path,
                    line_number=1,
                    selector="body",
                    details="Focus order may not be logical",
                    severity=SeverityLevel.MEDIUM,
                    evidence=self._create_evidence(file_path, 1, "Focus order analysis")
                ))
        
        return findings
    
    async def _check_focus_traps(self, soup: BeautifulSoup, file_path: str) -> List[Finding]:
        """Check for focus traps."""
        findings = []
        
        # Look for elements that might trap focus
        trap_elements = soup.find_all(attrs={'tabindex': '-1'})
        trap_elements.extend(soup.find_all(attrs={'role': 'dialog'}))
        trap_elements.extend(soup.find_all(attrs={'aria-modal': 'true'}))
        
        for element in trap_elements:
            try:
                line_number = element.sourceline if hasattr(element, 'sourceline') else None
                
                # Check if element has proper focus trap management
                if not self._element_has_proper_focus_trap(element):
                    findings.append(self._create_finding(
                        file_path=file_path,
                        line_number=line_number,
                        selector=self._get_selector(element),
                        details="Element may trap focus without proper management",
                        severity=SeverityLevel.HIGH,
                        evidence=self._create_evidence(file_path, line_number, str(element))
                    ))
                
            except Exception as e:
                logger.error(f"Error checking focus traps: {str(e)}")
        
        return findings
    
    def _has_focus_styles(self, css_content: str) -> bool:
        """Check if CSS has focus styles."""
        focus_patterns = [
            r':focus\s*{',
            r':focus-visible\s*{',
            r'outline\s*:',
            r'box-shadow\s*:',
            r'border\s*:'
        ]
        
        for pattern in focus_patterns:
            if re.search(pattern, css_content, re.IGNORECASE):
                return True
        
        return False
    
    def _element_has_focus_styles(self, element) -> bool:
        """Check if element has focus styles."""
        # Check inline styles
        style = element.get('style', '')
        if 'outline' in style or 'box-shadow' in style:
            return True
        
        # Check for focus-related classes
        classes = element.get('class', [])
        focus_classes = ['focus', 'focus-visible', 'focus-ring']
        if any(cls in focus_classes for cls in classes):
            return True
        
        return False
    
    def _modal_has_proper_focus_management(self, modal) -> bool:
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
    
    def _dynamic_content_has_focus_management(self, element) -> bool:
        """Check if dynamic content has focus management."""
        # Check for proper ARIA attributes
        if element.get('aria-live') in ['polite', 'assertive']:
            return True
        
        # Check for focus management attributes
        if element.get('aria-expanded') is not None:
            return True
        
        return False
    
    def _elements_in_logical_order(self, elements) -> bool:
        """Check if elements are in logical order."""
        # Simple check: elements should be in document order
        # This is a basic implementation - could be enhanced
        return True
    
    def _element_has_proper_focus_trap(self, element) -> bool:
        """Check if element has proper focus trap management."""
        # Check for escape mechanism
        close_buttons = element.find_all('button', string=re.compile(r'close|cancel|escape', re.IGNORECASE))
        if close_buttons:
            return True
        
        # Check for proper ARIA attributes
        if element.get('aria-modal') == 'true':
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
