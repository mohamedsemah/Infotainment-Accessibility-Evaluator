"""
Pydantic models for the Infotainment Accessibility Evaluator.
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Union
from enum import Enum
from datetime import datetime

class SeverityLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class ConfidenceLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class CriterionType(str, Enum):
    CONTRAST = "contrast"
    SEIZURE_SAFE = "seizure_safe"
    LANGUAGE = "language"
    ARIA = "aria"
    STATE_EXPLORER = "state_explorer"

class PatchType(str, Enum):
    CSS_UPDATE = "css_update"
    HTML_UPDATE = "html_update"
    ATTRIBUTE_ADD = "attribute_add"
    ATTRIBUTE_REMOVE = "attribute_remove"
    CONTENT_UPDATE = "content_update"

class UploadResult(BaseModel):
    upload_id: str
    file_manifest: List[Dict[str, Any]]
    total_files: int
    total_size: int
    upload_timestamp: datetime
    status: str = "uploaded"

class Evidence(BaseModel):
    file_path: str
    line_number: Optional[int] = None
    column_number: Optional[int] = None
    code_snippet: Optional[str] = None
    metrics: Optional[Dict[str, Any]] = None
    screenshot_path: Optional[str] = None
    before_value: Optional[str] = None
    after_value: Optional[str] = None

class Finding(BaseModel):
    id: str
    criterion: CriterionType
    selector: str
    component_id: Optional[str] = None
    screen: Optional[str] = None
    state: Optional[str] = None
    details: str
    evidence: List[Evidence]
    severity: SeverityLevel
    confidence: ConfidenceLevel
    wcag_criterion: str
    agent: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)

class ClusterKey(BaseModel):
    criterion: CriterionType
    key_components: Dict[str, Any]
    root_cause: str

class Patch(BaseModel):
    id: str
    type: PatchType
    file_path: str
    diff: str
    rationale: str
    risks: List[str] = []
    confidence: ConfidenceLevel
    created_at: datetime = Field(default_factory=datetime.now)

class Cluster(BaseModel):
    id: str
    criterion: CriterionType
    key: ClusterKey
    summary: str
    severity: SeverityLevel
    confidence: ConfidenceLevel
    occurrences: List[Finding]
    fixes: List[Patch] = []
    wcag_criterion: str
    created_at: datetime = Field(default_factory=datetime.now)

class AnalysisSummary(BaseModel):
    upload_id: str
    total_files: int
    issues_found: List[Dict[str, Any]]
    criteria_summary: Dict[str, int]
    estimated_processing_time: int  # seconds
    created_at: datetime = Field(default_factory=datetime.now)

class AgentPlan(BaseModel):
    upload_id: str
    agents_to_run: List[str]
    execution_order: List[str]
    parallel_groups: List[List[str]]
    estimated_duration: int  # seconds
    priority_weights: Dict[str, float]
    created_at: datetime = Field(default_factory=datetime.now)

class AgentResult(BaseModel):
    agent_name: str
    findings: List[Finding]
    processing_time: float
    tokens_used: Optional[int] = None
    success: bool = True
    error_message: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)

class ClusteringResult(BaseModel):
    upload_id: str
    clusters: List[Cluster]
    total_findings: int
    clustered_findings: int
    duplicate_ratio: float
    created_at: datetime = Field(default_factory=datetime.now)

class PatchRequest(BaseModel):
    upload_id: str
    patches: List[Patch]

class PatchResponse(BaseModel):
    success: bool
    message: str
    patches: List[Patch]
    total_patches: int

class PatchResult(BaseModel):
    upload_id: str
    patches: List[Patch]
    total_patches: int
    safe_patches: int
    risky_patches: int
    created_at: datetime = Field(default_factory=datetime.now)

class RecheckRequest(BaseModel):
    upload_id: str
    patch_ids: Optional[List[str]] = None

class RecheckResult(BaseModel):
    upload_id: str
    original_findings: int
    remaining_findings: int
    fixed_findings: int
    new_findings: int
    success_rate: float
    created_at: datetime = Field(default_factory=datetime.now)

class Report(BaseModel):
    upload_id: str
    summary: Dict[str, Any]
    clusters: List[Cluster]
    totals: Dict[str, int]
    passes_after_recheck: bool
    wcag_compliance: Dict[str, Any]
    recommendations: List[str]
    created_at: datetime = Field(default_factory=datetime.now)

class ProgressEvent(BaseModel):
    event_type: str
    upload_id: str
    agent_name: Optional[str] = None
    progress: float  # 0.0 to 1.0
    message: str
    timestamp: datetime = Field(default_factory=datetime.now)
    metadata: Optional[Dict[str, Any]] = None

class LLMRequest(BaseModel):
    prompt: str
    max_tokens: Optional[int] = 1000
    temperature: Optional[float] = 0.1
    model: Optional[str] = None

class LLMResponse(BaseModel):
    content: str
    tokens_used: int
    model: str
    finish_reason: str

class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)

class ClusterRequest(BaseModel):
    """Request for clustering findings"""
    findings: List[Finding]
    upload_id: str
    clustering_method: str = "semantic"  # semantic, rule_based, hybrid
    similarity_threshold: float = 0.7

class ClusterResponse(BaseModel):
    """Response from clustering findings"""
    clusters: List[Cluster]
    statistics: Dict[str, Any]
