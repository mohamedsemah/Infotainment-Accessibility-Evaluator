"""
SeizureSafeAgent - Evaluates seizure safety compliance for WCAG 2.2.
"""

import os
import re
from typing import List, Dict, Any, Optional
from pathlib import Path
from bs4 import BeautifulSoup
import tinycss2
from tinycss2 import parse_stylesheet

from models.schemas import Finding, Evidence, SeverityLevel, ConfidenceLevel, CriterionType
from utils.flash_metrics import analyze_animation_safety, FlashEvent
from utils.wcag_constants import FLASH_THRESHOLDS
from utils.id_gen import generate_finding_id
from services.agents.base_agent import BaseAgent

class SeizureSafeAgent(BaseAgent):
    """Agent responsible for evaluating seizure safety compliance."""
    
    def __init__(self):
        super().__init__(
            name="SeizureSafeAgent",
            description="Evaluates seizure safety compliance for WCAG 2.2",
            criterion=CriterionType.SEIZURE_SAFE,
            wcag_criterion="2.3.1"
        )
        self.findings = []
        self.thresholds = FLASH_THRESHOLDS
    
    async def analyze(self, upload_path: str) -> List[Finding]:
        """Analyze uploaded files for seizure safety issues."""
        self.findings = []
        
        # Find all HTML, CSS, and JavaScript files
        html_files = self._find_files(upload_path, ['.html', '.htm', '.xhtml'])
        css_files = self._find_files(upload_path, ['.css', '.scss', '.sass'])
        js_files = self._find_files(upload_path, ['.js', '.jsx', '.ts', '.tsx'])
        qml_files = self._find_files(upload_path, ['.qml'])
        
        # Analyze HTML files for animations and flashing content
        for html_file in html_files:
            await self._analyze_html_file(html_file, upload_path)
        
        # Analyze CSS files for animations and transitions
        for css_file in css_files:
            await self._analyze_css_file(css_file, upload_path)
        
        # Analyze JavaScript files for animation code
        for js_file in js_files:
            await self._analyze_js_file(js_file, upload_path)
        
        # Analyze QML files for animations
        for qml_file in qml_files:
            await self._analyze_qml_file(qml_file, upload_path)
        
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
        """Analyze HTML file for seizure-inducing content."""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            soup = BeautifulSoup(content, 'html.parser')
            relative_path = os.path.relpath(file_path, upload_path)
            
            # Check for inline styles with animations
            elements_with_animations = soup.find_all(attrs={'style': True})
            for element in elements_with_animations:
                style = element.get('style', '')
                if self._contains_animation(style):
                    await self._check_element_animation(element, style, relative_path, file_path)
            
            # Check for elements with animation classes
            elements_with_animation_classes = soup.find_all(class_=re.compile(r'animate|flash|blink|pulse'))
            for element in elements_with_animation_classes:
                classes = element.get('class', [])
                if isinstance(classes, str):
                    classes = classes.split()
                
                for class_name in classes:
                    if self._is_animation_class(class_name):
                        await self._check_animation_class(element, class_name, relative_path, file_path)
            
            # Check for video elements with autoplay
            video_elements = soup.find_all('video')
            for video in video_elements:
                if video.get('autoplay'):
                    await self._check_autoplay_video(video, relative_path, file_path)
            
            # Check for GIF images (potential seizure risk)
            img_elements = soup.find_all('img')
            for img in img_elements:
                src = img.get('src', '')
                if src.lower().endswith('.gif'):
                    await self._check_gif_image(img, relative_path, file_path)
        
        except Exception as e:
            self._add_error_finding(file_path, relative_path, f"Error analyzing HTML file: {str(e)}")
    
    async def _analyze_css_file(self, file_path: str, upload_path: str):
        """Analyze CSS file for seizure-inducing animations."""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            relative_path = os.path.relpath(file_path, upload_path)
            
            # Parse CSS
            stylesheet = parse_stylesheet(content)
            
            for rule in stylesheet:
                if hasattr(rule, 'prelude') and hasattr(rule, 'content'):
                    # Extract selectors
                    selectors = self._extract_selectors(rule.prelude)
                    
                    # Extract animation properties
                    animation_props = self._extract_animation_properties(rule.content)
                    
                    # Check for seizure-inducing animations
                    if animation_props:
                        await self._check_css_animations(selectors, animation_props, relative_path, file_path)
        
        except Exception as e:
            self._add_error_finding(file_path, relative_path, f"Error analyzing CSS file: {str(e)}")
    
    async def _analyze_js_file(self, file_path: str, upload_path: str):
        """Analyze JavaScript file for animation code."""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            relative_path = os.path.relpath(file_path, upload_path)
            
            # Check for animation-related code patterns
            animation_patterns = [
                r'setInterval\s*\([^,]+,\s*(\d+)',  # setInterval with timing
                r'setTimeout\s*\([^,]+,\s*(\d+)',   # setTimeout with timing
                r'requestAnimationFrame',            # requestAnimationFrame
                r'\.animate\s*\(',                   # jQuery animate
                r'\.transition\s*\(',                # CSS transitions
                r'\.transform\s*\(',                 # CSS transforms
                r'opacity\s*:\s*[\d.]+',            # Opacity changes
                r'visibility\s*:\s*(hidden|visible)', # Visibility changes
            ]
            
            for pattern in animation_patterns:
                matches = re.finditer(pattern, content, re.IGNORECASE)
                for match in matches:
                    await self._check_js_animation(match, pattern, relative_path, file_path)
        
        except Exception as e:
            self._add_error_finding(file_path, relative_path, f"Error analyzing JavaScript file: {str(e)}")
    
    async def _analyze_qml_file(self, file_path: str, upload_path: str):
        """Analyze QML file for animations."""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            relative_path = os.path.relpath(file_path, upload_path)
            
            # Check for QML animation patterns
            animation_patterns = [
                r'NumberAnimation',      # QML NumberAnimation
                r'PropertyAnimation',    # QML PropertyAnimation
                r'SequentialAnimation',  # QML SequentialAnimation
                r'ParallelAnimation',    # QML ParallelAnimation
                r'Animation\s*\{',       # QML Animation blocks
                r'duration\s*:\s*(\d+)', # Animation duration
                r'loops\s*:\s*Animation\.Infinite', # Infinite loops
            ]
            
            for pattern in animation_patterns:
                matches = re.finditer(pattern, content, re.IGNORECASE)
                for match in matches:
                    await self._check_qml_animation(match, pattern, relative_path, file_path)
        
        except Exception as e:
            self._add_error_finding(file_path, relative_path, f"Error analyzing QML file: {str(e)}")
    
    def _contains_animation(self, style: str) -> bool:
        """Check if CSS style contains animation properties."""
        animation_properties = [
            'animation', 'animation-name', 'animation-duration', 'animation-iteration-count',
            'transition', 'transform', 'opacity', 'visibility'
        ]
        
        for prop in animation_properties:
            if prop in style.lower():
                return True
        return False
    
    def _is_animation_class(self, class_name: str) -> bool:
        """Check if CSS class name suggests animation."""
        animation_keywords = [
            'animate', 'animation', 'flash', 'blink', 'pulse', 'fade', 'slide',
            'bounce', 'shake', 'wiggle', 'rotate', 'scale', 'zoom'
        ]
        
        class_lower = class_name.lower()
        for keyword in animation_keywords:
            if keyword in class_lower:
                return True
        return False
    
    def _extract_selectors(self, prelude) -> List[str]:
        """Extract CSS selectors from rule prelude."""
        selectors = []
        
        if isinstance(prelude, list):
            current_selector = ""
            for token in prelude:
                if hasattr(token, 'type'):
                    if token.type == 'ident':
                        if current_selector:
                            current_selector += " " + token.value
                        else:
                            current_selector = token.value
                    elif token.type == 'literal' and token.value == ',':
                        if current_selector:
                            selectors.append(current_selector.strip())
                            current_selector = ""
                    elif token.type == 'whitespace':
                        if current_selector:
                            current_selector += " "
            
            if current_selector:
                selectors.append(current_selector.strip())
        
        return selectors
    
    def _extract_animation_properties(self, content) -> Dict[str, str]:
        """Extract animation-related properties from CSS rule content."""
        animation_props = {}
        
        if isinstance(content, list):
            i = 0
            while i < len(content):
                token = content[i]
                
                if hasattr(token, 'type') and token.type == 'ident':
                    prop_name = token.value
                    
                    if prop_name in [
                        'animation', 'animation-name', 'animation-duration', 
                        'animation-iteration-count', 'animation-timing-function',
                        'transition', 'transition-duration', 'transition-timing-function'
                    ]:
                        # Look for the colon
                        i += 1
                        while i < len(content) and hasattr(content[i], 'type') and content[i].type in ['whitespace', 'literal']:
                            if hasattr(content[i], 'type') and content[i].type == 'literal' and content[i].value == ':':
                                break
                            i += 1
                        
                        # Skip whitespace after colon
                        i += 1
                        while i < len(content) and hasattr(content[i], 'type') and content[i].type == 'whitespace':
                            i += 1
                        
                        # Extract the value
                        if i < len(content):
                            value_token = content[i]
                            if hasattr(value_token, 'value'):
                                animation_props[prop_name] = str(value_token.value)
                
                i += 1
        
        return animation_props
    
    async def _check_element_animation(self, element, style: str, relative_path: str, file_path: str):
        """Check element for seizure-inducing animations."""
        try:
            # Analyze the style for seizure risks
            analysis = analyze_animation_safety(style)
            
            if not analysis["safe"]:
                for violation in analysis["violations"]:
                    self._add_seizure_finding(
                        element, violation, relative_path, file_path, 'inline_style'
                    )
        
        except Exception as e:
            self._add_error_finding(file_path, relative_path, f"Error checking element animation: {str(e)}")
    
    async def _check_animation_class(self, element, class_name: str, relative_path: str, file_path: str):
        """Check animation class for seizure risks."""
        try:
            # Create a mock violation for animation classes
            violation = {
                "type": "animation_class",
                "severity": "medium",
                "description": f"Animation class '{class_name}' may cause seizures",
                "criterion": "2.3.1",
                "frequency": "unknown",
                "duration": "unknown"
            }
            
            self._add_seizure_finding(
                element, violation, relative_path, file_path, 'animation_class'
            )
        
        except Exception as e:
            self._add_error_finding(file_path, relative_path, f"Error checking animation class: {str(e)}")
    
    async def _check_autoplay_video(self, video_element, relative_path: str, file_path: str):
        """Check autoplay video for seizure risks."""
        try:
            violation = {
                "type": "autoplay_video",
                "severity": "high",
                "description": "Autoplay video may cause seizures",
                "criterion": "2.3.1",
                "frequency": "unknown",
                "duration": "unknown"
            }
            
            self._add_seizure_finding(
                video_element, violation, relative_path, file_path, 'autoplay_video'
            )
        
        except Exception as e:
            self._add_error_finding(file_path, relative_path, f"Error checking autoplay video: {str(e)}")
    
    async def _check_gif_image(self, img_element, relative_path: str, file_path: str):
        """Check GIF image for seizure risks."""
        try:
            violation = {
                "type": "gif_image",
                "severity": "medium",
                "description": "Animated GIF may cause seizures",
                "criterion": "2.3.1",
                "frequency": "unknown",
                "duration": "unknown"
            }
            
            self._add_seizure_finding(
                img_element, violation, relative_path, file_path, 'gif_image'
            )
        
        except Exception as e:
            self._add_error_finding(file_path, relative_path, f"Error checking GIF image: {str(e)}")
    
    async def _check_css_animations(self, selectors: List[str], animation_props: Dict[str, str], relative_path: str, file_path: str):
        """Check CSS animations for seizure risks."""
        try:
            # Analyze animation properties
            duration = animation_props.get('animation-duration', '0s')
            iteration_count = animation_props.get('animation-iteration-count', '1')
            
            # Check for infinite animations
            if iteration_count == 'infinite':
                violation = {
                    "type": "infinite_animation",
                    "severity": "high",
                    "description": "Infinite animation may cause seizures",
                    "criterion": "2.3.1",
                    "frequency": "continuous",
                    "duration": duration
                }
                
                for selector in selectors:
                    self._add_css_seizure_finding(
                        selector, violation, relative_path, file_path
                    )
        
        except Exception as e:
            self._add_error_finding(file_path, relative_path, f"Error checking CSS animations: {str(e)}")
    
    async def _check_js_animation(self, match, pattern: str, relative_path: str, file_path: str):
        """Check JavaScript animation for seizure risks."""
        try:
            # Extract timing information if available
            timing_match = re.search(r'(\d+)', match.group(0))
            timing = int(timing_match.group(1)) if timing_match else 0
            
            # Check for rapid animations (less than 500ms)
            if timing > 0 and timing < 500:
                violation = {
                    "type": "rapid_animation",
                    "severity": "high",
                    "description": f"Rapid animation with {timing}ms timing may cause seizures",
                    "criterion": "2.3.1",
                    "frequency": f"{1000/timing:.1f}Hz",
                    "duration": f"{timing}ms"
                }
                
                self._add_js_seizure_finding(
                    match.group(0), violation, relative_path, file_path
                )
        
        except Exception as e:
            self._add_error_finding(file_path, relative_path, f"Error checking JavaScript animation: {str(e)}")
    
    async def _check_qml_animation(self, match, pattern: str, relative_path: str, file_path: str):
        """Check QML animation for seizure risks."""
        try:
            # Check for infinite loops
            if 'Infinite' in match.group(0):
                violation = {
                    "type": "infinite_qml_animation",
                    "severity": "high",
                    "description": "Infinite QML animation may cause seizures",
                    "criterion": "2.3.1",
                    "frequency": "continuous",
                    "duration": "unknown"
                }
                
                self._add_qml_seizure_finding(
                    match.group(0), violation, relative_path, file_path
                )
        
        except Exception as e:
            self._add_error_finding(file_path, relative_path, f"Error checking QML animation: {str(e)}")
    
    def _add_seizure_finding(self, element, violation: Dict[str, Any], relative_path: str, file_path: str, element_type: str):
        """Add a seizure safety finding."""
        finding_id = generate_finding_id()
        
        # Determine severity
        if violation["severity"] == "high":
            severity = SeverityLevel.HIGH
        elif violation["severity"] == "medium":
            severity = SeverityLevel.MEDIUM
        else:
            severity = SeverityLevel.LOW
        
        # Create evidence
        evidence = Evidence(
            file_path=relative_path,
            code_snippet=str(element),
            metrics=violation
        )
        
        # Create finding
        finding = Finding(
            id=finding_id,
            criterion=CriterionType.SEIZURE_SAFE,
            selector=self._get_element_selector(element),
            component_id=element.get('id', ''),
            details=violation["description"],
            evidence=[evidence],
            severity=severity,
            confidence=ConfidenceLevel.HIGH,
            wcag_criterion=violation["criterion"]
        )
        
        self.findings.append(finding)
    
    def _add_css_seizure_finding(self, selector: str, violation: Dict[str, Any], relative_path: str, file_path: str):
        """Add a CSS seizure safety finding."""
        finding_id = generate_finding_id()
        
        # Determine severity
        if violation["severity"] == "high":
            severity = SeverityLevel.HIGH
        elif violation["severity"] == "medium":
            severity = SeverityLevel.MEDIUM
        else:
            severity = SeverityLevel.LOW
        
        # Create evidence
        evidence = Evidence(
            file_path=relative_path,
            code_snippet=f"selector: {selector}",
            metrics=violation
        )
        
        # Create finding
        finding = Finding(
            id=finding_id,
            criterion=CriterionType.SEIZURE_SAFE,
            selector=selector,
            details=violation["description"],
            evidence=[evidence],
            severity=severity,
            confidence=ConfidenceLevel.HIGH,
            wcag_criterion=violation["criterion"]
        )
        
        self.findings.append(finding)
    
    def _add_js_seizure_finding(self, code_snippet: str, violation: Dict[str, Any], relative_path: str, file_path: str):
        """Add a JavaScript seizure safety finding."""
        finding_id = generate_finding_id()
        
        # Determine severity
        if violation["severity"] == "high":
            severity = SeverityLevel.HIGH
        elif violation["severity"] == "medium":
            severity = SeverityLevel.MEDIUM
        else:
            severity = SeverityLevel.LOW
        
        # Create evidence
        evidence = Evidence(
            file_path=relative_path,
            code_snippet=code_snippet,
            metrics=violation
        )
        
        # Create finding
        finding = Finding(
            id=finding_id,
            criterion=CriterionType.SEIZURE_SAFE,
            selector="javascript",
            details=violation["description"],
            evidence=[evidence],
            severity=severity,
            confidence=ConfidenceLevel.HIGH,
            wcag_criterion=violation["criterion"]
        )
        
        self.findings.append(finding)
    
    def _add_qml_seizure_finding(self, code_snippet: str, violation: Dict[str, Any], relative_path: str, file_path: str):
        """Add a QML seizure safety finding."""
        finding_id = generate_finding_id()
        
        # Determine severity
        if violation["severity"] == "high":
            severity = SeverityLevel.HIGH
        elif violation["severity"] == "medium":
            severity = SeverityLevel.MEDIUM
        else:
            severity = SeverityLevel.LOW
        
        # Create evidence
        evidence = Evidence(
            file_path=relative_path,
            code_snippet=code_snippet,
            metrics=violation
        )
        
        # Create finding
        finding = Finding(
            id=finding_id,
            criterion=CriterionType.SEIZURE_SAFE,
            selector="qml",
            details=violation["description"],
            evidence=[evidence],
            severity=severity,
            confidence=ConfidenceLevel.HIGH,
            wcag_criterion=violation["criterion"]
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
