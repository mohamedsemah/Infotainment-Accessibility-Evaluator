"""
Main patch generator service for creating accessibility fixes.
"""

import os
import re
from typing import List, Dict, Any, Optional
from pathlib import Path
from bs4 import BeautifulSoup
import tinycss2
from tinycss2 import parse_stylesheet

from models.schemas import Finding, Cluster, Patch, PatchType, ConfidenceLevel
from services.patching.contrast_patcher import ContrastPatcher
from services.patching.aria_patcher import ARIAPatcher
from services.patching.language_patcher import LanguagePatcher
from services.patching.seizure_patcher import SeizurePatcher
from utils.id_gen import generate_patch_id

class PatchGenerator:
    """Main service for generating accessibility patches."""
    
    def __init__(self):
        self.contrast_patcher = ContrastPatcher()
        self.aria_patcher = ARIAPatcher()
        self.language_patcher = LanguagePatcher()
        self.seizure_patcher = SeizurePatcher()
    
    async def generate_patches(self, clusters: List[Cluster], upload_path: str) -> List[Patch]:
        """Generate patches for clusters of findings."""
        patches = []
        
        for cluster in clusters:
            try:
                # Generate patches based on cluster type
                if cluster.criterion.value == "contrast":
                    cluster_patches = await self.contrast_patcher.generate_patches(cluster, upload_path)
                elif cluster.criterion.value == "aria":
                    cluster_patches = await self.aria_patcher.generate_patches(cluster, upload_path)
                elif cluster.criterion.value == "language":
                    cluster_patches = await self.language_patcher.generate_patches(cluster, upload_path)
                elif cluster.criterion.value == "seizure_safe":
                    cluster_patches = await self.seizure_patcher.generate_patches(cluster, upload_path)
                else:
                    # Generic patch generation for other criteria
                    cluster_patches = await self._generate_generic_patches(cluster, upload_path)
                
                patches.extend(cluster_patches)
                
            except Exception as e:
                print(f"Error generating patches for cluster {cluster.id}: {e}")
                # Create error patch
                error_patch = Patch(
                    id=generate_patch_id(),
                    type=PatchType.CONTENT_UPDATE,
                    file_path="",
                    diff=f"# Error generating patch: {str(e)}",
                    rationale=f"Failed to generate patch for cluster {cluster.id}",
                    risks=[f"Patch generation failed: {str(e)}"],
                    confidence=ConfidenceLevel.LOW
                )
                patches.append(error_patch)
        
        return patches
    
    async def _generate_generic_patches(self, cluster: Cluster, upload_path: str) -> List[Patch]:
        """Generate generic patches for unsupported criteria."""
        patches = []
        
        # Create a generic patch based on cluster summary
        patch_id = generate_patch_id()
        
        # Find the first finding to get file information
        if cluster.cluster_findings:
            first_finding = cluster.cluster_findings[0].finding
            file_path = first_finding.evidence[0].file_path if first_finding.evidence else ""
        else:
            file_path = ""
        
        # Create generic patch
        patch = Patch(
            id=patch_id,
            type=PatchType.CONTENT_UPDATE,
            file_path=file_path,
            diff=f"# Generic fix for {cluster.criterion.value} issues\n# {cluster.summary}",
            rationale=f"Generic fix for {cluster.criterion.value} issues: {cluster.summary}",
            risks=["Generic patch - manual review required"],
            confidence=ConfidenceLevel.LOW
        )
        
        patches.append(patch)
        return patches
    
    async def validate_patch(self, patch: Patch, upload_path: str) -> bool:
        """Validate that a patch can be applied safely."""
        try:
            file_path = os.path.join(upload_path, patch.file_path)
            
            if not os.path.exists(file_path):
                return False
            
            # Basic validation based on patch type
            if patch.type == PatchType.CSS_UPDATE:
                return await self._validate_css_patch(patch, file_path)
            elif patch.type == PatchType.HTML_UPDATE:
                return await self._validate_html_patch(patch, file_path)
            elif patch.type == PatchType.ATTRIBUTE_ADD:
                return await self._validate_attribute_add_patch(patch, file_path)
            elif patch.type == PatchType.ATTRIBUTE_REMOVE:
                return await self._validate_attribute_remove_patch(patch, file_path)
            elif patch.type == PatchType.CONTENT_UPDATE:
                return await self._validate_content_patch(patch, file_path)
            
            return True
            
        except Exception as e:
            print(f"Error validating patch {patch.id}: {e}")
            return False
    
    async def _validate_css_patch(self, patch: Patch, file_path: str) -> bool:
        """Validate CSS patch."""
        try:
            # Check if the file is a CSS file
            if not file_path.endswith(('.css', '.scss', '.sass')):
                return False
            
            # Try to parse the CSS to ensure it's valid
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse the existing CSS
            stylesheet = parse_stylesheet(content)
            
            # Check if the patch diff contains valid CSS
            if patch.diff:
                # Simple validation - check for basic CSS syntax
                if ':' in patch.diff and ';' in patch.diff:
                    return True
            
            return False
            
        except Exception as e:
            print(f"Error validating CSS patch: {e}")
            return False
    
    async def _validate_html_patch(self, patch: Patch, file_path: str) -> bool:
        """Validate HTML patch."""
        try:
            # Check if the file is an HTML file
            if not file_path.endswith(('.html', '.htm', '.xhtml')):
                return False
            
            # Try to parse the HTML to ensure it's valid
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            soup = BeautifulSoup(content, 'html.parser')
            
            # Check if the patch diff contains valid HTML
            if patch.diff:
                # Simple validation - check for basic HTML syntax
                if '<' in patch.diff and '>' in patch.diff:
                    return True
            
            return False
            
        except Exception as e:
            print(f"Error validating HTML patch: {e}")
            return False
    
    async def _validate_attribute_add_patch(self, patch: Patch, file_path: str) -> bool:
        """Validate attribute addition patch."""
        try:
            # Check if the file is an HTML file
            if not file_path.endswith(('.html', '.htm', '.xhtml')):
                return False
            
            # Check if the patch diff contains valid attribute syntax
            if patch.diff:
                # Simple validation - check for attribute=value syntax
                if '=' in patch.diff and '"' in patch.diff:
                    return True
            
            return False
            
        except Exception as e:
            print(f"Error validating attribute add patch: {e}")
            return False
    
    async def _validate_attribute_remove_patch(self, patch: Patch, file_path: str) -> bool:
        """Validate attribute removal patch."""
        try:
            # Check if the file is an HTML file
            if not file_path.endswith(('.html', '.htm', '.xhtml')):
                return False
            
            # Check if the patch diff contains valid attribute syntax
            if patch.diff:
                # Simple validation - check for attribute=value syntax
                if '=' in patch.diff and '"' in patch.diff:
                    return True
            
            return False
            
        except Exception as e:
            print(f"Error validating attribute remove patch: {e}")
            return False
    
    async def _validate_content_patch(self, patch: Patch, file_path: str) -> bool:
        """Validate content update patch."""
        try:
            # Check if the file exists
            if not os.path.exists(file_path):
                return False
            
            # Check if the patch diff contains content
            if patch.diff and patch.diff.strip():
                return True
            
            return False
            
        except Exception as e:
            print(f"Error validating content patch: {e}")
            return False
    
    async def get_patch_preview(self, patch: Patch, upload_path: str) -> Dict[str, Any]:
        """Get a preview of what the patch will do."""
        try:
            file_path = os.path.join(upload_path, patch.file_path)
            
            if not os.path.exists(file_path):
                return {"error": "File not found"}
            
            # Read the original file
            with open(file_path, 'r', encoding='utf-8') as f:
                original_content = f.read()
            
            # Generate preview based on patch type
            if patch.type == PatchType.CSS_UPDATE:
                return await self._get_css_patch_preview(patch, original_content)
            elif patch.type == PatchType.HTML_UPDATE:
                return await self._get_html_patch_preview(patch, original_content)
            elif patch.type == PatchType.ATTRIBUTE_ADD:
                return await self._get_attribute_add_patch_preview(patch, original_content)
            elif patch.type == PatchType.ATTRIBUTE_REMOVE:
                return await self._get_attribute_remove_patch_preview(patch, original_content)
            elif patch.type == PatchType.CONTENT_UPDATE:
                return await self._get_content_patch_preview(patch, original_content)
            
            return {"error": "Unknown patch type"}
            
        except Exception as e:
            return {"error": f"Error generating preview: {str(e)}"}
    
    async def _get_css_patch_preview(self, patch: Patch, original_content: str) -> Dict[str, Any]:
        """Get CSS patch preview."""
        return {
            "type": "css_update",
            "original": original_content,
            "patched": original_content + "\n" + patch.diff,
            "changes": [{"type": "addition", "content": patch.diff}]
        }
    
    async def _get_html_patch_preview(self, patch: Patch, original_content: str) -> Dict[str, Any]:
        """Get HTML patch preview."""
        return {
            "type": "html_update",
            "original": original_content,
            "patched": original_content + "\n" + patch.diff,
            "changes": [{"type": "addition", "content": patch.diff}]
        }
    
    async def _get_attribute_add_patch_preview(self, patch: Patch, original_content: str) -> Dict[str, Any]:
        """Get attribute addition patch preview."""
        # Simple preview - add the attribute to the first HTML element
        soup = BeautifulSoup(original_content, 'html.parser')
        first_element = soup.find()
        
        if first_element:
            # Add the attribute
            attr_name, attr_value = patch.diff.split('=', 1)
            first_element[attr_name.strip()] = attr_value.strip().strip('"')
            patched_content = str(soup)
        else:
            patched_content = original_content
        
        return {
            "type": "attribute_add",
            "original": original_content,
            "patched": patched_content,
            "changes": [{"type": "addition", "content": patch.diff}]
        }
    
    async def _get_attribute_remove_patch_preview(self, patch: Patch, original_content: str) -> Dict[str, Any]:
        """Get attribute removal patch preview."""
        # Simple preview - remove the attribute from all elements
        soup = BeautifulSoup(original_content, 'html.parser')
        
        # Find and remove the attribute
        attr_name = patch.diff.split('=')[0].strip()
        elements_with_attr = soup.find_all(attrs={attr_name: True})
        
        for element in elements_with_attr:
            del element[attr_name]
        
        patched_content = str(soup)
        
        return {
            "type": "attribute_remove",
            "original": original_content,
            "patched": patched_content,
            "changes": [{"type": "removal", "content": patch.diff}]
        }
    
    async def _get_content_patch_preview(self, patch: Patch, original_content: str) -> Dict[str, Any]:
        """Get content update patch preview."""
        return {
            "type": "content_update",
            "original": original_content,
            "patched": original_content + "\n" + patch.diff,
            "changes": [{"type": "addition", "content": patch.diff}]
        }

