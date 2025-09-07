"""
PredictabilityAgent - Detects predictability and consistency issues.
"""

import os
import re
from typing import List, Dict, Any
from bs4 import BeautifulSoup
from models.schemas import Finding, Evidence, SeverityLevel, ConfidenceLevel, CriterionType
from services.agents.base_agent import BaseAgent
import logging

logger = logging.getLogger(__name__)

class PredictabilityAgent(BaseAgent):
    """Agent for detecting predictability and consistency issues."""
    
    def __init__(self):
        super().__init__(
            name="PredictabilityAgent",
            description="Detects predictability and consistency issues",
            criterion=CriterionType.ARIA,
            wcag_criterion="3.2.1"
        )
    
    async def analyze(self, upload_path: str) -> List[Finding]:
        """Analyze files for predictability issues."""
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
            logger.error(f"PredictabilityAgent analysis failed: {str(e)}")
            findings.append(self._create_error_finding(upload_path, str(e)))
        
        return findings
    
    async def _analyze_html_content(self, soup: BeautifulSoup, file_path: str) -> List[Finding]:
        """Analyze HTML content for predictability issues."""
        findings = []
        
        # Check for unexpected changes
        change_findings = await self._check_unexpected_changes(soup, file_path)
        findings.extend(change_findings)
        
        # Check for consistent behavior
        behavior_findings = await self._check_consistent_behavior(soup, file_path)
        findings.extend(behavior_findings)
        
        # Check for clear navigation
        navigation_findings = await self._check_clear_navigation(soup, file_path)
        findings.extend(navigation_findings)
        
        return findings
    
    async def _check_unexpected_changes(self, soup: BeautifulSoup, file_path: str) -> List[Finding]:
        """Check for unexpected changes that might confuse users."""
        findings = []
        
        # Check for auto-submit forms
        forms = soup.find_all('form')
        for form in forms:
            try:
                line_number = form.sourceline if hasattr(form, 'sourceline') else None
                
                # Check for auto-submit on change
                inputs = form.find_all('input', attrs={'onchange': True})
                for input_elem in inputs:
                    onchange = input_elem.get('onchange', '')
                    if 'submit' in onchange.lower():
                        findings.append(self._create_finding(
                            file_path=file_path,
                            line_number=line_number,
                            selector=self._get_selector(form),
                            details="Form auto-submits on input change - may be unexpected",
                            severity=SeverityLevel.MEDIUM,
                            evidence=self._create_evidence(file_path, line_number, str(form))
                        ))
                
            except Exception as e:
                logger.error(f"Error checking auto-submit forms: {str(e)}")
        
        # Check for unexpected redirects
        meta_refresh = soup.find('meta', attrs={'http-equiv': 'refresh'})
        if meta_refresh:
            try:
                line_number = meta_refresh.sourceline if hasattr(meta_refresh, 'sourceline') else None
                content = meta_refresh.get('content', '')
                
                if 'url=' in content.lower():
                    findings.append(self._create_finding(
                        file_path=file_path,
                        line_number=line_number,
                        selector="meta[http-equiv='refresh']",
                        details="Page redirects automatically - may be unexpected",
                        severity=SeverityLevel.HIGH,
                        evidence=self._create_evidence(file_path, line_number, str(meta_refresh))
                    ))
                
            except Exception as e:
                logger.error(f"Error checking meta refresh: {str(e)}")
        
        return findings
    
    async def _check_consistent_behavior(self, soup: BeautifulSoup, file_path: str) -> List[Finding]:
        """Check for consistent behavior patterns."""
        findings = []
        
        # Check for consistent button styles
        buttons = soup.find_all('button')
        if len(buttons) > 1:
            button_styles = set()
            for button in buttons:
                style = button.get('style', '')
                if style:
                    button_styles.add(style)
            
            if len(button_styles) > len(buttons) / 2:  # Too many different styles
                findings.append(self._create_finding(
                    file_path=file_path,
                    line_number=1,
                    selector="body",
                    details="Buttons have inconsistent styling - consider consistency",
                    severity=SeverityLevel.LOW,
                    evidence=self._create_evidence(file_path, 1, f"Found {len(button_styles)} different button styles")
                ))
        
        # Check for consistent link behavior
        links = soup.find_all('a')
        if len(links) > 1:
            # Check for mixed link types
            external_links = 0
            internal_links = 0
            
            for link in links:
                href = link.get('href', '')
                if href.startswith('http') and not href.startswith('#'):
                    external_links += 1
                else:
                    internal_links += 1
            
            if external_links > 0 and internal_links > 0:
                # Check if external links are properly marked
                unmarked_external = 0
                for link in links:
                    href = link.get('href', '')
                    if href.startswith('http') and not link.get('target') == '_blank':
                        unmarked_external += 1
                
                if unmarked_external > 0:
                    findings.append(self._create_finding(
                        file_path=file_path,
                        line_number=1,
                        selector="body",
                        details="External links not consistently marked - consider consistency",
                        severity=SeverityLevel.LOW,
                        evidence=self._create_evidence(file_path, 1, f"Found {unmarked_external} unmarked external links")
                    ))
        
        return findings
    
    async def _check_clear_navigation(self, soup: BeautifulSoup, file_path: str) -> List[Finding]:
        """Check for clear navigation patterns."""
        findings = []
        
        # Check for breadcrumbs
        breadcrumbs = soup.find_all(attrs={'aria-label': re.compile(r'breadcrumb', re.IGNORECASE)})
        if not breadcrumbs:
            # Check for common breadcrumb patterns
            breadcrumb_patterns = soup.find_all('nav', string=re.compile(r'breadcrumb', re.IGNORECASE))
            if not breadcrumb_patterns:
                findings.append(self._create_finding(
                    file_path=file_path,
                    line_number=1,
                    selector="body",
                    details="No breadcrumb navigation found - consider adding for clarity",
                    severity=SeverityLevel.LOW,
                    evidence=self._create_evidence(file_path, 1, "No breadcrumb navigation found")
                ))
        
        # Check for clear page titles
        title = soup.find('title')
        if title:
            title_text = title.get_text().strip()
            if not title_text or len(title_text) < 3:
                findings.append(self._create_finding(
                    file_path=file_path,
                    line_number=1,
                    selector="title",
                    details="Page title is missing or too short",
                    severity=SeverityLevel.MEDIUM,
                    evidence=self._create_evidence(file_path, 1, str(title))
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
