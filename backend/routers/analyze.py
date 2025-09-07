"""
Analysis router for pre-scanning uploaded files.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Dict, Any, List
import os
from pathlib import Path
import re

from models.schemas import AnalysisSummary, ErrorResponse
from routers.upload import get_upload_path
from utils.wcag_constants import get_criterion_by_type
from utils.contrast_ratio import find_contrast_issues_in_css
from utils.flash_metrics import analyze_animation_safety
from utils.bcp47 import validate_language_tag
from utils.aria_maps import get_roles_by_category

router = APIRouter()

@router.get("/analyze", response_model=AnalysisSummary)
async def analyze_upload(
    upload_id: str = Query(..., description="Upload ID to analyze")
):
    """Perform pre-scan analysis on uploaded files."""
    try:
        # Get upload path
        upload_path = get_upload_path(upload_id)
        if not upload_path:
            raise HTTPException(status_code=404, detail="Upload not found")
        
        # Initialize analysis results
        issues_found = []
        criteria_summary = {
            "contrast": 0,
            "seizure_safe": 0,
            "language": 0,
            "aria": 0,
            "state_explorer": 0
        }
        
        total_files = 0
        
        # Scan all files
        for root, dirs, files in os.walk(upload_path):
            for file in files:
                file_path = os.path.join(root, file)
                relative_path = os.path.relpath(file_path, upload_path)
                file_ext = Path(file).suffix.lower()
                
                total_files += 1
                
                # Analyze HTML files
                if file_ext in ['.html', '.htm', '.xhtml']:
                    html_issues = await _analyze_html_file(file_path, relative_path)
                    issues_found.extend(html_issues)
                    criteria_summary["language"] += len([i for i in html_issues if i["criterion"] == "language"])
                    criteria_summary["aria"] += len([i for i in html_issues if i["criterion"] == "aria"])
                
                # Analyze CSS files
                elif file_ext in ['.css', '.scss', '.sass']:
                    css_issues = await _analyze_css_file(file_path, relative_path)
                    issues_found.extend(css_issues)
                    criteria_summary["contrast"] += len([i for i in css_issues if i["criterion"] == "contrast"])
                    criteria_summary["seizure_safe"] += len([i for i in css_issues if i["criterion"] == "seizure_safe"])
                
                # Analyze QML files
                elif file_ext == '.qml':
                    qml_issues = await _analyze_qml_file(file_path, relative_path)
                    issues_found.extend(qml_issues)
                    criteria_summary["language"] += len([i for i in qml_issues if i["criterion"] == "language"])
                    criteria_summary["aria"] += len([i for i in qml_issues if i["criterion"] == "aria"])
        
        # Calculate estimated processing time
        estimated_time = _calculate_processing_time(criteria_summary, total_files)
        
        # Create analysis summary
        summary = AnalysisSummary(
            upload_id=upload_id,
            total_files=total_files,
            issues_found=issues_found,
            criteria_summary=criteria_summary,
            estimated_processing_time=estimated_time
        )
        
        return summary
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Analysis failed",
                "details": str(e)
            }
        )

async def _analyze_html_file(file_path: str, relative_path: str) -> List[Dict[str, Any]]:
    """Analyze HTML file for basic accessibility issues."""
    issues = []
    
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # Check for language attribute
        lang_match = re.search(r'<html[^>]*lang\s*=\s*["\']([^"\']*)["\']', content, re.IGNORECASE)
        if not lang_match:
            issues.append({
                "criterion": "language",
                "severity": "high",
                "file": relative_path,
                "line": 1,
                "description": "Missing lang attribute on html element",
                "wcag_criterion": "3.1.1"
            })
        else:
            lang_value = lang_match.group(1)
            validation = validate_language_tag(lang_value)
            if not validation["valid"]:
                issues.append({
                    "criterion": "language",
                    "severity": "medium",
                    "file": relative_path,
                    "line": 1,
                    "description": f"Invalid language tag: {lang_value}",
                    "wcag_criterion": "3.1.1"
                })
        
        # Check for ARIA roles
        aria_roles = re.findall(r'role\s*=\s*["\']([^"\']*)["\']', content, re.IGNORECASE)
        for role in aria_roles:
            if role not in get_roles_by_category("widget") + get_roles_by_category("composite") + get_roles_by_category("document") + get_roles_by_category("landmark"):
                issues.append({
                    "criterion": "aria",
                    "severity": "medium",
                    "file": relative_path,
                    "line": 1,
                    "description": f"Unknown ARIA role: {role}",
                    "wcag_criterion": "4.1.2"
                })
        
        # Check for missing alt attributes on images
        img_tags = re.findall(r'<img[^>]*>', content, re.IGNORECASE)
        for img_tag in img_tags:
            if 'alt=' not in img_tag.lower():
                issues.append({
                    "criterion": "aria",
                    "severity": "high",
                    "file": relative_path,
                    "line": 1,
                    "description": "Image missing alt attribute",
                    "wcag_criterion": "1.1.1"
                })
        
    except Exception as e:
        issues.append({
            "criterion": "general",
            "severity": "low",
            "file": relative_path,
            "line": 1,
            "description": f"Error analyzing file: {str(e)}",
            "wcag_criterion": "N/A"
        })
    
    return issues

async def _analyze_css_file(file_path: str, relative_path: str) -> List[Dict[str, Any]]:
    """Analyze CSS file for accessibility issues."""
    issues = []
    
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # Check for contrast issues
        contrast_issues = find_contrast_issues_in_css(content)
        for issue in contrast_issues:
            issues.append({
                "criterion": "contrast",
                "severity": "high" if issue["result"]["severity"] in ["high", "critical"] else "medium",
                "file": relative_path,
                "line": issue["line_number"],
                "description": f"Contrast ratio {issue['result']['ratio']:.1f} below required {issue['result']['required_ratio']:.1f}",
                "wcag_criterion": "1.4.3"
            })
        
        # Check for animation/flash issues
        flash_analysis = analyze_animation_safety(content)
        if not flash_analysis["safe"]:
            for violation in flash_analysis["violations"]:
                issues.append({
                    "criterion": "seizure_safe",
                    "severity": "high" if violation["severity"] == "high" else "medium",
                    "file": relative_path,
                    "line": 1,
                    "description": violation["description"],
                    "wcag_criterion": violation["criterion"]
                })
        
    except Exception as e:
        issues.append({
            "criterion": "general",
            "severity": "low",
            "file": relative_path,
            "line": 1,
            "description": f"Error analyzing CSS file: {str(e)}",
            "wcag_criterion": "N/A"
        })
    
    return issues

async def _analyze_qml_file(file_path: str, relative_path: str) -> List[Dict[str, Any]]:
    """Analyze QML file for accessibility issues."""
    issues = []
    
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # Check for accessibility properties
        if 'Accessible' not in content and 'accessible' not in content:
            issues.append({
                "criterion": "aria",
                "severity": "medium",
                "file": relative_path,
                "line": 1,
                "description": "QML file missing accessibility properties",
                "wcag_criterion": "4.1.2"
            })
        
        # Check for text properties
        if 'text' in content.lower() and 'Accessible.name' not in content:
            issues.append({
                "criterion": "aria",
                "severity": "high",
                "file": relative_path,
                "line": 1,
                "description": "QML text elements missing accessible names",
                "wcag_criterion": "4.1.2"
            })
        
    except Exception as e:
        issues.append({
            "criterion": "general",
            "severity": "low",
            "file": relative_path,
            "line": 1,
            "description": f"Error analyzing QML file: {str(e)}",
            "wcag_criterion": "N/A"
        })
    
    return issues

def _calculate_processing_time(criteria_summary: Dict[str, int], total_files: int) -> int:
    """Calculate estimated processing time in seconds."""
    # Base time per file
    base_time = 2
    
    # Additional time per issue type
    issue_weights = {
        "contrast": 3,
        "seizure_safe": 5,
        "language": 1,
        "aria": 2,
        "state_explorer": 4
    }
    
    total_time = total_files * base_time
    
    for criterion, count in criteria_summary.items():
        total_time += count * issue_weights.get(criterion, 1)
    
    return min(total_time, 300)  # Cap at 5 minutes
