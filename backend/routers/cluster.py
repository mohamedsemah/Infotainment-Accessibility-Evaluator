from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import List
from models.schemas import Finding, Cluster, ClusterRequest, ClusterResponse
from services.clustering.cluster_findings import ClusterFindingsService
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

# Initialize clustering service
cluster_service = ClusterFindingsService()

@router.post("/cluster", response_model=ClusterResponse)
async def cluster_findings(
    request: ClusterRequest,
    background_tasks: BackgroundTasks
):
    """
    Cluster findings by root cause and similarity
    """
    try:
        logger.info(f"Clustering {len(request.findings)} findings")
        print(f"DEBUG: Cluster request - findings count: {len(request.findings)}")
        print(f"DEBUG: Cluster request - method: {request.clustering_method}")
        print(f"DEBUG: Cluster request - threshold: {request.similarity_threshold}")
        
        # Perform clustering
        clusters = await cluster_service.cluster_findings(
            findings=request.findings,
            clustering_method=request.clustering_method,
            similarity_threshold=request.similarity_threshold
        )
        
        # Calculate statistics
        total_clusters = len(clusters)
        total_findings = sum(len(cluster.occurrences) for cluster in clusters)
        
        # Group by severity
        severity_counts = {}
        for cluster in clusters:
            severity = cluster.severity
            severity_counts[severity] = severity_counts.get(severity, 0) + len(cluster.occurrences)
        
        # Group by agent
        agent_counts = {}
        for cluster in clusters:
            agent = cluster.occurrences[0].agent if cluster.occurrences else 'unknown'
            agent_counts[agent] = agent_counts.get(agent, 0) + len(cluster.occurrences)
        
        response = ClusterResponse(
            clusters=clusters,
            statistics={
                "total_clusters": total_clusters,
                "total_findings": total_findings,
                "severity_counts": severity_counts,
                "agent_counts": agent_counts,
                "clustering_method": request.clustering_method,
                "similarity_threshold": request.similarity_threshold
            }
        )
        
        logger.info(f"Clustering completed: {total_clusters} clusters, {total_findings} findings")
        return response
        
    except Exception as e:
        logger.error(f"Clustering failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Clustering failed: {str(e)}")

@router.get("/cluster/{cluster_id}", response_model=Cluster)
async def get_cluster(cluster_id: str):
    """
    Get a specific cluster by ID
    """
    try:
        cluster = await cluster_service.get_cluster(cluster_id)
        if not cluster:
            raise HTTPException(status_code=404, detail="Cluster not found")
        return cluster
    except Exception as e:
        logger.error(f"Failed to get cluster {cluster_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get cluster: {str(e)}")

@router.put("/cluster/{cluster_id}", response_model=Cluster)
async def update_cluster(
    cluster_id: str,
    cluster: Cluster
):
    """
    Update a cluster
    """
    try:
        updated_cluster = await cluster_service.update_cluster(cluster_id, cluster)
        if not updated_cluster:
            raise HTTPException(status_code=404, detail="Cluster not found")
        return updated_cluster
    except Exception as e:
        logger.error(f"Failed to update cluster {cluster_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to update cluster: {str(e)}")

@router.delete("/cluster/{cluster_id}")
async def delete_cluster(cluster_id: str):
    """
    Delete a cluster
    """
    try:
        success = await cluster_service.delete_cluster(cluster_id)
        if not success:
            raise HTTPException(status_code=404, detail="Cluster not found")
        return {"message": "Cluster deleted successfully"}
    except Exception as e:
        logger.error(f"Failed to delete cluster {cluster_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to delete cluster: {str(e)}")

@router.post("/cluster/{cluster_id}/merge")
async def merge_clusters(
    cluster_id: str,
    target_cluster_ids: List[str]
):
    """
    Merge multiple clusters into one
    """
    try:
        merged_cluster = await cluster_service.merge_clusters(
            source_cluster_id=cluster_id,
            target_cluster_ids=target_cluster_ids
        )
        if not merged_cluster:
            raise HTTPException(status_code=404, detail="Source cluster not found")
        return merged_cluster
    except Exception as e:
        logger.error(f"Failed to merge clusters: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to merge clusters: {str(e)}")

@router.post("/cluster/{cluster_id}/split")
async def split_cluster(
    cluster_id: str,
    split_criteria: dict
):
    """
    Split a cluster into multiple clusters
    """
    try:
        new_clusters = await cluster_service.split_cluster(
            cluster_id=cluster_id,
            split_criteria=split_criteria
        )
        if not new_clusters:
            raise HTTPException(status_code=404, detail="Cluster not found")
        return {"clusters": new_clusters}
    except Exception as e:
        logger.error(f"Failed to split cluster: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to split cluster: {str(e)}")
