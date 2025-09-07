"""
SensoryAgent - Detects sensory accessibility issues (color, sound, visual).
"""

import os
import re
from typing import List, Dict, Any
from bs4 import BeautifulSoup
from models.schemas import Finding, Evidence, SeverityLevel, ConfidenceLevel, CriterionType
from services.agents.base_agent import BaseAgent
import logging

logger = logging.getLogger(__name__)

class SensoryAgent(BaseAgent):
    """Agent for detecting sensory accessibility issues."""
    
    def __init__(self):
        super().__init__(
            name="SensoryAgent",
            description="Detects sensory accessibility issues (color, sound, visual)",
            criterion=CriterionType.CONTRAST,
            wcag_criterion="1.4.1"
        )
    
    async def analyze(self, upload_path: str) -> List[Finding]:
        """Analyze files for sensory accessibility issues."""
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
            logger.error(f"SensoryAgent analysis failed: {str(e)}")
            findings.append(self._create_error_finding(upload_path, str(e)))
        
        return findings
    
    async def _analyze_html_content(self, soup: BeautifulSoup, file_path: str) -> List[Finding]:
        """Analyze HTML content for sensory accessibility issues."""
        findings = []
        
        # Check color-only information
        color_findings = await self._check_color_only_information(soup, file_path)
        findings.extend(color_findings)
        
        # Check audio-only information
        audio_findings = await self._check_audio_only_information(soup, file_path)
        findings.extend(audio_findings)
        
        # Check visual-only information
        visual_findings = await self._check_visual_only_information(soup, file_path)
        findings.extend(visual_findings)
        
        # Check text alternatives for images
        image_findings = await self._check_image_text_alternatives(soup, file_path)
        findings.extend(image_findings)
        
        return findings
    
    async def _check_color_only_information(self, soup: BeautifulSoup, file_path: str) -> List[Finding]:
        """Check for information conveyed only through color."""
        findings = []
        
        # Look for color-based indicators in text
        color_indicators = [
            r'\b(red|green|blue|yellow|orange|purple|pink|brown|black|white|gray|grey)\b',
            r'\b(click|select|choose)\s+(the\s+)?(red|green|blue|yellow|orange|purple|pink|brown|black|white|gray|grey)\s+(button|link|text|element)\b',
            r'\b(red|green|blue|yellow|orange|purple|pink|brown|black|white|gray|grey)\s+(button|link|text|element)\b',
            r'\b(see|look|notice)\s+(the\s+)?(red|green|blue|yellow|orange|purple|pink|brown|black|white|gray|grey)\b'
        ]
        
        text_elements = soup.find_all(['p', 'div', 'span', 'a', 'button', 'label'])
        
        for element in text_elements:
            try:
                text = element.get_text().strip()
                if not text:
                    continue
                
                line_number = element.sourceline if hasattr(element, 'sourceline') else None
                
                for pattern in color_indicators:
                    if re.search(pattern, text, re.IGNORECASE):
                        # Check if there's additional context beyond color
                        has_additional_context = self._has_additional_context(text, pattern)
                        
                        if not has_additional_context:
                            findings.append(self._create_finding(
                                file_path=file_path,
                                line_number=line_number,
                                selector=self._get_selector(element),
                                details=f"Information conveyed only through color: '{text[:100]}...'",
                                severity=SeverityLevel.MEDIUM,
                                evidence=self._create_evidence(file_path, line_number, str(element))
                            ))
                
            except Exception as e:
                logger.error(f"Error checking color-only information: {str(e)}")
        
        return findings
    
    async def _check_audio_only_information(self, soup: BeautifulSoup, file_path: str) -> List[Finding]:
        """Check for information conveyed only through audio."""
        findings = []
        
        # Check audio elements without transcripts
        for audio in soup.find_all('audio'):
            try:
                line_number = audio.sourceline if hasattr(audio, 'sourceline') else None
                
                # Check if audio has transcript or captions
                has_transcript = (
                    audio.find('track', kind='captions') is not None or
                    audio.find('track', kind='subtitles') is not None or
                    audio.find_next_sibling('a', href=lambda x: x and 'transcript' in x.lower()) is not None
                )
                
                if not has_transcript:
                    findings.append(self._create_finding(
                        file_path=file_path,
                        line_number=line_number,
                        selector=self._get_selector(audio),
                        details="Audio content missing transcript or captions",
                        severity=SeverityLevel.HIGH,
                        evidence=self._create_evidence(file_path, line_number, str(audio))
                    ))
                
            except Exception as e:
                logger.error(f"Error checking audio-only information: {str(e)}")
        
        return findings
    
    async def _check_visual_only_information(self, soup: BeautifulSoup, file_path: str) -> List[Finding]:
        """Check for information conveyed only through visual means."""
        findings = []
        
        # Check for images with important information
        for img in soup.find_all('img'):
            try:
                line_number = img.sourceline if hasattr(img, 'sourceline') else None
                alt_text = img.get('alt', '').strip()
                
                # Check if image appears to contain important information
                if self._appears_to_contain_information(img):
                    if not alt_text or alt_text in ['', 'image', 'picture', 'photo']:
                        findings.append(self._create_finding(
                            file_path=file_path,
                            line_number=line_number,
                            selector=self._get_selector(img),
                            details="Image appears to contain important information but has inadequate alt text",
                            severity=SeverityLevel.HIGH,
                            evidence=self._create_evidence(file_path, line_number, str(img))
                        ))
                
            except Exception as e:
                logger.error(f"Error checking visual-only information: {str(e)}")
        
        # Check for CSS-based visual indicators
        css_visual_findings = await self._check_css_visual_indicators(soup, file_path)
        findings.extend(css_visual_findings)
        
        return findings
    
    async def _check_image_text_alternatives(self, soup: BeautifulSoup, file_path: str) -> List[Finding]:
        """Check for images that contain text without proper alternatives."""
        findings = []
        
        for img in soup.find_all('img'):
            try:
                line_number = img.sourceline if hasattr(img, 'sourceline') else None
                src = img.get('src', '').lower()
                
                # Check for images that might contain text
                text_image_indicators = [
                    'logo', 'banner', 'header', 'title', 'heading',
                    'button', 'icon', 'badge', 'label', 'text'
                ]
                
                if any(indicator in src for indicator in text_image_indicators):
                    alt_text = img.get('alt', '').strip()
                    
                    if not alt_text or alt_text in ['', 'image', 'picture', 'photo']:
                        findings.append(self._create_finding(
                            file_path=file_path,
                            line_number=line_number,
                            selector=self._get_selector(img),
                            details="Image likely contains text but has inadequate alt text",
                            severity=SeverityLevel.MEDIUM,
                            evidence=self._create_evidence(file_path, line_number, str(img))
                        ))
                
            except Exception as e:
                logger.error(f"Error checking image text alternatives: {str(e)}")
        
        return findings
    
    async def _check_css_visual_indicators(self, soup: BeautifulSoup, file_path: str) -> List[Finding]:
        """Check for CSS-based visual indicators that might not be accessible."""
        findings = []
        
        # Look for elements with color-based styling
        elements_with_color = soup.find_all(attrs={'style': re.compile(r'color\s*:', re.IGNORECASE)})
        
        for element in elements_with_color:
            try:
                line_number = element.sourceline if hasattr(element, 'sourceline') else None
                style = element.get('style', '')
                
                # Check if color is used to convey meaning
                if self._color_conveys_meaning(style, element.get_text()):
                    findings.append(self._create_finding(
                        file_path=file_path,
                        line_number=line_number,
                        selector=self._get_selector(element),
                        details="Element uses color to convey meaning without additional indicators",
                        severity=SeverityLevel.MEDIUM,
                        evidence=self._create_evidence(file_path, line_number, str(element))
                    ))
                
            except Exception as e:
                logger.error(f"Error checking CSS visual indicators: {str(e)}")
        
        return findings
    
    def _has_additional_context(self, text: str, pattern: str) -> bool:
        """Check if text has additional context beyond color."""
        # Look for additional descriptive words
        additional_words = [
            'button', 'link', 'text', 'element', 'icon', 'symbol',
            'error', 'success', 'warning', 'info', 'status',
            'required', 'optional', 'active', 'inactive', 'selected'
        ]
        
        text_lower = text.lower()
        for word in additional_words:
            if word in text_lower:
                return True
        
        return False
    
    def _appears_to_contain_information(self, img) -> bool:
        """Check if image appears to contain important information."""
        src = img.get('src', '').lower()
        
        # Check for indicators that image contains information
        info_indicators = [
            'chart', 'graph', 'diagram', 'map', 'screenshot',
            'infographic', 'timeline', 'flowchart', 'table'
        ]
        
        return any(indicator in src for indicator in info_indicators)
    
    def _color_conveys_meaning(self, style: str, text: str) -> bool:
        """Check if color is used to convey meaning."""
        # Look for color values that might convey meaning
        meaningful_colors = [
            'red', 'green', 'blue', 'yellow', 'orange',
            '#ff0000', '#00ff00', '#0000ff', '#ffff00', '#ffa500',
            '#f00', '#0f0', '#00f', '#ff0', '#fa0'
        ]
        
        style_lower = style.lower()
        for color in meaningful_colors:
            if color in style_lower:
                # Check if text doesn't provide additional context
                if not self._has_additional_context(text, ''):
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
