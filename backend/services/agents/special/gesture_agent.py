"""
GestureAgent - Detects gesture and touch accessibility issues.
"""

import os
import re
from typing import List, Dict, Any
from bs4 import BeautifulSoup
from models.schemas import Finding, Evidence, SeverityLevel, ConfidenceLevel, CriterionType
from services.agents.base_agent import BaseAgent
import logging

logger = logging.getLogger(__name__)

class GestureAgent(BaseAgent):
    """Agent for detecting gesture and touch accessibility issues."""
    
    def __init__(self):
        super().__init__(
            name="GestureAgent",
            description="Detects gesture and touch accessibility issues",
            criterion=CriterionType.ARIA,
            wcag_criterion="2.5.1"
        )
    
    async def analyze(self, upload_path: str) -> List[Finding]:
        """Analyze files for gesture issues."""
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
            logger.error(f"GestureAgent analysis failed: {str(e)}")
            findings.append(self._create_error_finding(upload_path, str(e)))
        
        return findings
    
    async def _analyze_html_content(self, soup: BeautifulSoup, file_path: str) -> List[Finding]:
        """Analyze HTML content for gesture issues."""
        findings = []
        
        # Check gesture-only interactions
        gesture_findings = await self._check_gesture_only_interactions(soup, file_path)
        findings.extend(gesture_findings)
        
        # Check touch target sizes
        touch_target_findings = await self._check_touch_target_sizes(soup, file_path)
        findings.extend(touch_target_findings)
        
        # Check swipe gestures
        swipe_findings = await self._check_swipe_gestures(soup, file_path)
        findings.extend(swipe_findings)
        
        # Check pinch gestures
        pinch_findings = await self._check_pinch_gestures(soup, file_path)
        findings.extend(pinch_findings)
        
        return findings
    
    async def _check_gesture_only_interactions(self, soup: BeautifulSoup, file_path: str) -> List[Finding]:
        """Check for interactions that require gestures without alternatives."""
        findings = []
        
        # Check for elements with gesture-only event handlers
        gesture_elements = soup.find_all(attrs={
            'ontouchstart': True,
            'ontouchend': True,
            'ontouchmove': True,
            'ongesturestart': True,
            'ongesturechange': True,
            'ongestureend': True
        })
        
        for element in gesture_elements:
            try:
                line_number = element.sourceline if hasattr(element, 'sourceline') else None
                
                # Check if element has alternative interaction methods
                if not self._has_alternative_interaction(element):
                    findings.append(self._create_finding(
                        file_path=file_path,
                        line_number=line_number,
                        selector=self._get_selector(element),
                        details="Element requires gesture interaction without alternative",
                        severity=SeverityLevel.HIGH,
                        evidence=self._create_evidence(file_path, line_number, str(element))
                    ))
                
            except Exception as e:
                logger.error(f"Error checking gesture-only interactions: {str(e)}")
        
        # Check for JavaScript gesture handlers
        script_elements = soup.find_all('script')
        for script in script_elements:
            try:
                line_number = script.sourceline if hasattr(script, 'sourceline') else None
                script_content = script.get_text()
                
                # Look for gesture-related JavaScript
                gesture_patterns = [
                    r'addEventListener\s*\(\s*[\'"]touchstart[\'"]',
                    r'addEventListener\s*\(\s*[\'"]touchend[\'"]',
                    r'addEventListener\s*\(\s*[\'"]touchmove[\'"]',
                    r'addEventListener\s*\(\s*[\'"]gesturestart[\'"]',
                    r'addEventListener\s*\(\s*[\'"]gesturechange[\'"]',
                    r'addEventListener\s*\(\s*[\'"]gestureend[\'"]'
                ]
                
                for pattern in gesture_patterns:
                    if re.search(pattern, script_content):
                        findings.append(self._create_finding(
                            file_path=file_path,
                            line_number=line_number,
                            selector="script",
                            details="JavaScript uses gesture events - ensure alternative interactions",
                            severity=SeverityLevel.MEDIUM,
                            evidence=self._create_evidence(file_path, line_number, str(script))
                        ))
                
            except Exception as e:
                logger.error(f"Error checking JavaScript gesture handlers: {str(e)}")
        
        return findings
    
    async def _check_touch_target_sizes(self, soup: BeautifulSoup, file_path: str) -> List[Finding]:
        """Check touch target sizes for accessibility."""
        findings = []
        
        # Check interactive elements for adequate touch target size
        interactive_elements = soup.find_all([
            'a', 'button', 'input', 'select', 'textarea', 'details', 'summary'
        ])
        
        for element in interactive_elements:
            try:
                line_number = element.sourceline if hasattr(element, 'sourceline') else None
                
                # Check if element has size constraints
                style = element.get('style', '')
                if style:
                    # Look for width and height in styles
                    width_match = re.search(r'width\s*:\s*(\d+(?:\.\d+)?)(px|em|rem|%)', style)
                    height_match = re.search(r'height\s*:\s*(\d+(?:\.\d+)?)(px|em|rem|%)', style)
                    
                    if width_match and height_match:
                        width = float(width_match.group(1))
                        height = float(height_match.group(1))
                        
                        # Check if touch target is too small (less than 44px)
                        if width < 44 or height < 44:
                            findings.append(self._create_finding(
                                file_path=file_path,
                                line_number=line_number,
                                selector=self._get_selector(element),
                                details=f"Touch target too small ({width}x{height}px) - minimum 44x44px recommended",
                                severity=SeverityLevel.MEDIUM,
                                evidence=self._create_evidence(file_path, line_number, str(element))
                            ))
                
            except Exception as e:
                logger.error(f"Error checking touch target sizes: {str(e)}")
        
        return findings
    
    async def _check_swipe_gestures(self, soup: BeautifulSoup, file_path: str) -> List[Finding]:
        """Check for swipe gesture implementations."""
        findings = []
        
        # Check for swipe-related JavaScript
        script_elements = soup.find_all('script')
        for script in script_elements:
            try:
                line_number = script.sourceline if hasattr(script, 'sourceline') else None
                script_content = script.get_text()
                
                # Look for swipe-related code
                swipe_patterns = [
                    r'swipe',
                    r'touchstart.*touchmove.*touchend',
                    r'gesture.*swipe',
                    r'pan.*gesture'
                ]
                
                for pattern in swipe_patterns:
                    if re.search(pattern, script_content, re.IGNORECASE):
                        findings.append(self._create_finding(
                            file_path=file_path,
                            line_number=line_number,
                            selector="script",
                            details="Swipe gesture detected - ensure alternative navigation methods",
                            severity=SeverityLevel.MEDIUM,
                            evidence=self._create_evidence(file_path, line_number, str(script))
                        ))
                
            except Exception as e:
                logger.error(f"Error checking swipe gestures: {str(e)}")
        
        return findings
    
    async def _check_pinch_gestures(self, soup: BeautifulSoup, file_path: str) -> List[Finding]:
        """Check for pinch gesture implementations."""
        findings = []
        
        # Check for pinch-related JavaScript
        script_elements = soup.find_all('script')
        for script in script_elements:
            try:
                line_number = script.sourceline if hasattr(script, 'sourceline') else None
                script_content = script.get_text()
                
                # Look for pinch-related code
                pinch_patterns = [
                    r'pinch',
                    r'gesture.*pinch',
                    r'scale.*gesture',
                    r'zoom.*gesture'
                ]
                
                for pattern in pinch_patterns:
                    if re.search(pattern, script_content, re.IGNORECASE):
                        findings.append(self._create_finding(
                            file_path=file_path,
                            line_number=line_number,
                            selector="script",
                            details="Pinch gesture detected - ensure alternative zoom methods",
                            severity=SeverityLevel.MEDIUM,
                            evidence=self._create_evidence(file_path, line_number, str(script))
                        ))
                
            except Exception as e:
                logger.error(f"Error checking pinch gestures: {str(e)}")
        
        return findings
    
    def _has_alternative_interaction(self, element) -> bool:
        """Check if element has alternative interaction methods."""
        # Check for keyboard event handlers
        keyboard_events = ['onkeydown', 'onkeyup', 'onkeypress']
        if any(event in element.attrs for event in keyboard_events):
            return True
        
        # Check for click handlers
        if 'onclick' in element.attrs:
            return True
        
        # Check for proper ARIA roles
        role = element.get('role')
        if role in ['button', 'link', 'menuitem', 'tab']:
            return True
        
        # Check if element is naturally interactive
        if element.name in ['a', 'button', 'input', 'select', 'textarea']:
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
