"""
ReadabilityAgent - Detects readability and text clarity issues.
"""

import os
import re
from typing import List, Dict, Any
from bs4 import BeautifulSoup
from models.schemas import Finding, Evidence, SeverityLevel, ConfidenceLevel, CriterionType
from services.agents.base_agent import BaseAgent
import logging

logger = logging.getLogger(__name__)

class ReadabilityAgent(BaseAgent):
    """Agent for detecting readability and text clarity issues."""
    
    def __init__(self):
        super().__init__(
            name="ReadabilityAgent",
            description="Detects readability and text clarity issues",
            criterion=CriterionType.ARIA,
            wcag_criterion="3.1.5"
        )
    
    async def analyze(self, upload_path: str) -> List[Finding]:
        """Analyze files for readability issues."""
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
            logger.error(f"ReadabilityAgent analysis failed: {str(e)}")
            findings.append(self._create_error_finding(upload_path, str(e)))
        
        return findings
    
    async def _analyze_html_content(self, soup: BeautifulSoup, file_path: str) -> List[Finding]:
        """Analyze HTML content for readability issues."""
        findings = []
        
        # Check text clarity
        clarity_findings = await self._check_text_clarity(soup, file_path)
        findings.extend(clarity_findings)
        
        # Check sentence length
        sentence_findings = await self._check_sentence_length(soup, file_path)
        findings.extend(sentence_findings)
        
        # Check paragraph length
        paragraph_findings = await self._check_paragraph_length(soup, file_path)
        findings.extend(paragraph_findings)
        
        # Check heading structure
        heading_findings = await self._check_heading_structure(soup, file_path)
        findings.extend(heading_findings)
        
        return findings
    
    async def _check_text_clarity(self, soup: BeautifulSoup, file_path: str) -> List[Finding]:
        """Check text clarity and readability."""
        findings = []
        
        # Check for unclear text patterns
        text_elements = soup.find_all(['p', 'div', 'span', 'li'])
        for element in text_elements:
            try:
                text = element.get_text().strip()
                if not text or len(text) < 10:
                    continue
                
                line_number = element.sourceline if hasattr(element, 'sourceline') else None
                
                # Check for unclear text patterns
                unclear_patterns = [
                    r'\b(click here|read more|see more|learn more)\b',
                    r'\b(this|that|it|these|those)\b.*\b(this|that|it|these|those)\b',
                    r'\b(obviously|clearly|of course|naturally)\b',
                    r'\b(etc|etc\.|and so on|and more)\b'
                ]
                
                for pattern in unclear_patterns:
                    if re.search(pattern, text, re.IGNORECASE):
                        findings.append(self._create_finding(
                            file_path=file_path,
                            line_number=line_number,
                            selector=self._get_selector(element),
                            details=f"Unclear text pattern detected: {text[:50]}...",
                            severity=SeverityLevel.LOW,
                            evidence=self._create_evidence(file_path, line_number, str(element))
                        ))
                
            except Exception as e:
                logger.error(f"Error checking text clarity: {str(e)}")
        
        return findings
    
    async def _check_sentence_length(self, soup: BeautifulSoup, file_path: str) -> List[Finding]:
        """Check sentence length for readability."""
        findings = []
        
        text_elements = soup.find_all(['p', 'div', 'span', 'li'])
        for element in text_elements:
            try:
                text = element.get_text().strip()
                if not text:
                    continue
                
                line_number = element.sourceline if hasattr(element, 'sourceline') else None
                
                # Split into sentences
                sentences = re.split(r'[.!?]+', text)
                for sentence in sentences:
                    sentence = sentence.strip()
                    if not sentence or len(sentence) < 10:
                        continue
                    
                    # Check for very long sentences
                    if len(sentence) > 100:
                        findings.append(self._create_finding(
                            file_path=file_path,
                            line_number=line_number,
                            selector=self._get_selector(element),
                            details=f"Very long sentence detected: {sentence[:50]}...",
                            severity=SeverityLevel.LOW,
                            evidence=self._create_evidence(file_path, line_number, str(element))
                        ))
                    
                    # Check for very short sentences
                    elif len(sentence) < 5:
                        findings.append(self._create_finding(
                            file_path=file_path,
                            line_number=line_number,
                            selector=self._get_selector(element),
                            details=f"Very short sentence detected: {sentence}",
                            severity=SeverityLevel.LOW,
                            evidence=self._create_evidence(file_path, line_number, str(element))
                        ))
                
            except Exception as e:
                logger.error(f"Error checking sentence length: {str(e)}")
        
        return findings
    
    async def _check_paragraph_length(self, soup: BeautifulSoup, file_path: str) -> List[Finding]:
        """Check paragraph length for readability."""
        findings = []
        
        paragraphs = soup.find_all('p')
        for paragraph in paragraphs:
            try:
                text = paragraph.get_text().strip()
                if not text:
                    continue
                
                line_number = paragraph.sourceline if hasattr(paragraph, 'sourceline') else None
                
                # Check for very long paragraphs
                if len(text) > 500:
                    findings.append(self._create_finding(
                        file_path=file_path,
                        line_number=line_number,
                        selector=self._get_selector(paragraph),
                        details=f"Very long paragraph detected ({len(text)} characters) - consider breaking up",
                        severity=SeverityLevel.LOW,
                        evidence=self._create_evidence(file_path, line_number, str(paragraph))
                    ))
                
                # Check for very short paragraphs
                elif len(text) < 20:
                    findings.append(self._create_finding(
                        file_path=file_path,
                        line_number=line_number,
                        selector=self._get_selector(paragraph),
                        details=f"Very short paragraph detected - consider combining or expanding",
                        severity=SeverityLevel.LOW,
                        evidence=self._create_evidence(file_path, line_number, str(paragraph))
                    ))
                
            except Exception as e:
                logger.error(f"Error checking paragraph length: {str(e)}")
        
        return findings
    
    async def _check_heading_structure(self, soup: BeautifulSoup, file_path: str) -> List[Finding]:
        """Check heading structure for readability."""
        findings = []
        
        headings = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
        
        for heading in headings:
            try:
                text = heading.get_text().strip()
                if not text:
                    continue
                
                line_number = heading.sourceline if hasattr(heading, 'sourceline') else None
                
                # Check for very long headings
                if len(text) > 100:
                    findings.append(self._create_finding(
                        file_path=file_path,
                        line_number=line_number,
                        selector=self._get_selector(heading),
                        details=f"Very long heading detected: {text[:50]}...",
                        severity=SeverityLevel.LOW,
                        evidence=self._create_evidence(file_path, line_number, str(heading))
                    ))
                
                # Check for very short headings
                elif len(text) < 3:
                    findings.append(self._create_finding(
                        file_path=file_path,
                        line_number=line_number,
                        selector=self._get_selector(heading),
                        details=f"Very short heading detected: {text}",
                        severity=SeverityLevel.LOW,
                        evidence=self._create_evidence(file_path, line_number, str(heading))
                    ))
                
                # Check for unclear headings
                unclear_heading_patterns = [
                    r'^\d+\.?\s*$',  # Just numbers
                    r'^[A-Z\s]+$',  # All caps
                    r'^[a-z\s]+$',  # All lowercase
                    r'^\s*$'  # Empty or whitespace
                ]
                
                for pattern in unclear_heading_patterns:
                    if re.match(pattern, text):
                        findings.append(self._create_finding(
                            file_path=file_path,
                            line_number=line_number,
                            selector=self._get_selector(heading),
                            details=f"Unclear heading detected: {text}",
                            severity=SeverityLevel.LOW,
                            evidence=self._create_evidence(file_path, line_number, str(heading))
                        ))
                
            except Exception as e:
                logger.error(f"Error checking heading structure: {str(e)}")
        
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
