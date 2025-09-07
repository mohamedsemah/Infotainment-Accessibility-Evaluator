"""
SeizureSafeAgent - Detects seizure-inducing content and animation issues.
"""

import os
import re
from typing import List, Dict, Any
from bs4 import BeautifulSoup
from models.schemas import Finding, Evidence, SeverityLevel, ConfidenceLevel, CriterionType
from services.agents.base_agent import BaseAgent
import logging

logger = logging.getLogger(__name__)

class SeizureSafeAgent(BaseAgent):
    """Agent for detecting seizure-inducing content and animation issues."""
    
    def __init__(self):
        super().__init__(
            name="SeizureSafeAgent",
            description="Detects seizure-inducing content and animation issues",
            criterion=CriterionType.ARIA,
            wcag_criterion="2.3.1"
        )
    
    async def analyze(self, upload_path: str) -> List[Finding]:
        """Analyze files for seizure-inducing content."""
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
            logger.error(f"SeizureSafeAgent analysis failed: {str(e)}")
            findings.append(self._create_error_finding(upload_path, str(e)))
        
        return findings
    
    async def _analyze_html_content(self, soup: BeautifulSoup, file_path: str) -> List[Finding]:
        """Analyze HTML content for seizure-inducing content."""
        findings = []
        
        # Check for flashing content
        flashing_findings = await self._check_flashing_content(soup, file_path)
        findings.extend(flashing_findings)
        
        # Check for rapid animations
        animation_findings = await self._check_rapid_animations(soup, file_path)
        findings.extend(animation_findings)
        
        return findings
    
    async def _check_flashing_content(self, soup: BeautifulSoup, file_path: str) -> List[Finding]:
        """Check for flashing content that could trigger seizures."""
        findings = []
        
        # Check for blink elements
        blink_elements = soup.find_all('blink')
        for element in blink_elements:
            try:
                line_number = element.sourceline if hasattr(element, 'sourceline') else None
                
                findings.append(self._create_finding(
                    file_path=file_path,
                    line_number=line_number,
                    selector=self._get_selector(element),
                    details="Blink element may cause seizures - use CSS animations instead",
                    severity=SeverityLevel.HIGH,
                    evidence=self._create_evidence(file_path, line_number, str(element))
                ))
                
            except Exception as e:
                logger.error(f"Error checking blink elements: {str(e)}")
        
        return findings
    
    async def _check_rapid_animations(self, soup: BeautifulSoup, file_path: str) -> List[Finding]:
        """Check for rapid animations that could be problematic."""
        findings = []
        
        # Check CSS animations
        style_elements = soup.find_all('style')
        for style in style_elements:
            try:
                line_number = style.sourceline if hasattr(style, 'sourceline') else None
                css_content = style.get_text()
                
                # Look for rapid animations
                if self._has_rapid_animations(css_content):
                    findings.append(self._create_finding(
                        file_path=file_path,
                        line_number=line_number,
                        selector="style",
                        details="Rapid animation detected - may cause seizures",
                        severity=SeverityLevel.HIGH,
                        evidence=self._create_evidence(file_path, line_number, str(style))
                    ))
                
            except Exception as e:
                logger.error(f"Error checking rapid animations: {str(e)}")
        
        return findings
    
    def _has_rapid_animations(self, css_content: str) -> bool:
        """Check if CSS has rapid animations."""
        # Look for animation duration less than 0.5 seconds
        duration_match = re.search(r'animation-duration\s*:\s*(\d+(?:\.\d+)?)s', css_content)
        if duration_match:
            duration = float(duration_match.group(1))
            if duration < 0.5:  # Less than 0.5 seconds
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