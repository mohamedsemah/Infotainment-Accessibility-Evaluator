"""
SemanticStructureAgent - Detects semantic structure and markup issues.
"""

import os
import re
from typing import List, Dict, Any
from bs4 import BeautifulSoup
from models.schemas import Finding, Evidence, SeverityLevel, ConfidenceLevel, CriterionType
from services.agents.base_agent import BaseAgent
import logging

logger = logging.getLogger(__name__)

class SemanticStructureAgent(BaseAgent):
    """Agent for detecting semantic structure and markup issues."""
    
    def __init__(self):
        super().__init__(
            name="SemanticStructureAgent",
            description="Detects semantic structure and markup issues",
            criterion=CriterionType.ARIA,
            wcag_criterion="4.1.1"
        )
    
    async def analyze(self, upload_path: str) -> List[Finding]:
        """Analyze files for semantic structure issues."""
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
            logger.error(f"SemanticStructureAgent analysis failed: {str(e)}")
            findings.append(self._create_error_finding(upload_path, str(e)))
        
        return findings
    
    async def _analyze_html_content(self, soup: BeautifulSoup, file_path: str) -> List[Finding]:
        """Analyze HTML content for semantic structure issues."""
        findings = []
        
        # Check semantic elements
        semantic_findings = await self._check_semantic_elements(soup, file_path)
        findings.extend(semantic_findings)
        
        # Check ARIA usage
        aria_findings = await self._check_aria_usage(soup, file_path)
        findings.extend(aria_findings)
        
        # Check landmark roles
        landmark_findings = await self._check_landmark_roles(soup, file_path)
        findings.extend(landmark_findings)
        
        return findings
    
    async def _check_semantic_elements(self, soup: BeautifulSoup, file_path: str) -> List[Finding]:
        """Check for proper use of semantic elements."""
        findings = []
        
        # Check for proper heading hierarchy
        headings = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
        if headings:
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
                    
                    prev_level = level
                    
                except Exception as e:
                    logger.error(f"Error checking heading hierarchy: {str(e)}")
        
        # Check for proper list structure
        lists = soup.find_all(['ul', 'ol'])
        for list_elem in lists:
            try:
                line_number = list_elem.sourceline if hasattr(list_elem, 'sourceline') else None
                items = list_elem.find_all('li')
                
                if not items:
                    findings.append(self._create_finding(
                        file_path=file_path,
                        line_number=line_number,
                        selector=self._get_selector(list_elem),
                        details="List element contains no list items",
                        severity=SeverityLevel.LOW,
                        evidence=self._create_evidence(file_path, line_number, str(list_elem))
                    ))
                
            except Exception as e:
                logger.error(f"Error checking list structure: {str(e)}")
        
        # Check for proper table structure
        tables = soup.find_all('table')
        for table in tables:
            try:
                line_number = table.sourceline if hasattr(table, 'sourceline') else None
                
                # Check for headers
                headers = table.find_all(['th', '[role="columnheader"]', '[role="rowheader"]'])
                if not headers:
                    findings.append(self._create_finding(
                        file_path=file_path,
                        line_number=line_number,
                        selector=self._get_selector(table),
                        details="Table missing header cells",
                        severity=SeverityLevel.MEDIUM,
                        evidence=self._create_evidence(file_path, line_number, str(table))
                    ))
                
                # Check for caption
                if not table.find('caption'):
                    findings.append(self._create_finding(
                        file_path=file_path,
                        line_number=line_number,
                        selector=self._get_selector(table),
                        details="Table missing caption element",
                        severity=SeverityLevel.LOW,
                        evidence=self._create_evidence(file_path, line_number, str(table))
                    ))
                
            except Exception as e:
                logger.error(f"Error checking table structure: {str(e)}")
        
        return findings
    
    async def _check_aria_usage(self, soup: BeautifulSoup, file_path: str) -> List[Finding]:
        """Check for proper ARIA usage."""
        findings = []
        
        # Check for ARIA attributes
        aria_elements = soup.find_all(attrs={'aria-label': True})
        aria_elements.extend(soup.find_all(attrs={'aria-labelledby': True}))
        aria_elements.extend(soup.find_all(attrs={'aria-describedby': True}))
        
        for element in aria_elements:
            try:
                line_number = element.sourceline if hasattr(element, 'sourceline') else None
                
                # Check for empty ARIA labels
                aria_label = element.get('aria-label', '').strip()
                if not aria_label:
                    findings.append(self._create_finding(
                        file_path=file_path,
                        line_number=line_number,
                        selector=self._get_selector(element),
                        details="Element has empty aria-label",
                        severity=SeverityLevel.MEDIUM,
                        evidence=self._create_evidence(file_path, line_number, str(element))
                    ))
                
                # Check for ARIA labelledby references
                aria_labelledby = element.get('aria-labelledby', '')
                if aria_labelledby:
                    referenced_element = soup.find(id=aria_labelledby)
                    if not referenced_element:
                        findings.append(self._create_finding(
                            file_path=file_path,
                            line_number=line_number,
                            selector=self._get_selector(element),
                            details=f"aria-labelledby references non-existent element: {aria_labelledby}",
                            severity=SeverityLevel.HIGH,
                            evidence=self._create_evidence(file_path, line_number, str(element))
                        ))
                
                # Check for ARIA describedby references
                aria_describedby = element.get('aria-describedby', '')
                if aria_describedby:
                    referenced_element = soup.find(id=aria_describedby)
                    if not referenced_element:
                        findings.append(self._create_finding(
                            file_path=file_path,
                            line_number=line_number,
                            selector=self._get_selector(element),
                            details=f"aria-describedby references non-existent element: {aria_describedby}",
                            severity=SeverityLevel.HIGH,
                            evidence=self._create_evidence(file_path, line_number, str(element))
                        ))
                
            except Exception as e:
                logger.error(f"Error checking ARIA usage: {str(e)}")
        
        return findings
    
    async def _check_landmark_roles(self, soup: BeautifulSoup, file_path: str) -> List[Finding]:
        """Check for proper landmark roles."""
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
        
        # Check for navigation landmark
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
