"""
Smoke tests for the orchestrator pipeline.
Tests the complete 4-stage pipeline with mock data.
"""

import pytest
import asyncio
from pathlib import Path
from app.orchestrator import AccessibilityOrchestrator
from app.models import PipelineRequest, ModelMap, FileContent


class TestOrchestratorSmoke:
    """Smoke tests for the orchestrator."""
    
    @pytest.fixture
    def sample_files(self):
        """Load sample UI files for testing."""
        fixtures_dir = Path(__file__).parent / "fixtures" / "sample_ui"
        
        files = []
        for file_path in fixtures_dir.glob("*"):
            if file_path.is_file():
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                files.append(FileContent(
                    path=file_path.name,
                    content=content
                ))
        
        return files
    
    @pytest.fixture
    def orchestrator(self):
        """Create orchestrator instance."""
        return AccessibilityOrchestrator()
    
    @pytest.fixture
    def pipeline_request(self, sample_files):
        """Create a pipeline request with sample files."""
        model_map = ModelMap(
            llm1="claude-opus-4-1-20250805",
            llm2="deepseek-chat",
            llm3="grok-4",
            llm4="gpt-5"
        )
        
        return PipelineRequest(
            session_id="test-session-123",
            model_map=model_map,
            files=sample_files
        )
    
    @pytest.mark.asyncio
    async def test_pipeline_completes(self, orchestrator, pipeline_request):
        """Test that the pipeline completes without errors."""
        # Enable mock mode for testing
        orchestrator.mock_mode = True
        
        response = await orchestrator.run_pipeline(pipeline_request)
        
        assert response.session_id == "test-session-123"
        assert response.timings.total_ms is not None
        assert response.timings.total_ms > 0
        assert response.model_map_used.llm1 == "claude-opus-4-1-20250805"
    
    @pytest.mark.asyncio
    async def test_pipeline_discovers_issues(self, orchestrator, pipeline_request):
        """Test that the pipeline discovers accessibility issues."""
        orchestrator.mock_mode = True
        
        response = await orchestrator.run_pipeline(pipeline_request)
        
        # Should discover some issues from the sample files
        assert len(response.candidates) > 0
        
        # Check for expected issues
        rule_ids = [c.rule_id for c in response.candidates]
        assert "1.1.1" in rule_ids  # Missing alt text
        assert "1.4.3" in rule_ids  # Contrast issues
    
    @pytest.mark.asyncio
    async def test_pipeline_computes_metrics(self, orchestrator, pipeline_request):
        """Test that the pipeline computes metrics."""
        orchestrator.mock_mode = True
        
        response = await orchestrator.run_pipeline(pipeline_request)
        
        # Should compute some metrics
        assert len(response.metrics) > 0
        
        # Check for expected metrics
        metric_names = [m.name for m in response.metrics]
        assert "contrast_ratio" in metric_names
        assert "target_size_min_px" in metric_names
    
    @pytest.mark.asyncio
    async def test_pipeline_validates_decisions(self, orchestrator, pipeline_request):
        """Test that the pipeline makes validation decisions."""
        orchestrator.mock_mode = True
        
        response = await orchestrator.run_pipeline(pipeline_request)
        
        # Should make validation decisions
        assert len(response.decisions) > 0
        
        # Should have some failed decisions
        failed_decisions = [d for d in response.decisions if not d.passed]
        assert len(failed_decisions) > 0
        
        # Check severity levels
        severities = [d.severity for d in response.decisions]
        valid_severities = ["info", "minor", "moderate", "serious", "critical"]
        assert all(s in valid_severities for s in severities)
    
    @pytest.mark.asyncio
    async def test_pipeline_generates_fixes(self, orchestrator, pipeline_request):
        """Test that the pipeline generates fix suggestions."""
        orchestrator.mock_mode = True
        
        response = await orchestrator.run_pipeline(pipeline_request)
        
        # Should generate fixes for failed decisions
        assert len(response.fixes) > 0
        
        # Check fix structure
        for fix in response.fixes:
            assert fix.candidate_id is not None
            assert fix.rule_id is not None
            assert fix.summary is not None
            assert isinstance(fix.side_effects, list)
            assert isinstance(fix.test_suggestions, list)
    
    @pytest.mark.asyncio
    async def test_pipeline_timings(self, orchestrator, pipeline_request):
        """Test that pipeline records timing information."""
        orchestrator.mock_mode = True
        
        response = await orchestrator.run_pipeline(pipeline_request)
        
        # Check timing information
        timings = response.timings
        assert timings.llm1_discovery_ms is not None
        assert timings.llm2_metrics_ms is not None
        assert timings.llm3_validation_ms is not None
        assert timings.llm4_fixes_ms is not None
        assert timings.total_ms is not None
        
        # Total should be sum of individual stages
        individual_total = (
            timings.llm1_discovery_ms +
            timings.llm2_metrics_ms +
            timings.llm3_validation_ms +
            timings.llm4_fixes_ms
        )
        assert timings.total_ms >= individual_total
    
    @pytest.mark.asyncio
    async def test_deterministic_contrast_computation(self, orchestrator, sample_files):
        """Test deterministic contrast ratio computation."""
        # Create a request with CSS that has explicit colors
        css_file = next(f for f in sample_files if f.path.endswith('.css'))
        
        request = PipelineRequest(
            session_id="test-deterministic",
            model_map=ModelMap(
                llm1="claude-opus-4-1-20250805",
                llm2="deepseek-chat",
                llm3="grok-4",
                llm4="gpt-5"
            ),
            files=[css_file]
        )
        
        orchestrator.mock_mode = True
        response = await orchestrator.run_pipeline(request)
        
        # Should compute contrast ratio deterministically
        contrast_metrics = [m for m in response.metrics if m.name == "contrast_ratio"]
        assert len(contrast_metrics) > 0
        
        # Check that values are reasonable
        for metric in contrast_metrics:
            assert isinstance(metric.value, (int, float))
            assert 1.0 <= metric.value <= 21.0  # Valid contrast ratio range
    
    @pytest.mark.asyncio
    async def test_deterministic_target_size_computation(self, orchestrator, sample_files):
        """Test deterministic target size computation."""
        css_file = next(f for f in sample_files if f.path.endswith('.css'))
        
        request = PipelineRequest(
            session_id="test-target-size",
            model_map=ModelMap(
                llm1="claude-opus-4-1-20250805",
                llm2="deepseek-chat",
                llm3="grok-4",
                llm4="gpt-5"
            ),
            files=[css_file]
        )
        
        orchestrator.mock_mode = True
        response = await orchestrator.run_pipeline(request)
        
        # Should compute target size deterministically
        size_metrics = [m for m in response.metrics if m.name == "target_size_min_px"]
        assert len(size_metrics) > 0
        
        # Check that values are reasonable
        for metric in size_metrics:
            assert isinstance(metric.value, (int, float))
            assert metric.value > 0  # Positive size values
    
    @pytest.mark.asyncio
    async def test_pipeline_handles_empty_files(self, orchestrator):
        """Test that pipeline handles empty file lists gracefully."""
        request = PipelineRequest(
            session_id="test-empty",
            model_map=ModelMap(
                llm1="claude-opus-4-1-20250805",
                llm2="deepseek-chat",
                llm3="grok-4",
                llm4="gpt-5"
            ),
            files=[]
        )
        
        orchestrator.mock_mode = True
        
        with pytest.raises(Exception):  # Should raise an error for empty files
            await orchestrator.run_pipeline(request)
    
    @pytest.mark.asyncio
    async def test_pipeline_handles_malformed_files(self, orchestrator):
        """Test that pipeline handles malformed files gracefully."""
        malformed_file = FileContent(
            path="malformed.html",
            content="<html><body><img src='test.jpg'><button style='width: 10px; height: 10px;'>OK</button></body></html>"
        )
        
        request = PipelineRequest(
            session_id="test-malformed",
            model_map=ModelMap(
                llm1="claude-opus-4-1-20250805",
                llm2="deepseek-chat",
                llm3="grok-4",
                llm4="gpt-5"
            ),
            files=[malformed_file]
        )
        
        orchestrator.mock_mode = True
        response = await orchestrator.run_pipeline(request)
        
        # Should still complete successfully
        assert response.session_id == "test-malformed"
        assert len(response.candidates) > 0  # Should find issues in malformed content
