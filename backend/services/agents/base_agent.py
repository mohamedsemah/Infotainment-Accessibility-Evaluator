"""
BaseAgent - Base class for all accessibility agents.
"""

import os
import logging
from typing import List, Dict, Any
from pathlib import Path

from models.schemas import Finding, Evidence, SeverityLevel, ConfidenceLevel, CriterionType
from utils.id_gen import generate_finding_id

logger = logging.getLogger(__name__)

class BaseAgent:
    """Base class for all accessibility agents."""
    
    def __init__(self, name: str, description: str, criterion: CriterionType, wcag_criterion: str):
        self.name = name
        self.description = description
        self.criterion = criterion
        self.wcag_criterion = wcag_criterion
    
    async def analyze(self, upload_path: str) -> List[Finding]:
        """Analyze files for accessibility issues. Override in subclasses."""
        raise NotImplementedError("Subclasses must implement analyze method")
    
    def _find_files(self, upload_path: str, extensions: List[str]) -> List[str]:
        """Find files with specified extensions in upload path."""
        files = []
        upload_dir = Path(upload_path)
        
        if upload_dir.is_file():
            if any(upload_dir.suffix.lower() == ext for ext in extensions):
                files.append(str(upload_dir))
        else:
            for ext in extensions:
                files.extend([str(f) for f in upload_dir.rglob(f'*{ext}')])
        
        return files
    
    def _create_finding(
        self,
        file_path: str,
        line_number: int,
        selector: str,
        details: str,
        severity: SeverityLevel,
        evidence: Evidence,
        wcag_criterion: str = None
    ) -> Finding:
        """Create a finding with consistent structure."""
        return Finding(
            id=generate_finding_id(),
            details=details,
            severity=severity,
            confidence=ConfidenceLevel.HIGH,
            criterion=self.criterion,
            wcag_criterion=wcag_criterion or self.wcag_criterion,
            selector=selector,
            evidence=[evidence]
        )
    
    def _create_evidence(self, file_path: str, line_number: int, context: str) -> Evidence:
        """Create evidence for a finding."""
        return Evidence(
            file_path=file_path,
            line_number=line_number,
            code_snippet=context
        )
    
    def _create_error_finding(self, file_path: str, error_message: str) -> Finding:
        """Create a finding for analysis errors."""
        return Finding(
            id=generate_finding_id(),
            details=f"Analysis error: {error_message}",
            severity=SeverityLevel.LOW,
            confidence=ConfidenceLevel.LOW,
            criterion=self.criterion,
            wcag_criterion=self.wcag_criterion,
            selector="unknown",
            evidence=[Evidence(
                file_path=file_path,
                line_number=1,
                code_snippet=error_message
            )]
        )
