"""
CompatibilityAgent - Detects compatibility and standards issues.
"""

import os
import re
from typing import List, Dict, Any
from bs4 import BeautifulSoup
from models.schemas import Finding, Evidence, SeverityLevel, ConfidenceLevel, CriterionType
from services.agents.base_agent import BaseAgent
import logging

logger = logging.getLogger(__name__)

class CompatibilityAgent(BaseAgent):
    """Agent for detecting compatibility and standards issues."""
    
    def __init__(self):
        super().__init__(
            name="CompatibilityAgent",
            description="Detects compatibility and standards issues",
            criterion=CriterionType.ARIA,
            wcag_criterion="4.1.2"
        )
    
    async def analyze(self, upload_path: str) -> List[Finding]:
        """Analyze files for compatibility issues."""
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
            logger.error(f"CompatibilityAgent analysis failed: {str(e)}")
            findings.append(self._create_error_finding(upload_path, str(e)))
        
        return findings
    
    async def _analyze_html_content(self, soup: BeautifulSoup, file_path: str) -> List[Finding]:
        """Analyze HTML content for compatibility issues."""
        findings = []
        
        # Check HTML validation
        validation_findings = await self._check_html_validation(soup, file_path)
        findings.extend(validation_findings)
        
        # Check deprecated elements
        deprecated_findings = await self._check_deprecated_elements(soup, file_path)
        findings.extend(deprecated_findings)
        
        # Check browser compatibility
        browser_findings = await self._check_browser_compatibility(soup, file_path)
        findings.extend(browser_findings)
        
        return findings
    
    async def _check_html_validation(self, soup: BeautifulSoup, file_path: str) -> List[Finding]:
        """Check HTML validation issues."""
        findings = []
        
        # Check for missing DOCTYPE
        if not soup.find('html'):
            findings.append(self._create_finding(
                file_path=file_path,
                line_number=1,
                selector="html",
                details="Missing HTML element",
                severity=SeverityLevel.HIGH,
                evidence=self._create_evidence(file_path, 1, "No html element found")
            ))
        
        # Check for duplicate IDs
        ids = []
        elements_with_ids = soup.find_all(attrs={'id': True})
        for element in elements_with_ids:
            try:
                element_id = element.get('id')
                if element_id in ids:
                    line_number = element.sourceline if hasattr(element, 'sourceline') else None
                    findings.append(self._create_finding(
                        file_path=file_path,
                        line_number=line_number,
                        selector=self._get_selector(element),
                        details=f"Duplicate ID found: {element_id}",
                        severity=SeverityLevel.HIGH,
                        evidence=self._create_evidence(file_path, line_number, str(element))
                    ))
                else:
                    ids.append(element_id)
                
            except Exception as e:
                logger.error(f"Error checking duplicate IDs: {str(e)}")
        
        # Check for invalid attributes
        invalid_attributes = ['onclick', 'onload', 'onchange', 'onsubmit']
        for attr in invalid_attributes:
            elements_with_attr = soup.find_all(attrs={attr: True})
            for element in elements_with_attr:
                try:
                    line_number = element.sourceline if hasattr(element, 'sourceline') else None
                    findings.append(self._create_finding(
                        file_path=file_path,
                        line_number=line_number,
                        selector=self._get_selector(element),
                        details=f"Element uses inline event handler: {attr}",
                        severity=SeverityLevel.LOW,
                        evidence=self._create_evidence(file_path, line_number, str(element))
                    ))
                
                except Exception as e:
                    logger.error(f"Error checking invalid attributes: {str(e)}")
        
        return findings
    
    async def _check_deprecated_elements(self, soup: BeautifulSoup, file_path: str) -> List[Finding]:
        """Check for deprecated HTML elements."""
        findings = []
        
        deprecated_elements = [
            'applet', 'basefont', 'center', 'dir', 'font', 'frame', 'frameset',
            'isindex', 'noframes', 'strike', 'tt', 'u', 'xmp'
        ]
        
        for element_name in deprecated_elements:
            elements = soup.find_all(element_name)
            for element in elements:
                try:
                    line_number = element.sourceline if hasattr(element, 'sourceline') else None
                    findings.append(self._create_finding(
                        file_path=file_path,
                        line_number=line_number,
                        selector=self._get_selector(element),
                        details=f"Deprecated HTML element used: {element_name}",
                        severity=SeverityLevel.MEDIUM,
                        evidence=self._create_evidence(file_path, line_number, str(element))
                    ))
                
                except Exception as e:
                    logger.error(f"Error checking deprecated elements: {str(e)}")
        
        return findings
    
    async def _check_browser_compatibility(self, soup: BeautifulSoup, file_path: str) -> List[Finding]:
        """Check for browser compatibility issues."""
        findings = []
        
        # Check for CSS Grid usage
        style_elements = soup.find_all('style')
        for style in style_elements:
            try:
                line_number = style.sourceline if hasattr(style, 'sourceline') else None
                css_content = style.get_text()
                
                # Check for CSS Grid
                if 'display: grid' in css_content or 'display:grid' in css_content:
                    findings.append(self._create_finding(
                        file_path=file_path,
                        line_number=line_number,
                        selector="style",
                        details="CSS Grid used - ensure browser compatibility",
                        severity=SeverityLevel.LOW,
                        evidence=self._create_evidence(file_path, line_number, str(style))
                    ))
                
                # Check for CSS Flexbox
                if 'display: flex' in css_content or 'display:flex' in css_content:
                    findings.append(self._create_finding(
                        file_path=file_path,
                        line_number=line_number,
                        selector="style",
                        details="CSS Flexbox used - ensure browser compatibility",
                        severity=SeverityLevel.LOW,
                        evidence=self._create_evidence(file_path, line_number, str(style))
                    ))
                
            except Exception as e:
                logger.error(f"Error checking browser compatibility: {str(e)}")
        
        # Check for modern JavaScript features
        script_elements = soup.find_all('script')
        for script in script_elements:
            try:
                line_number = script.sourceline if hasattr(script, 'sourceline') else None
                script_content = script.get_text()
                
                # Check for modern JavaScript features
                modern_js_features = [
                    'const ', 'let ', '=>', 'async ', 'await ',
                    'class ', 'import ', 'export ', '...'
                ]
                
                for feature in modern_js_features:
                    if feature in script_content:
                        findings.append(self._create_finding(
                            file_path=file_path,
                            line_number=line_number,
                            selector="script",
                            details=f"Modern JavaScript feature used: {feature} - ensure browser compatibility",
                            severity=SeverityLevel.LOW,
                            evidence=self._create_evidence(file_path, line_number, str(script))
                        ))
                
            except Exception as e:
                logger.error(f"Error checking JavaScript compatibility: {str(e)}")
        
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
