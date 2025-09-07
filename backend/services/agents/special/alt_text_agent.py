"""
AltTextAgent - Detects missing or inadequate alt text for images and media.
"""

import os
import re
from typing import List, Dict, Any
from bs4 import BeautifulSoup
from models.schemas import Finding, Evidence, SeverityLevel, ConfidenceLevel, CriterionType
from services.agents.base_agent import BaseAgent
import logging

logger = logging.getLogger(__name__)

class AltTextAgent(BaseAgent):
    """Agent for detecting alt text issues in HTML content."""
    
    def __init__(self):
        super().__init__(
            name="AltTextAgent",
            description="Detects missing or inadequate alt text for images and media elements",
            criterion=CriterionType.ARIA,
            wcag_criterion="1.1.1"
        )
    
    async def analyze(self, upload_path: str) -> List[Finding]:
        """Analyze files for alt text issues."""
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
            logger.error(f"AltTextAgent analysis failed: {str(e)}")
            findings.append(self._create_error_finding(upload_path, str(e)))
        
        return findings
    
    async def _analyze_html_content(self, soup: BeautifulSoup, file_path: str) -> List[Finding]:
        """Analyze HTML content for alt text issues."""
        findings = []
        
        # Check img elements
        img_findings = await self._check_img_elements(soup, file_path)
        findings.extend(img_findings)
        
        # Check area elements (image maps)
        area_findings = await self._check_area_elements(soup, file_path)
        findings.extend(area_findings)
        
        # Check input elements with type="image"
        input_findings = await self._check_input_elements(soup, file_path)
        findings.extend(input_findings)
        
        # Check object and embed elements
        object_findings = await self._check_object_elements(soup, file_path)
        findings.extend(object_findings)
        
        return findings
    
    async def _check_img_elements(self, soup: BeautifulSoup, file_path: str) -> List[Finding]:
        """Check img elements for alt text issues."""
        findings = []
        
        for img in soup.find_all('img'):
            try:
                # Get element position
                line_number = img.sourceline if hasattr(img, 'sourceline') else None
                
                # Check for missing alt attribute
                if 'alt' not in img.attrs:
                    findings.append(self._create_finding(
                        file_path=file_path,
                        line_number=line_number,
                        selector=self._get_selector(img),
                        details="Image element missing alt attribute",
                        severity=SeverityLevel.HIGH,
                        evidence=self._create_evidence(file_path, line_number, str(img))
                    ))
                
                # Check for empty alt attribute
                elif img.get('alt', '').strip() == '':
                    # Check if image is decorative (has role="presentation" or aria-hidden="true")
                    is_decorative = (
                        img.get('role') == 'presentation' or 
                        img.get('aria-hidden') == 'true'
                    )
                    
                    if not is_decorative:
                        findings.append(self._create_finding(
                            file_path=file_path,
                            line_number=line_number,
                            selector=self._get_selector(img),
                            details="Image element has empty alt attribute but is not marked as decorative",
                            severity=SeverityLevel.MEDIUM,
                            evidence=self._create_evidence(file_path, line_number, str(img))
                        ))
                
                # Check for alt text quality
                else:
                    alt_text = img.get('alt', '').strip()
                    if self._is_poor_alt_text(alt_text):
                        findings.append(self._create_finding(
                            file_path=file_path,
                            line_number=line_number,
                            selector=self._get_selector(img),
                            details=f"Image alt text may be inadequate: '{alt_text}'",
                            severity=SeverityLevel.LOW,
                            evidence=self._create_evidence(file_path, line_number, str(img))
                        ))
                
            except Exception as e:
                logger.error(f"Error checking img element: {str(e)}")
        
        return findings
    
    async def _check_area_elements(self, soup: BeautifulSoup, file_path: str) -> List[Finding]:
        """Check area elements for alt text issues."""
        findings = []
        
        for area in soup.find_all('area'):
            try:
                line_number = area.sourceline if hasattr(area, 'sourceline') else None
                
                # Check for missing alt attribute
                if 'alt' not in area.attrs:
                    findings.append(self._create_finding(
                        file_path=file_path,
                        line_number=line_number,
                        selector=self._get_selector(area),
                        details="Area element missing alt attribute",
                        severity=SeverityLevel.HIGH,
                        evidence=self._create_evidence(file_path, line_number, str(area))
                    ))
                
                # Check for empty alt attribute
                elif area.get('alt', '').strip() == '':
                    findings.append(self._create_finding(
                        file_path=file_path,
                        line_number=line_number,
                        selector=self._get_selector(area),
                        details="Area element has empty alt attribute",
                        severity=SeverityLevel.MEDIUM,
                        evidence=self._create_evidence(file_path, line_number, str(area))
                    ))
                
            except Exception as e:
                logger.error(f"Error checking area element: {str(e)}")
        
        return findings
    
    async def _check_input_elements(self, soup: BeautifulSoup, file_path: str) -> List[Finding]:
        """Check input elements with type='image' for alt text issues."""
        findings = []
        
        for input_elem in soup.find_all('input', type='image'):
            try:
                line_number = input_elem.sourceline if hasattr(input_elem, 'sourceline') else None
                
                # Check for missing alt attribute
                if 'alt' not in input_elem.attrs:
                    findings.append(self._create_finding(
                        file_path=file_path,
                        line_number=line_number,
                        selector=self._get_selector(input_elem),
                        details="Input element with type='image' missing alt attribute",
                        severity=SeverityLevel.HIGH,
                        evidence=self._create_evidence(file_path, line_number, str(input_elem))
                    ))
                
                # Check for empty alt attribute
                elif input_elem.get('alt', '').strip() == '':
                    findings.append(self._create_finding(
                        file_path=file_path,
                        line_number=line_number,
                        selector=self._get_selector(input_elem),
                        details="Input element with type='image' has empty alt attribute",
                        severity=SeverityLevel.MEDIUM,
                        evidence=self._create_evidence(file_path, line_number, str(input_elem))
                    ))
                
            except Exception as e:
                logger.error(f"Error checking input element: {str(e)}")
        
        return findings
    
    async def _check_object_elements(self, soup: BeautifulSoup, file_path: str) -> List[Finding]:
        """Check object and embed elements for alternative content."""
        findings = []
        
        for obj in soup.find_all(['object', 'embed']):
            try:
                line_number = obj.sourceline if hasattr(obj, 'sourceline') else None
                
                # Check if object has alternative content
                has_alt_content = (
                    obj.find('img') is not None or
                    obj.find('video') is not None or
                    obj.find('audio') is not None or
                    (obj.get_text() and obj.get_text().strip())
                )
                
                if not has_alt_content:
                    findings.append(self._create_finding(
                        file_path=file_path,
                        line_number=line_number,
                        selector=self._get_selector(obj),
                        details=f"{obj.name.title()} element missing alternative content",
                        severity=SeverityLevel.MEDIUM,
                        evidence=self._create_evidence(file_path, line_number, str(obj))
                    ))
                
            except Exception as e:
                logger.error(f"Error checking {obj.name} element: {str(e)}")
        
        return findings
    
    def _is_poor_alt_text(self, alt_text: str) -> bool:
        """Check if alt text is of poor quality."""
        if not alt_text:
            return True
        
        # Check for common poor alt text patterns
        poor_patterns = [
            r'^image\s*$',
            r'^picture\s*$',
            r'^photo\s*$',
            r'^img\s*$',
            r'^\.(jpg|jpeg|png|gif|svg|webp)\s*$',
            r'^\d+\s*$',  # Just numbers
            r'^[a-z]+\s*$',  # Just lowercase letters (likely filename)
        ]
        
        for pattern in poor_patterns:
            if re.match(pattern, alt_text, re.IGNORECASE):
                return True
        
        # Check for very short alt text (unless it's intentionally short)
        if len(alt_text.strip()) < 3:
            return True
        
        return False
    
    def _get_selector(self, element) -> str:
        """Generate CSS selector for element."""
        try:
            if element.name == 'img':
                if element.get('id'):
                    return f"#{element.get('id')}"
                elif element.get('class'):
                    return f".{'.'.join(element.get('class'))}"
                else:
                    return f"img[{element.get('src', '')}]"
            elif element.name == 'area':
                if element.get('id'):
                    return f"#{element.get('id')}"
                else:
                    return f"area[{element.get('href', '')}]"
            elif element.name == 'input':
                if element.get('id'):
                    return f"#{element.get('id')}"
                else:
                    return f"input[type='{element.get('type', '')}']"
            else:
                return element.name
        except:
            return element.name if hasattr(element, 'name') else 'unknown'
