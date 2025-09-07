"""
ID generation utilities for creating unique identifiers.
"""

import uuid
import time
import random
import string
from typing import Optional

def generate_id() -> str:
    """Generate a generic unique ID."""
    return uuid.uuid4().hex[:12]

def generate_upload_id() -> str:
    """Generate a unique upload ID."""
    return f"upload_{uuid.uuid4().hex[:12]}"

def generate_finding_id() -> str:
    """Generate a unique finding ID."""
    return f"finding_{uuid.uuid4().hex[:12]}"

def generate_cluster_id() -> str:
    """Generate a unique cluster ID."""
    return f"cluster_{uuid.uuid4().hex[:12]}"

def generate_patch_id() -> str:
    """Generate a unique patch ID."""
    return f"patch_{uuid.uuid4().hex[:12]}"

def generate_agent_id() -> str:
    """Generate a unique agent ID."""
    return f"agent_{uuid.uuid4().hex[:12]}"

def generate_session_id() -> str:
    """Generate a unique session ID."""
    return f"session_{uuid.uuid4().hex[:12]}"

def generate_short_id(length: int = 8) -> str:
    """Generate a short random ID."""
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

def generate_timestamped_id(prefix: str = "id") -> str:
    """Generate an ID with timestamp."""
    timestamp = int(time.time() * 1000)  # milliseconds
    return f"{prefix}_{timestamp}_{generate_short_id(4)}"

def generate_sequential_id(prefix: str = "id", start: int = 1) -> str:
    """Generate a sequential ID (not thread-safe)."""
    if not hasattr(generate_sequential_id, 'counter'):
        generate_sequential_id.counter = start - 1
    
    generate_sequential_id.counter += 1
    return f"{prefix}_{generate_sequential_id.counter:06d}"

def generate_component_id(component_type: str, name: Optional[str] = None) -> str:
    """Generate a component ID with type and optional name."""
    if name:
        # Sanitize name for use in ID
        sanitized_name = ''.join(c for c in name if c.isalnum() or c in '_-').lower()
        return f"{component_type}_{sanitized_name}_{generate_short_id(4)}"
    else:
        return f"{component_type}_{generate_short_id(8)}"

def generate_file_id(filename: str) -> str:
    """Generate a file ID based on filename."""
    # Extract name without extension
    name = filename.rsplit('.', 1)[0] if '.' in filename else filename
    # Sanitize for use in ID
    sanitized_name = ''.join(c for c in name if c.isalnum() or c in '_-').lower()
    return f"file_{sanitized_name}_{generate_short_id(4)}"

def generate_selector_id(selector: str) -> str:
    """Generate an ID for a CSS selector."""
    # Create a hash-like ID from selector
    import hashlib
    selector_hash = hashlib.md5(selector.encode()).hexdigest()[:8]
    return f"sel_{selector_hash}"

def generate_state_id(element_id: str, state: str) -> str:
    """Generate an ID for an element state."""
    return f"{element_id}_{state}"

def generate_screen_id(screen_name: str) -> str:
    """Generate an ID for a screen/view."""
    sanitized_name = ''.join(c for c in screen_name if c.isalnum() or c in '_-').lower()
    return f"screen_{sanitized_name}_{generate_short_id(4)}"

def generate_evidence_id(finding_id: str, evidence_type: str) -> str:
    """Generate an ID for evidence."""
    return f"evidence_{finding_id}_{evidence_type}_{generate_short_id(4)}"

def generate_report_id(upload_id: str) -> str:
    """Generate a report ID based on upload ID."""
    return f"report_{upload_id}"

def generate_sandbox_id(upload_id: str) -> str:
    """Generate a sandbox ID based on upload ID."""
    return f"sandbox_{upload_id}_{generate_short_id(4)}"

def generate_workspace_id() -> str:
    """Generate a workspace ID."""
    return f"workspace_{uuid.uuid4().hex[:16]}"

def generate_task_id(agent_name: str) -> str:
    """Generate a task ID for an agent."""
    return f"task_{agent_name}_{generate_short_id(6)}"

def generate_batch_id() -> str:
    """Generate a batch ID for processing multiple items."""
    return f"batch_{int(time.time())}_{generate_short_id(4)}"

def generate_correlation_id() -> str:
    """Generate a correlation ID for tracking related operations."""
    return f"corr_{uuid.uuid4().hex[:16]}"

def generate_checksum_id(content: str) -> str:
    """Generate an ID based on content checksum."""
    import hashlib
    checksum = hashlib.sha256(content.encode()).hexdigest()[:12]
    return f"checksum_{checksum}"

def generate_version_id(major: int = 1, minor: int = 0, patch: int = 0) -> str:
    """Generate a version ID."""
    return f"v{major}.{minor}.{patch}"

def generate_build_id() -> str:
    """Generate a build ID."""
    timestamp = int(time.time())
    return f"build_{timestamp}_{generate_short_id(4)}"

def generate_release_id() -> str:
    """Generate a release ID."""
    return f"release_{uuid.uuid4().hex[:12]}"

def generate_experiment_id(name: str) -> str:
    """Generate an experiment ID."""
    sanitized_name = ''.join(c for c in name if c.isalnum() or c in '_-').lower()
    return f"exp_{sanitized_name}_{generate_short_id(4)}"

def generate_metric_id(metric_name: str) -> str:
    """Generate a metric ID."""
    sanitized_name = ''.join(c for c in metric_name if c.isalnum() or c in '_-').lower()
    return f"metric_{sanitized_name}_{generate_short_id(4)}"

def generate_alert_id(alert_type: str) -> str:
    """Generate an alert ID."""
    return f"alert_{alert_type}_{generate_short_id(6)}"

def generate_notification_id() -> str:
    """Generate a notification ID."""
    return f"notif_{uuid.uuid4().hex[:12]}"

def generate_webhook_id() -> str:
    """Generate a webhook ID."""
    return f"webhook_{uuid.uuid4().hex[:12]}"

def generate_api_key() -> str:
    """Generate an API key."""
    return f"ak_{uuid.uuid4().hex[:32]}"

def generate_secret_key() -> str:
    """Generate a secret key."""
    return f"sk_{uuid.uuid4().hex[:32]}"

def generate_token() -> str:
    """Generate a random token."""
    return f"token_{uuid.uuid4().hex[:24]}"

def generate_reference_id() -> str:
    """Generate a reference ID."""
    return f"ref_{uuid.uuid4().hex[:16]}"

def generate_trace_id() -> str:
    """Generate a trace ID for distributed tracing."""
    return f"trace_{uuid.uuid4().hex[:16]}"

def generate_span_id() -> str:
    """Generate a span ID for distributed tracing."""
    return f"span_{uuid.uuid4().hex[:12]}"

def generate_request_id() -> str:
    """Generate a request ID."""
    return f"req_{uuid.uuid4().hex[:16]}"

def generate_response_id() -> str:
    """Generate a response ID."""
    return f"resp_{uuid.uuid4().hex[:16]}"

def generate_event_id() -> str:
    """Generate an event ID."""
    return f"event_{uuid.uuid4().hex[:12]}"

def generate_audit_id() -> str:
    """Generate an audit ID."""
    return f"audit_{uuid.uuid4().hex[:12]}"

def generate_log_id() -> str:
    """Generate a log ID."""
    return f"log_{uuid.uuid4().hex[:12]}"

def generate_metric_id(metric_name: str) -> str:
    """Generate a metric ID."""
    sanitized_name = ''.join(c for c in metric_name if c.isalnum() or c in '_-').lower()
    return f"metric_{sanitized_name}_{generate_short_id(4)}"

def generate_alert_id(alert_type: str) -> str:
    """Generate an alert ID."""
    return f"alert_{alert_type}_{generate_short_id(6)}"

def generate_notification_id() -> str:
    """Generate a notification ID."""
    return f"notif_{uuid.uuid4().hex[:12]}"

def generate_webhook_id() -> str:
    """Generate a webhook ID."""
    return f"webhook_{uuid.uuid4().hex[:12]}"

def generate_api_key() -> str:
    """Generate an API key."""
    return f"ak_{uuid.uuid4().hex[:32]}"

def generate_secret_key() -> str:
    """Generate a secret key."""
    return f"sk_{uuid.uuid4().hex[:32]}"

def generate_token() -> str:
    """Generate a random token."""
    return f"token_{uuid.uuid4().hex[:24]}"

def generate_reference_id() -> str:
    """Generate a reference ID."""
    return f"ref_{uuid.uuid4().hex[:16]}"

def generate_trace_id() -> str:
    """Generate a trace ID for distributed tracing."""
    return f"trace_{uuid.uuid4().hex[:16]}"

def generate_span_id() -> str:
    """Generate a span ID for distributed tracing."""
    return f"span_{uuid.uuid4().hex[:12]}"

def generate_request_id() -> str:
    """Generate a request ID."""
    return f"req_{uuid.uuid4().hex[:16]}"

def generate_response_id() -> str:
    """Generate a response ID."""
    return f"resp_{uuid.uuid4().hex[:16]}"

def generate_event_id() -> str:
    """Generate an event ID."""
    return f"event_{uuid.uuid4().hex[:12]}"

def generate_audit_id() -> str:
    """Generate an audit ID."""
    return f"audit_{uuid.uuid4().hex[:12]}"

def generate_log_id() -> str:
    """Generate a log ID."""
    return f"log_{uuid.uuid4().hex[:12]}"
