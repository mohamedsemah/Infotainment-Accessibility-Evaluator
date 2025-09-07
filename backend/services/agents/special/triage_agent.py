"""
TriageAgent - Normalizes, scores, and merges findings by root cause.
"""

import re
from typing import List, Dict, Any, Optional, Set
from collections import defaultdict
from difflib import SequenceMatcher

from models.schemas import Finding, Cluster, ClusterKey, SeverityLevel, ConfidenceLevel, CriterionType
from utils.id_gen import generate_cluster_id, generate_finding_id

class TriageAgent:
    """Agent responsible for triaging and normalizing findings."""
    
    def __init__(self):
        self.findings = []
        self.clusters = []
    
    async def analyze(self, findings: List[Finding], upload_id: str) -> List[Cluster]:
        """Triage findings and create clusters."""
        self.findings = findings
        self.clusters = []
        
        # Normalize findings
        normalized_findings = self._normalize_findings(findings)
        
        # Group findings by criterion
        findings_by_criterion = self._group_by_criterion(normalized_findings)
        
        # Create clusters for each criterion
        for criterion, criterion_findings in findings_by_criterion.items():
            clusters = await self._create_clusters_for_criterion(criterion, criterion_findings)
            self.clusters.extend(clusters)
        
        return self.clusters
    
    def _normalize_findings(self, findings: List[Finding]) -> List[Finding]:
        """Normalize findings for consistent processing."""
        normalized = []
        
        for finding in findings:
            # Normalize selector
            finding.selector = self._normalize_selector(finding.selector)
            
            # Normalize details
            finding.details = self._normalize_details(finding.details)
            
            # Normalize component_id
            if not finding.component_id:
                finding.component_id = self._extract_component_id(finding.selector)
            
            # Normalize screen
            if not finding.screen:
                finding.screen = self._extract_screen(finding.selector)
            
            # Normalize state
            if not finding.state:
                finding.state = self._extract_state(finding.selector)
            
            # Normalize severity and confidence
            finding.severity = self._normalize_severity(finding.severity, finding.criterion)
            finding.confidence = self._normalize_confidence(finding.confidence, finding.criterion)
            
            normalized.append(finding)
        
        return normalized
    
    def _normalize_selector(self, selector: str) -> str:
        """Normalize CSS selector."""
        if not selector:
            return ""
        
        # Remove extra whitespace
        selector = re.sub(r'\s+', ' ', selector.strip())
        
        # Normalize class selectors
        selector = re.sub(r'\.([a-zA-Z0-9_-]+)', r'.\1', selector)
        
        # Normalize ID selectors
        selector = re.sub(r'#([a-zA-Z0-9_-]+)', r'#\1', selector)
        
        return selector
    
    def _normalize_details(self, details: str) -> str:
        """Normalize finding details."""
        if not details:
            return ""
        
        # Remove extra whitespace
        details = re.sub(r'\s+', ' ', details.strip())
        
        # Normalize common patterns
        details = re.sub(r'(\d+\.\d+)', r'\1', details)  # Normalize numbers
        details = re.sub(r'([a-zA-Z]+)\s*:\s*([a-zA-Z0-9]+)', r'\1: \2', details)  # Normalize key-value pairs
        
        return details
    
    def _extract_component_id(self, selector: str) -> str:
        """Extract component ID from selector."""
        if not selector:
            return ""
        
        # Look for ID selector
        id_match = re.search(r'#([a-zA-Z0-9_-]+)', selector)
        if id_match:
            return id_match.group(1)
        
        # Look for class selector
        class_match = re.search(r'\.([a-zA-Z0-9_-]+)', selector)
        if class_match:
            return class_match.group(1)
        
        return selector.split()[0] if selector else ""
    
    def _extract_screen(self, selector: str) -> str:
        """Extract screen name from selector."""
        if not selector:
            return "unknown"
        
        # Look for screen-related patterns
        screen_patterns = [
            r'screen-([a-zA-Z0-9_-]+)',
            r'page-([a-zA-Z0-9_-]+)',
            r'view-([a-zA-Z0-9_-]+)',
            r'panel-([a-zA-Z0-9_-]+)'
        ]
        
        for pattern in screen_patterns:
            match = re.search(pattern, selector)
            if match:
                return match.group(1)
        
        return "unknown"
    
    def _extract_state(self, selector: str) -> str:
        """Extract state from selector."""
        if not selector:
            return "default"
        
        # Look for state-related patterns
        state_patterns = [
            r':hover',
            r':focus',
            r':active',
            r':disabled',
            r':selected',
            r':expanded',
            r':collapsed'
        ]
        
        for pattern in state_patterns:
            if re.search(pattern, selector):
                return pattern[1:]  # Remove the colon
        
        return "default"
    
    def _normalize_severity(self, severity: SeverityLevel, criterion: CriterionType) -> SeverityLevel:
        """Normalize severity based on criterion."""
        # Some criteria are inherently more severe
        high_severity_criteria = [CriterionType.SEIZURE_SAFE, CriterionType.CONTRAST]
        
        if criterion in high_severity_criteria and severity == SeverityLevel.LOW:
            return SeverityLevel.MEDIUM
        
        return severity
    
    def _normalize_confidence(self, confidence: ConfidenceLevel, criterion: CriterionType) -> ConfidenceLevel:
        """Normalize confidence based on criterion."""
        # Some criteria have more reliable detection
        high_confidence_criteria = [CriterionType.CONTRAST, CriterionType.LANGUAGE]
        
        if criterion in high_confidence_criteria and confidence == ConfidenceLevel.LOW:
            return ConfidenceLevel.MEDIUM
        
        return confidence
    
    def _group_by_criterion(self, findings: List[Finding]) -> Dict[CriterionType, List[Finding]]:
        """Group findings by criterion."""
        grouped = defaultdict(list)
        
        for finding in findings:
            grouped[finding.criterion].append(finding)
        
        return dict(grouped)
    
    async def _create_clusters_for_criterion(self, criterion: CriterionType, findings: List[Finding]) -> List[Cluster]:
        """Create clusters for a specific criterion."""
        clusters = []
        
        if criterion == CriterionType.CONTRAST:
            clusters = await self._cluster_contrast_findings(findings)
        elif criterion == CriterionType.SEIZURE_SAFE:
            clusters = await self._cluster_seizure_findings(findings)
        elif criterion == CriterionType.LANGUAGE:
            clusters = await self._cluster_language_findings(findings)
        elif criterion == CriterionType.ARIA:
            clusters = await self._cluster_aria_findings(findings)
        elif criterion == CriterionType.STATE_EXPLORER:
            clusters = await self._cluster_state_findings(findings)
        else:
            # Generic clustering
            clusters = await self._cluster_generic_findings(findings)
        
        return clusters
    
    async def _cluster_contrast_findings(self, findings: List[Finding]) -> List[Cluster]:
        """Cluster contrast findings by color combination and context."""
        clusters = []
        color_groups = defaultdict(list)
        
        for finding in findings:
            # Extract color information from evidence
            color_key = self._extract_contrast_key(finding)
            color_groups[color_key].append(finding)
        
        for color_key, group_findings in color_groups.items():
            if len(group_findings) > 0:
                cluster = await self._create_contrast_cluster(color_key, group_findings)
                clusters.append(cluster)
        
        return clusters
    
    async def _cluster_seizure_findings(self, findings: List[Finding]) -> List[Cluster]:
        """Cluster seizure findings by animation type and frequency."""
        clusters = []
        animation_groups = defaultdict(list)
        
        for finding in findings:
            # Extract animation information
            animation_key = self._extract_seizure_key(finding)
            animation_groups[animation_key].append(finding)
        
        for animation_key, group_findings in animation_groups.items():
            if len(group_findings) > 0:
                cluster = await self._create_seizure_cluster(animation_key, group_findings)
                clusters.append(cluster)
        
        return clusters
    
    async def _cluster_language_findings(self, findings: List[Finding]) -> List[Cluster]:
        """Cluster language findings by language tag and scope."""
        clusters = []
        language_groups = defaultdict(list)
        
        for finding in findings:
            # Extract language information
            language_key = self._extract_language_key(finding)
            language_groups[language_key].append(finding)
        
        for language_key, group_findings in language_groups.items():
            if len(group_findings) > 0:
                cluster = await self._create_language_cluster(language_key, group_findings)
                clusters.append(cluster)
        
        return clusters
    
    async def _cluster_aria_findings(self, findings: List[Finding]) -> List[Cluster]:
        """Cluster ARIA findings by role and attribute type."""
        clusters = []
        aria_groups = defaultdict(list)
        
        for finding in findings:
            # Extract ARIA information
            aria_key = self._extract_aria_key(finding)
            aria_groups[aria_key].append(finding)
        
        for aria_key, group_findings in aria_groups.items():
            if len(group_findings) > 0:
                cluster = await self._create_aria_cluster(aria_key, group_findings)
                clusters.append(cluster)
        
        return clusters
    
    async def _cluster_state_findings(self, findings: List[Finding]) -> List[Cluster]:
        """Cluster state findings by state type and element."""
        clusters = []
        state_groups = defaultdict(list)
        
        for finding in findings:
            # Extract state information
            state_key = self._extract_state_key(finding)
            state_groups[state_key].append(finding)
        
        for state_key, group_findings in state_groups.items():
            if len(group_findings) > 0:
                cluster = await self._create_state_cluster(state_key, group_findings)
                clusters.append(cluster)
        
        return clusters
    
    async def _cluster_generic_findings(self, findings: List[Finding]) -> List[Cluster]:
        """Generic clustering for other criteria."""
        clusters = []
        
        # Group by similar details
        detail_groups = defaultdict(list)
        
        for finding in findings:
            # Create a simplified key from details
            detail_key = self._simplify_details(finding.details)
            detail_groups[detail_key].append(finding)
        
        for detail_key, group_findings in detail_groups.items():
            if len(group_findings) > 0:
                cluster = await self._create_generic_cluster(detail_key, group_findings)
                clusters.append(cluster)
        
        return clusters
    
    def _extract_contrast_key(self, finding: Finding) -> str:
        """Extract key for contrast clustering."""
        # Extract color information from evidence
        colors = []
        for evidence in finding.evidence:
            if evidence.metrics:
                fg_color = evidence.metrics.get('foreground', {}).get('hex', '')
                bg_color = evidence.metrics.get('background', {}).get('hex', '')
                if fg_color and bg_color:
                    colors.append(f"{fg_color}-{bg_color}")
        
        if colors:
            color_combo = colors[0]  # Use first color combination
        else:
            color_combo = "unknown"
        
        return f"{finding.criterion.value}:{color_combo}:{finding.component_id}:{finding.state}"
    
    def _extract_seizure_key(self, finding: Finding) -> str:
        """Extract key for seizure clustering."""
        # Extract animation information from evidence
        animation_type = "unknown"
        frequency = "unknown"
        
        for evidence in finding.evidence:
            if evidence.metrics:
                animation_type = evidence.metrics.get('animation_type', 'unknown')
                frequency = evidence.metrics.get('frequency', 'unknown')
                break
        
        return f"{finding.criterion.value}:{animation_type}:{frequency}:{finding.component_id}"
    
    def _extract_language_key(self, finding: Finding) -> str:
        """Extract key for language clustering."""
        # Extract language information from evidence
        lang_value = "unknown"
        scope = "unknown"
        
        for evidence in finding.evidence:
            if evidence.metrics:
                lang_value = evidence.metrics.get('lang_value', 'unknown')
                scope = evidence.metrics.get('scope', 'unknown')
                break
        
        return f"{finding.criterion.value}:{lang_value}:{scope}"
    
    def _extract_aria_key(self, finding: Finding) -> str:
        """Extract key for ARIA clustering."""
        # Extract ARIA information from evidence
        role = "unknown"
        attribute = "unknown"
        
        for evidence in finding.evidence:
            if evidence.metrics:
                role = evidence.metrics.get('role', 'unknown')
                attribute = evidence.metrics.get('attribute', 'unknown')
                break
        
        return f"{finding.criterion.value}:{role}:{attribute}"
    
    def _extract_state_key(self, finding: Finding) -> str:
        """Extract key for state clustering."""
        return f"{finding.criterion.value}:{finding.component_id}:{finding.state}"
    
    def _simplify_details(self, details: str) -> str:
        """Simplify details for generic clustering."""
        # Remove specific values and keep general patterns
        simplified = re.sub(r'\d+\.\d+', 'X.X', details)  # Replace numbers
        simplified = re.sub(r'"[^"]*"', '"..."', simplified)  # Replace quoted strings
        simplified = re.sub(r'[a-zA-Z0-9_-]+@[a-zA-Z0-9_-]+', 'email', simplified)  # Replace emails
        
        return simplified
    
    async def _create_contrast_cluster(self, color_key: str, findings: List[Finding]) -> Cluster:
        """Create a contrast cluster."""
        cluster_id = generate_cluster_id()
        
        # Extract key components
        parts = color_key.split(':')
        criterion = CriterionType(parts[0])
        color_combo = parts[1]
        component_id = parts[2]
        state = parts[3]
        
        # Create cluster key
        cluster_key = ClusterKey(
            criterion=criterion,
            key_components={
                "color_combo": color_combo,
                "component_id": component_id,
                "state": state
            },
            root_cause=f"Contrast issue with {color_combo} in {component_id} ({state})"
        )
        
        # Calculate cluster severity and confidence
        severities = [f.severity for f in findings]
        confidences = [f.confidence for f in findings]
        
        cluster_severity = self._calculate_cluster_severity(severities)
        cluster_confidence = self._calculate_cluster_confidence(confidences)
        
        # Create summary
        summary = f"Contrast issues with {color_combo} color combination in {component_id} component"
        if state != "default":
            summary += f" ({state} state)"
        
        return Cluster(
            id=cluster_id,
            criterion=criterion,
            key=cluster_key,
            summary=summary,
            severity=cluster_severity,
            confidence=cluster_confidence,
            occurrences=findings,
            wcag_criterion="1.4.3"
        )
    
    async def _create_seizure_cluster(self, animation_key: str, findings: List[Finding]) -> Cluster:
        """Create a seizure cluster."""
        cluster_id = generate_cluster_id()
        
        # Extract key components
        parts = animation_key.split(':')
        criterion = CriterionType(parts[0])
        animation_type = parts[1]
        frequency = parts[2]
        component_id = parts[3]
        
        # Create cluster key
        cluster_key = ClusterKey(
            criterion=criterion,
            key_components={
                "animation_type": animation_type,
                "frequency": frequency,
                "component_id": component_id
            },
            root_cause=f"Seizure risk with {animation_type} animation at {frequency}Hz in {component_id}"
        )
        
        # Calculate cluster severity and confidence
        severities = [f.severity for f in findings]
        confidences = [f.confidence for f in findings]
        
        cluster_severity = self._calculate_cluster_severity(severities)
        cluster_confidence = self._calculate_cluster_confidence(confidences)
        
        # Create summary
        summary = f"Seizure risk with {animation_type} animation at {frequency}Hz in {component_id}"
        
        return Cluster(
            id=cluster_id,
            criterion=criterion,
            key=cluster_key,
            summary=summary,
            severity=cluster_severity,
            confidence=cluster_confidence,
            occurrences=findings,
            wcag_criterion="2.3.1"
        )
    
    async def _create_language_cluster(self, language_key: str, findings: List[Finding]) -> Cluster:
        """Create a language cluster."""
        cluster_id = generate_cluster_id()
        
        # Extract key components
        parts = language_key.split(':')
        criterion = CriterionType(parts[0])
        lang_value = parts[1]
        scope = parts[2]
        
        # Create cluster key
        cluster_key = ClusterKey(
            criterion=criterion,
            key_components={
                "lang_value": lang_value,
                "scope": scope
            },
            root_cause=f"Language issue with {lang_value} in {scope}"
        )
        
        # Calculate cluster severity and confidence
        severities = [f.severity for f in findings]
        confidences = [f.confidence for f in findings]
        
        cluster_severity = self._calculate_cluster_severity(severities)
        cluster_confidence = self._calculate_cluster_confidence(confidences)
        
        # Create summary
        summary = f"Language issues with {lang_value} in {scope}"
        
        return Cluster(
            id=cluster_id,
            criterion=criterion,
            key=cluster_key,
            summary=summary,
            severity=cluster_severity,
            confidence=cluster_confidence,
            occurrences=findings,
            wcag_criterion="3.1.1"
        )
    
    async def _create_aria_cluster(self, aria_key: str, findings: List[Finding]) -> Cluster:
        """Create an ARIA cluster."""
        cluster_id = generate_cluster_id()
        
        # Extract key components
        parts = aria_key.split(':')
        criterion = CriterionType(parts[0])
        role = parts[1]
        attribute = parts[2]
        
        # Create cluster key
        cluster_key = ClusterKey(
            criterion=criterion,
            key_components={
                "role": role,
                "attribute": attribute
            },
            root_cause=f"ARIA issue with {role} role and {attribute} attribute"
        )
        
        # Calculate cluster severity and confidence
        severities = [f.severity for f in findings]
        confidences = [f.confidence for f in findings]
        
        cluster_severity = self._calculate_cluster_severity(severities)
        cluster_confidence = self._calculate_cluster_confidence(confidences)
        
        # Create summary
        summary = f"ARIA issues with {role} role and {attribute} attribute"
        
        return Cluster(
            id=cluster_id,
            criterion=criterion,
            key=cluster_key,
            summary=summary,
            severity=cluster_severity,
            confidence=cluster_confidence,
            occurrences=findings,
            wcag_criterion="4.1.2"
        )
    
    async def _create_state_cluster(self, state_key: str, findings: List[Finding]) -> Cluster:
        """Create a state cluster."""
        cluster_id = generate_cluster_id()
        
        # Extract key components
        parts = state_key.split(':')
        criterion = CriterionType(parts[0])
        component_id = parts[1]
        state = parts[2]
        
        # Create cluster key
        cluster_key = ClusterKey(
            criterion=criterion,
            key_components={
                "component_id": component_id,
                "state": state
            },
            root_cause=f"State issue with {component_id} in {state} state"
        )
        
        # Calculate cluster severity and confidence
        severities = [f.severity for f in findings]
        confidences = [f.confidence for f in findings]
        
        cluster_severity = self._calculate_cluster_severity(severities)
        cluster_confidence = self._calculate_cluster_confidence(confidences)
        
        # Create summary
        summary = f"State issues with {component_id} in {state} state"
        
        return Cluster(
            id=cluster_id,
            criterion=criterion,
            key=cluster_key,
            summary=summary,
            severity=cluster_severity,
            confidence=cluster_confidence,
            occurrences=findings,
            wcag_criterion="4.1.2"
        )
    
    async def _create_generic_cluster(self, detail_key: str, findings: List[Finding]) -> Cluster:
        """Create a generic cluster."""
        cluster_id = generate_cluster_id()
        
        # Use the first finding's criterion
        criterion = findings[0].criterion
        
        # Create cluster key
        cluster_key = ClusterKey(
            criterion=criterion,
            key_components={
                "detail_pattern": detail_key
            },
            root_cause=f"Generic {criterion.value} issue"
        )
        
        # Calculate cluster severity and confidence
        severities = [f.severity for f in findings]
        confidences = [f.confidence for f in findings]
        
        cluster_severity = self._calculate_cluster_severity(severities)
        cluster_confidence = self._calculate_cluster_confidence(confidences)
        
        # Create summary
        summary = f"Multiple {criterion.value} issues with similar patterns"
        
        return Cluster(
            id=cluster_id,
            criterion=criterion,
            key=cluster_key,
            summary=summary,
            severity=cluster_severity,
            confidence=cluster_confidence,
            occurrences=findings,
            wcag_criterion="N/A"
        )
    
    def _calculate_cluster_severity(self, severities: List[SeverityLevel]) -> SeverityLevel:
        """Calculate cluster severity from individual severities."""
        if not severities:
            return SeverityLevel.LOW
        
        # Use the highest severity
        severity_order = [SeverityLevel.LOW, SeverityLevel.MEDIUM, SeverityLevel.HIGH, SeverityLevel.CRITICAL]
        max_severity = max(severities, key=lambda s: severity_order.index(s))
        
        return max_severity
    
    def _calculate_cluster_confidence(self, confidences: List[ConfidenceLevel]) -> ConfidenceLevel:
        """Calculate cluster confidence from individual confidences."""
        if not confidences:
            return ConfidenceLevel.LOW
        
        # Use the average confidence
        confidence_order = [ConfidenceLevel.LOW, ConfidenceLevel.MEDIUM, ConfidenceLevel.HIGH]
        avg_confidence = sum(confidence_order.index(c) for c in confidences) / len(confidences)
        
        if avg_confidence >= 2:
            return ConfidenceLevel.HIGH
        elif avg_confidence >= 1:
            return ConfidenceLevel.MEDIUM
        else:
            return ConfidenceLevel.LOW
