"""
Tests for Pydantic models and schema validation.
"""

import pytest
from uuid import uuid4
from app.models import (
    FileSpan, CandidateIssue, Metric, ValidationDecision, FixSuggestion,
    PipelineRequest, PipelineResponse, ModelMap, FileContent
)


class TestModels:
    """Test Pydantic model validation and serialization."""
    
    def test_file_span(self):
        """Test FileSpan model."""
        span = FileSpan(
            file_path="test.html",
            start_line=10,
            end_line=15,
            code_snippet="<img src='test.jpg'>"
        )
        
        assert span.file_path == "test.html"
        assert span.start_line == 10
        assert span.end_line == 15
        assert span.code_snippet == "<img src='test.jpg'>"
        
        # Test JSON serialization
        json_data = span.dict()
        assert json_data["file_path"] == "test.html"
        assert json_data["start_line"] == 10
    
    def test_file_span_validation(self):
        """Test FileSpan validation rules."""
        # Valid span
        span = FileSpan(
            file_path="test.html",
            start_line=1,
            end_line=5,
            code_snippet="test"
        )
        assert span.start_line == 1
        assert span.end_line == 5
        
        # Invalid: end_line < start_line
        with pytest.raises(ValueError):
            FileSpan(
                file_path="test.html",
                start_line=10,
                end_line=5,
                code_snippet="test"
            )
    
    def test_candidate_issue(self):
        """Test CandidateIssue model."""
        evidence = [
            FileSpan(
                file_path="test.html",
                start_line=10,
                end_line=15,
                code_snippet="<img src='test.jpg'>"
            )
        ]
        
        candidate = CandidateIssue(
            rule_id="1.1.1",
            title="Missing alt text",
            description="Image lacks alt attribute",
            evidence=evidence,
            tags=["images", "alt-text"],
            llm_model="claude-opus",
            confidence="high"
        )
        
        assert candidate.rule_id == "1.1.1"
        assert candidate.title == "Missing alt text"
        assert len(candidate.evidence) == 1
        assert candidate.confidence == "high"
        assert isinstance(candidate.id, uuid4)
    
    def test_metric(self):
        """Test Metric model."""
        evidence = [
            FileSpan(
                file_path="test.css",
                start_line=5,
                end_line=10,
                code_snippet="color: #777;"
            )
        ]
        
        metric = Metric(
            name="contrast_ratio",
            scope_id="test.css:button",
            value=2.5,
            unit="ratio",
            computed_from=evidence,
            notes="Low contrast detected",
            llm_model="deepseek"
        )
        
        assert metric.name == "contrast_ratio"
        assert metric.value == 2.5
        assert metric.unit == "ratio"
        assert len(metric.computed_from) == 1
    
    def test_validation_decision(self):
        """Test ValidationDecision model."""
        decision = ValidationDecision(
            candidate_id=uuid4(),
            rule_id="1.4.3",
            passed=False,
            severity="moderate",
            reasoning="Contrast ratio 2.5 is below threshold 4.5",
            metrics_used={"contrast_ratio": 2.5},
            llm_model="grok-4"
        )
        
        assert decision.rule_id == "1.4.3"
        assert decision.passed is False
        assert decision.severity == "moderate"
        assert "2.5" in decision.reasoning
    
    def test_fix_suggestion(self):
        """Test FixSuggestion model."""
        fix = FixSuggestion(
            candidate_id=uuid4(),
            rule_id="1.1.1",
            patch_unified_diff="--- a/test.html\n+++ b/test.html\n@@ -1,1 +1,1 @@\n-<img src='test.jpg'>\n+<img src='test.jpg' alt='Test image'>",
            summary="Add alt attribute to image",
            side_effects=["May affect SEO"],
            test_suggestions=["Test with screen reader"],
            llm_model="gpt-5"
        )
        
        assert fix.rule_id == "1.1.1"
        assert "alt=" in fix.patch_unified_diff
        assert len(fix.side_effects) == 1
        assert len(fix.test_suggestions) == 1
    
    def test_model_map(self):
        """Test ModelMap model."""
        model_map = ModelMap(
            llm1="claude-opus-4-1",
            llm2="deepseek-chat",
            llm3="grok-4",
            llm4="gpt-5"
        )
        
        assert model_map.llm1 == "claude-opus-4-1"
        assert model_map.llm2 == "deepseek-chat"
        assert model_map.llm3 == "grok-4"
        assert model_map.llm4 == "gpt-5"
    
    def test_pipeline_request(self):
        """Test PipelineRequest model."""
        files = [
            FileContent(path="test.html", content="<html><body>Test</body></html>")
        ]
        
        model_map = ModelMap(
            llm1="claude-opus-4-1",
            llm2="deepseek-chat",
            llm3="grok-4",
            llm4="gpt-5"
        )
        
        request = PipelineRequest(
            session_id="test-session-123",
            model_map=model_map,
            files=files
        )
        
        assert request.session_id == "test-session-123"
        assert len(request.files) == 1
        assert request.files[0].path == "test.html"
    
    def test_pipeline_response(self):
        """Test PipelineResponse model."""
        from app.models import PipelineTimings, CostEstimate
        
        timings = PipelineTimings(
            llm1_discovery_ms=1000,
            llm2_metrics_ms=500,
            llm3_validation_ms=300,
            llm4_fixes_ms=800,
            total_ms=2600
        )
        
        cost_estimate = CostEstimate(
            llm1_tokens=1000,
            llm2_tokens=500,
            llm3_tokens=300,
            llm4_tokens=800,
            total_estimated_cost_usd=0.05
        )
        
        model_map = ModelMap(
            llm1="claude-opus-4-1",
            llm2="deepseek-chat",
            llm3="grok-4",
            llm4="gpt-5"
        )
        
        response = PipelineResponse(
            session_id="test-session-123",
            candidates=[],
            metrics=[],
            decisions=[],
            fixes=[],
            timings=timings,
            cost_estimate=cost_estimate,
            model_map_used=model_map
        )
        
        assert response.session_id == "test-session-123"
        assert response.timings.total_ms == 2600
        assert response.cost_estimate.total_estimated_cost_usd == 0.05
    
    def test_json_serialization(self):
        """Test JSON serialization and deserialization."""
        # Create a complex object
        evidence = [
            FileSpan(
                file_path="test.html",
                start_line=10,
                end_line=15,
                code_snippet="<img src='test.jpg'>"
            )
        ]
        
        candidate = CandidateIssue(
            rule_id="1.1.1",
            title="Missing alt text",
            description="Image lacks alt attribute",
            evidence=evidence,
            tags=["images"],
            llm_model="claude-opus",
            confidence="high"
        )
        
        # Serialize to JSON
        json_data = candidate.dict()
        
        # Deserialize from JSON
        candidate_restored = CandidateIssue(**json_data)
        
        assert candidate_restored.rule_id == candidate.rule_id
        assert candidate_restored.title == candidate.title
        assert len(candidate_restored.evidence) == len(candidate.evidence)
        assert candidate_restored.evidence[0].file_path == evidence[0].file_path
    
    def test_confidence_validation(self):
        """Test confidence level validation."""
        valid_confidences = ["low", "medium", "high"]
        
        for confidence in valid_confidences:
            candidate = CandidateIssue(
                rule_id="1.1.1",
                title="Test",
                description="Test description",
                evidence=[],
                llm_model="test",
                confidence=confidence
            )
            assert candidate.confidence == confidence
        
        # Invalid confidence should raise validation error
        with pytest.raises(ValueError):
            CandidateIssue(
                rule_id="1.1.1",
                title="Test",
                description="Test description",
                evidence=[],
                llm_model="test",
                confidence="invalid"
            )
    
    def test_severity_validation(self):
        """Test severity level validation."""
        valid_severities = ["info", "minor", "moderate", "serious", "critical"]
        
        for severity in valid_severities:
            decision = ValidationDecision(
                candidate_id=uuid4(),
                rule_id="1.1.1",
                passed=False,
                severity=severity,
                reasoning="Test",
                metrics_used={},
                llm_model="test"
            )
            assert decision.severity == severity
        
        # Invalid severity should raise validation error
        with pytest.raises(ValueError):
            ValidationDecision(
                candidate_id=uuid4(),
                rule_id="1.1.1",
                passed=False,
                severity="invalid",
                reasoning="Test",
                metrics_used={},
                llm_model="test"
            )
