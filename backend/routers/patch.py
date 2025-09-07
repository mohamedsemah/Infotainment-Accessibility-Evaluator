"""
Patch router for generating and applying accessibility fixes.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Dict, Any, List
import os
import tempfile
import shutil
from pathlib import Path

from models.schemas import Patch, PatchResult, RecheckResult, ErrorResponse
from routers.upload import get_upload_path
from services.sandbox.apply_patches import apply_patches
from services.sandbox.recheck import recheck_accessibility
from utils.id_gen import generate_patch_id

router = APIRouter()

# In-memory storage for patches (in production, use a database)
patches_storage = {}

@router.post("/patch", response_model=PatchResult)
async def generate_patches(
    upload_id: str = Query(..., description="Upload ID to patch"),
    clusters: List[Dict[str, Any]] = None
):
    """Generate patches for accessibility issues."""
    try:
        # Get upload path
        upload_path = get_upload_path(upload_id)
        if not upload_path:
            raise HTTPException(status_code=404, detail="Upload not found")
        
        # Generate patches based on clusters
        patches = await _generate_patches_from_clusters(clusters or [], upload_path)
        
        # Store patches
        patch_result = PatchResult(
            upload_id=upload_id,
            patches=patches,
            total_patches=len(patches),
            safe_patches=len([p for p in patches if not p.risks]),
            risky_patches=len([p for p in patches if p.risks])
        )
        
        patches_storage[upload_id] = patch_result
        
        return patch_result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Patch generation failed",
                "details": str(e)
            }
        )

@router.post("/patch/apply", response_model=Dict[str, Any])
async def apply_patches_to_upload(
    upload_id: str = Query(..., description="Upload ID to patch"),
    patch_ids: List[str] = None
):
    """Apply patches to an upload."""
    try:
        # Get upload path
        upload_path = get_upload_path(upload_id)
        if not upload_path:
            raise HTTPException(status_code=404, detail="Upload not found")
        
        # Get patches
        if upload_id not in patches_storage:
            raise HTTPException(status_code=404, detail="No patches found for upload")
        
        patch_result = patches_storage[upload_id]
        
        # Filter patches if specific IDs provided
        if patch_ids:
            patches_to_apply = [p for p in patch_result.patches if p.id in patch_ids]
        else:
            patches_to_apply = patch_result.patches
        
        # Apply patches
        result = await apply_patches(upload_path, patches_to_apply)
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Patch application failed",
                "details": str(e)
            }
        )

@router.post("/patch/recheck", response_model=RecheckResult)
async def recheck_after_patches(
    upload_id: str = Query(..., description="Upload ID to recheck"),
    patch_ids: List[str] = None
):
    """Recheck accessibility after applying patches."""
    try:
        # Get upload path
        upload_path = get_upload_path(upload_id)
        if not upload_path:
            raise HTTPException(status_code=404, detail="Upload not found")
        
        # Recheck accessibility
        result = await recheck_accessibility(upload_path, patch_ids)
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Recheck failed",
                "details": str(e)
            }
        )

@router.get("/patch/{upload_id}")
async def get_patches(upload_id: str):
    """Get patches for an upload."""
    if upload_id not in patches_storage:
        raise HTTPException(status_code=404, detail="No patches found for upload")
    
    return patches_storage[upload_id]

@router.get("/patch/{upload_id}/{patch_id}")
async def get_patch(upload_id: str, patch_id: str):
    """Get a specific patch."""
    if upload_id not in patches_storage:
        raise HTTPException(status_code=404, detail="No patches found for upload")
    
    patch_result = patches_storage[upload_id]
    patch = next((p for p in patch_result.patches if p.id == patch_id), None)
    
    if not patch:
        raise HTTPException(status_code=404, detail="Patch not found")
    
    return patch

@router.delete("/patch/{upload_id}/{patch_id}")
async def delete_patch(upload_id: str, patch_id: str):
    """Delete a specific patch."""
    if upload_id not in patches_storage:
        raise HTTPException(status_code=404, detail="No patches found for upload")
    
    patch_result = patches_storage[upload_id]
    patch_result.patches = [p for p in patch_result.patches if p.id != patch_id]
    patch_result.total_patches = len(patch_result.patches)
    patch_result.safe_patches = len([p for p in patch_result.patches if not p.risks])
    patch_result.risky_patches = len([p for p in patch_result.patches if p.risks])
    
    return {"message": "Patch deleted successfully"}

@router.post("/patch/{upload_id}/preview")
async def preview_patches(
    upload_id: str,
    patch_ids: List[str] = None
):
    """Preview patches before applying."""
    try:
        # Get upload path
        upload_path = get_upload_path(upload_id)
        if not upload_path:
            raise HTTPException(status_code=404, detail="Upload not found")
        
        # Get patches
        if upload_id not in patches_storage:
            raise HTTPException(status_code=404, detail="No patches found for upload")
        
        patch_result = patches_storage[upload_id]
        
        # Filter patches if specific IDs provided
        if patch_ids:
            patches_to_preview = [p for p in patch_result.patches if p.id in patch_ids]
        else:
            patches_to_preview = patch_result.patches
        
        # Create preview
        preview = await _create_patch_preview(upload_path, patches_to_preview)
        
        return preview
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Patch preview failed",
                "details": str(e)
            }
        )

async def _generate_patches_from_clusters(clusters: List[Dict[str, Any]], upload_path: str) -> List[Patch]:
    """Generate patches from clusters."""
    patches = []
    
    for cluster in clusters:
        # Generate patches based on cluster type
        if cluster.get('criterion') == 'contrast':
            patches.extend(await _generate_contrast_patches(cluster, upload_path))
        elif cluster.get('criterion') == 'seizure_safe':
            patches.extend(await _generate_seizure_patches(cluster, upload_path))
        elif cluster.get('criterion') == 'language':
            patches.extend(await _generate_language_patches(cluster, upload_path))
        elif cluster.get('criterion') == 'aria':
            patches.extend(await _generate_aria_patches(cluster, upload_path))
        elif cluster.get('criterion') == 'state_explorer':
            patches.extend(await _generate_state_patches(cluster, upload_path))
    
    return patches

async def _generate_contrast_patches(cluster: Dict[str, Any], upload_path: str) -> List[Patch]:
    """Generate contrast patches."""
    patches = []
    
    # Extract color information from cluster
    key_components = cluster.get('key', {}).get('key_components', {})
    color_combo = key_components.get('color_combo', '')
    component_id = key_components.get('component_id', '')
    state = key_components.get('state', 'default')
    
    if color_combo and ':' in color_combo:
        fg_color, bg_color = color_combo.split('-', 1)
        
        # Generate CSS patch
        patch_id = generate_patch_id()
        
        css_patch = f"""
/* Fix contrast for {component_id} in {state} state */
{component_id}:{state} {{
    color: {fg_color};
    background-color: {bg_color};
}}

/* Alternative with better contrast */
{component_id}:{state} {{
    color: {_improve_contrast_color(fg_color)};
    background-color: {_improve_contrast_color(bg_color)};
}}
"""
        
        patch = Patch(
            id=patch_id,
            type="css_update",
            file_path="contrast-fixes.css",
            diff=css_patch,
            rationale=f"Fix contrast ratio for {component_id} in {state} state",
            risks=["May affect other elements", "Requires testing across all states"],
            confidence="high"
        )
        
        patches.append(patch)
    
    return patches

async def _generate_seizure_patches(cluster: Dict[str, Any], upload_path: str) -> List[Patch]:
    """Generate seizure safety patches."""
    patches = []
    
    # Extract animation information from cluster
    key_components = cluster.get('key', {}).get('key_components', {})
    animation_type = key_components.get('animation_type', '')
    frequency = key_components.get('frequency', '')
    component_id = key_components.get('component_id', '')
    
    if animation_type and frequency:
        # Generate CSS patch
        patch_id = generate_patch_id()
        
        css_patch = f"""
/* Fix seizure safety for {component_id} */
{component_id} {{
    animation-duration: {_safe_animation_duration(frequency)};
}}

/* Respect user's motion preferences */
@media (prefers-reduced-motion: reduce) {{
    {component_id} {{
        animation: none;
    }}
}}
"""
        
        patch = Patch(
            id=patch_id,
            type="css_update",
            file_path="seizure-fixes.css",
            diff=css_patch,
            rationale=f"Fix seizure safety for {component_id} animation",
            risks=["May affect animation timing", "Requires testing across all states"],
            confidence="high"
        )
        
        patches.append(patch)
    
    return patches

async def _generate_language_patches(cluster: Dict[str, Any], upload_path: str) -> List[Patch]:
    """Generate language patches."""
    patches = []
    
    # Extract language information from cluster
    key_components = cluster.get('key', {}).get('key_components', {})
    lang_value = key_components.get('lang_value', '')
    scope = key_components.get('scope', '')
    
    if lang_value and scope:
        # Generate HTML patch
        patch_id = generate_patch_id()
        
        if scope == 'html':
            html_patch = f'<html lang="{_canonicalize_language_tag(lang_value)}">'
        else:
            html_patch = f'<span lang="{_canonicalize_language_tag(lang_value)}">'
        
        patch = Patch(
            id=patch_id,
            type="html_update",
            file_path="language-fixes.html",
            diff=html_patch,
            rationale=f"Fix language tag for {scope}: {lang_value}",
            risks=["May affect text rendering", "Requires testing across all languages"],
            confidence="medium"
        )
        
        patches.append(patch)
    
    return patches

async def _generate_aria_patches(cluster: Dict[str, Any], upload_path: str) -> List[Patch]:
    """Generate ARIA patches."""
    patches = []
    
    # Extract ARIA information from cluster
    key_components = cluster.get('key', {}).get('key_components', {})
    role = key_components.get('role', '')
    attribute = key_components.get('attribute', '')
    
    if role and attribute:
        # Generate HTML patch
        patch_id = generate_patch_id()
        
        html_patch = f'<div role="{role}" {attribute}="...">'
        
        patch = Patch(
            id=patch_id,
            type="html_update",
            file_path="aria-fixes.html",
            diff=html_patch,
            rationale=f"Fix ARIA {role} role with {attribute} attribute",
            risks=["May affect screen reader experience", "Requires testing with assistive technology"],
            confidence="medium"
        )
        
        patches.append(patch)
    
    return patches

async def _generate_state_patches(cluster: Dict[str, Any], upload_path: str) -> List[Patch]:
    """Generate state patches."""
    patches = []
    
    # Extract state information from cluster
    key_components = cluster.get('key', {}).get('key_components', {})
    component_id = key_components.get('component_id', '')
    state = key_components.get('state', '')
    
    if component_id and state:
        # Generate CSS patch
        patch_id = generate_patch_id()
        
        css_patch = f"""
/* Fix state handling for {component_id} */
{component_id}:{state} {{
    /* Add appropriate state styles */
    outline: 2px solid #007bff;
    outline-offset: 2px;
}}
"""
        
        patch = Patch(
            id=patch_id,
            type="css_update",
            file_path="state-fixes.css",
            diff=css_patch,
            rationale=f"Fix state handling for {component_id} in {state} state",
            risks=["May affect visual appearance", "Requires testing across all states"],
            confidence="medium"
        )
        
        patches.append(patch)
    
    return patches

async def _create_patch_preview(upload_path: str, patches: List[Patch]) -> Dict[str, Any]:
    """Create a preview of patches."""
    preview = {
        "upload_path": upload_path,
        "patches": [],
        "total_changes": 0,
        "files_affected": set()
    }
    
    for patch in patches:
        patch_preview = {
            "id": patch.id,
            "type": patch.type,
            "file_path": patch.file_path,
            "rationale": patch.rationale,
            "risks": patch.risks,
            "confidence": patch.confidence,
            "diff_preview": patch.diff[:200] + "..." if len(patch.diff) > 200 else patch.diff
        }
        
        preview["patches"].append(patch_preview)
        preview["total_changes"] += 1
        preview["files_affected"].add(patch.file_path)
    
    preview["files_affected"] = list(preview["files_affected"])
    
    return preview

def _improve_contrast_color(color: str) -> str:
    """Improve contrast color (simplified)."""
    # This would use the color math utilities to improve contrast
    return color

def _safe_animation_duration(frequency: str) -> str:
    """Get safe animation duration for frequency."""
    try:
        freq = float(frequency)
        if freq > 3.0:
            return "1000ms"  # 1 second for safe frequency
        else:
            return "300ms"   # 300ms for normal frequency
    except ValueError:
        return "300ms"

def _canonicalize_language_tag(lang: str) -> str:
    """Canonicalize language tag (simplified)."""
    # This would use the BCP-47 utilities
    return lang.lower()
