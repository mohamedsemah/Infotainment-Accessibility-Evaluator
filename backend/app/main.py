"""
FastAPI application for the Infotainment Accessibility Pipeline.
Provides REST endpoints for the 4-stage LLM pipeline.
"""

import logging
import os
import uuid
from typing import List
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
import tempfile
import zipfile
from pathlib import Path

from .models import (
    PipelineRequest, PipelineResponse, HealthResponse, UploadResponse,
    FileContent, ModelMap
)
from .orchestrator import AccessibilityOrchestrator

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Infotainment Accessibility Evaluator",
    description="4-stage LLM pipeline for WCAG 2.2 accessibility evaluation",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],  # Frontend URLs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize orchestrator
orchestrator = AccessibilityOrchestrator()

# In-memory storage for uploaded files (in production, use proper storage)
uploaded_files = {}


@app.get("/healthz", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    import datetime
    return HealthResponse(
        status="ok",
        timestamp=datetime.datetime.utcnow().isoformat()
    )


@app.post("/upload/files", response_model=UploadResponse)
async def upload_files(files: List[UploadFile] = File(...)):
    """
    Upload files for accessibility analysis.
    
    Args:
        files: List of uploaded files
        
    Returns:
        Upload response with session ID and file manifest
    """
    session_id = str(uuid.uuid4())
    file_manifest = []
    
    try:
        for file in files:
            # Read file content
            content = await file.read()
            
            # Store file info
            file_info = {
                "path": file.filename,
                "content": content.decode('utf-8', errors='ignore')
            }
            
            if session_id not in uploaded_files:
                uploaded_files[session_id] = []
            
            uploaded_files[session_id].append(file_info)
            file_manifest.append(file.filename)
        
        logger.info(f"Uploaded {len(files)} files for session {session_id}")
        
        return UploadResponse(
            session_id=session_id,
            files_uploaded=len(files),
            file_manifest=file_manifest
        )
    
    except Exception as e:
        logger.error(f"File upload failed: {e}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@app.post("/pipeline/run", response_model=PipelineResponse)
async def run_pipeline(request: PipelineRequest):
    """
    Run the complete accessibility evaluation pipeline.
    
    Args:
        request: Pipeline request with session ID, model map, and files
        
    Returns:
        Pipeline response with results from all 4 stages
    """
    try:
        logger.info(f"Starting pipeline for session {request.session_id}")
        
        # Get files from uploaded files or use provided files
        if request.session_id in uploaded_files:
            files = uploaded_files[request.session_id]
        else:
            files = request.files
        
        if not files:
            raise HTTPException(status_code=400, detail="No files provided for analysis")
        
        # Run the pipeline
        response = await orchestrator.run_pipeline(request)
        
        logger.info(f"Pipeline completed for session {request.session_id}")
        return response
    
    except Exception as e:
        logger.error(f"Pipeline execution failed: {e}")
        raise HTTPException(status_code=500, detail=f"Pipeline failed: {str(e)}")


@app.get("/report/pdf")
async def generate_pdf_report(session_id: str):
    """
    Generate a PDF report for a completed pipeline run.
    
    Args:
        session_id: Session ID to generate report for
        
    Returns:
        PDF file response
    """
    try:
        # In a real implementation, you would:
        # 1. Retrieve the pipeline results from storage
        # 2. Generate HTML report
        # 3. Convert to PDF using WeasyPrint or similar
        
        # For now, return a placeholder
        return JSONResponse(
            content={"message": "PDF report generation not yet implemented"},
            status_code=501
        )
    
    except Exception as e:
        logger.error(f"PDF generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"PDF generation failed: {str(e)}")


@app.get("/export/zip")
async def export_patched_files(session_id: str):
    """
    Export patched files as a ZIP archive.
    
    Args:
        session_id: Session ID to export files for
        
    Returns:
        ZIP file response
    """
    try:
        # In a real implementation, you would:
        # 1. Retrieve the pipeline results and fixes
        # 2. Apply patches to original files
        # 3. Create ZIP archive
        # 4. Return the ZIP file
        
        # For now, return a placeholder
        return JSONResponse(
            content={"message": "ZIP export not yet implemented"},
            status_code=501
        )
    
    except Exception as e:
        logger.error(f"ZIP export failed: {e}")
        raise HTTPException(status_code=500, detail=f"ZIP export failed: {str(e)}")


@app.get("/config/model-map")
async def get_model_map():
    """Get the current model configuration."""
    return {
        "model_map": orchestrator.model_map.dict(),
        "wcag_rules": list(orchestrator.wcag_config.get('rules', {}).keys())
    }


@app.post("/config/model-map")
async def update_model_map(model_map: ModelMap):
    """Update the model configuration."""
    try:
        orchestrator.model_map = model_map
        logger.info(f"Updated model map: {model_map.dict()}")
        return {"message": "Model map updated successfully"}
    
    except Exception as e:
        logger.error(f"Model map update failed: {e}")
        raise HTTPException(status_code=500, detail=f"Update failed: {str(e)}")


@app.get("/sessions/{session_id}/files")
async def get_session_files(session_id: str):
    """Get files for a specific session."""
    if session_id not in uploaded_files:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return {
        "session_id": session_id,
        "files": uploaded_files[session_id]
    }


@app.delete("/sessions/{session_id}")
async def clear_session(session_id: str):
    """Clear files for a specific session."""
    if session_id in uploaded_files:
        del uploaded_files[session_id]
        logger.info(f"Cleared session {session_id}")
        return {"message": "Session cleared successfully"}
    else:
        raise HTTPException(status_code=404, detail="Session not found")


# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content={"detail": "Resource not found"}
    )


@app.exception_handler(500)
async def internal_error_handler(request, exc):
    logger.error(f"Internal server error: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )


if __name__ == "__main__":
    import uvicorn
    
    host = os.getenv("APP_HOST", "0.0.0.0")
    port = int(os.getenv("APP_PORT", 8000))
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=True,
        log_level="info"
    )
