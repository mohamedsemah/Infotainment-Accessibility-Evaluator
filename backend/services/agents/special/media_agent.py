"""
MediaAgent - Detects accessibility issues in video and audio elements.
"""

import os
import re
from typing import List, Dict, Any
from bs4 import BeautifulSoup
from models.schemas import Finding, Evidence, SeverityLevel, ConfidenceLevel, CriterionType
from services.agents.base_agent import BaseAgent
import logging

logger = logging.getLogger(__name__)

class MediaAgent(BaseAgent):
    """Agent for detecting accessibility issues in media elements."""
    
    def __init__(self):
        super().__init__(
            name="MediaAgent",
            description="Detects accessibility issues in video and audio elements",
            criterion=CriterionType.ARIA,
            wcag_criterion="1.2.1"
        )
    
    async def analyze(self, upload_path: str) -> List[Finding]:
        """Analyze files for media accessibility issues."""
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
            logger.error(f"MediaAgent analysis failed: {str(e)}")
            findings.append(self._create_error_finding(upload_path, str(e)))
        
        return findings
    
    async def _analyze_html_content(self, soup: BeautifulSoup, file_path: str) -> List[Finding]:
        """Analyze HTML content for media accessibility issues."""
        findings = []
        
        # Check video elements
        video_findings = await self._check_video_elements(soup, file_path)
        findings.extend(video_findings)
        
        # Check audio elements
        audio_findings = await self._check_audio_elements(soup, file_path)
        findings.extend(audio_findings)
        
        # Check iframe elements (embedded media)
        iframe_findings = await self._check_iframe_elements(soup, file_path)
        findings.extend(iframe_findings)
        
        return findings
    
    async def _check_video_elements(self, soup: BeautifulSoup, file_path: str) -> List[Finding]:
        """Check video elements for accessibility issues."""
        findings = []
        
        for video in soup.find_all('video'):
            try:
                line_number = video.sourceline if hasattr(video, 'sourceline') else None
                
                # Check for missing captions
                has_captions = (
                    video.find('track', kind='captions') is not None or
                    video.find('track', kind='subtitles') is not None
                )
                
                if not has_captions:
                    findings.append(self._create_finding(
                        file_path=file_path,
                        line_number=line_number,
                        selector=self._get_selector(video),
                        details="Video element missing captions or subtitles",
                        severity=SeverityLevel.HIGH,
                        evidence=self._create_evidence(file_path, line_number, str(video))
                    ))
                
                # Check for missing audio description
                has_audio_description = (
                    video.find('track', kind='descriptions') is not None or
                    video.get('aria-describedby') is not None
                )
                
                if not has_audio_description:
                    findings.append(self._create_finding(
                        file_path=file_path,
                        line_number=line_number,
                        selector=self._get_selector(video),
                        details="Video element missing audio description for visual content",
                        severity=SeverityLevel.MEDIUM,
                        evidence=self._create_evidence(file_path, line_number, str(video))
                    ))
                
                # Check for missing controls
                if not video.get('controls'):
                    findings.append(self._create_finding(
                        file_path=file_path,
                        line_number=line_number,
                        selector=self._get_selector(video),
                        details="Video element missing controls attribute",
                        severity=SeverityLevel.MEDIUM,
                        evidence=self._create_evidence(file_path, line_number, str(video))
                    ))
                
                # Check for autoplay without user control
                if video.get('autoplay') and not video.get('muted'):
                    findings.append(self._create_finding(
                        file_path=file_path,
                        line_number=line_number,
                        selector=self._get_selector(video),
                        details="Video element autoplays without being muted",
                        severity=SeverityLevel.HIGH,
                        evidence=self._create_evidence(file_path, line_number, str(video))
                    ))
                
                # Check for missing poster image
                if not video.get('poster'):
                    findings.append(self._create_finding(
                        file_path=file_path,
                        line_number=line_number,
                        selector=self._get_selector(video),
                        details="Video element missing poster image",
                        severity=SeverityLevel.LOW,
                        evidence=self._create_evidence(file_path, line_number, str(video))
                    ))
                
            except Exception as e:
                logger.error(f"Error checking video element: {str(e)}")
        
        return findings
    
    async def _check_audio_elements(self, soup: BeautifulSoup, file_path: str) -> List[Finding]:
        """Check audio elements for accessibility issues."""
        findings = []
        
        for audio in soup.find_all('audio'):
            try:
                line_number = audio.sourceline if hasattr(audio, 'sourceline') else None
                
                # Check for missing transcript or captions
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
                        details="Audio element missing transcript or captions",
                        severity=SeverityLevel.HIGH,
                        evidence=self._create_evidence(file_path, line_number, str(audio))
                    ))
                
                # Check for missing controls
                if not audio.get('controls'):
                    findings.append(self._create_finding(
                        file_path=file_path,
                        line_number=line_number,
                        selector=self._get_selector(audio),
                        details="Audio element missing controls attribute",
                        severity=SeverityLevel.MEDIUM,
                        evidence=self._create_evidence(file_path, line_number, str(audio))
                    ))
                
                # Check for autoplay
                if audio.get('autoplay'):
                    findings.append(self._create_finding(
                        file_path=file_path,
                        line_number=line_number,
                        selector=self._get_selector(audio),
                        details="Audio element has autoplay attribute",
                        severity=SeverityLevel.HIGH,
                        evidence=self._create_evidence(file_path, line_number, str(audio))
                    ))
                
            except Exception as e:
                logger.error(f"Error checking audio element: {str(e)}")
        
        return findings
    
    async def _check_iframe_elements(self, soup: BeautifulSoup, file_path: str) -> List[Finding]:
        """Check iframe elements for embedded media accessibility."""
        findings = []
        
        for iframe in soup.find_all('iframe'):
            try:
                line_number = iframe.sourceline if hasattr(iframe, 'sourceline') else None
                src = iframe.get('src', '')
                
                # Check for YouTube/Vimeo embeds without proper accessibility
                if 'youtube.com' in src or 'youtu.be' in src or 'vimeo.com' in src:
                    # Check for missing title
                    if not iframe.get('title'):
                        findings.append(self._create_finding(
                            file_path=file_path,
                            line_number=line_number,
                            selector=self._get_selector(iframe),
                            details="Embedded video iframe missing title attribute",
                            severity=SeverityLevel.MEDIUM,
                            evidence=self._create_evidence(file_path, line_number, str(iframe))
                        ))
                    
                    # Check for missing aria-label
                    if not iframe.get('aria-label') and not iframe.get('title'):
                        findings.append(self._create_finding(
                            file_path=file_path,
                            line_number=line_number,
                            selector=self._get_selector(iframe),
                            details="Embedded video iframe missing accessible name",
                            severity=SeverityLevel.MEDIUM,
                            evidence=self._create_evidence(file_path, line_number, str(iframe))
                        ))
                
                # Check for missing title on all iframes
                if not iframe.get('title') and not iframe.get('aria-label'):
                    findings.append(self._create_finding(
                        file_path=file_path,
                        line_number=line_number,
                        selector=self._get_selector(iframe),
                        details="Iframe element missing title or aria-label",
                        severity=SeverityLevel.MEDIUM,
                        evidence=self._create_evidence(file_path, line_number, str(iframe))
                    ))
                
            except Exception as e:
                logger.error(f"Error checking iframe element: {str(e)}")
        
        return findings
    
    def _get_selector(self, element) -> str:
        """Generate CSS selector for element."""
        try:
            if element.get('id'):
                return f"#{element.get('id')}"
            elif element.get('class'):
                return f".{'.'.join(element.get('class'))}"
            elif element.get('src'):
                return f"{element.name}[src='{element.get('src')}']"
            else:
                return element.name
        except:
            return element.name if hasattr(element, 'name') else 'unknown'
