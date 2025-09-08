"""
Run router for executing agent plans.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Dict, Any, List
import asyncio

from models.schemas import AgentResult, AgentPlan, ErrorResponse
from services.agents.super_agent import SuperAgent
from routers.upload import get_upload_path
from routers.plan import create_agent_plan

router = APIRouter()

# Global SuperAgent instance
super_agent = None

def get_super_agent() -> SuperAgent:
    """Get or create SuperAgent instance."""
    global super_agent
    if super_agent is None:
        super_agent = SuperAgent()
    return super_agent

@router.post("/run", response_model=Dict[str, Any])
async def run_agents(
    upload_id: str = Query(..., description="Upload ID to analyze")
):
    """Run agents according to a plan."""
    try:
        # Get upload path
        upload_path = get_upload_path(upload_id)
        if not upload_path:
            raise HTTPException(status_code=404, detail="Upload not found")
        
        # Create plan
        from routers.plan import create_agent_plan
        plan = await create_agent_plan(upload_id)
        
        # Get SuperAgent
        agent = get_super_agent()
        
        # Execute plan
        results = await agent.execute_plan(plan, upload_path)
        
        print(f"DEBUG: Run router returning results with {len(results.get('all_findings', []))} findings")
        print(f"DEBUG: Run router results keys: {list(results.keys())}")
        if results.get('all_findings'):
            print(f"DEBUG: First finding in results: {results['all_findings'][0] if results['all_findings'] else 'None'}")
        
        return results
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Agent execution failed",
                "details": str(e)
            }
        )

@router.get("/run/{upload_id}/status")
async def get_execution_status(upload_id: str):
    """Get execution status for an upload."""
    try:
        agent = get_super_agent()
        status = await agent.get_all_agents_status()
        
        return {
            "upload_id": upload_id,
            "agents": status,
            "overall_status": "running" if any(agent["status"] == "running" for agent in status.values()) else "completed"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Failed to get execution status",
                "details": str(e)
            }
        )

@router.get("/run/{upload_id}/results")
async def get_execution_results(upload_id: str):
    """Get execution results for an upload."""
    try:
        agent = get_super_agent()
        
        # This would typically fetch from a database
        # For now, return a placeholder
        return {
            "upload_id": upload_id,
            "results": {},
            "findings": [],
            "clusters": [],
            "patches": []
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Failed to get execution results",
                "details": str(e)
            }
        )

@router.post("/run/{upload_id}/reset")
async def reset_execution(upload_id: str):
    """Reset execution for an upload."""
    try:
        agent = get_super_agent()
        success = await agent.reset_all_agents()
        
        if success:
            return {"message": "Execution reset successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to reset execution")
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Failed to reset execution",
                "details": str(e)
            }
        )

@router.get("/agents")
async def list_agents():
    """List all available agents."""
    try:
        agent = get_super_agent()
        capabilities = await agent.get_agent_capabilities()
        
        return {
            "agents": capabilities,
            "total_count": len(capabilities)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Failed to list agents",
                "details": str(e)
            }
        )

@router.get("/agents/{agent_name}")
async def get_agent_info(agent_name: str):
    """Get information about a specific agent."""
    try:
        agent = get_super_agent()
        capabilities = await agent.get_agent_capabilities()
        
        if agent_name not in capabilities:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        return {
            "name": agent_name,
            "capabilities": capabilities[agent_name],
            "status": await agent.get_agent_status(agent_name)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Failed to get agent info",
                "details": str(e)
            }
        )

@router.post("/agents/{agent_name}/reset")
async def reset_agent(agent_name: str):
    """Reset a specific agent."""
    try:
        agent = get_super_agent()
        success = await agent.reset_agent(agent_name)
        
        if success:
            return {"message": f"Agent {agent_name} reset successfully"}
        else:
            raise HTTPException(status_code=404, detail="Agent not found")
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Failed to reset agent",
                "details": str(e)
            }
        )

@router.post("/agents/{agent_name}/run")
async def run_single_agent(
    agent_name: str,
    upload_id: str = Query(..., description="Upload ID to analyze")
):
    """Run a single agent."""
    try:
        # Get upload path
        upload_path = get_upload_path(upload_id)
        if not upload_path:
            raise HTTPException(status_code=404, detail="Upload not found")
        
        # Get SuperAgent
        agent = get_super_agent()
        
        # Check if agent exists
        if agent_name not in agent.agents:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        # Create a simple plan for single agent
        from models.schemas import AgentPlan
        plan = AgentPlan(
            upload_id=upload_id,
            agents_to_run=[agent_name],
            execution_order=[agent_name],
            parallel_groups=[[agent_name]],
            estimated_duration=60,
            priority_weights={agent_name: 1.0}
        )
        
        # Execute plan
        results = await agent.execute_plan(plan, upload_path)
        
        return results
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Failed to run agent",
                "details": str(e)
            }
        )
