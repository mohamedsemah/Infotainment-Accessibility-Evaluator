from typing import List, Dict, Any, Optional
from models.schemas import Finding, Cluster
from utils.id_gen import generate_id
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class ClusterFindingsService:
    """Service for clustering findings by root cause and similarity"""
    
    def __init__(self):
        self.clusters: Dict[str, Cluster] = {}
    
    async def cluster_findings(
        self,
        findings: List[Finding],
        clustering_method: str = "semantic",
        similarity_threshold: float = 0.7
    ) -> List[Cluster]:
        """
        Cluster findings by root cause and similarity
        """
        logger.info(f"Clustering {len(findings)} findings using {clustering_method} method")
        
        if clustering_method == "semantic":
            return await self._cluster_by_semantic_similarity(findings, similarity_threshold)
        elif clustering_method == "rule_based":
            return await self._cluster_by_rules(findings)
        elif clustering_method == "hybrid":
            return await self._cluster_hybrid(findings, similarity_threshold)
        else:
            raise ValueError(f"Unknown clustering method: {clustering_method}")
    
    async def _cluster_by_semantic_similarity(
        self,
        findings: List[Finding],
        similarity_threshold: float
    ) -> List[Cluster]:
        """Cluster findings using semantic similarity"""
        clusters = []
        processed_findings = set()
        
        for i, finding in enumerate(findings):
            if finding.id in processed_findings:
                continue
                
            # Create new cluster
            cluster = Cluster(
                id=generate_id(),
                title=self._generate_cluster_title(finding),
                description=self._generate_cluster_description(finding),
                severity=finding.severity,
                confidence=finding.confidence,
                agent=finding.agent,
                wcag_criterion=finding.wcag_criterion,
                root_cause=self._extract_root_cause(finding),
                impact=self._assess_impact(finding),
                priority=self._calculate_priority(finding),
                status="open",
                occurrences=[finding],
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            
            # Find similar findings
            similar_findings = []
            for j, other_finding in enumerate(findings[i+1:], i+1):
                if other_finding.id in processed_findings:
                    continue
                    
                similarity = self._calculate_similarity(finding, other_finding)
                if similarity >= similarity_threshold:
                    similar_findings.append(other_finding)
                    processed_findings.add(other_finding.id)
            
            # Add similar findings to cluster
            cluster.occurrences.extend(similar_findings)
            processed_findings.add(finding.id)
            clusters.append(cluster)
        
        logger.info(f"Created {len(clusters)} clusters from {len(findings)} findings")
        return clusters
    
    async def _cluster_by_rules(self, findings: List[Finding]) -> List[Cluster]:
        """Cluster findings using rule-based approach"""
        clusters = []
        
        # Group by agent and WCAG criterion
        grouped = {}
        for finding in findings:
            key = (finding.agent, finding.wcag_criterion)
            if key not in grouped:
                grouped[key] = []
            grouped[key].append(finding)
        
        # Create clusters for each group
        for (agent, wcag_criterion), group_findings in grouped.items():
            if not group_findings:
                continue
                
            # Use first finding as template
            template = group_findings[0]
            
            cluster = Cluster(
                id=generate_id(),
                title=self._generate_cluster_title(template),
                description=self._generate_cluster_description(template),
                severity=self._get_highest_severity(group_findings),
                confidence=self._get_highest_confidence(group_findings),
                agent=agent,
                wcag_criterion=wcag_criterion,
                root_cause=self._extract_root_cause(template),
                impact=self._assess_impact(template),
                priority=self._calculate_priority(template),
                status="open",
                occurrences=group_findings,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            clusters.append(cluster)
        
        logger.info(f"Created {len(clusters)} rule-based clusters")
        return clusters
    
    async def _cluster_hybrid(
        self,
        findings: List[Finding],
        similarity_threshold: float
    ) -> List[Cluster]:
        """Hybrid clustering approach combining rules and similarity"""
        # First, do rule-based clustering
        rule_clusters = await self._cluster_by_rules(findings)
        
        # Then, merge similar clusters
        merged_clusters = []
        processed_clusters = set()
        
        for i, cluster in enumerate(rule_clusters):
            if cluster.id in processed_clusters:
                continue
                
            # Find similar clusters
            similar_clusters = []
            for j, other_cluster in enumerate(rule_clusters[i+1:], i+1):
                if other_cluster.id in processed_clusters:
                    continue
                    
                if self._are_clusters_similar(cluster, other_cluster, similarity_threshold):
                    similar_clusters.append(other_cluster)
                    processed_clusters.add(other_cluster.id)
            
            # Merge similar clusters
            if similar_clusters:
                merged_cluster = self._merge_clusters([cluster] + similar_clusters)
                merged_clusters.append(merged_cluster)
            else:
                merged_clusters.append(cluster)
            
            processed_clusters.add(cluster.id)
        
        logger.info(f"Created {len(merged_clusters)} hybrid clusters")
        return merged_clusters
    
    def _calculate_similarity(self, finding1: Finding, finding2: Finding) -> float:
        """Calculate similarity between two findings"""
        similarity = 0.0
        
        # Agent similarity
        if finding1.agent == finding2.agent:
            similarity += 0.3
        
        # WCAG criterion similarity
        if finding1.wcag_criterion == finding2.wcag_criterion:
            similarity += 0.3
        
        # Severity similarity
        if finding1.severity == finding2.severity:
            similarity += 0.2
        
        # Element similarity
        if finding1.element == finding2.element:
            similarity += 0.2
        
        return similarity
    
    def _are_clusters_similar(
        self,
        cluster1: Cluster,
        cluster2: Cluster,
        threshold: float
    ) -> bool:
        """Check if two clusters are similar enough to merge"""
        similarity = 0.0
        
        # Agent similarity
        if cluster1.agent == cluster2.agent:
            similarity += 0.3
        
        # WCAG criterion similarity
        if cluster1.wcag_criterion == cluster2.wcag_criterion:
            similarity += 0.3
        
        # Severity similarity
        if cluster1.severity == cluster2.severity:
            similarity += 0.2
        
        # Root cause similarity
        if cluster1.root_cause == cluster2.root_cause:
            similarity += 0.2
        
        return similarity >= threshold
    
    def _generate_cluster_title(self, finding: Finding) -> str:
        """Generate a cluster title from a finding"""
        if finding.element:
            return f"{finding.element} {finding.wcag_criterion} issues"
        return f"{finding.wcag_criterion} accessibility issues"
    
    def _generate_cluster_description(self, finding: Finding) -> str:
        """Generate a cluster description from a finding"""
        return f"Multiple instances of {finding.wcag_criterion} violations found in {finding.agent} analysis"
    
    def _extract_root_cause(self, finding: Finding) -> str:
        """Extract root cause from finding"""
        if finding.element:
            return f"Missing or incorrect {finding.element} implementation"
        return f"WCAG {finding.wcag_criterion} compliance issue"
    
    def _assess_impact(self, finding: Finding) -> str:
        """Assess the impact of a finding"""
        if finding.severity == "critical":
            return "Blocks users with disabilities from using the interface"
        elif finding.severity == "high":
            return "Significantly impacts user experience for users with disabilities"
        elif finding.severity == "medium":
            return "Moderately impacts accessibility and user experience"
        else:
            return "Minor impact on accessibility"
    
    def _calculate_priority(self, finding: Finding) -> str:
        """Calculate priority based on severity and confidence"""
        if finding.severity == "critical" and finding.confidence == "high":
            return "urgent"
        elif finding.severity in ["critical", "high"] and finding.confidence in ["high", "medium"]:
            return "high"
        elif finding.severity == "medium" and finding.confidence == "high":
            return "medium"
        else:
            return "low"
    
    def _get_highest_severity(self, findings: List[Finding]) -> str:
        """Get the highest severity from a list of findings"""
        severity_order = ["critical", "high", "medium", "low"]
        for severity in severity_order:
            if any(f.severity == severity for f in findings):
                return severity
        return "low"
    
    def _get_highest_confidence(self, findings: List[Finding]) -> str:
        """Get the highest confidence from a list of findings"""
        confidence_order = ["high", "medium", "low"]
        for confidence in confidence_order:
            if any(f.confidence == confidence for f in findings):
                return confidence
        return "low"
    
    def _merge_clusters(self, clusters: List[Cluster]) -> Cluster:
        """Merge multiple clusters into one"""
        if not clusters:
            raise ValueError("Cannot merge empty cluster list")
        
        # Use first cluster as base
        merged = clusters[0]
        
        # Merge occurrences from all clusters
        all_occurrences = []
        for cluster in clusters:
            all_occurrences.extend(cluster.occurrences)
        
        merged.occurrences = all_occurrences
        
        # Update metadata
        merged.title = f"Merged: {merged.title}"
        merged.description = f"Combined cluster containing {len(all_occurrences)} occurrences"
        merged.severity = self._get_highest_severity(all_occurrences)
        merged.confidence = self._get_highest_confidence(all_occurrences)
        merged.updated_at = datetime.now()
        
        return merged
    
    async def get_cluster(self, cluster_id: str) -> Optional[Cluster]:
        """Get a cluster by ID"""
        return self.clusters.get(cluster_id)
    
    async def update_cluster(self, cluster_id: str, cluster: Cluster) -> Optional[Cluster]:
        """Update a cluster"""
        if cluster_id in self.clusters:
            cluster.updated_at = datetime.now()
            self.clusters[cluster_id] = cluster
            return cluster
        return None
    
    async def delete_cluster(self, cluster_id: str) -> bool:
        """Delete a cluster"""
        if cluster_id in self.clusters:
            del self.clusters[cluster_id]
            return True
        return False
    
    async def merge_clusters(
        self,
        source_cluster_id: str,
        target_cluster_ids: List[str]
    ) -> Optional[Cluster]:
        """Merge multiple clusters into one"""
        clusters_to_merge = []
        
        # Get source cluster
        if source_cluster_id in self.clusters:
            clusters_to_merge.append(self.clusters[source_cluster_id])
        else:
            return None
        
        # Get target clusters
        for target_id in target_cluster_ids:
            if target_id in self.clusters:
                clusters_to_merge.append(self.clusters[target_id])
        
        if len(clusters_to_merge) < 2:
            return None
        
        # Merge clusters
        merged_cluster = self._merge_clusters(clusters_to_merge)
        
        # Update storage
        self.clusters[merged_cluster.id] = merged_cluster
        
        # Remove old clusters
        for cluster in clusters_to_merge:
            if cluster.id != merged_cluster.id:
                del self.clusters[cluster.id]
        
        return merged_cluster
    
    async def split_cluster(
        self,
        cluster_id: str,
        split_criteria: Dict[str, Any]
    ) -> Optional[List[Cluster]]:
        """Split a cluster into multiple clusters"""
        if cluster_id not in self.clusters:
            return None
        
        cluster = self.clusters[cluster_id]
        new_clusters = []
        
        # Group occurrences by split criteria
        groups = {}
        for finding in cluster.occurrences:
            key = self._get_split_key(finding, split_criteria)
            if key not in groups:
                groups[key] = []
            groups[key].append(finding)
        
        # Create new clusters
        for key, findings in groups.items():
            if not findings:
                continue
                
            new_cluster = Cluster(
                id=generate_id(),
                title=f"{cluster.title} - {key}",
                description=f"Split from cluster {cluster_id}",
                severity=cluster.severity,
                confidence=cluster.confidence,
                agent=cluster.agent,
                wcag_criterion=cluster.wcag_criterion,
                root_cause=cluster.root_cause,
                impact=cluster.impact,
                priority=cluster.priority,
                status=cluster.status,
                occurrences=findings,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            new_clusters.append(new_cluster)
            self.clusters[new_cluster.id] = new_cluster
        
        # Remove original cluster
        del self.clusters[cluster_id]
        
        return new_clusters
    
    def _get_split_key(self, finding: Finding, criteria: Dict[str, Any]) -> str:
        """Get split key for a finding based on criteria"""
        if "element" in criteria:
            return finding.element or "unknown"
        elif "severity" in criteria:
            return finding.severity
        elif "confidence" in criteria:
            return finding.confidence
        else:
            return "default"
