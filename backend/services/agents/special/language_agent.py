"""
LanguageAgent - Detects language and readability issues.
"""

import os
import re
from typing import List, Dict, Any
from bs4 import BeautifulSoup
from models.schemas import Finding, Evidence, SeverityLevel, ConfidenceLevel, CriterionType
from services.agents.base_agent import BaseAgent
import logging

logger = logging.getLogger(__name__)

class LanguageAgent(BaseAgent):
    """Agent for detecting language and readability issues."""
    
    def __init__(self):
        super().__init__(
            name="LanguageAgent",
            description="Detects language and readability issues",
            criterion=CriterionType.ARIA,
            wcag_criterion="3.1.1"
        )
    
    async def analyze(self, upload_path: str) -> List[Finding]:
        """Analyze files for language issues."""
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
            logger.error(f"LanguageAgent analysis failed: {str(e)}")
            findings.append(self._create_error_finding(upload_path, str(e)))
        
        return findings
    
    async def _analyze_html_content(self, soup: BeautifulSoup, file_path: str) -> List[Finding]:
        """Analyze HTML content for language issues."""
        findings = []
        
        # Check language attributes
        language_findings = await self._check_language_attributes(soup, file_path)
        findings.extend(language_findings)
        
        # Check readability
        readability_findings = await self._check_readability(soup, file_path)
        findings.extend(readability_findings)
        
        # Check technical language
        technical_findings = await self._check_technical_language(soup, file_path)
        findings.extend(technical_findings)
        
        return findings
    
    async def _check_language_attributes(self, soup: BeautifulSoup, file_path: str) -> List[Finding]:
        """Check for proper language attributes."""
        findings = []
        
        # Check html lang attribute
        html = soup.find('html')
        if html:
            if not html.get('lang'):
                findings.append(self._create_finding(
                    file_path=file_path,
                    line_number=1,
                    selector="html",
                    details="HTML element missing lang attribute",
                    severity=SeverityLevel.HIGH,
                    evidence=self._create_evidence(file_path, 1, str(html))
                ))
            else:
                lang = html.get('lang')
                if not self._is_valid_language_code(lang):
                    findings.append(self._create_finding(
                        file_path=file_path,
                        line_number=1,
                        selector="html",
                        details=f"Invalid language code: {lang}",
                        severity=SeverityLevel.MEDIUM,
                        evidence=self._create_evidence(file_path, 1, str(html))
                    ))
        
        # Check for language changes
        elements_with_lang = soup.find_all(attrs={'lang': True})
        for element in elements_with_lang:
            try:
                line_number = element.sourceline if hasattr(element, 'sourceline') else None
                lang = element.get('lang')
                
                if not self._is_valid_language_code(lang):
                    findings.append(self._create_finding(
                        file_path=file_path,
                        line_number=line_number,
                        selector=self._get_selector(element),
                        details=f"Invalid language code: {lang}",
                        severity=SeverityLevel.MEDIUM,
                        evidence=self._create_evidence(file_path, line_number, str(element))
                    ))
                
            except Exception as e:
                logger.error(f"Error checking language attributes: {str(e)}")
        
        return findings
    
    async def _check_readability(self, soup: BeautifulSoup, file_path: str) -> List[Finding]:
        """Check for readability issues."""
        findings = []
        
        # Check for long sentences
        text_elements = soup.find_all(['p', 'div', 'span', 'li'])
        for element in text_elements:
            try:
                text = element.get_text().strip()
                if not text:
                    continue
                
                line_number = element.sourceline if hasattr(element, 'sourceline') else None
                
                # Check for very long sentences
                sentences = text.split('.')
                for sentence in sentences:
                    if len(sentence.strip()) > 100:  # Very long sentence
                        findings.append(self._create_finding(
                            file_path=file_path,
                            line_number=line_number,
                            selector=self._get_selector(element),
                            details=f"Very long sentence detected: {sentence[:50]}...",
                            severity=SeverityLevel.LOW,
                            evidence=self._create_evidence(file_path, line_number, str(element))
                        ))
                
            except Exception as e:
                logger.error(f"Error checking readability: {str(e)}")
        
        return findings
    
    async def _check_technical_language(self, soup: BeautifulSoup, file_path: str) -> List[Finding]:
        """Check for technical language that might need explanation."""
        findings = []
        
        # Technical terms that might need explanation
        technical_terms = [
            'API', 'URL', 'HTTP', 'HTTPS', 'CSS', 'HTML', 'JavaScript',
            'database', 'server', 'client', 'authentication', 'authorization',
            'cookies', 'session', 'cache', 'browser', 'responsive'
        ]
        
        text_elements = soup.find_all(['p', 'div', 'span', 'li', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
        for element in text_elements:
            try:
                text = element.get_text().strip()
                if not text:
                    continue
                
                line_number = element.sourceline if hasattr(element, 'sourceline') else None
                
                # Check for technical terms
                found_terms = []
                for term in technical_terms:
                    if term.lower() in text.lower():
                        found_terms.append(term)
                
                if found_terms:
                    findings.append(self._create_finding(
                        file_path=file_path,
                        line_number=line_number,
                        selector=self._get_selector(element),
                        details=f"Technical terms found: {', '.join(found_terms)} - consider explaining",
                        severity=SeverityLevel.LOW,
                        evidence=self._create_evidence(file_path, line_number, str(element))
                    ))
                
            except Exception as e:
                logger.error(f"Error checking technical language: {str(e)}")
        
        return findings
    
    def _is_valid_language_code(self, lang: str) -> bool:
        """Check if language code is valid."""
        if not lang:
            return False
        
        # Basic validation for language codes
        # Should be 2-3 characters for language, optionally followed by country code
        pattern = r'^[a-z]{2,3}(-[A-Z]{2})?$'
        return bool(re.match(pattern, lang))
    
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