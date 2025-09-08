"""
Report router for generating accessibility reports.
"""

from fastapi import APIRouter, HTTPException, Query, Response
from fastapi.responses import HTMLResponse, FileResponse
from typing import Dict, Any, List
import os
import tempfile
import zipfile
from datetime import datetime
from pathlib import Path

from models.schemas import Report, ErrorResponse
from routers.upload import get_upload_path
from services.reporting.html_report import generate_html_report
from services.reporting.pdf_report import generate_pdf_report
from services.reporting.csv_report import generate_csv_report
from services.reporting.json_report import generate_json_report
from utils.id_gen import generate_report_id

router = APIRouter()

# In-memory storage for reports (in production, use a database)
reports_storage = {}

# In-memory storage for analysis results (in production, use a database)
analysis_storage = {}

def store_analysis_results(upload_id: str, clusters: List[Dict[str, Any]], findings: List[Dict[str, Any]]):
    """Store analysis results for report generation."""
    analysis_storage[upload_id] = {
        'clusters': clusters,
        'findings': findings,
        'timestamp': datetime.now()
    }

def get_analysis_results(upload_id: str) -> Dict[str, Any]:
    """Get stored analysis results."""
    return analysis_storage.get(upload_id, {'clusters': [], 'findings': []})

@router.get("/report")
async def generate_report(
    upload_id: str = Query(..., description="Upload ID to report on"),
    format: str = Query("html", description="Report format (html, pdf, csv, json)"),
    include_patches: bool = Query(True, description="Include patches in report"),
    compliance_level: str = Query("AA", description="Target WCAG compliance level (A, AA, AAA)")
):
    """Generate accessibility report."""
    try:
        # Validate compliance level
        if compliance_level.upper() not in ["A", "AA", "AAA"]:
            raise HTTPException(status_code=400, detail="Invalid compliance level. Use: A, AA, or AAA")
        
        # Get upload path
        upload_path = get_upload_path(upload_id)
        if not upload_path:
            raise HTTPException(status_code=404, detail="Upload not found")
        
        # Generate report based on format
        if format == "html":
            html_content = await generate_html_report(upload_id, upload_path, include_patches, compliance_level.upper())
            return HTMLResponse(content=html_content, media_type="text/html")
        elif format == "pdf":
            pdf_path = await _generate_pdf_report(upload_id, upload_path, include_patches, compliance_level.upper())
            return FileResponse(
                path=pdf_path,
                media_type="application/pdf",
                filename=f"accessibility-report-{upload_id}.pdf"
            )
        elif format == "csv":
            csv_path = await _generate_csv_report(upload_id, upload_path, include_patches, compliance_level.upper())
            return FileResponse(
                path=csv_path,
                media_type="text/csv",
                filename=f"accessibility-report-{upload_id}.csv"
            )
        elif format == "json":
            json_data = await _generate_json_report(upload_id, upload_path, include_patches, compliance_level.upper())
            return json_data
        else:
            raise HTTPException(status_code=400, detail="Invalid format. Use: html, pdf, csv, json")
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Report generation failed",
                "details": str(e)
            }
        )

@router.get("/report/{upload_id}/html")
async def get_html_report(upload_id: str):
    """Get HTML report."""
    try:
        # Get upload path
        upload_path = get_upload_path(upload_id)
        if not upload_path:
            raise HTTPException(status_code=404, detail="Upload not found")
        
        # Generate HTML report
        html_content = await generate_html_report(upload_id, upload_path, True)
        
        return HTMLResponse(content=html_content, media_type="text/html")
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "error": "HTML report generation failed",
                "details": str(e)
            }
        )

@router.get("/report/{upload_id}/pdf")
async def get_pdf_report(upload_id: str):
    """Get PDF report."""
    try:
        # Get upload path
        upload_path = get_upload_path(upload_id)
        if not upload_path:
            raise HTTPException(status_code=404, detail="Upload not found")
        
        # Generate PDF report
        pdf_path = await generate_pdf_report(upload_id, upload_path, True)
        
        return FileResponse(
            path=pdf_path,
            media_type="application/pdf",
            filename=f"accessibility-report-{upload_id}.pdf"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "error": "PDF report generation failed",
                "details": str(e)
            }
        )

@router.get("/report/{upload_id}/csv")
async def get_csv_report(upload_id: str):
    """Get CSV report."""
    try:
        # Get upload path
        upload_path = get_upload_path(upload_id)
        if not upload_path:
            raise HTTPException(status_code=404, detail="Upload not found")
        
        # Generate CSV report
        csv_path = await generate_csv_report(upload_id, upload_path, True)
        
        return FileResponse(
            path=csv_path,
            media_type="text/csv",
            filename=f"accessibility-report-{upload_id}.csv"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "error": "CSV report generation failed",
                "details": str(e)
            }
        )

@router.get("/report/{upload_id}/json")
async def get_json_report(upload_id: str):
    """Get JSON report."""
    try:
        # Get upload path
        upload_path = get_upload_path(upload_id)
        if not upload_path:
            raise HTTPException(status_code=404, detail="Upload not found")
        
        # Generate JSON report
        json_data = await generate_json_report(upload_id, upload_path, True)
        
        return json_data
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "error": "JSON report generation failed",
                "details": str(e)
            }
        )

@router.get("/report/{upload_id}/download")
async def download_fixed_build(upload_id: str):
    """Download fixed build with patches applied."""
    try:
        # Get upload path
        upload_path = get_upload_path(upload_id)
        if not upload_path:
            raise HTTPException(status_code=404, detail="Upload not found")
        
        # Check if patches exist
        if upload_id not in patches_storage:
            raise HTTPException(status_code=404, detail="No patches found for upload")
        
        # Create fixed build
        fixed_build_path = await _create_fixed_build(upload_id, upload_path)
        
        return FileResponse(
            path=fixed_build_path,
            media_type="application/zip",
            filename=f"fixed-build-{upload_id}.zip"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Fixed build creation failed",
                "details": str(e)
            }
        )

@router.get("/report/{upload_id}/summary")
async def get_report_summary(upload_id: str):
    """Get report summary."""
    try:
        # Get upload path
        upload_path = get_upload_path(upload_id)
        if not upload_path:
            raise HTTPException(status_code=404, detail="Upload not found")
        
        # Generate summary
        summary = await _generate_report_summary(upload_id, upload_path)
        
        return summary
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Report summary generation failed",
                "details": str(e)
            }
        )

async def _generate_html_report(upload_id: str, upload_path: str, include_patches: bool) -> Report:
    """Generate HTML report."""
    report_id = generate_report_id()
    
    # Get real analysis data
    analysis_data = get_analysis_results(upload_id)
    clusters = analysis_data.get('clusters', [])
    findings = analysis_data.get('findings', [])
    
    patches = []
    if include_patches and upload_id in patches_storage:
        patches = patches_storage[upload_id].patches
    
    # Calculate totals from real data
    total_findings = sum(len(cluster.get('occurrences', [])) for cluster in clusters)
    total_clusters = len(clusters)
    total_patches = len(patches)
    
    # Calculate WCAG compliance
    wcag_compliance = {
        "A": {"total": 0, "passed": 0, "failed": 0},
        "AA": {"total": 0, "passed": 0, "failed": 0},
        "AAA": {"total": 0, "passed": 0, "failed": 0}
    }
    
    # Generate recommendations
    recommendations = [
        "Fix color contrast issues for better readability",
        "Add proper ARIA labels to interactive elements",
        "Implement keyboard navigation support",
        "Add language attributes to HTML elements",
        "Ensure animations respect user preferences"
    ]
    
    report = Report(
        upload_id=upload_id,
        summary={
            "total_findings": total_findings,
            "total_clusters": total_clusters,
            "total_patches": total_patches,
            "compliance_level": "AA",
            "overall_score": 75
        },
        clusters=clusters,
        totals={
            "findings": total_findings,
            "clusters": total_clusters,
            "patches": total_patches,
            "files_analyzed": len(list(Path(upload_path).rglob("*")))
        },
        passes_after_recheck=False,
        wcag_compliance=wcag_compliance,
        recommendations=recommendations
    )
    
    # Store report
    reports_storage[upload_id] = report
    
    return report

async def _generate_pdf_report(upload_id: str, upload_path: str, include_patches: bool, compliance_level: str = "AA") -> str:
    """Generate PDF report."""
    # This would generate a PDF report
    # For now, return a placeholder path
    
    temp_dir = tempfile.mkdtemp()
    pdf_path = os.path.join(temp_dir, f"accessibility-report-{upload_id}.pdf")
    
    # Create a placeholder PDF file
    with open(pdf_path, 'w') as f:
        f.write("PDF report placeholder")
    
    return pdf_path

async def _generate_csv_report(upload_id: str, upload_path: str, include_patches: bool, compliance_level: str = "AA") -> str:
    """Generate CSV report."""
    # This would generate a CSV report
    # For now, return a placeholder path
    
    temp_dir = tempfile.mkdtemp()
    csv_path = os.path.join(temp_dir, f"accessibility-report-{upload_id}.csv")
    
    # Create a placeholder CSV file
    with open(csv_path, 'w') as f:
        f.write("Finding ID,Severity,WCAG Criterion,Description,File Path,Line Number\n")
        f.write("finding-1,high,1.4.3,Contrast ratio below threshold,index.html,15\n")
    
    return csv_path

async def _generate_json_report(upload_id: str, upload_path: str, include_patches: bool, compliance_level: str = "AA") -> Dict[str, Any]:
    """Generate JSON report."""
    # This would generate a JSON report
    # For now, return mock data
    
    return {
        "upload_id": upload_id,
        "timestamp": datetime.now().isoformat(),
        "summary": {
            "total_findings": 5,
            "total_clusters": 3,
            "total_patches": 2,
            "compliance_level": compliance_level,
            "overall_score": 75
        },
        "findings": [
            {
                "id": "finding-1",
                "severity": "high",
                "wcag_criterion": "1.4.3",
                "description": "Contrast ratio below threshold",
                "file_path": "index.html",
                "line_number": 15
            }
        ],
        "clusters": [
            {
                "id": "cluster-1",
                "criterion": "contrast",
                "summary": "Multiple contrast issues with blue text on white background",
                "occurrences": 3
            }
        ],
        "patches": [
            {
                "id": "patch-1",
                "type": "css_update",
                "file_path": "contrast-fixes.css",
                "rationale": "Fix contrast ratio for blue text"
            }
        ]
    }

async def _create_fixed_build(upload_id: str, upload_path: str) -> str:
    """Create fixed build with patches applied."""
    # This would apply patches and create a zip file
    # For now, create a placeholder zip
    
    temp_dir = tempfile.mkdtemp()
    zip_path = os.path.join(temp_dir, f"fixed-build-{upload_id}.zip")
    
    # Create a placeholder zip file
    with zipfile.ZipFile(zip_path, 'w') as zip_file:
        zip_file.writestr("README.txt", "Fixed build placeholder")
    
    return zip_path

async def _generate_report_summary(upload_id: str, upload_path: str) -> Dict[str, Any]:
    """Generate report summary."""
    # This would generate a summary
    # For now, return mock data
    
    return {
        "upload_id": upload_id,
        "timestamp": datetime.now().isoformat(),
        "total_findings": 5,
        "total_clusters": 3,
        "total_patches": 2,
        "compliance_level": "AA",
        "overall_score": 75,
        "critical_issues": 1,
        "high_issues": 2,
        "medium_issues": 2,
        "low_issues": 0
    }
