"""
Main orchestrator for the 4-stage accessibility pipeline.
Coordinates LLM calls and deterministic computations.
"""

import asyncio
import json
import logging
import os
import time
import yaml
from typing import Dict, List, Optional, Set, Any
from pathlib import Path

from .models import (
    PipelineRequest, PipelineResponse, PipelineTimings, CostEstimate,
    CandidateIssue, Metric, ValidationDecision, FixSuggestion,
    ModelMap
)
from .utils.chunking import chunk_file
from .utils.color_contrast import contrast_ratio, is_large_text, get_contrast_threshold
from .utils.css_utils import parse_css_rules, extract_font_size, extract_font_weight, get_target_size
from .utils.hashing import span_hash, rule_hash
from .utils.diffs import validate_diff
from .providers.anthropic_client import ClaudeClient
from .providers.deepseek_client import DeepSeekClient
from .providers.xai_client import XAIClient
from .providers.openai_client import OpenAIClient

logger = logging.getLogger(__name__)


class AccessibilityOrchestrator:
    """Orchestrates the 4-stage accessibility evaluation pipeline."""
    
    def __init__(self):
        self.wcag_config = self._load_wcag_config()
        self.model_map = self._load_model_map()
        self.mock_mode = os.getenv("MOCK_MODE", "false").lower() == "true"
        
        # Initialize LLM clients
        self.claude_client = ClaudeClient(self.model_map.llm1)
        self.deepseek_client = DeepSeekClient(self.model_map.llm2)
        self.xai_client = XAIClient(self.model_map.llm3)
        self.openai_client = OpenAIClient(self.model_map.llm4)
    
    def _load_wcag_config(self) -> Dict[str, Any]:
        """Load WCAG thresholds configuration."""
        config_path = Path(__file__).parent / "config" / "wcag22_thresholds.yaml"
        try:
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.error(f"Failed to load WCAG config: {e}")
            return {}
    
    def _load_model_map(self) -> ModelMap:
        """Load model configuration."""
        config_path = Path(__file__).parent / "config" / "model_map_premium.json"
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
                return ModelMap(**config)
        except Exception as e:
            logger.error(f"Failed to load model map: {e}")
            # Default fallback
            return ModelMap(
                llm1="claude-opus-4-1-20250805",
                llm2="deepseek-chat",
                llm3="grok-4",
                llm4="gpt-5"
            )
    
    async def run_pipeline(self, request: PipelineRequest) -> PipelineResponse:
        """
        Run the complete 4-stage accessibility pipeline.
        
        Args:
            request: Pipeline request with files and configuration
            
        Returns:
            Pipeline response with results and metadata
        """
        start_time = time.time()
        timings = PipelineTimings()
        cost_estimate = CostEstimate()
        
        logger.info(f"Starting pipeline for session {request.session_id}")
        
        try:
            # Stage 1: Discovery
            logger.info("Stage 1: Running LLM-1 Discovery")
            stage1_start = time.time()
            candidates = await self.run_llm1_discovery(request.files)
            timings.llm1_discovery_ms = int((time.time() - stage1_start) * 1000)
            
            # Stage 2: Metrics
            logger.info("Stage 2: Running LLM-2 Metrics")
            stage2_start = time.time()
            metrics = await self.run_llm2_metrics(candidates, request.files)
            timings.llm2_metrics_ms = int((time.time() - stage2_start) * 1000)
            
            # Stage 3: Validation
            logger.info("Stage 3: Running LLM-3 Validation")
            stage3_start = time.time()
            decisions = await self.run_llm3_validation(candidates, metrics)
            timings.llm3_validation_ms = int((time.time() - stage3_start) * 1000)
            
            # Stage 4: Fixes
            logger.info("Stage 4: Running LLM-4 Fixes")
            stage4_start = time.time()
            fixes = await self.run_llm4_fixes(decisions, request.files)
            timings.llm4_fixes_ms = int((time.time() - stage4_start) * 1000)
            
            timings.total_ms = int((time.time() - start_time) * 1000)
            
            logger.info(f"Pipeline completed in {timings.total_ms}ms")
            
            return PipelineResponse(
                session_id=request.session_id,
                candidates=candidates,
                metrics=metrics,
                decisions=decisions,
                fixes=fixes,
                timings=timings,
                cost_estimate=cost_estimate,
                model_map_used=self.model_map
            )
            
        except Exception as e:
            logger.error(f"Pipeline failed: {e}")
            raise
    
    async def run_llm1_discovery(self, files: List[Dict[str, str]]) -> List[CandidateIssue]:
        """
        Stage 1: Discover candidate accessibility issues.
        
        Args:
            files: List of files to analyze
            
        Returns:
            List of discovered candidate issues
        """
        all_candidates = []
        
        for file_info in files:
            file_path = file_info['path']
            content = file_info['content']
            
            # Chunk the file
            chunks = chunk_file(content, max_tokens=3000, overlap_lines=20)
            
            for start_line, end_line, chunk_content in chunks:
                try:
                    if self.mock_mode or not self.claude_client.is_available():
                        # Use mock response
                        candidates = self._mock_discovery_response(file_path, start_line, end_line, chunk_content)
                    else:
                        # Use real LLM
                        candidates = await self.claude_client.discover_issues(
                            [chunk_content], [file_path]
                        )
                    
                    # Normalize and deduplicate
                    for candidate in candidates:
                        # Update line numbers to be absolute
                        for evidence in candidate.evidence:
                            evidence.start_line += start_line - 1
                            evidence.end_line += start_line - 1
                        
                        # Add span hash for deduplication
                        span_hashes = [span_hash(e.file_path, e.start_line, e.end_line, e.code_snippet) 
                                     for e in candidate.evidence]
                        candidate_hash = rule_hash(candidate.rule_id, candidate.title, 
                                                 max(span_hashes) if span_hashes else "")
                        
                        all_candidates.append(candidate)
                
                except Exception as e:
                    logger.warning(f"Failed to process chunk in {file_path}: {e}")
                    continue
        
        # Deduplicate candidates
        seen_hashes = set()
        unique_candidates = []
        for candidate in all_candidates:
            span_hashes = [span_hash(e.file_path, e.start_line, e.end_line, e.code_snippet) 
                          for e in candidate.evidence]
            candidate_hash = rule_hash(candidate.rule_id, candidate.title, 
                                     max(span_hashes) if span_hashes else "")
            
            if candidate_hash not in seen_hashes:
                seen_hashes.add(candidate_hash)
                unique_candidates.append(candidate)
        
        return unique_candidates
    
    async def run_llm2_metrics(self, candidates: List[CandidateIssue], 
                              files: List[Dict[str, str]]) -> List[Metric]:
        """
        Stage 2: Compute required metrics for candidates.
        
        Args:
            candidates: List of candidate issues
            files: List of files for context
            
        Returns:
            List of computed metrics
        """
        all_metrics = []
        
        # Build set of needed metrics from WCAG config
        needed_metrics = set()
        for rule_id, rule_config in self.wcag_config.get('rules', {}).items():
            needed_metrics.add(rule_config.get('metric'))
        
        # Group candidates by rule
        candidates_by_rule = {}
        for candidate in candidates:
            rule_id = candidate.rule_id
            if rule_id not in candidates_by_rule:
                candidates_by_rule[rule_id] = []
            candidates_by_rule[rule_id].append(candidate)
        
        for rule_id, rule_candidates in candidates_by_rule.items():
            rule_config = self.wcag_config.get('rules', {}).get(rule_id, {})
            metric_name = rule_config.get('metric')
            
            if not metric_name:
                continue
            
            for candidate in rule_candidates:
                # Try deterministic computation first
                deterministic_metrics = self._compute_deterministic_metrics(
                    metric_name, candidate, files
                )
                
                if deterministic_metrics:
                    all_metrics.extend(deterministic_metrics)
                else:
                    # Fall back to LLM computation
                    try:
                        if self.mock_mode or not self.deepseek_client.is_available():
                            llm_metrics = self._mock_metrics_response(metric_name, candidate)
                        else:
                            llm_metrics = await self.deepseek_client.compute_metrics(
                                candidate.dict(), 
                                [e.dict() for e in candidate.evidence],
                                [metric_name]
                            )
                        
                        # Fill in computed_from
                        for metric in llm_metrics:
                            metric.computed_from = candidate.evidence
                        
                        all_metrics.extend(llm_metrics)
                    
                    except Exception as e:
                        logger.warning(f"Failed to compute metrics for {candidate.id}: {e}")
                        continue
        
        return all_metrics
    
    async def run_llm3_validation(self, candidates: List[CandidateIssue], 
                                 metrics: List[Metric]) -> List[ValidationDecision]:
        """
        Stage 3: Validate candidates against WCAG thresholds.
        
        Args:
            candidates: List of candidate issues
            metrics: List of computed metrics
            
        Returns:
            List of validation decisions
        """
        decisions = []
        
        # Group metrics by candidate
        metrics_by_candidate = {}
        for metric in metrics:
            # Find the candidate this metric applies to
            for candidate in candidates:
                if any(span.file_path in str(metric.computed_from) for span in candidate.evidence):
                    if candidate.id not in metrics_by_candidate:
                        metrics_by_candidate[candidate.id] = []
                    metrics_by_candidate[candidate.id].append(metric)
                    break
        
        for candidate in candidates:
            candidate_metrics = metrics_by_candidate.get(candidate.id, [])
            rule_config = self.wcag_config.get('rules', {}).get(candidate.rule_id, {})
            
            if not rule_config:
                # Default decision for unknown rules
                decision = ValidationDecision(
                    candidate_id=candidate.id,
                    rule_id=candidate.rule_id,
                    passed=True,  # Assume pass for unknown rules
                    severity='info',
                    reasoning="Unknown rule - assuming compliance",
                    metrics_used={},
                    llm_model=self.model_map.llm3
                )
                decisions.append(decision)
                continue
            
            try:
                # Try deterministic validation first
                deterministic_decision = self._validate_deterministically(
                    candidate, candidate_metrics, rule_config
                )
                
                if deterministic_decision:
                    decisions.append(deterministic_decision)
                else:
                    # Fall back to LLM validation
                    if self.mock_mode or not self.xai_client.is_available():
                        decision = self._mock_validation_response(candidate, candidate_metrics, rule_config)
                    else:
                        decision = await self.xai_client.validate_decision(
                            candidate.dict(),
                            candidate_metrics,
                            rule_config
                        )
                    
                    decisions.append(decision)
            
            except Exception as e:
                logger.warning(f"Failed to validate {candidate.id}: {e}")
                # Default failed decision
                decision = ValidationDecision(
                    candidate_id=candidate.id,
                    rule_id=candidate.rule_id,
                    passed=False,
                    severity='moderate',
                    reasoning=f"Validation failed: {str(e)}",
                    metrics_used={},
                    llm_model=self.model_map.llm3
                )
                decisions.append(decision)
        
        return decisions
    
    async def run_llm4_fixes(self, decisions: List[ValidationDecision], 
                            files: List[Dict[str, str]]) -> List[FixSuggestion]:
        """
        Stage 4: Generate fix suggestions for failed decisions.
        
        Args:
            decisions: List of validation decisions
            files: List of files for context
            
        Returns:
            List of fix suggestions
        """
        fixes = []
        
        # Only generate fixes for failed decisions
        failed_decisions = [d for d in decisions if not d.passed]
        
        for decision in failed_decisions:
            try:
                if self.mock_mode or not self.openai_client.is_available():
                    fix = self._mock_fixes_response(decision, files)
                else:
                    fix = await self.openai_client.generate_fixes(
                        decision.dict(),
                        []  # Code spans would be retrieved from candidates
                    )
                
                # Validate the diff
                if fix.patch_unified_diff:
                    is_valid, error_msg = validate_diff(fix.patch_unified_diff, "")
                    if not is_valid:
                        fix.side_effects.append(f"Diff validation warning: {error_msg}")
                
                fixes.append(fix)
            
            except Exception as e:
                logger.warning(f"Failed to generate fix for {decision.candidate_id}: {e}")
                # Default fix suggestion
                fix = FixSuggestion(
                    candidate_id=decision.candidate_id,
                    rule_id=decision.rule_id,
                    patch_unified_diff="",
                    summary=f"Fix generation failed: {str(e)}",
                    side_effects=["Manual review required"],
                    test_suggestions=["Manual testing recommended"],
                    llm_model=self.model_map.llm4
                )
                fixes.append(fix)
        
        return fixes
    
    def _compute_deterministic_metrics(self, metric_name: str, candidate: CandidateIssue, 
                                     files: List[Dict[str, str]]) -> List[Metric]:
        """Compute metrics deterministically when possible."""
        metrics = []
        
        if metric_name == "contrast_ratio":
            # Try to compute contrast ratio from CSS
            for evidence in candidate.evidence:
                if evidence.file_path.endswith('.css'):
                    css_rules = parse_css_rules(evidence.code_snippet)
                    for selector, properties in css_rules.items():
                        foreground, background = self._extract_colors(properties)
                        if foreground and background:
                            ratio = contrast_ratio(foreground, background)
                            if ratio is not None:
                                # Determine if large text
                                font_size = extract_font_size(properties)
                                font_weight = extract_font_weight(properties)
                                is_large = is_large_text(font_size or 16, font_weight)
                                
                                metric = Metric(
                                    name="contrast_ratio",
                                    scope_id=f"{evidence.file_path}:{selector}",
                                    value=ratio,
                                    unit="ratio",
                                    computed_from=[evidence],
                                    notes=f"Large text: {is_large}",
                                    llm_model="deterministic"
                                )
                                metrics.append(metric)
        
        elif metric_name == "target_size_min_px":
            # Try to compute target size from CSS
            for evidence in candidate.evidence:
                if evidence.file_path.endswith('.css'):
                    css_rules = parse_css_rules(evidence.code_snippet)
                    for selector, properties in css_rules.items():
                        size = get_target_size(properties)
                        if size is not None:
                            metric = Metric(
                                name="target_size_min_px",
                                scope_id=f"{evidence.file_path}:{selector}",
                                value=size,
                                unit="px",
                                computed_from=[evidence],
                                notes="Computed from CSS dimensions",
                                llm_model="deterministic"
                            )
                            metrics.append(metric)
        
        return metrics
    
    def _validate_deterministically(self, candidate: CandidateIssue, metrics: List[Metric], 
                                  rule_config: Dict[str, Any]) -> Optional[ValidationDecision]:
        """Validate candidates deterministically when possible."""
        metric_name = rule_config.get('metric')
        comparator = rule_config.get('comparator')
        thresholds = rule_config.get('thresholds', {})
        
        if not metric_name or not comparator or not thresholds:
            return None
        
        # Find relevant metrics
        relevant_metrics = [m for m in metrics if m.name == metric_name]
        if not relevant_metrics:
            return None
        
        # Use the first relevant metric
        metric = relevant_metrics[0]
        value = metric.value
        
        # Determine which threshold to use
        threshold = thresholds.get('default')
        if 'normal_text' in thresholds and 'large_text' in thresholds:
            # Need to determine if text is large
            is_large = metric.notes and 'Large text: True' in metric.notes
            threshold = thresholds.get('large_text' if is_large else 'normal_text')
        
        if threshold is None:
            return None
        
        # Compare values
        passed = self._compare_values(value, comparator, threshold)
        
        return ValidationDecision(
            candidate_id=candidate.id,
            rule_id=candidate.rule_id,
            passed=passed,
            severity='minor' if passed else 'moderate',
            reasoning=f"Deterministic validation: {value} {comparator} {threshold}",
            metrics_used={metric_name: value},
            llm_model="deterministic"
        )
    
    def _compare_values(self, value: Any, comparator: str, threshold: Any) -> bool:
        """Compare values using the specified comparator."""
        try:
            if comparator == ">=":
                return float(value) >= float(threshold)
            elif comparator == "<=":
                return float(value) <= float(threshold)
            elif comparator == "==":
                return value == threshold
            elif comparator == "!=":
                return value != threshold
            else:
                return False
        except (ValueError, TypeError):
            return False
    
    def _extract_colors(self, properties: Dict[str, str]) -> tuple:
        """Extract foreground and background colors from CSS properties."""
        foreground = properties.get('color')
        background = properties.get('background-color') or properties.get('background')
        return foreground, background
    
    # Mock response methods for testing
    def _mock_discovery_response(self, file_path: str, start_line: int, end_line: int, 
                               chunk_content: str) -> List[CandidateIssue]:
        """Generate mock discovery responses for testing."""
        candidates = []
        
        # Simple heuristics for mock responses
        if 'img' in chunk_content and 'alt=' not in chunk_content:
            candidates.append(CandidateIssue(
                rule_id="1.1.1",
                title="Missing alt text",
                description="Image element lacks alt attribute",
                evidence=[{
                    "file_path": file_path,
                    "start_line": start_line,
                    "end_line": end_line,
                    "code_snippet": chunk_content
                }],
                tags=["images", "alt-text"],
                llm_model="mock",
                confidence="high"
            ))
        
        if 'color:' in chunk_content and 'background' in chunk_content:
            candidates.append(CandidateIssue(
                rule_id="1.4.3",
                title="Potential contrast issue",
                description="Text and background colors may have insufficient contrast",
                evidence=[{
                    "file_path": file_path,
                    "start_line": start_line,
                    "end_line": end_line,
                    "code_snippet": chunk_content
                }],
                tags=["contrast", "colors"],
                llm_model="mock",
                confidence="medium"
            ))
        
        return candidates
    
    def _mock_metrics_response(self, metric_name: str, candidate: CandidateIssue) -> List[Metric]:
        """Generate mock metrics responses for testing."""
        if metric_name == "contrast_ratio":
            return [Metric(
                name="contrast_ratio",
                scope_id=f"mock:{candidate.id}",
                value=2.5,  # Below threshold
                unit="ratio",
                computed_from=candidate.evidence,
                notes="Mock computation",
                llm_model="mock"
            )]
        elif metric_name == "target_size_min_px":
            return [Metric(
                name="target_size_min_px",
                scope_id=f"mock:{candidate.id}",
                value=24,  # Below 44px threshold
                unit="px",
                computed_from=candidate.evidence,
                notes="Mock computation",
                llm_model="mock"
            )]
        
        return []
    
    def _mock_validation_response(self, candidate: CandidateIssue, metrics: List[Metric], 
                                rule_config: Dict[str, Any]) -> ValidationDecision:
        """Generate mock validation responses for testing."""
        # Simple mock logic
        passed = len(metrics) == 0 or all(m.value is not None for m in metrics)
        
        return ValidationDecision(
            candidate_id=candidate.id,
            rule_id=candidate.rule_id,
            passed=passed,
            severity='minor' if passed else 'moderate',
            reasoning="Mock validation decision",
            metrics_used={m.name: m.value for m in metrics},
            llm_model="mock"
        )
    
    def _mock_fixes_response(self, decision: ValidationDecision, files: List[Dict[str, str]]) -> FixSuggestion:
        """Generate mock fix responses for testing."""
        return FixSuggestion(
            candidate_id=decision.candidate_id,
            rule_id=decision.rule_id,
            patch_unified_diff="--- a/test.css\n+++ b/test.css\n@@ -1,3 +1,3 @@\n .button {\n-  width: 24px;\n+  width: 44px;\n }",
            summary="Mock fix suggestion",
            side_effects=["May affect layout"],
            test_suggestions=["Test with screen reader", "Verify touch accessibility"],
            llm_model="mock"
        )
