"""
KeyboardNavigationAgent - Detects keyboard navigation accessibility issues.
"""

import os
import re
from typing import List, Dict, Any
from bs4 import BeautifulSoup
from models.schemas import Finding, Evidence, SeverityLevel, ConfidenceLevel, CriterionType
from services.agents.base_agent import BaseAgent
import logging

logger = logging.getLogger(__name__)

class KeyboardNavigationAgent(BaseAgent):
    """Agent for detecting keyboard navigation accessibility issues."""
    
    def __init__(self):
        super().__init__(
            name="KeyboardNavigationAgent",
            description="Detects keyboard navigation accessibility issues",
            criterion=CriterionType.ARIA,
            wcag_criterion="2.1.1"
        )
    
    async def analyze(self, upload_path: str) -> List[Finding]:
        """Analyze files for keyboard navigation issues."""
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
            logger.error(f"KeyboardNavigationAgent analysis failed: {str(e)}")
            findings.append(self._create_error_finding(upload_path, str(e)))
        
        return findings
    
    async def _analyze_html_content(self, soup: BeautifulSoup, file_path: str) -> List[Finding]:
        """Analyze HTML content for keyboard navigation issues."""
        findings = []
        
        # Check interactive elements
        interactive_findings = await self._check_interactive_elements(soup, file_path)
        findings.extend(interactive_findings)
        
        # Check tab order
        tab_order_findings = await self._check_tab_order(soup, file_path)
        findings.extend(tab_order_findings)
        
        # Check keyboard traps
        trap_findings = await self._check_keyboard_traps(soup, file_path)
        findings.extend(trap_findings)
        
        # Check skip links
        skip_link_findings = await self._check_skip_links(soup, file_path)
        findings.extend(skip_link_findings)
        
        return findings
    
    async def _check_interactive_elements(self, soup: BeautifulSoup, file_path: str) -> List[Finding]:
        """Check interactive elements for keyboard accessibility."""
        findings = []
        
        # Check buttons
        button_findings = await self._check_buttons(soup, file_path)
        findings.extend(button_findings)
        
        # Check links
        link_findings = await self._check_links(soup, file_path)
        findings.extend(link_findings)
        
        # Check form controls
        form_findings = await self._check_form_controls(soup, file_path)
        findings.extend(form_findings)
        
        # Check custom interactive elements
        custom_findings = await self._check_custom_interactive_elements(soup, file_path)
        findings.extend(custom_findings)
        
        return findings
    
    async def _check_buttons(self, soup: BeautifulSoup, file_path: str) -> List[Finding]:
        """Check button elements for keyboard accessibility."""
        findings = []
        
        for button in soup.find_all('button'):
            try:
                line_number = button.sourceline if hasattr(button, 'sourceline') else None
                
                # Check for disabled buttons
                if button.get('disabled'):
                    findings.append(self._create_finding(
                        file_path=file_path,
                        line_number=line_number,
                        selector=self._get_selector(button),
                        details="Disabled button should not be focusable",
                        severity=SeverityLevel.MEDIUM,
                        evidence=self._create_evidence(file_path, line_number, str(button))
                    ))
                
                # Check for empty buttons
                if not button.get_text().strip() and not button.find('img'):
                    findings.append(self._create_finding(
                        file_path=file_path,
                        line_number=line_number,
                        selector=self._get_selector(button),
                        details="Button has no accessible name",
                        severity=SeverityLevel.HIGH,
                        evidence=self._create_evidence(file_path, line_number, str(button))
                    ))
                
                # Check for buttons with only icons
                if button.find('img') and not button.get('aria-label') and not button.get('title'):
                    findings.append(self._create_finding(
                        file_path=file_path,
                        line_number=line_number,
                        selector=self._get_selector(button),
                        details="Button with icon missing accessible name",
                        severity=SeverityLevel.HIGH,
                        evidence=self._create_evidence(file_path, line_number, str(button))
                    ))
                
            except Exception as e:
                logger.error(f"Error checking button: {str(e)}")
        
        return findings
    
    async def _check_links(self, soup: BeautifulSoup, file_path: str) -> List[Finding]:
        """Check link elements for keyboard accessibility."""
        findings = []
        
        for link in soup.find_all('a'):
            try:
                line_number = link.sourceline if hasattr(link, 'sourceline') else None
                href = link.get('href', '')
                
                # Check for empty links
                if not link.get_text().strip() and not link.find('img'):
                    findings.append(self._create_finding(
                        file_path=file_path,
                        line_number=line_number,
                        selector=self._get_selector(link),
                        details="Link has no accessible name",
                        severity=SeverityLevel.HIGH,
                        evidence=self._create_evidence(file_path, line_number, str(link))
                    ))
                
                # Check for links with only icons
                if link.find('img') and not link.get('aria-label') and not link.get('title'):
                    findings.append(self._create_finding(
                        file_path=file_path,
                        line_number=line_number,
                        selector=self._get_selector(link),
                        details="Link with icon missing accessible name",
                        severity=SeverityLevel.HIGH,
                        evidence=self._create_evidence(file_path, line_number, str(link))
                    ))
                
                # Check for JavaScript-only links
                if href.startswith('javascript:') or href == '#':
                    if not link.get('role') and not link.get('onclick'):
                        findings.append(self._create_finding(
                            file_path=file_path,
                            line_number=line_number,
                            selector=self._get_selector(link),
                            details="JavaScript link should have proper role or keyboard handler",
                            severity=SeverityLevel.MEDIUM,
                            evidence=self._create_evidence(file_path, line_number, str(link))
                        ))
                
                # Check for duplicate link text
                link_text = link.get_text().strip()
                if link_text and len(link_text) < 4:  # Short link text
                    similar_links = soup.find_all('a', string=re.compile(re.escape(link_text), re.IGNORECASE))
                    if len(similar_links) > 1:
                        findings.append(self._create_finding(
                            file_path=file_path,
                            line_number=line_number,
                            selector=self._get_selector(link),
                            details=f"Multiple links with same text '{link_text}' - may be confusing",
                            severity=SeverityLevel.MEDIUM,
                            evidence=self._create_evidence(file_path, line_number, str(link))
                        ))
                
            except Exception as e:
                logger.error(f"Error checking link: {str(e)}")
        
        return findings
    
    async def _check_form_controls(self, soup: BeautifulSoup, file_path: str) -> List[Finding]:
        """Check form controls for keyboard accessibility."""
        findings = []
        
        # Check input elements
        for input_elem in soup.find_all('input'):
            try:
                line_number = input_elem.sourceline if hasattr(input_elem, 'sourceline') else None
                input_type = input_elem.get('type', 'text')
                
                # Skip hidden inputs
                if input_type == 'hidden':
                    continue
                
                # Check for missing labels
                input_id = input_elem.get('id')
                if input_id:
                    label = soup.find('label', {'for': input_id})
                    if not label:
                        findings.append(self._create_finding(
                            file_path=file_path,
                            line_number=line_number,
                            selector=self._get_selector(input_elem),
                            details="Form input missing associated label",
                            severity=SeverityLevel.HIGH,
                            evidence=self._create_evidence(file_path, line_number, str(input_elem))
                        ))
                else:
                    # Check for implicit label
                    parent_label = input_elem.find_parent('label')
                    if not parent_label:
                        findings.append(self._create_finding(
                            file_path=file_path,
                            line_number=line_number,
                            selector=self._get_selector(input_elem),
                            details="Form input missing label (no id or implicit label)",
                            severity=SeverityLevel.HIGH,
                            evidence=self._create_evidence(file_path, line_number, str(input_elem))
                        ))
                
                # Check for required fields
                if input_elem.get('required') and not input_elem.get('aria-required'):
                    findings.append(self._create_finding(
                        file_path=file_path,
                        line_number=line_number,
                        selector=self._get_selector(input_elem),
                        details="Required input missing aria-required attribute",
                        severity=SeverityLevel.MEDIUM,
                        evidence=self._create_evidence(file_path, line_number, str(input_elem))
                    ))
                
            except Exception as e:
                logger.error(f"Error checking input: {str(e)}")
        
        # Check select elements
        for select in soup.find_all('select'):
            try:
                line_number = select.sourceline if hasattr(select, 'sourceline') else None
                
                # Check for missing labels
                select_id = select.get('id')
                if select_id:
                    label = soup.find('label', {'for': select_id})
                    if not label:
                        findings.append(self._create_finding(
                            file_path=file_path,
                            line_number=line_number,
                            selector=self._get_selector(select),
                            details="Select element missing associated label",
                            severity=SeverityLevel.HIGH,
                            evidence=self._create_evidence(file_path, line_number, str(select))
                        ))
                
            except Exception as e:
                logger.error(f"Error checking select: {str(e)}")
        
        # Check textarea elements
        for textarea in soup.find_all('textarea'):
            try:
                line_number = textarea.sourceline if hasattr(textarea, 'sourceline') else None
                
                # Check for missing labels
                textarea_id = textarea.get('id')
                if textarea_id:
                    label = soup.find('label', {'for': textarea_id})
                    if not label:
                        findings.append(self._create_finding(
                            file_path=file_path,
                            line_number=line_number,
                            selector=self._get_selector(textarea),
                            details="Textarea element missing associated label",
                            severity=SeverityLevel.HIGH,
                            evidence=self._create_evidence(file_path, line_number, str(textarea))
                        ))
                
            except Exception as e:
                logger.error(f"Error checking textarea: {str(e)}")
        
        return findings
    
    async def _check_custom_interactive_elements(self, soup: BeautifulSoup, file_path: str) -> List[Finding]:
        """Check custom interactive elements for keyboard accessibility."""
        findings = []
        
        # Check elements with click handlers
        click_elements = soup.find_all(attrs={'onclick': True})
        click_elements.extend(soup.find_all(attrs={'onmousedown': True}))
        click_elements.extend(soup.find_all(attrs={'onmouseup': True}))
        
        for element in click_elements:
            try:
                line_number = element.sourceline if hasattr(element, 'sourceline') else None
                
                # Check if element is keyboard accessible
                if not self._is_keyboard_accessible(element):
                    findings.append(self._create_finding(
                        file_path=file_path,
                        line_number=line_number,
                        selector=self._get_selector(element),
                        details="Interactive element missing keyboard accessibility",
                        severity=SeverityLevel.HIGH,
                        evidence=self._create_evidence(file_path, line_number, str(element))
                    ))
                
            except Exception as e:
                logger.error(f"Error checking custom interactive element: {str(e)}")
        
        return findings
    
    async def _check_tab_order(self, soup: BeautifulSoup, file_path: str) -> List[Finding]:
        """Check tab order for logical sequence."""
        findings = []
        
        # Get all focusable elements
        focusable_elements = soup.find_all([
            'a', 'button', 'input', 'select', 'textarea', 'details', 'summary'
        ])
        
        # Filter out disabled and hidden elements
        focusable_elements = [
            elem for elem in focusable_elements
            if not elem.get('disabled') and not elem.get('hidden') and not elem.get('style', '').__contains__('display: none')
        ]
        
        # Check for negative tabindex
        for element in focusable_elements:
            try:
                line_number = element.sourceline if hasattr(element, 'sourceline') else None
                tabindex = element.get('tabindex')
                
                if tabindex and int(tabindex) < 0:
                    findings.append(self._create_finding(
                        file_path=file_path,
                        line_number=line_number,
                        selector=self._get_selector(element),
                        details="Element with negative tabindex may break tab order",
                        severity=SeverityLevel.MEDIUM,
                        evidence=self._create_evidence(file_path, line_number, str(element))
                    ))
                
            except Exception as e:
                logger.error(f"Error checking tab order: {str(e)}")
        
        return findings
    
    async def _check_keyboard_traps(self, soup: BeautifulSoup, file_path: str) -> List[Finding]:
        """Check for keyboard traps."""
        findings = []
        
        # Check for elements that might trap keyboard focus
        trap_indicators = [
            'role="dialog"',
            'role="alertdialog"',
            'aria-modal="true"',
            'tabindex="-1"'
        ]
        
        for element in soup.find_all():
            try:
                element_str = str(element)
                if any(indicator in element_str for indicator in trap_indicators):
                    line_number = element.sourceline if hasattr(element, 'sourceline') else None
                    
                    # Check if element has escape mechanism
                    if not self._has_escape_mechanism(element):
                        findings.append(self._create_finding(
                            file_path=file_path,
                            line_number=line_number,
                            selector=self._get_selector(element),
                            details="Modal or dialog element may trap keyboard focus without escape mechanism",
                            severity=SeverityLevel.HIGH,
                            evidence=self._create_evidence(file_path, line_number, str(element))
                        ))
                
            except Exception as e:
                logger.error(f"Error checking keyboard traps: {str(e)}")
        
        return findings
    
    async def _check_skip_links(self, soup: BeautifulSoup, file_path: str) -> List[Finding]:
        """Check for skip links."""
        findings = []
        
        # Look for skip links
        skip_links = soup.find_all('a', href=lambda x: x and x.startswith('#'))
        
        # Check if there are skip links to main content
        has_skip_to_main = any(
            link.get('href') == '#main' or 
            'main' in link.get_text().lower() or
            'skip' in link.get_text().lower()
            for link in skip_links
        )
        
        if not has_skip_to_main:
            findings.append(self._create_finding(
                file_path=file_path,
                line_number=1,
                selector="body",
                details="Page missing skip link to main content",
                severity=SeverityLevel.MEDIUM,
                evidence=self._create_evidence(file_path, 1, "No skip link found")
            ))
        
        return findings
    
    def _is_keyboard_accessible(self, element) -> bool:
        """Check if element is keyboard accessible."""
        # Check if element has proper role
        if element.get('role') in ['button', 'link', 'menuitem', 'tab']:
            return True
        
        # Check if element has tabindex
        if element.get('tabindex') is not None:
            return True
        
        # Check if element is naturally focusable
        if element.name in ['a', 'button', 'input', 'select', 'textarea']:
            return True
        
        return False
    
    def _has_escape_mechanism(self, element) -> bool:
        """Check if element has escape mechanism."""
        # Look for close buttons or escape handlers
        close_buttons = element.find_all(['button', 'a'], string=re.compile(r'close|cancel|escape', re.IGNORECASE))
        if close_buttons:
            return True
        
        # Check for aria-label with close indication
        if 'close' in element.get('aria-label', '').lower():
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
