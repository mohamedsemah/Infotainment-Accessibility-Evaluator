"""
TimingAgent - Detects timing-related accessibility issues.
"""

import os
import re
from typing import List, Dict, Any
from bs4 import BeautifulSoup
from models.schemas import Finding, Evidence, SeverityLevel, ConfidenceLevel, CriterionType
from services.agents.base_agent import BaseAgent
import logging

logger = logging.getLogger(__name__)

class TimingAgent(BaseAgent):
    """Agent for detecting timing-related accessibility issues."""
    
    def __init__(self):
        super().__init__(
            name="TimingAgent",
            description="Detects timing-related accessibility issues",
            criterion=CriterionType.ARIA,
            wcag_criterion="2.2.1"
        )
    
    async def analyze(self, upload_path: str) -> List[Finding]:
        """Analyze files for timing issues."""
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
            logger.error(f"TimingAgent analysis failed: {str(e)}")
            findings.append(self._create_error_finding(upload_path, str(e)))
        
        return findings
    
    async def _analyze_html_content(self, soup: BeautifulSoup, file_path: str) -> List[Finding]:
        """Analyze HTML content for timing issues."""
        findings = []
        
        # Check time limits
        time_limit_findings = await self._check_time_limits(soup, file_path)
        findings.extend(time_limit_findings)
        
        # Check auto-refresh
        auto_refresh_findings = await self._check_auto_refresh(soup, file_path)
        findings.extend(auto_refresh_findings)
        
        # Check timeouts
        timeout_findings = await self._check_timeouts(soup, file_path)
        findings.extend(timeout_findings)
        
        # Check session timeouts
        session_timeout_findings = await self._check_session_timeouts(soup, file_path)
        findings.extend(session_timeout_findings)
        
        return findings
    
    async def _check_time_limits(self, soup: BeautifulSoup, file_path: str) -> List[Finding]:
        """Check for time limits that might be too restrictive."""
        findings = []
        
        # Check for meta refresh
        meta_refresh = soup.find('meta', attrs={'http-equiv': 'refresh'})
        if meta_refresh:
            try:
                line_number = meta_refresh.sourceline if hasattr(meta_refresh, 'sourceline') else None
                content = meta_refresh.get('content', '')
                
                # Extract timeout value
                timeout_match = re.search(r'(\d+)', content)
                if timeout_match:
                    timeout_seconds = int(timeout_match.group(1))
                    
                    if timeout_seconds < 20:  # Less than 20 seconds
                        findings.append(self._create_finding(
                            file_path=file_path,
                            line_number=line_number,
                            selector="meta[http-equiv='refresh']",
                            details=f"Page auto-refreshes too quickly ({timeout_seconds} seconds) - may not give users enough time",
                            severity=SeverityLevel.HIGH,
                            evidence=self._create_evidence(file_path, line_number, str(meta_refresh))
                        ))
                    elif timeout_seconds < 60:  # Less than 1 minute
                        findings.append(self._create_finding(
                            file_path=file_path,
                            line_number=line_number,
                            selector="meta[http-equiv='refresh']",
                            details=f"Page auto-refreshes quickly ({timeout_seconds} seconds) - consider user needs",
                            severity=SeverityLevel.MEDIUM,
                            evidence=self._create_evidence(file_path, line_number, str(meta_refresh))
                        ))
                
            except Exception as e:
                logger.error(f"Error checking meta refresh: {str(e)}")
        
        # Check for JavaScript timeouts
        script_elements = soup.find_all('script')
        for script in script_elements:
            try:
                line_number = script.sourceline if hasattr(script, 'sourceline') else None
                script_content = script.get_text()
                
                # Look for setTimeout with short delays
                timeout_matches = re.findall(r'setTimeout\s*\(\s*[^,]+,\s*(\d+)\s*\)', script_content)
                for timeout_ms in timeout_matches:
                    timeout_seconds = int(timeout_ms) / 1000
                    
                    if timeout_seconds < 5:  # Less than 5 seconds
                        findings.append(self._create_finding(
                            file_path=file_path,
                            line_number=line_number,
                            selector="script",
                            details=f"JavaScript timeout too short ({timeout_seconds} seconds) - may not give users enough time",
                            severity=SeverityLevel.MEDIUM,
                            evidence=self._create_evidence(file_path, line_number, str(script))
                        ))
                
            except Exception as e:
                logger.error(f"Error checking JavaScript timeouts: {str(e)}")
        
        return findings
    
    async def _check_auto_refresh(self, soup: BeautifulSoup, file_path: str) -> List[Finding]:
        """Check for auto-refresh functionality."""
        findings = []
        
        # Check for meta refresh
        meta_refresh = soup.find('meta', attrs={'http-equiv': 'refresh'})
        if meta_refresh:
            try:
                line_number = meta_refresh.sourceline if hasattr(meta_refresh, 'sourceline') else None
                content = meta_refresh.get('content', '')
                
                # Check if refresh is to same page (auto-refresh)
                if 'url=' not in content.lower():
                    findings.append(self._create_finding(
                        file_path=file_path,
                        line_number=line_number,
                        selector="meta[http-equiv='refresh']",
                        details="Page auto-refreshes without user control - may be disruptive",
                        severity=SeverityLevel.HIGH,
                        evidence=self._create_evidence(file_path, line_number, str(meta_refresh))
                    ))
                
            except Exception as e:
                logger.error(f"Error checking auto-refresh: {str(e)}")
        
        # Check for JavaScript auto-refresh
        script_elements = soup.find_all('script')
        for script in script_elements:
            try:
                line_number = script.sourceline if hasattr(script, 'sourceline') else None
                script_content = script.get_text()
                
                # Look for location.reload or window.location.reload
                if 'location.reload' in script_content or 'window.location.reload' in script_content:
                    findings.append(self._create_finding(
                        file_path=file_path,
                        line_number=line_number,
                        selector="script",
                        details="Page uses JavaScript auto-refresh - ensure user control",
                        severity=SeverityLevel.MEDIUM,
                        evidence=self._create_evidence(file_path, line_number, str(script))
                    ))
                
            except Exception as e:
                logger.error(f"Error checking JavaScript auto-refresh: {str(e)}")
        
        return findings
    
    async def _check_timeouts(self, soup: BeautifulSoup, file_path: str) -> List[Finding]:
        """Check for timeout-related issues."""
        findings = []
        
        # Check for form timeouts
        forms = soup.find_all('form')
        for form in forms:
            try:
                line_number = form.sourceline if hasattr(form, 'sourceline') else None
                
                # Check for timeout-related attributes or scripts
                form_script = form.find_next_sibling('script')
                if form_script:
                    script_content = form_script.get_text()
                    
                    # Look for form timeout patterns
                    if 'timeout' in script_content.lower() or 'expire' in script_content.lower():
                        findings.append(self._create_finding(
                            file_path=file_path,
                            line_number=line_number,
                            selector=self._get_selector(form),
                            details="Form may have timeout restrictions - ensure adequate time",
                            severity=SeverityLevel.MEDIUM,
                            evidence=self._create_evidence(file_path, line_number, str(form))
                        ))
                
            except Exception as e:
                logger.error(f"Error checking form timeouts: {str(e)}")
        
        # Check for session timeout warnings
        timeout_warnings = soup.find_all(string=re.compile(r'timeout|expire|session.*expir', re.IGNORECASE))
        for warning in timeout_warnings:
            try:
                parent = warning.parent
                line_number = parent.sourceline if hasattr(parent, 'sourceline') else None
                
                findings.append(self._create_finding(
                    file_path=file_path,
                    line_number=line_number,
                    selector=self._get_selector(parent),
                    details="Page contains timeout warnings - ensure adequate time and user control",
                    severity=SeverityLevel.LOW,
                    evidence=self._create_evidence(file_path, line_number, str(parent))
                ))
                
            except Exception as e:
                logger.error(f"Error checking timeout warnings: {str(e)}")
        
        return findings
    
    async def _check_session_timeouts(self, soup: BeautifulSoup, file_path: str) -> List[Finding]:
        """Check for session timeout issues."""
        findings = []
        
        # Look for session-related elements
        session_elements = soup.find_all(string=re.compile(r'session|login.*timeout|idle.*timeout', re.IGNORECASE))
        
        for element in session_elements:
            try:
                parent = element.parent
                line_number = parent.sourceline if hasattr(parent, 'sourceline') else None
                
                # Check if there's a way to extend session
                extend_session = parent.find_next(string=re.compile(r'extend|continue|stay.*logged', re.IGNORECASE))
                
                if not extend_session:
                    findings.append(self._create_finding(
                        file_path=file_path,
                        line_number=line_number,
                        selector=self._get_selector(parent),
                        details="Session timeout without extension option - users may lose work",
                        severity=SeverityLevel.HIGH,
                        evidence=self._create_evidence(file_path, line_number, str(parent))
                    ))
                else:
                    findings.append(self._create_finding(
                        file_path=file_path,
                        line_number=line_number,
                        selector=self._get_selector(parent),
                        details="Session timeout present - ensure adequate warning time",
                        severity=SeverityLevel.LOW,
                        evidence=self._create_evidence(file_path, line_number, str(parent))
                    ))
                
            except Exception as e:
                logger.error(f"Error checking session timeouts: {str(e)}")
        
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
