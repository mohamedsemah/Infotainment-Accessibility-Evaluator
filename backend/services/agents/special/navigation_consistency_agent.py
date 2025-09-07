"""
NavigationConsistencyAgent - Detects navigation consistency issues.
"""

import os
import re
from typing import List, Dict, Any
from bs4 import BeautifulSoup
from models.schemas import Finding, Evidence, SeverityLevel, ConfidenceLevel, CriterionType
from services.agents.base_agent import BaseAgent
import logging

logger = logging.getLogger(__name__)

class NavigationConsistencyAgent(BaseAgent):
    """Agent for detecting navigation consistency issues."""
    
    def __init__(self):
        super().__init__(
            name="NavigationConsistencyAgent",
            description="Detects navigation consistency issues",
            criterion=CriterionType.ARIA,
            wcag_criterion="3.2.3"
        )
    
    async def analyze(self, upload_path: str) -> List[Finding]:
        """Analyze files for navigation consistency issues."""
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
            logger.error(f"NavigationConsistencyAgent analysis failed: {str(e)}")
            findings.append(self._create_error_finding(upload_path, str(e)))
        
        return findings
    
    async def _analyze_html_content(self, soup: BeautifulSoup, file_path: str) -> List[Finding]:
        """Analyze HTML content for navigation consistency issues."""
        findings = []
        
        # Check navigation structure
        nav_findings = await self._check_navigation_structure(soup, file_path)
        findings.extend(nav_findings)
        
        # Check link consistency
        link_findings = await self._check_link_consistency(soup, file_path)
        findings.extend(link_findings)
        
        # Check form consistency
        form_findings = await self._check_form_consistency(soup, file_path)
        findings.extend(form_findings)
        
        return findings
    
    async def _check_navigation_structure(self, soup: BeautifulSoup, file_path: str) -> List[Finding]:
        """Check navigation structure for consistency."""
        findings = []
        
        # Check for multiple navigation areas
        nav_elements = soup.find_all('nav')
        if len(nav_elements) > 1:
            findings.append(self._create_finding(
                file_path=file_path,
                line_number=1,
                selector="body",
                details=f"Multiple navigation areas found ({len(nav_elements)}) - ensure consistent structure",
                severity=SeverityLevel.LOW,
                evidence=self._create_evidence(file_path, 1, f"Found {len(nav_elements)} nav elements")
            ))
        
        # Check for missing navigation
        if not nav_elements:
            findings.append(self._create_finding(
                file_path=file_path,
                line_number=1,
                selector="body",
                details="No navigation elements found - consider adding navigation",
                severity=SeverityLevel.MEDIUM,
                evidence=self._create_evidence(file_path, 1, "No nav elements found")
            ))
        
        return findings
    
    async def _check_link_consistency(self, soup: BeautifulSoup, file_path: str) -> List[Finding]:
        """Check link consistency."""
        findings = []
        
        # Check for duplicate link text
        links = soup.find_all('a')
        link_texts = {}
        
        for link in links:
            try:
                text = link.get_text().strip()
                if text and len(text) > 3:  # Only check meaningful text
                    if text in link_texts:
                        link_texts[text].append(link)
                    else:
                        link_texts[text] = [link]
                
            except Exception as e:
                logger.error(f"Error checking link text: {str(e)}")
        
        # Check for duplicate link texts
        for text, link_list in link_texts.items():
            if len(link_list) > 1:
                line_number = link_list[0].sourceline if hasattr(link_list[0], 'sourceline') else None
                findings.append(self._create_finding(
                    file_path=file_path,
                    line_number=line_number,
                    selector=self._get_selector(link_list[0]),
                    details=f"Multiple links with same text '{text}' - may be confusing",
                    severity=SeverityLevel.MEDIUM,
                    evidence=self._create_evidence(file_path, line_number, str(link_list[0]))
                ))
        
        return findings
    
    async def _check_form_consistency(self, soup: BeautifulSoup, file_path: str) -> List[Finding]:
        """Check form consistency."""
        findings = []
        
        # Check for consistent form styling
        forms = soup.find_all('form')
        if len(forms) > 1:
            # Check for consistent input types
            input_types = set()
            for form in forms:
                inputs = form.find_all('input')
                for input_elem in inputs:
                    input_type = input_elem.get('type', 'text')
                    input_types.add(input_type)
            
            if len(input_types) > 5:  # Too many different input types
                findings.append(self._create_finding(
                    file_path=file_path,
                    line_number=1,
                    selector="body",
                    details="Forms use many different input types - consider consistency",
                    severity=SeverityLevel.LOW,
                    evidence=self._create_evidence(file_path, 1, f"Found {len(input_types)} input types")
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
