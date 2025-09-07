"""
LayoutAgent - Detects layout and structure accessibility issues.
"""

import os
import re
from typing import List, Dict, Any
from bs4 import BeautifulSoup
from models.schemas import Finding, Evidence, SeverityLevel, ConfidenceLevel, CriterionType
from services.agents.base_agent import BaseAgent
import logging

logger = logging.getLogger(__name__)

class LayoutAgent(BaseAgent):
    """Agent for detecting layout and structure accessibility issues."""
    
    def __init__(self):
        super().__init__(
            name="LayoutAgent",
            description="Detects layout and structure accessibility issues",
            criterion=CriterionType.ARIA,
            wcag_criterion="1.3.1"
        )
    
    async def analyze(self, upload_path: str) -> List[Finding]:
        """Analyze files for layout accessibility issues."""
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
            logger.error(f"LayoutAgent analysis failed: {str(e)}")
            findings.append(self._create_error_finding(upload_path, str(e)))
        
        return findings
    
    async def _analyze_html_content(self, soup: BeautifulSoup, file_path: str) -> List[Finding]:
        """Analyze HTML content for layout accessibility issues."""
        findings = []
        
        # Check heading structure
        heading_findings = await self._check_heading_structure(soup, file_path)
        findings.extend(heading_findings)
        
        # Check landmark regions
        landmark_findings = await self._check_landmark_regions(soup, file_path)
        findings.extend(landmark_findings)
        
        # Check table structure
        table_findings = await self._check_table_structure(soup, file_path)
        findings.extend(table_findings)
        
        # Check list structure
        list_findings = await self._check_list_structure(soup, file_path)
        findings.extend(list_findings)
        
        # Check form structure
        form_findings = await self._check_form_structure(soup, file_path)
        findings.extend(form_findings)
        
        return findings
    
    async def _check_heading_structure(self, soup: BeautifulSoup, file_path: str) -> List[Finding]:
        """Check heading structure for proper hierarchy."""
        findings = []
        
        headings = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
        
        if not headings:
            findings.append(self._create_finding(
                file_path=file_path,
                line_number=1,
                selector="body",
                details="Page missing heading structure",
                severity=SeverityLevel.HIGH,
                evidence=self._create_evidence(file_path, 1, "No heading elements found")
            ))
            return findings
        
        # Check for missing h1
        h1_count = len(soup.find_all('h1'))
        if h1_count == 0:
            findings.append(self._create_finding(
                file_path=file_path,
                line_number=headings[0].sourceline if hasattr(headings[0], 'sourceline') else 1,
                selector="body",
                details="Page missing h1 heading",
                severity=SeverityLevel.HIGH,
                evidence=self._create_evidence(file_path, 1, "No h1 element found")
            ))
        elif h1_count > 1:
            findings.append(self._create_finding(
                file_path=file_path,
                line_number=headings[0].sourceline if hasattr(headings[0], 'sourceline') else 1,
                selector="body",
                details=f"Page has {h1_count} h1 headings (should have only one)",
                severity=SeverityLevel.MEDIUM,
                evidence=self._create_evidence(file_path, 1, f"Found {h1_count} h1 elements")
            ))
        
        # Check heading hierarchy
        prev_level = 0
        for heading in headings:
            try:
                level = int(heading.name[1])
                line_number = heading.sourceline if hasattr(heading, 'sourceline') else None
                
                # Check for skipped heading levels
                if level > prev_level + 1:
                    findings.append(self._create_finding(
                        file_path=file_path,
                        line_number=line_number,
                        selector=self._get_selector(heading),
                        details=f"Heading level skipped from h{prev_level} to h{level}",
                        severity=SeverityLevel.MEDIUM,
                        evidence=self._create_evidence(file_path, line_number, str(heading))
                    ))
                
                # Check for empty headings
                if not heading.get_text().strip():
                    findings.append(self._create_finding(
                        file_path=file_path,
                        line_number=line_number,
                        selector=self._get_selector(heading),
                        details=f"Empty {heading.name} heading",
                        severity=SeverityLevel.MEDIUM,
                        evidence=self._create_evidence(file_path, line_number, str(heading))
                    ))
                
                prev_level = level
                
            except Exception as e:
                logger.error(f"Error checking heading: {str(e)}")
        
        return findings
    
    async def _check_landmark_regions(self, soup: BeautifulSoup, file_path: str) -> List[Finding]:
        """Check for proper landmark regions."""
        findings = []
        
        # Check for main landmark
        main_landmarks = soup.find_all(['main', '[role="main"]'])
        if not main_landmarks:
            findings.append(self._create_finding(
                file_path=file_path,
                line_number=1,
                selector="body",
                details="Page missing main landmark region",
                severity=SeverityLevel.HIGH,
                evidence=self._create_evidence(file_path, 1, "No main landmark found")
            ))
        
        # Check for navigation landmarks
        nav_landmarks = soup.find_all(['nav', '[role="navigation"]'])
        if not nav_landmarks:
            findings.append(self._create_finding(
                file_path=file_path,
                line_number=1,
                selector="body",
                details="Page missing navigation landmark region",
                severity=SeverityLevel.MEDIUM,
                evidence=self._create_evidence(file_path, 1, "No navigation landmark found")
            ))
        
        # Check for banner landmark
        banner_landmarks = soup.find_all(['header', '[role="banner"]'])
        if not banner_landmarks:
            findings.append(self._create_finding(
                file_path=file_path,
                line_number=1,
                selector="body",
                details="Page missing banner landmark region",
                severity=SeverityLevel.MEDIUM,
                evidence=self._create_evidence(file_path, 1, "No banner landmark found")
            ))
        
        # Check for contentinfo landmark
        contentinfo_landmarks = soup.find_all(['footer', '[role="contentinfo"]'])
        if not contentinfo_landmarks:
            findings.append(self._create_finding(
                file_path=file_path,
                line_number=1,
                selector="body",
                details="Page missing contentinfo landmark region",
                severity=SeverityLevel.MEDIUM,
                evidence=self._create_evidence(file_path, 1, "No contentinfo landmark found")
            ))
        
        return findings
    
    async def _check_table_structure(self, soup: BeautifulSoup, file_path: str) -> List[Finding]:
        """Check table structure for accessibility."""
        findings = []
        
        for table in soup.find_all('table'):
            try:
                line_number = table.sourceline if hasattr(table, 'sourceline') else None
                
                # Check for missing caption
                if not table.find('caption'):
                    findings.append(self._create_finding(
                        file_path=file_path,
                        line_number=line_number,
                        selector=self._get_selector(table),
                        details="Table missing caption element",
                        severity=SeverityLevel.MEDIUM,
                        evidence=self._create_evidence(file_path, line_number, str(table))
                    ))
                
                # Check for missing headers
                headers = table.find_all(['th', '[role="columnheader"]', '[role="rowheader"]'])
                if not headers:
                    findings.append(self._create_finding(
                        file_path=file_path,
                        line_number=line_number,
                        selector=self._get_selector(table),
                        details="Table missing header cells",
                        severity=SeverityLevel.HIGH,
                        evidence=self._create_evidence(file_path, line_number, str(table))
                    ))
                
                # Check for proper header association
                rows = table.find_all('tr')
                if rows and headers:
                    first_row = rows[0]
                    first_row_headers = first_row.find_all(['th', 'td'])
                    
                    # Check if first row has headers
                    if not any(cell.name == 'th' for cell in first_row_headers):
                        findings.append(self._create_finding(
                            file_path=file_path,
                            line_number=line_number,
                            selector=self._get_selector(table),
                            details="Table first row should contain header cells",
                            severity=SeverityLevel.MEDIUM,
                            evidence=self._create_evidence(file_path, line_number, str(table))
                        ))
                
            except Exception as e:
                logger.error(f"Error checking table: {str(e)}")
        
        return findings
    
    async def _check_list_structure(self, soup: BeautifulSoup, file_path: str) -> List[Finding]:
        """Check list structure for accessibility."""
        findings = []
        
        # Check for proper list usage
        for ul in soup.find_all('ul'):
            try:
                line_number = ul.sourceline if hasattr(ul, 'sourceline') else None
                items = ul.find_all('li')
                
                if not items:
                    findings.append(self._create_finding(
                        file_path=file_path,
                        line_number=line_number,
                        selector=self._get_selector(ul),
                        details="Unordered list contains no list items",
                        severity=SeverityLevel.LOW,
                        evidence=self._create_evidence(file_path, line_number, str(ul))
                    ))
                
            except Exception as e:
                logger.error(f"Error checking ul: {str(e)}")
        
        for ol in soup.find_all('ol'):
            try:
                line_number = ol.sourceline if hasattr(ol, 'sourceline') else None
                items = ol.find_all('li')
                
                if not items:
                    findings.append(self._create_finding(
                        file_path=file_path,
                        line_number=line_number,
                        selector=self._get_selector(ol),
                        details="Ordered list contains no list items",
                        severity=SeverityLevel.LOW,
                        evidence=self._create_evidence(file_path, line_number, str(ol))
                    ))
                
            except Exception as e:
                logger.error(f"Error checking ol: {str(e)}")
        
        return findings
    
    async def _check_form_structure(self, soup: BeautifulSoup, file_path: str) -> List[Finding]:
        """Check form structure for accessibility."""
        findings = []
        
        for form in soup.find_all('form'):
            try:
                line_number = form.sourceline if hasattr(form, 'sourceline') else None
                
                # Check for missing fieldset for related fields
                inputs = form.find_all(['input', 'select', 'textarea'])
                if len(inputs) > 1:
                    fieldsets = form.find_all('fieldset')
                    if not fieldsets:
                        findings.append(self._create_finding(
                            file_path=file_path,
                            line_number=line_number,
                            selector=self._get_selector(form),
                            details="Form with multiple inputs missing fieldset grouping",
                            severity=SeverityLevel.MEDIUM,
                            evidence=self._create_evidence(file_path, line_number, str(form))
                        ))
                
                # Check for proper label association
                for input_elem in inputs:
                    input_line = input_elem.sourceline if hasattr(input_elem, 'sourceline') else None
                    
                    # Skip hidden inputs
                    if input_elem.get('type') == 'hidden':
                        continue
                    
                    # Check for label association
                    input_id = input_elem.get('id')
                    if input_id:
                        label = form.find('label', {'for': input_id})
                        if not label:
                            findings.append(self._create_finding(
                                file_path=file_path,
                                line_number=input_line,
                                selector=self._get_selector(input_elem),
                                details="Form input missing associated label",
                                severity=SeverityLevel.HIGH,
                                evidence=self._create_evidence(file_path, input_line, str(input_elem))
                            ))
                    else:
                        # Check for implicit label
                        parent_label = input_elem.find_parent('label')
                        if not parent_label:
                            findings.append(self._create_finding(
                                file_path=file_path,
                                line_number=input_line,
                                selector=self._get_selector(input_elem),
                                details="Form input missing label (no id or implicit label)",
                                severity=SeverityLevel.HIGH,
                                evidence=self._create_evidence(file_path, input_line, str(input_elem))
                            ))
                
            except Exception as e:
                logger.error(f"Error checking form: {str(e)}")
        
        return findings
    
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
