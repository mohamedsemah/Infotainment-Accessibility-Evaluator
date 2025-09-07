"""
HTML report generation service.
"""

import os
from typing import Dict, Any, List
from datetime import datetime
from jinja2 import Template

async def generate_html_report(upload_id: str, upload_path: str, include_patches: bool = True) -> str:
    """Generate HTML accessibility report."""
    
    # Mock data - in production, this would fetch from database
    report_data = {
        "upload_id": upload_id,
        "timestamp": datetime.now().isoformat(),
        "summary": {
            "total_findings": 15,
            "total_clusters": 8,
            "total_patches": 5,
            "compliance_level": "AA",
            "overall_score": 75
        },
        "findings": [
            {
                "id": "finding-1",
                "criterion": "contrast",
                "severity": "high",
                "wcag_criterion": "1.4.3",
                "description": "Contrast ratio 2.1:1 below required 4.5:1",
                "file_path": "index.html",
                "line_number": 15,
                "selector": ".header-text"
            },
            {
                "id": "finding-2",
                "criterion": "seizure_safe",
                "severity": "critical",
                "wcag_criterion": "2.3.1",
                "description": "Animation exceeds 3 flashes per second",
                "file_path": "styles.css",
                "line_number": 42,
                "selector": ".animated-banner"
            },
            {
                "id": "finding-3",
                "criterion": "language",
                "severity": "medium",
                "wcag_criterion": "3.1.1",
                "description": "Missing lang attribute on html element",
                "file_path": "index.html",
                "line_number": 1,
                "selector": "html"
            },
            {
                "id": "finding-4",
                "criterion": "aria",
                "severity": "high",
                "wcag_criterion": "4.1.2",
                "description": "Button missing aria-label",
                "file_path": "index.html",
                "line_number": 28,
                "selector": ".submit-button"
            },
            {
                "id": "finding-5",
                "criterion": "state_explorer",
                "severity": "medium",
                "wcag_criterion": "2.4.7",
                "description": "Missing focus styles",
                "file_path": "styles.css",
                "line_number": 15,
                "selector": ".interactive-element"
            }
        ],
        "clusters": [
            {
                "id": "cluster-1",
                "criterion": "contrast",
                "summary": "Multiple contrast issues with blue text on white background",
                "severity": "high",
                "occurrences": 5,
                "wcag_criterion": "1.4.3"
            },
            {
                "id": "cluster-2",
                "criterion": "seizure_safe",
                "summary": "Animation frequency exceeds safe threshold",
                "severity": "critical",
                "occurrences": 2,
                "wcag_criterion": "2.3.1"
            },
            {
                "id": "cluster-3",
                "criterion": "language",
                "summary": "Missing language attributes",
                "severity": "medium",
                "occurrences": 3,
                "wcag_criterion": "3.1.1"
            }
        ],
        "patches": [
            {
                "id": "patch-1",
                "type": "css_update",
                "file_path": "contrast-fixes.css",
                "rationale": "Fix contrast ratio for blue text",
                "risks": ["May affect other elements"],
                "confidence": "high"
            },
            {
                "id": "patch-2",
                "type": "css_update",
                "file_path": "animation-fixes.css",
                "rationale": "Reduce animation frequency to safe levels",
                "risks": ["May affect animation timing"],
                "confidence": "high"
            }
        ] if include_patches else [],
        "wcag_compliance": {
            "A": {"total": 25, "passed": 20, "failed": 5},
            "AA": {"total": 15, "passed": 10, "failed": 5},
            "AAA": {"total": 8, "passed": 3, "failed": 5}
        },
        "recommendations": [
            "Fix color contrast issues for better readability",
            "Add proper ARIA labels to interactive elements",
            "Implement keyboard navigation support",
            "Add language attributes to HTML elements",
            "Ensure animations respect user preferences"
        ]
    }
    
    # Load HTML template
    template = _get_html_template()
    
    # Render template
    html_content = template.render(**report_data)
    
    return html_content

def _get_html_template() -> Template:
    """Get HTML report template."""
    template_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Accessibility Report - {{ upload_id }}</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 2rem;
            border-radius: 10px;
            margin-bottom: 2rem;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        
        .header h1 {
            margin: 0;
            font-size: 2.5rem;
            font-weight: 300;
        }
        
        .header p {
            margin: 0.5rem 0 0 0;
            opacity: 0.9;
        }
        
        .summary-cards {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1rem;
            margin-bottom: 2rem;
        }
        
        .card {
            background: white;
            padding: 1.5rem;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            text-align: center;
        }
        
        .card h3 {
            margin: 0 0 0.5rem 0;
            color: #666;
            font-size: 0.9rem;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        .card .value {
            font-size: 2rem;
            font-weight: bold;
            color: #333;
        }
        
        .card .score {
            color: #28a745;
        }
        
        .card .critical {
            color: #dc3545;
        }
        
        .card .high {
            color: #fd7e14;
        }
        
        .card .medium {
            color: #ffc107;
        }
        
        .section {
            background: white;
            margin-bottom: 2rem;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            overflow: hidden;
        }
        
        .section-header {
            background: #f8f9fa;
            padding: 1rem 1.5rem;
            border-bottom: 1px solid #dee2e6;
            font-weight: 600;
            color: #495057;
        }
        
        .section-content {
            padding: 1.5rem;
        }
        
        .finding {
            border-left: 4px solid #dee2e6;
            padding: 1rem;
            margin-bottom: 1rem;
            background: #f8f9fa;
            border-radius: 0 4px 4px 0;
        }
        
        .finding.critical {
            border-left-color: #dc3545;
            background: #f8d7da;
        }
        
        .finding.high {
            border-left-color: #fd7e14;
            background: #fff3cd;
        }
        
        .finding.medium {
            border-left-color: #ffc107;
            background: #d1ecf1;
        }
        
        .finding.low {
            border-left-color: #17a2b8;
            background: #d4edda;
        }
        
        .finding-header {
            display: flex;
            justify-content: between;
            align-items: center;
            margin-bottom: 0.5rem;
        }
        
        .finding-title {
            font-weight: 600;
            color: #333;
        }
        
        .finding-severity {
            padding: 0.25rem 0.5rem;
            border-radius: 4px;
            font-size: 0.8rem;
            font-weight: 600;
            text-transform: uppercase;
        }
        
        .severity-critical {
            background: #dc3545;
            color: white;
        }
        
        .severity-high {
            background: #fd7e14;
            color: white;
        }
        
        .severity-medium {
            background: #ffc107;
            color: #333;
        }
        
        .severity-low {
            background: #17a2b8;
            color: white;
        }
        
        .finding-details {
            color: #666;
            font-size: 0.9rem;
        }
        
        .finding-location {
            margin-top: 0.5rem;
            font-family: 'Monaco', 'Menlo', monospace;
            font-size: 0.8rem;
            color: #6c757d;
        }
        
        .cluster {
            border: 1px solid #dee2e6;
            border-radius: 6px;
            margin-bottom: 1rem;
            overflow: hidden;
        }
        
        .cluster-header {
            background: #f8f9fa;
            padding: 1rem;
            border-bottom: 1px solid #dee2e6;
            font-weight: 600;
        }
        
        .cluster-content {
            padding: 1rem;
        }
        
        .patch {
            border: 1px solid #dee2e6;
            border-radius: 6px;
            margin-bottom: 1rem;
            overflow: hidden;
        }
        
        .patch-header {
            background: #e9ecef;
            padding: 1rem;
            border-bottom: 1px solid #dee2e6;
            font-weight: 600;
        }
        
        .patch-content {
            padding: 1rem;
        }
        
        .patch-diff {
            background: #f8f9fa;
            border: 1px solid #dee2e6;
            border-radius: 4px;
            padding: 1rem;
            font-family: 'Monaco', 'Menlo', monospace;
            font-size: 0.8rem;
            white-space: pre-wrap;
            overflow-x: auto;
        }
        
        .compliance-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 1rem;
        }
        
        .compliance-item {
            text-align: center;
            padding: 1rem;
            border: 1px solid #dee2e6;
            border-radius: 6px;
        }
        
        .compliance-level {
            font-weight: bold;
            font-size: 1.2rem;
            margin-bottom: 0.5rem;
        }
        
        .compliance-stats {
            font-size: 0.9rem;
            color: #666;
        }
        
        .recommendations {
            list-style: none;
            padding: 0;
        }
        
        .recommendations li {
            padding: 0.5rem 0;
            border-bottom: 1px solid #dee2e6;
        }
        
        .recommendations li:last-child {
            border-bottom: none;
        }
        
        .recommendations li::before {
            content: "✓";
            color: #28a745;
            font-weight: bold;
            margin-right: 0.5rem;
        }
        
        .footer {
            text-align: center;
            color: #666;
            margin-top: 2rem;
            padding: 1rem;
            border-top: 1px solid #dee2e6;
        }
        
        @media (max-width: 768px) {
            body {
                padding: 10px;
            }
            
            .header h1 {
                font-size: 2rem;
            }
            
            .summary-cards {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>Accessibility Report</h1>
        <p>Upload ID: {{ upload_id }} | Generated: {{ timestamp }}</p>
    </div>
    
    <div class="summary-cards">
        <div class="card">
            <h3>Total Findings</h3>
            <div class="value">{{ summary.total_findings }}</div>
        </div>
        <div class="card">
            <h3>Clusters</h3>
            <div class="value">{{ summary.total_clusters }}</div>
        </div>
        <div class="card">
            <h3>Patches</h3>
            <div class="value">{{ summary.total_patches }}</div>
        </div>
        <div class="card">
            <h3>Compliance Level</h3>
            <div class="value">{{ summary.compliance_level }}</div>
        </div>
        <div class="card">
            <h3>Overall Score</h3>
            <div class="value score">{{ summary.overall_score }}%</div>
        </div>
    </div>
    
    <div class="section">
        <div class="section-header">WCAG Compliance</div>
        <div class="section-content">
            <div class="compliance-grid">
                {% for level, stats in wcag_compliance.items() %}
                <div class="compliance-item">
                    <div class="compliance-level">Level {{ level }}</div>
                    <div class="compliance-stats">
                        {{ stats.passed }}/{{ stats.total }} passed<br>
                        {{ stats.failed }} failed
                    </div>
                </div>
                {% endfor %}
            </div>
        </div>
    </div>
    
    <div class="section">
        <div class="section-header">Findings</div>
        <div class="section-content">
            {% for finding in findings %}
            <div class="finding {{ finding.severity }}">
                <div class="finding-header">
                    <div class="finding-title">{{ finding.description }}</div>
                    <div class="finding-severity severity-{{ finding.severity }}">{{ finding.severity }}</div>
                </div>
                <div class="finding-details">
                    <strong>WCAG Criterion:</strong> {{ finding.wcag_criterion }}<br>
                    <strong>Criterion Type:</strong> {{ finding.criterion }}
                </div>
                <div class="finding-location">
                    {{ finding.file_path }}:{{ finding.line_number }} ({{ finding.selector }})
                </div>
            </div>
            {% endfor %}
        </div>
    </div>
    
    <div class="section">
        <div class="section-header">Clusters</div>
        <div class="section-content">
            {% for cluster in clusters %}
            <div class="cluster">
                <div class="cluster-header">
                    {{ cluster.summary }}
                    <span class="finding-severity severity-{{ cluster.severity }}">{{ cluster.severity }}</span>
                </div>
                <div class="cluster-content">
                    <strong>WCAG Criterion:</strong> {{ cluster.wcag_criterion }}<br>
                    <strong>Occurrences:</strong> {{ cluster.occurrences }}
                </div>
            </div>
            {% endfor %}
        </div>
    </div>
    
    {% if patches %}
    <div class="section">
        <div class="section-header">Patches</div>
        <div class="section-content">
            {% for patch in patches %}
            <div class="patch">
                <div class="patch-header">
                    {{ patch.rationale }}
                </div>
                <div class="patch-content">
                    <strong>Type:</strong> {{ patch.type }}<br>
                    <strong>File:</strong> {{ patch.file_path }}<br>
                    <strong>Confidence:</strong> {{ patch.confidence }}<br>
                    {% if patch.risks %}
                    <strong>Risks:</strong> {{ patch.risks|join(', ') }}<br>
                    {% endif %}
                    <div class="patch-diff">{{ patch.diff[:500] }}{% if patch.diff|length > 500 %}...{% endif %}</div>
                </div>
            </div>
            {% endfor %}
        </div>
    </div>
    {% endif %}
    
    <div class="section">
        <div class="section-header">Recommendations</div>
        <div class="section-content">
            <ul class="recommendations">
                {% for recommendation in recommendations %}
                <li>{{ recommendation }}</li>
                {% endfor %}
            </ul>
        </div>
    </div>
    
    <div class="footer">
        <p>Generated by Infotainment Accessibility Evaluator</p>
    </div>
</body>
</html>
    """
    
    return Template(template_content)
