"""
SeizureSafeAgent - Evaluates seizure safety compliance for WCAG 2.2.
"""

import os
import re
from typing import List, Dict, Any, Optional
from pathlib import Path
from bs4 import BeautifulSoup

from models.schemas import Finding, Evidence, SeverityLevel, ConfidenceLevel, CriterionType
from utils.flash_metrics import FlashDetector, FlashEvent, analyze_animation_safety
from utils.wcag_constants import FLASH_THRESHOLDS
from utils.id_gen import generate_finding_id

class SeizureSafeAgent:
    """Agent responsible for evaluating seizure safety compliance."""
    
    def __init__(self):
        self.flash_detector = FlashDetector()
        self.findings = []
    
    async def analyze(self, upload_path: str, upload_id: str) -> List[Finding]:
        """Analyze uploaded files for seizure safety issues."""
        self.findings = []
        
        # Find all HTML, CSS, and QML files
        html_files = self._find_files(upload_path, ['.html', '.htm', '.xhtml'])
        css_files = self._find_files(upload_path, ['.css', '.scss', '.sass'])
        qml_files = self._find_files(upload_path, ['.qml'])
        js_files = self._find_files(upload_path, ['.js', '.jsx', '.ts', '.tsx'])
        
        # Analyze HTML files for animations and media
        for html_file in html_files:
            await self._analyze_html_file(html_file, upload_path)
        
        # Analyze CSS files for animations
        for css_file in css_files:
            await self._analyze_css_file(css_file, upload_path)
        
        # Analyze QML files for animations
        for qml_file in qml_files:
            await self._analyze_qml_file(qml_file, upload_path)
        
        # Analyze JavaScript files for animations
        for js_file in js_files:
            await self._analyze_js_file(js_file, upload_path)
        
        return self.findings
    
    def _find_files(self, upload_path: str, extensions: List[str]) -> List[str]:
        """Find files with specific extensions."""
        files = []
        for root, dirs, filenames in os.walk(upload_path):
            for filename in filenames:
                if Path(filename).suffix.lower() in extensions:
                    files.append(os.path.join(root, filename))
        return files
    
    async def _analyze_html_file(self, file_path: str, upload_path: str):
        """Analyze HTML file for seizure safety issues."""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            soup = BeautifulSoup(content, 'html.parser')
            relative_path = os.path.relpath(file_path, upload_path)
            
            # Check for auto-playing media
            await self._check_auto_playing_media(soup, relative_path, file_path)
            
            # Check for animated elements
            await self._check_animated_elements(soup, relative_path, file_path)
            
            # Check for flash content
            await self._check_flash_content(soup, relative_path, file_path)
        
        except Exception as e:
            self._add_error_finding(file_path, upload_path, f"Error analyzing HTML file: {str(e)}")
    
    async def _analyze_css_file(self, file_path: str, upload_path: str):
        """Analyze CSS file for seizure safety issues."""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            relative_path = os.path.relpath(file_path, upload_path)
            
            # Detect flash patterns in CSS
            flashes = self.flash_detector.detect_css_flashes(content)
            
            if flashes:
                # Analyze flash safety
                safety_analysis = self.flash_detector.analyze_flash_safety(flashes)
                
                if not safety_analysis["safe"]:
                    await self._add_flash_findings(flashes, safety_analysis, relative_path, file_path)
        
        except Exception as e:
            self._add_error_finding(file_path, upload_path, f"Error analyzing CSS file: {str(e)}")
    
    async def _analyze_qml_file(self, file_path: str, upload_path: str):
        """Analyze QML file for seizure safety issues."""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            relative_path = os.path.relpath(file_path, upload_path)
            
            # Check for QML animations
            await self._check_qml_animations(content, relative_path, file_path)
            
            # Check for QML transitions
            await self._check_qml_transitions(content, relative_path, file_path)
        
        except Exception as e:
            self._add_error_finding(file_path, upload_path, f"Error analyzing QML file: {str(e)}")
    
    async def _analyze_js_file(self, file_path: str, upload_path: str):
        """Analyze JavaScript file for seizure safety issues."""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            relative_path = os.path.relpath(file_path, upload_path)
            
            # Check for animation-related JavaScript
            await self._check_js_animations(content, relative_path, file_path)
        
        except Exception as e:
            self._add_error_finding(file_path, upload_path, f"Error analyzing JavaScript file: {str(e)}")
    
    async def _check_auto_playing_media(self, soup: BeautifulSoup, relative_path: str, file_path: str):
        """Check for auto-playing media elements."""
        # Check for video elements
        videos = soup.find_all('video')
        for video in videos:
            if video.get('autoplay') or video.get('autoplay') == '':
                self._add_media_finding(
                    video, "Auto-playing video detected", relative_path, file_path, "video"
                )
        
        # Check for audio elements
        audios = soup.find_all('audio')
        for audio in audios:
            if audio.get('autoplay') or audio.get('autoplay') == '':
                self._add_media_finding(
                    audio, "Auto-playing audio detected", relative_path, file_path, "audio"
                )
        
        # Check for iframe elements (potential embedded media)
        iframes = soup.find_all('iframe')
        for iframe in iframes:
            src = iframe.get('src', '')
            if any(platform in src.lower() for platform in ['youtube', 'vimeo', 'dailymotion']):
                if iframe.get('autoplay') or 'autoplay' in src:
                    self._add_media_finding(
                        iframe, "Auto-playing embedded media detected", relative_path, file_path, "iframe"
                    )
    
    async def _check_animated_elements(self, soup: BeautifulSoup, relative_path: str, file_path: str):
        """Check for animated elements."""
        # Check for elements with animation classes
        animated_elements = soup.find_all(class_=re.compile(r'animate|animation|flash|blink|pulse|spin|bounce'))
        
        for element in animated_elements:
            self._add_animation_finding(
                element, "Animated element detected", relative_path, file_path, "class-based"
            )
        
        # Check for elements with inline animation styles
        elements_with_animation = soup.find_all(style=re.compile(r'animation|transition|transform'))
        
        for element in elements_with_animation:
            style = element.get('style', '')
            if 'animation' in style.lower() or 'transition' in style.lower():
                self._add_animation_finding(
                    element, "Element with inline animation styles", relative_path, file_path, "inline-style"
                )
    
    async def _check_flash_content(self, soup: BeautifulSoup, relative_path: str, file_path: str):
        """Check for flash content."""
        # Check for Flash objects
        flash_objects = soup.find_all(['object', 'embed'], type=re.compile(r'application/x-shockwave-flash|flash'))
        
        for obj in flash_objects:
            self._add_flash_finding(
                obj, "Flash content detected", relative_path, file_path, "flash-object"
            )
    
    async def _check_qml_animations(self, content: str, relative_path: str, file_path: str):
        """Check for QML animations."""
        # Find QML animation elements
        animation_pattern = r'<(\w*Animation|NumberAnimation|PropertyAnimation|ColorAnimation|RotationAnimation|ScaleAnimation|SequentialAnimation|ParallelAnimation|PauseAnimation|ScriptAction)'
        matches = re.finditer(animation_pattern, content, re.IGNORECASE)
        
        for match in matches:
            animation_type = match.group(1)
            # Check for duration and loops
            duration_match = re.search(r'duration\s*:\s*(\d+)', content, re.IGNORECASE)
            loops_match = re.search(r'loops\s*:\s*(\d+)', content, re.IGNORECASE)
            
            if duration_match and loops_match:
                duration = int(duration_match.group(1))
                loops = int(loops_match.group(1))
                
                # Calculate frequency
                if duration > 0:
                    frequency = loops / (duration / 1000.0)  # Convert ms to seconds
                    
                    if frequency > FLASH_THRESHOLDS["max_frequency"]:
                        self._add_qml_animation_finding(
                            animation_type, frequency, duration, loops, relative_path, file_path
                        )
    
    async def _check_qml_transitions(self, content: str, relative_path: str, file_path: str):
        """Check for QML transitions."""
        # Find QML transition elements
        transition_pattern = r'<Transition'
        matches = re.finditer(transition_pattern, content, re.IGNORECASE)
        
        for match in matches:
            # Check for duration
            duration_match = re.search(r'duration\s*:\s*(\d+)', content, re.IGNORECASE)
            
            if duration_match:
                duration = int(duration_match.group(1))
                
                # Check if transition is too fast
                if duration < 100:  # Less than 100ms
                    self._add_qml_transition_finding(
                        duration, relative_path, file_path
                    )
    
    async def _check_js_animations(self, content: str, relative_path: str, file_path: str):
        """Check for JavaScript animations."""
        # Look for animation-related JavaScript
        animation_patterns = [
            r'setInterval\s*\([^,]+,\s*(\d+)\)',  # setInterval with timing
            r'setTimeout\s*\([^,]+,\s*(\d+)\)',   # setTimeout with timing
            r'requestAnimationFrame',              # requestAnimationFrame
            r'animate\s*\([^)]+\)',               # animate functions
            r'transition\s*\([^)]+\)',            # transition functions
        ]
        
        for pattern in animation_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            
            for match in matches:
                if 'setInterval' in pattern or 'setTimeout' in pattern:
                    # Extract timing
                    timing = int(match.group(1))
                    frequency = 1000.0 / timing  # Convert ms to Hz
                    
                    if frequency > FLASH_THRESHOLDS["max_frequency"]:
                        self._add_js_animation_finding(
                            match.group(0), frequency, timing, relative_path, file_path
                        )
                else:
                    # General animation detection
                    self._add_js_animation_finding(
                        match.group(0), 0, 0, relative_path, file_path
                    )
    
    async def _add_flash_findings(self, flashes: List[FlashEvent], safety_analysis: Dict[str, Any], relative_path: str, file_path: str):
        """Add findings for flash patterns."""
        for flash in flashes:
            if flash.is_dangerous or flash.frequency > FLASH_THRESHOLDS["max_frequency"]:
                self._add_flash_finding(
                    flash, safety_analysis, relative_path, file_path
                )
    
    def _add_media_finding(self, element, message: str, relative_path: str, file_path: str, media_type: str):
        """Add a media-related finding."""
        finding_id = generate_finding_id()
        
        evidence = Evidence(
            file_path=relative_path,
            code_snippet=str(element),
            metrics={"media_type": media_type, "autoplay": True}
        )
        
        finding = Finding(
            id=finding_id,
            criterion=CriterionType.SEIZURE_SAFE,
            selector=self._get_element_selector(element),
            details=message,
            evidence=[evidence],
            severity=SeverityLevel.HIGH,
            confidence=ConfidenceLevel.HIGH,
            wcag_criterion="2.2.2"
        )
        
        self.findings.append(finding)
    
    def _add_animation_finding(self, element, message: str, relative_path: str, file_path: str, animation_type: str):
        """Add an animation-related finding."""
        finding_id = generate_finding_id()
        
        evidence = Evidence(
            file_path=relative_path,
            code_snippet=str(element),
            metrics={"animation_type": animation_type}
        )
        
        finding = Finding(
            id=finding_id,
            criterion=CriterionType.SEIZURE_SAFE,
            selector=self._get_element_selector(element),
            details=message,
            evidence=[evidence],
            severity=SeverityLevel.MEDIUM,
            confidence=ConfidenceLevel.MEDIUM,
            wcag_criterion="2.3.3"
        )
        
        self.findings.append(finding)
    
    def _add_flash_finding(self, flash: FlashEvent, safety_analysis: Dict[str, Any], relative_path: str, file_path: str):
        """Add a flash-related finding."""
        finding_id = generate_finding_id()
        
        evidence = Evidence(
            file_path=relative_path,
            code_snippet="",
            metrics={
                "frequency": flash.frequency,
                "intensity": flash.intensity,
                "area_ratio": flash.area_ratio,
                "luminance_change": flash.luminance_change,
                "is_dangerous": flash.is_dangerous
            }
        )
        
        severity = SeverityLevel.CRITICAL if flash.is_dangerous else SeverityLevel.HIGH
        
        finding = Finding(
            id=finding_id,
            criterion=CriterionType.SEIZURE_SAFE,
            selector="",
            details=f"Flash pattern detected: {flash.frequency:.1f} Hz (threshold: {FLASH_THRESHOLDS['max_frequency']} Hz)",
            evidence=[evidence],
            severity=severity,
            confidence=ConfidenceLevel.HIGH,
            wcag_criterion="2.3.1"
        )
        
        self.findings.append(finding)
    
    def _add_qml_animation_finding(self, animation_type: str, frequency: float, duration: int, loops: int, relative_path: str, file_path: str):
        """Add a QML animation finding."""
        finding_id = generate_finding_id()
        
        evidence = Evidence(
            file_path=relative_path,
            code_snippet=f"{animation_type} with duration: {duration}ms, loops: {loops}",
            metrics={
                "animation_type": animation_type,
                "frequency": frequency,
                "duration": duration,
                "loops": loops
            }
        )
        
        severity = SeverityLevel.CRITICAL if frequency > FLASH_THRESHOLDS["dangerous_frequency"] else SeverityLevel.HIGH
        
        finding = Finding(
            id=finding_id,
            criterion=CriterionType.SEIZURE_SAFE,
            selector=animation_type,
            details=f"QML animation exceeds frequency threshold: {frequency:.1f} Hz",
            evidence=[evidence],
            severity=severity,
            confidence=ConfidenceLevel.HIGH,
            wcag_criterion="2.3.1"
        )
        
        self.findings.append(finding)
    
    def _add_qml_transition_finding(self, duration: int, relative_path: str, file_path: str):
        """Add a QML transition finding."""
        finding_id = generate_finding_id()
        
        evidence = Evidence(
            file_path=relative_path,
            code_snippet=f"Transition with duration: {duration}ms",
            metrics={"duration": duration}
        )
        
        finding = Finding(
            id=finding_id,
            criterion=CriterionType.SEIZURE_SAFE,
            selector="Transition",
            details=f"QML transition duration too short: {duration}ms (may cause rapid changes)",
            evidence=[evidence],
            severity=SeverityLevel.MEDIUM,
            confidence=ConfidenceLevel.MEDIUM,
            wcag_criterion="2.3.3"
        )
        
        self.findings.append(finding)
    
    def _add_js_animation_finding(self, code: str, frequency: float, timing: int, relative_path: str, file_path: str):
        """Add a JavaScript animation finding."""
        finding_id = generate_finding_id()
        
        evidence = Evidence(
            file_path=relative_path,
            code_snippet=code,
            metrics={"frequency": frequency, "timing": timing}
        )
        
        severity = SeverityLevel.HIGH if frequency > FLASH_THRESHOLDS["max_frequency"] else SeverityLevel.MEDIUM
        
        finding = Finding(
            id=finding_id,
            criterion=CriterionType.SEIZURE_SAFE,
            selector="",
            details=f"JavaScript animation detected: {code}",
            evidence=[evidence],
            severity=severity,
            confidence=ConfidenceLevel.MEDIUM,
            wcag_criterion="2.3.3"
        )
        
        self.findings.append(finding)
    
    def _add_error_finding(self, file_path: str, relative_path: str, error_message: str):
        """Add an error finding."""
        finding_id = generate_finding_id()
        
        evidence = Evidence(
            file_path=relative_path,
            code_snippet="",
            metrics={"error": error_message}
        )
        
        finding = Finding(
            id=finding_id,
            criterion=CriterionType.SEIZURE_SAFE,
            selector="",
            details=f"Error analyzing file: {error_message}",
            evidence=[evidence],
            severity=SeverityLevel.LOW,
            confidence=ConfidenceLevel.LOW,
            wcag_criterion="N/A"
        )
        
        self.findings.append(finding)
    
    def _get_element_selector(self, element) -> str:
        """Get a CSS selector for an element."""
        if element.get('id'):
            return f"#{element['id']}"
        elif element.get('class'):
            classes = element['class']
            if isinstance(classes, list):
                classes = ' '.join(classes)
            return f".{classes.replace(' ', '.')}"
        else:
            return element.name
