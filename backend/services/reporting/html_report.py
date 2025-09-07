"""
HTML report generation service.
"""

import os
from typing import Dict, Any, List
from datetime import datetime
from jinja2 import Template

async def generate_html_report(upload_id: str, upload_path: str, include_patches: bool = True) -> str:
    """Generate HTML accessibility report."""
    
    # Import here to avoid circular imports
    from routers.report import get_analysis_results
    
    # Get real analysis data
    analysis_data = get_analysis_results(upload_id)
    clusters = analysis_data.get('clusters', [])
    findings = analysis_data.get('findings', [])
    
    # Calculate totals from real data
    total_findings = sum(len(cluster.get('occurrences', [])) for cluster in clusters)
    total_clusters = len(clusters)
    
    # Calculate WCAG compliance from real data
    wcag_compliance = {
        "A": {"total": 0, "passed": 0, "failed": 0},
        "AA": {"total": 0, "passed": 0, "failed": 0},
        "AAA": {"total": 0, "passed": 0, "failed": 0}
    }
    
    # Count findings by WCAG level
    for finding in findings:
        wcag_criterion = finding.get('wcag_criterion', 'N/A')
        if wcag_criterion.startswith('1.'):
            wcag_compliance["A"]["total"] += 1
            wcag_compliance["A"]["failed"] += 1
        elif wcag_criterion.startswith('2.') or wcag_criterion.startswith('3.'):
            wcag_compliance["AA"]["total"] += 1
            wcag_compliance["AA"]["failed"] += 1
        elif wcag_criterion.startswith('4.'):
            wcag_compliance["AAA"]["total"] += 1
            wcag_compliance["AAA"]["failed"] += 1
    
    # Calculate overall score (simplified)
    total_issues = sum(level["failed"] for level in wcag_compliance.values())
    total_checks = sum(level["total"] for level in wcag_compliance.values())
    overall_score = max(0, 100 - (total_issues * 10)) if total_checks > 0 else 100
    
    # Generate recommendations based on findings
    recommendations = []
    if any(f.get('criterion') == 'contrast' for f in findings):
        recommendations.append("Fix color contrast issues for better readability")
    if any(f.get('criterion') == 'aria' for f in findings):
        recommendations.append("Add proper ARIA labels to interactive elements")
    if any(f.get('criterion') == 'language' for f in findings):
        recommendations.append("Add language attributes to HTML elements")
    if any(f.get('criterion') == 'seizure_safe' for f in findings):
        recommendations.append("Ensure animations respect user preferences")
    if not recommendations:
        recommendations.append("Implement keyboard navigation support")
    
    report_data = {
        "upload_id": upload_id,
        "timestamp": datetime.now().isoformat(),
        "summary": {
            "total_findings": total_findings,
            "total_clusters": total_clusters,
            "total_patches": 0,  # No patches generated yet
            "compliance_level": "AA",
            "overall_score": overall_score
        },
        "findings": findings,
        "clusters": clusters,
        "patches": [],  # No patches generated yet
        "wcag_compliance": wcag_compliance,
        "recommendations": recommendations
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
