"""
Upload router for handling file uploads and validation.
"""

from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from fastapi.responses import JSONResponse
import os
import tempfile
import shutil
from pathlib import Path
from typing import List, Optional
import uuid
from datetime import datetime

from models.schemas import UploadResult, ErrorResponse
from utils.file_safe import validate_upload, safe_extract_zip, get_file_manifest
from utils.id_gen import generate_upload_id

router = APIRouter()

# In-memory storage for uploads (in production, use a database)
uploads_storage = {}

@router.post("/upload", response_model=UploadResult)
async def upload_files(
    files: List[UploadFile] = File(...),
    upload_type: str = Form("zip")
):
    """Upload files for accessibility evaluation."""
    try:
        upload_id = generate_upload_id()
        
        # Create temporary directory for upload
        temp_dir = tempfile.mkdtemp(prefix=f"upload_{upload_id}_")
        
        total_size = 0
        file_manifest = []
        
        if upload_type == "zip" and len(files) == 1:
            # Handle ZIP upload
            file = files[0]
            
            # Save ZIP file
            zip_path = os.path.join(temp_dir, file.filename)
            with open(zip_path, "wb") as buffer:
                content = await file.read()
                buffer.write(content)
                total_size = len(content)
            
            # Validate ZIP file
            validation_result = validate_upload(zip_path)
            if not validation_result["valid"]:
                shutil.rmtree(temp_dir, ignore_errors=True)
                raise HTTPException(
                    status_code=400,
                    detail={
                        "error": "Invalid ZIP file",
                        "details": validation_result["errors"]
                    }
                )
            
            # Extract ZIP file
            extract_dir = os.path.join(temp_dir, "extracted")
            extract_result = safe_extract_zip(zip_path, extract_dir)
            
            if not extract_result["success"]:
                shutil.rmtree(temp_dir, ignore_errors=True)
                raise HTTPException(
                    status_code=400,
                    detail={
                        "error": "Failed to extract ZIP file",
                        "details": extract_result["errors"]
                    }
                )
            
            # Get manifest of extracted files
            manifest = get_file_manifest(extract_dir)
            file_manifest = [
                {
                    "path": f["path"],
                    "size": f["size"],
                    "extension": f["extension"],
                    "mime_type": f["mime_type"],
                    "safe": f["safe"]
                }
                for f in manifest
            ]
            
            total_size = sum(f["size"] for f in file_manifest)
            
        else:
            # Handle individual files
            for file in files:
                # Validate file
                file_path = os.path.join(temp_dir, file.filename)
                with open(file_path, "wb") as buffer:
                    content = await file.read()
                    buffer.write(content)
                    total_size += len(content)
                
                # Get file info
                file_info = {
                    "path": file.filename,
                    "size": len(content),
                    "extension": Path(file.filename).suffix.lower(),
                    "mime_type": file.content_type or "application/octet-stream",
                    "safe": True  # Basic validation for now
                }
                file_manifest.append(file_info)
        
        # Store upload information
        upload_result = UploadResult(
            upload_id=upload_id,
            file_manifest=file_manifest,
            total_files=len(file_manifest),
            total_size=total_size,
            upload_timestamp=datetime.now(),
            status="uploaded"
        )
        
        uploads_storage[upload_id] = {
            "result": upload_result,
            "temp_dir": temp_dir,
            "extracted_dir": os.path.join(temp_dir, "extracted") if upload_type == "zip" else temp_dir
        }
        
        return upload_result
        
    except HTTPException:
        raise
    except Exception as e:
        # Clean up on error
        if 'temp_dir' in locals():
            shutil.rmtree(temp_dir, ignore_errors=True)
        
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Upload failed",
                "details": str(e)
            }
        )

@router.get("/upload/{upload_id}")
async def get_upload_info(upload_id: str):
    """Get information about an uploaded file set."""
    if upload_id not in uploads_storage:
        raise HTTPException(status_code=404, detail="Upload not found")
    
    return uploads_storage[upload_id]["result"]

@router.delete("/upload/{upload_id}")
async def delete_upload(upload_id: str):
    """Delete an uploaded file set."""
    if upload_id not in uploads_storage:
        raise HTTPException(status_code=404, detail="Upload not found")
    
    # Clean up temporary files
    temp_dir = uploads_storage[upload_id]["temp_dir"]
    shutil.rmtree(temp_dir, ignore_errors=True)
    
    # Remove from storage
    del uploads_storage[upload_id]
    
    return {"message": "Upload deleted successfully"}

@router.get("/upload/{upload_id}/files")
async def list_upload_files(upload_id: str):
    """List all files in an upload."""
    if upload_id not in uploads_storage:
        raise HTTPException(status_code=404, detail="Upload not found")
    
    upload_info = uploads_storage[upload_id]
    return {
        "upload_id": upload_id,
        "files": upload_info["result"].file_manifest,
        "total_files": upload_info["result"].total_files,
        "total_size": upload_info["result"].total_size
    }

@router.get("/upload/{upload_id}/files/{file_path:path}")
async def get_upload_file(upload_id: str, file_path: str):
    """Get a specific file from an upload."""
    if upload_id not in uploads_storage:
        raise HTTPException(status_code=404, detail="Upload not found")
    
    upload_info = uploads_storage[upload_id]
    extracted_dir = upload_info["extracted_dir"]
    full_path = os.path.join(extracted_dir, file_path)
    
    if not os.path.exists(full_path) or not os.path.isfile(full_path):
        raise HTTPException(status_code=404, detail="File not found")
    
    # Check if file is safe
    from utils.file_safe import FileSafetyChecker
    checker = FileSafetyChecker()
    file_info = checker.check_file(full_path)
    
    if not file_info.is_safe:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "File is not safe",
                "reason": file_info.reason
            }
        )
    
    # Return file content
    with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    return {
        "file_path": file_path,
        "content": content,
        "size": file_info.size,
        "mime_type": file_info.mime_type
    }

@router.get("/uploads")
async def list_uploads():
    """List all uploads."""
    return {
        "uploads": [
            {
                "upload_id": upload_id,
                "total_files": info["result"].total_files,
                "total_size": info["result"].total_size,
                "upload_timestamp": info["result"].upload_timestamp,
                "status": info["result"].status
            }
            for upload_id, info in uploads_storage.items()
        ]
    }

def get_upload_path(upload_id: str) -> Optional[str]:
    """Get the path to an upload's extracted directory."""
    if upload_id not in uploads_storage:
        return None
    return uploads_storage[upload_id]["extracted_dir"]
