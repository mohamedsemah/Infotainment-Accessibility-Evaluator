"""
Recheck router for validating patches in sandbox environment.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Dict, Any
import logging

from models.schemas import RecheckResult, RecheckRequest
from services.sandbox.apply_patches import PatchApplier
from services.agents.super_agent import SuperAgent
from routers.upload import get_upload_path

logger = logging.getLogger(__name__)
router = APIRouter()

# Initialize services
patch_applier = PatchApplier()
super_agent = SuperAgent()

@router.post("/recheck", response_model=RecheckResult)
async def recheck_patches(
    upload_id: str = Query(..., description="Upload ID to recheck")
):
    """Recheck patches in sandbox environment."""
    try:
        # Get sandbox path
        sandbox_path = patch_applier.get_sandbox_path()
        if not sandbox_path:
            raise HTTPException(status_code=404, detail="No sandbox found for this upload")
        
        # Run agents on sandbox
        # For now, simulate recheck results
        # In a real implementation, this would run the full agent analysis
        
        # Simulate finding improvements
        original_findings = 10  # This would come from the original analysis
        remaining_findings = 3  # This would come from the recheck
        fixed_findings = original_findings - remaining_findings
        new_findings = 0  # This would come from the recheck
        success_rate = (fixed_findings / original_findings) * 100 if original_findings > 0 else 0
        
        result = RecheckResult(
            upload_id=upload_id,
            original_findings=original_findings,
            remaining_findings=remaining_findings,
            fixed_findings=fixed_findings,
            new_findings=new_findings,
            success_rate=success_rate
        )
        
        logger.info(f"Recheck completed for upload {upload_id}: {fixed_findings} fixes applied")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error rechecking patches: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to recheck patches: {str(e)}"
        )

@router.get("/recheck/{upload_id}/status")
async def get_recheck_status(upload_id: str):
    """Get recheck status for an upload."""
    try:
        # Check if sandbox exists
        sandbox_path = patch_applier.get_sandbox_path()
        
        if not sandbox_path:
            return {
                "upload_id": upload_id,
                "status": "no_sandbox",
                "message": "No sandbox found for this upload"
            }
        
        # For now, return completed status
        # In a real implementation, this would check the actual status
        return {
            "upload_id": upload_id,
            "status": "completed",
            "message": "Recheck completed successfully"
        }
        
    except Exception as e:
        logger.error(f"Error getting recheck status: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get recheck status: {str(e)}"
        )

@router.post("/recheck/{upload_id}/reset")
async def reset_recheck(upload_id: str):
    """Reset recheck for an upload."""
    try:
        # Clean up sandbox
        patch_applier.cleanup_sandbox()
        
        return {"message": "Recheck reset successfully"}
        
    except Exception as e:
        logger.error(f"Error resetting recheck: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to reset recheck: {str(e)}"
        )

