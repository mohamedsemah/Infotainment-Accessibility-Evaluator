"""
Flash and animation detection utilities for seizure safety evaluation.
"""

import re
import math
from typing import List, Dict, Any, Tuple, Optional
from dataclasses import dataclass
from .wcag_constants import FLASH_THRESHOLDS

@dataclass
class FlashEvent:
    """Represents a flash event with timing and intensity data."""
    start_time: float
    end_time: float
    frequency: float
    intensity: float
    area_ratio: float
    luminance_change: float
    is_dangerous: bool

@dataclass
class AnimationFrame:
    """Represents a single frame of an animation."""
    timestamp: float
    properties: Dict[str, Any]
    luminance: float
    opacity: float

class FlashDetector:
    """Detects and analyzes flash patterns in CSS animations and media."""
    
    def __init__(self):
        self.flash_threshold = FLASH_THRESHOLDS["max_frequency"]
        self.dangerous_threshold = FLASH_THRESHOLDS["dangerous_frequency"]
        self.safe_threshold = FLASH_THRESHOLDS["safe_frequency"]
    
    def detect_css_flashes(self, css_content: str) -> List[FlashEvent]:
        """Detect flash patterns in CSS animations and transitions."""
        flashes = []
        
        # Find keyframe animations
        keyframe_pattern = r'@keyframes\s+(\w+)\s*\{([^}]+)\}'
        keyframe_matches = re.finditer(keyframe_pattern, css_content, re.IGNORECASE | re.DOTALL)
        
        for match in keyframe_matches:
            animation_name = match.group(1)
            keyframe_content = match.group(2)
            
            # Analyze keyframes for flash patterns
            keyframe_flashes = self._analyze_keyframes(animation_name, keyframe_content)
            flashes.extend(keyframe_flashes)
        
        # Find animation properties
        animation_pattern = r'animation\s*:\s*([^;]+)'
        animation_matches = re.finditer(animation_pattern, css_content, re.IGNORECASE)
        
        for match in animation_matches:
            animation_value = match.group(1)
            animation_flashes = self._analyze_animation_property(animation_value)
            flashes.extend(animation_flashes)
        
        return flashes
    
    def _analyze_keyframes(self, animation_name: str, keyframe_content: str) -> List[FlashEvent]:
        """Analyze keyframe content for flash patterns."""
        flashes = []
        
        # Parse keyframe steps
        keyframe_steps = re.findall(r'(\d+(?:\.\d+)?%?)\s*\{([^}]+)\}', keyframe_content)
        
        if len(keyframe_steps) < 2:
            return flashes
        
        # Convert to time-based frames
        frames = []
        for step, properties in keyframe_steps:
            # Convert percentage to time (assuming 1 second duration for now)
            if step.endswith('%'):
                time = float(step[:-1]) / 100.0
            else:
                time = float(step)
            
            # Extract luminance and opacity changes
            luminance = self._extract_luminance(properties)
            opacity = self._extract_opacity(properties)
            
            frames.append(AnimationFrame(time, properties, luminance, opacity))
        
        # Sort frames by time
        frames.sort(key=lambda f: f.timestamp)
        
        # Detect flash patterns
        for i in range(len(frames) - 1):
            current_frame = frames[i]
            next_frame = frames[i + 1]
            
            # Calculate luminance change
            luminance_change = abs(next_frame.luminance - current_frame.luminance)
            
            # Calculate frequency (simplified)
            time_diff = next_frame.timestamp - current_frame.timestamp
            if time_diff > 0:
                frequency = 1.0 / time_diff
            else:
                continue
            
            # Check if this constitutes a flash
            if luminance_change > 0.1 and frequency > self.safe_threshold:  # 10% luminance change threshold
                flash = FlashEvent(
                    start_time=current_frame.timestamp,
                    end_time=next_frame.timestamp,
                    frequency=frequency,
                    intensity=luminance_change,
                    area_ratio=1.0,  # Assume full area for CSS animations
                    luminance_change=luminance_change,
                    is_dangerous=frequency > self.dangerous_threshold
                )
                flashes.append(flash)
        
        return flashes
    
    def _analyze_animation_property(self, animation_value: str) -> List[FlashEvent]:
        """Analyze animation property for potential flash patterns."""
        flashes = []
        
        # Parse animation components
        components = [comp.strip() for comp in animation_value.split()]
        
        # Look for duration and iteration count
        duration = 1.0  # Default duration
        iteration_count = 1  # Default iteration count
        
        for component in components:
            if component.endswith('s') or component.endswith('ms'):
                try:
                    if component.endswith('ms'):
                        duration = float(component[:-2]) / 1000.0
                    else:
                        duration = float(component[:-1])
                except ValueError:
                    pass
            elif component.isdigit() or component == 'infinite':
                if component == 'infinite':
                    iteration_count = float('inf')
                else:
                    iteration_count = float(component)
        
        # Calculate effective frequency
        if duration > 0 and iteration_count > 0:
            effective_frequency = iteration_count / duration
            
            if effective_frequency > self.safe_threshold:
                flash = FlashEvent(
                    start_time=0.0,
                    end_time=duration,
                    frequency=effective_frequency,
                    intensity=0.5,  # Default intensity
                    area_ratio=1.0,
                    luminance_change=0.5,
                    is_dangerous=effective_frequency > self.dangerous_threshold
                )
                flashes.append(flash)
        
        return flashes
    
    def _extract_luminance(self, properties: str) -> float:
        """Extract luminance value from CSS properties."""
        # Look for color properties
        color_pattern = r'(?:color|background-color|border-color|outline-color)\s*:\s*([^;]+)'
        color_match = re.search(color_pattern, properties, re.IGNORECASE)
        
        if color_match:
            color_value = color_match.group(1).strip()
            # Convert color to luminance (simplified)
            return self._color_to_luminance(color_value)
        
        return 0.5  # Default luminance
    
    def _extract_opacity(self, properties: str) -> float:
        """Extract opacity value from CSS properties."""
        opacity_pattern = r'opacity\s*:\s*([^;]+)'
        opacity_match = re.search(opacity_pattern, properties, re.IGNORECASE)
        
        if opacity_match:
            try:
                return float(opacity_match.group(1).strip())
            except ValueError:
                pass
        
        return 1.0  # Default opacity
    
    def _color_to_luminance(self, color_value: str) -> float:
        """Convert CSS color value to relative luminance."""
        # This is a simplified implementation
        # In practice, you'd use the full color parsing and luminance calculation
        
        # Handle common color names
        color_map = {
            'black': 0.0,
            'white': 1.0,
            'red': 0.3,
            'green': 0.6,
            'blue': 0.1,
            'yellow': 0.9,
            'cyan': 0.7,
            'magenta': 0.4,
            'gray': 0.5,
            'grey': 0.5,
            'silver': 0.8,
            'maroon': 0.2,
            'olive': 0.4,
            'lime': 0.8,
            'aqua': 0.7,
            'teal': 0.3,
            'navy': 0.1,
            'fuchsia': 0.5,
            'purple': 0.3,
            'orange': 0.6,
            'pink': 0.8,
            'brown': 0.2
        }
        
        color_value = color_value.lower().strip()
        
        if color_value in color_map:
            return color_map[color_value]
        
        # Handle hex colors (simplified)
        if color_value.startswith('#'):
            try:
                hex_color = color_value[1:]
                if len(hex_color) == 3:
                    hex_color = ''.join([c*2 for c in hex_color])
                
                r = int(hex_color[0:2], 16) / 255.0
                g = int(hex_color[2:4], 16) / 255.0
                b = int(hex_color[4:6], 16) / 255.0
                
                # Simple luminance calculation
                return 0.299 * r + 0.587 * g + 0.114 * b
            except ValueError:
                pass
        
        return 0.5  # Default luminance
    
    def detect_media_flashes(self, media_path: str) -> List[FlashEvent]:
        """Detect flash patterns in media files (images, videos)."""
        # This would require image/video processing libraries
        # For now, return empty list
        return []
    
    def analyze_flash_safety(self, flashes: List[FlashEvent]) -> Dict[str, Any]:
        """Analyze flash events for safety compliance."""
        if not flashes:
            return {
                "safe": True,
                "violations": [],
                "recommendations": [],
                "max_frequency": 0.0,
                "dangerous_flashes": 0
            }
        
        violations = []
        recommendations = []
        max_frequency = max(flash.frequency for flash in flashes)
        dangerous_flashes = sum(1 for flash in flashes if flash.is_dangerous)
        
        # Check WCAG 2.3.1 (Three Flashes or Below Threshold)
        if max_frequency > self.flash_threshold:
            violations.append({
                "criterion": "2.3.1",
                "description": f"Animation exceeds 3 flashes per second (found {max_frequency:.1f} Hz)",
                "severity": "high"
            })
            recommendations.append({
                "type": "reduce_frequency",
                "description": "Reduce animation frequency to 3 Hz or below",
                "implementation": "Adjust animation duration or iteration count"
            })
        
        # Check for dangerous flash patterns
        if dangerous_flashes > 0:
            violations.append({
                "criterion": "2.3.2",
                "description": f"Found {dangerous_flashes} dangerous flash patterns",
                "severity": "critical"
            })
            recommendations.append({
                "type": "add_controls",
                "description": "Add pause/stop controls for animations",
                "implementation": "Implement prefers-reduced-motion media query"
            })
        
        # General recommendations
        if max_frequency > self.safe_threshold:
            recommendations.append({
                "type": "prefers_reduced_motion",
                "description": "Respect user's motion preferences",
                "implementation": "@media (prefers-reduced-motion: reduce) { animation: none; }"
            })
        
        return {
            "safe": len(violations) == 0,
            "violations": violations,
            "recommendations": recommendations,
            "max_frequency": max_frequency,
            "dangerous_flashes": dangerous_flashes,
            "total_flashes": len(flashes)
        }
    
    def generate_safe_alternatives(self, flashes: List[FlashEvent]) -> List[Dict[str, str]]:
        """Generate safe alternatives for flash patterns."""
        alternatives = []
        
        for flash in flashes:
            if flash.is_dangerous or flash.frequency > self.flash_threshold:
                # Calculate safe duration
                safe_duration = 1.0 / self.safe_threshold
                
                alternatives.append({
                    "original_frequency": f"{flash.frequency:.1f} Hz",
                    "safe_frequency": f"{self.safe_threshold} Hz",
                    "safe_duration": f"{safe_duration:.1f}s",
                    "css_fix": f"animation-duration: {safe_duration:.1f}s;",
                    "media_query": "@media (prefers-reduced-motion: reduce) { animation: none; }"
                })
        
        return alternatives

def detect_animation_flashes(css_content: str) -> List[FlashEvent]:
    """Convenience function to detect flashes in CSS content."""
    detector = FlashDetector()
    return detector.detect_css_flashes(css_content)

def analyze_animation_safety(css_content: str) -> Dict[str, Any]:
    """Convenience function to analyze animation safety."""
    detector = FlashDetector()
    flashes = detector.detect_css_flashes(css_content)
    return detector.analyze_flash_safety(flashes)
