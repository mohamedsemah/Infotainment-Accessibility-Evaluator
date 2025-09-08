"""
Contrast patcher for generating color contrast fixes.
"""

import os
import re
from typing import List, Dict, Any, Optional
from pathlib import Path
from bs4 import BeautifulSoup
import tinycss2
from tinycss2 import parse_stylesheet

from models.schemas import Cluster, Patch, PatchType, ConfidenceLevel
from utils.color_math import parse_css_color, RGB
from utils.contrast_ratio import calculate_contrast_ratio
from utils.id_gen import generate_patch_id

class ContrastPatcher:
    """Service for generating contrast-related patches."""
    
    def __init__(self):
        self.minimum_contrast_ratio = 4.5  # WCAG AA standard
        self.large_text_contrast_ratio = 3.0  # WCAG AA for large text
    
    async def generate_patches(self, cluster: Cluster, upload_path: str) -> List[Patch]:
        """Generate contrast patches for a cluster."""
        patches = []
        
        try:
            # Analyze the cluster to determine the best fix approach
            analysis = await self._analyze_cluster(cluster, upload_path)
            
            if analysis["approach"] == "css_color_update":
                patches.extend(await self._generate_css_color_patches(cluster, upload_path, analysis))
            elif analysis["approach"] == "css_variable_update":
                patches.extend(await self._generate_css_variable_patches(cluster, upload_path, analysis))
            elif analysis["approach"] == "html_style_update":
                patches.extend(await self._generate_html_style_patches(cluster, upload_path, analysis))
            else:
                # Fallback to generic contrast fix
                patches.extend(await self._generate_generic_contrast_patches(cluster, upload_path))
            
        except Exception as e:
            print(f"Error generating contrast patches: {e}")
            # Create error patch
            error_patch = Patch(
                id=generate_patch_id(),
                type=PatchType.CSS_UPDATE,
                file_path="",
                diff=f"/* Error generating contrast patch: {str(e)} */",
                rationale=f"Failed to generate contrast patch: {str(e)}",
                risks=[f"Patch generation failed: {str(e)}"],
                confidence=ConfidenceLevel.LOW
            )
            patches.append(error_patch)
        
        return patches
    
    async def _analyze_cluster(self, cluster: Cluster, upload_path: str) -> Dict[str, Any]:
        """Analyze cluster to determine the best fix approach."""
        analysis = {
            "approach": "generic",
            "files": [],
            "color_issues": [],
            "css_files": [],
            "html_files": []
        }
        
        # Analyze findings in the cluster
        for cluster_finding in cluster.cluster_findings:
            finding = cluster_finding.finding
            
            # Get file information
            if finding.evidence:
                file_path = finding.evidence[0].file_path
                analysis["files"].append(file_path)
                
                # Check file type
                if file_path.endswith(('.css', '.scss', '.sass')):
                    analysis["css_files"].append(file_path)
                elif file_path.endswith(('.html', '.htm', '.xhtml')):
                    analysis["html_files"].append(file_path)
                
                # Extract color information
                if finding.evidence[0].metrics:
                    metrics = finding.evidence[0].metrics
                    if "foreground_color" in metrics and "background_color" in metrics:
                        analysis["color_issues"].append({
                            "foreground": metrics["foreground_color"],
                            "background": metrics["background_color"],
                            "ratio": metrics.get("ratio", 0),
                            "file": file_path
                        })
        
        # Determine the best approach
        if analysis["css_files"]:
            analysis["approach"] = "css_color_update"
        elif analysis["html_files"]:
            analysis["approach"] = "html_style_update"
        else:
            analysis["approach"] = "generic"
        
        return analysis
    
    async def _generate_css_color_patches(self, cluster: Cluster, upload_path: str, analysis: Dict[str, Any]) -> List[Patch]:
        """Generate CSS color update patches."""
        patches = []
        
        for css_file in analysis["css_files"]:
            try:
                file_path = os.path.join(upload_path, css_file)
                
                if not os.path.exists(file_path):
                    continue
                
                # Read the CSS file
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Parse CSS
                stylesheet = parse_stylesheet(content)
                
                # Find color issues in this file
                file_color_issues = [issue for issue in analysis["color_issues"] if issue["file"] == css_file]
                
                if not file_color_issues:
                    continue
                
                # Generate patches for each color issue
                for issue in file_color_issues:
                    patch = await self._create_css_color_patch(
                        issue, css_file, content, stylesheet
                    )
                    if patch:
                        patches.append(patch)
                
            except Exception as e:
                print(f"Error processing CSS file {css_file}: {e}")
                continue
        
        return patches
    
    async def _create_css_color_patch(self, issue: Dict[str, Any], file_path: str, content: str, stylesheet) -> Optional[Patch]:
        """Create a CSS color patch for a specific issue."""
        try:
            foreground_color = issue["foreground"]
            background_color = issue["background"]
            current_ratio = issue["ratio"]
            
            # Calculate required contrast ratio
            required_ratio = self.minimum_contrast_ratio
            
            # Generate improved colors
            improved_colors = await self._generate_improved_colors(
                foreground_color, background_color, required_ratio
            )
            
            if not improved_colors:
                return None
            
            # Create the patch
            patch_id = generate_patch_id()
            
            # Generate CSS diff
            diff = self._generate_css_color_diff(improved_colors)
            
            patch = Patch(
                id=patch_id,
                type=PatchType.CSS_UPDATE,
                file_path=file_path,
                diff=diff,
                rationale=f"Fix color contrast ratio from {current_ratio:.1f}:1 to {improved_colors['new_ratio']:.1f}:1",
                risks=["May affect visual design", "Test in different lighting conditions"],
                confidence=ConfidenceLevel.HIGH
            )
            
            return patch
            
        except Exception as e:
            print(f"Error creating CSS color patch: {e}")
            return None
    
    async def _generate_improved_colors(self, fg_color: str, bg_color: str, required_ratio: float) -> Optional[Dict[str, Any]]:
        """Generate improved colors that meet contrast requirements."""
        try:
            # Parse colors
            fg_rgb = parse_css_color(fg_color)
            bg_rgb = parse_css_color(bg_color)
            
            if not fg_rgb or not bg_rgb:
                return None
            
            # Try different approaches to improve contrast
            approaches = [
                self._darken_foreground,
                self._lighten_background,
                self._invert_colors,
                self._use_high_contrast_colors
            ]
            
            for approach in approaches:
                result = approach(fg_rgb, bg_rgb, required_ratio)
                if result:
                    return result
            
            return None
            
        except Exception as e:
            print(f"Error generating improved colors: {e}")
            return None
    
    def _darken_foreground(self, fg_rgb: RGB, bg_rgb: RGB, required_ratio: float) -> Optional[Dict[str, Any]]:
        """Try darkening the foreground color."""
        # Darken the foreground color
        new_fg = RGB(
            max(0, fg_rgb.r - 50),
            max(0, fg_rgb.g - 50),
            max(0, fg_rgb.b - 50)
        )
        
        new_ratio = calculate_contrast_ratio(new_fg, bg_rgb)
        
        if new_ratio >= required_ratio:
            return {
                "foreground": new_fg.to_hex(),
                "background": bg_rgb.to_hex(),
                "new_ratio": new_ratio,
                "approach": "darken_foreground"
            }
        
        return None
    
    def _lighten_background(self, fg_rgb: RGB, bg_rgb: RGB, required_ratio: float) -> Optional[Dict[str, Any]]:
        """Try lightening the background color."""
        # Lighten the background color
        new_bg = RGB(
            min(255, bg_rgb.r + 50),
            min(255, bg_rgb.g + 50),
            min(255, bg_rgb.b + 50)
        )
        
        new_ratio = calculate_contrast_ratio(fg_rgb, new_bg)
        
        if new_ratio >= required_ratio:
            return {
                "foreground": fg_rgb.to_hex(),
                "background": new_bg.to_hex(),
                "new_ratio": new_ratio,
                "approach": "lighten_background"
            }
        
        return None
    
    def _invert_colors(self, fg_rgb: RGB, bg_rgb: RGB, required_ratio: float) -> Optional[Dict[str, Any]]:
        """Try inverting the colors."""
        # Invert the colors
        new_fg = RGB(255 - bg_rgb.r, 255 - bg_rgb.g, 255 - bg_rgb.b)
        new_bg = RGB(255 - fg_rgb.r, 255 - fg_rgb.g, 255 - fg_rgb.b)
        
        new_ratio = calculate_contrast_ratio(new_fg, new_bg)
        
        if new_ratio >= required_ratio:
            return {
                "foreground": new_fg.to_hex(),
                "background": new_bg.to_hex(),
                "new_ratio": new_ratio,
                "approach": "invert_colors"
            }
        
        return None
    
    def _use_high_contrast_colors(self, fg_rgb: RGB, bg_rgb: RGB, required_ratio: float) -> Optional[Dict[str, Any]]:
        """Use high contrast colors (black/white)."""
        # Use high contrast colors
        new_fg = RGB(0, 0, 0)  # Black
        new_bg = RGB(255, 255, 255)  # White
        
        new_ratio = calculate_contrast_ratio(new_fg, new_bg)
        
        if new_ratio >= required_ratio:
            return {
                "foreground": new_fg.to_hex(),
                "background": new_bg.to_hex(),
                "new_ratio": new_ratio,
                "approach": "high_contrast"
            }
        
        return None
    
    def _generate_css_color_diff(self, improved_colors: Dict[str, Any]) -> str:
        """Generate CSS diff for color improvements."""
        approach = improved_colors["approach"]
        
        if approach == "darken_foreground":
            return f"""
/* Fix color contrast - darken foreground */
color: {improved_colors["foreground"]};
"""
        elif approach == "lighten_background":
            return f"""
/* Fix color contrast - lighten background */
background-color: {improved_colors["background"]};
"""
        elif approach == "invert_colors":
            return f"""
/* Fix color contrast - invert colors */
color: {improved_colors["foreground"]};
background-color: {improved_colors["background"]};
"""
        elif approach == "high_contrast":
            return f"""
/* Fix color contrast - use high contrast colors */
color: {improved_colors["foreground"]};
background-color: {improved_colors["background"]};
"""
        else:
            return f"""
/* Fix color contrast */
color: {improved_colors["foreground"]};
background-color: {improved_colors["background"]};
"""
    
    async def _generate_css_variable_patches(self, cluster: Cluster, upload_path: str, analysis: Dict[str, Any]) -> List[Patch]:
        """Generate CSS variable update patches."""
        patches = []
        
        # This would involve updating CSS custom properties
        # For now, fall back to generic patches
        return await self._generate_generic_contrast_patches(cluster, upload_path)
    
    async def _generate_html_style_patches(self, cluster: Cluster, upload_path: str, analysis: Dict[str, Any]) -> List[Patch]:
        """Generate HTML style update patches."""
        patches = []
        
        for html_file in analysis["html_files"]:
            try:
                file_path = os.path.join(upload_path, html_file)
                
                if not os.path.exists(file_path):
                    continue
                
                # Read the HTML file
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Parse HTML
                soup = BeautifulSoup(content, 'html.parser')
                
                # Find color issues in this file
                file_color_issues = [issue for issue in analysis["color_issues"] if issue["file"] == html_file]
                
                if not file_color_issues:
                    continue
                
                # Generate patches for each color issue
                for issue in file_color_issues:
                    patch = await self._create_html_style_patch(
                        issue, html_file, content, soup
                    )
                    if patch:
                        patches.append(patch)
                
            except Exception as e:
                print(f"Error processing HTML file {html_file}: {e}")
                continue
        
        return patches
    
    async def _create_html_style_patch(self, issue: Dict[str, Any], file_path: str, content: str, soup: BeautifulSoup) -> Optional[Patch]:
        """Create an HTML style patch for a specific issue."""
        try:
            foreground_color = issue["foreground"]
            background_color = issue["background"]
            current_ratio = issue["ratio"]
            
            # Calculate required contrast ratio
            required_ratio = self.minimum_contrast_ratio
            
            # Generate improved colors
            improved_colors = await self._generate_improved_colors(
                foreground_color, background_color, required_ratio
            )
            
            if not improved_colors:
                return None
            
            # Create the patch
            patch_id = generate_patch_id()
            
            # Generate HTML diff
            diff = self._generate_html_style_diff(improved_colors)
            
            patch = Patch(
                id=patch_id,
                type=PatchType.HTML_UPDATE,
                file_path=file_path,
                diff=diff,
                rationale=f"Fix color contrast ratio from {current_ratio:.1f}:1 to {improved_colors['new_ratio']:.1f}:1",
                risks=["May affect visual design", "Test in different lighting conditions"],
                confidence=ConfidenceLevel.HIGH
            )
            
            return patch
            
        except Exception as e:
            print(f"Error creating HTML style patch: {e}")
            return None
    
    def _generate_html_style_diff(self, improved_colors: Dict[str, Any]) -> str:
        """Generate HTML diff for style improvements."""
        return f"""
<!-- Fix color contrast -->
<style>
    .contrast-fix {{
        color: {improved_colors["foreground"]};
        background-color: {improved_colors["background"]};
    }}
</style>
"""
    
    async def _generate_generic_contrast_patches(self, cluster: Cluster, upload_path: str) -> List[Patch]:
        """Generate generic contrast patches."""
        patches = []
        
        # Create a generic contrast fix patch
        patch_id = generate_patch_id()
        
        # Find the first file in the cluster
        file_path = ""
        if cluster.cluster_findings:
            first_finding = cluster.cluster_findings[0].finding
            if first_finding.evidence:
                file_path = first_finding.evidence[0].file_path
        
        # Create generic patch
        patch = Patch(
            id=patch_id,
            type=PatchType.CSS_UPDATE,
            file_path=file_path,
            diff="""
/* Generic contrast fix - manual review required */
.contrast-fix {
    color: #000000;
    background-color: #ffffff;
    /* Ensure contrast ratio is at least 4.5:1 */
}
""",
            rationale=f"Generic contrast fix for {cluster.summary}",
            risks=["Generic patch - manual review required", "May affect visual design"],
            confidence=ConfidenceLevel.LOW
        )
        
        patches.append(patch)
        return patches

