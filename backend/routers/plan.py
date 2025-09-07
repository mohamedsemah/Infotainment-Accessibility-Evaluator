"""
Planning router for SuperAgent coordination.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Dict, Any, List
from datetime import datetime

from models.schemas import AgentPlan, AnalysisSummary, ErrorResponse
from routers.upload import get_upload_path
from routers.analyze import analyze_upload

router = APIRouter()

@router.post("/plan", response_model=AgentPlan)
async def create_agent_plan(
    upload_id: str = Query(..., description="Upload ID to create plan for")
):
    """Create an execution plan for Special Agents."""
    try:
        print(f"DEBUG: Plan request - upload_id: {upload_id}")
        # Get analysis summary
        analysis_summary = await analyze_upload(upload_id)
        
        # Determine which agents to run based on issues found
        agents_to_run = []
        priority_weights = {}
        
        # Always run TriageAgent last
        agents_to_run.append("TriageAgent")
        priority_weights["TriageAgent"] = 0.1
        
        # Determine agents based on issues found
        if analysis_summary.criteria_summary.get("contrast", 0) > 0:
            agents_to_run.insert(0, "ContrastAgent")
            priority_weights["ContrastAgent"] = 0.3
        
        if analysis_summary.criteria_summary.get("seizure_safe", 0) > 0:
            agents_to_run.insert(0, "SeizureSafeAgent")
            priority_weights["SeizureSafeAgent"] = 0.4  # Highest priority
        
        if analysis_summary.criteria_summary.get("language", 0) > 0:
            agents_to_run.insert(-1, "LanguageAgent")
            priority_weights["LanguageAgent"] = 0.2
        
        if analysis_summary.criteria_summary.get("aria", 0) > 0:
            agents_to_run.insert(-1, "ARIAAgent")
            priority_weights["ARIAAgent"] = 0.25
        
        # StateExplorerAgent runs on demand
        if analysis_summary.criteria_summary.get("state_explorer", 0) > 0:
            agents_to_run.insert(-1, "StateExplorerAgent")
            priority_weights["StateExplorerAgent"] = 0.15
        
        # TokenHarmonizerAgent runs after other agents
        if len(agents_to_run) > 1:  # If we have other agents
            agents_to_run.insert(-1, "TokenHarmonizerAgent")
            priority_weights["TokenHarmonizerAgent"] = 0.1
        
        # Determine execution order (priority-based)
        execution_order = sorted(agents_to_run, key=lambda x: priority_weights.get(x, 0), reverse=True)
        
        # Determine parallel groups
        parallel_groups = _determine_parallel_groups(execution_order, priority_weights)
        
        # Calculate estimated duration
        estimated_duration = _calculate_estimated_duration(analysis_summary, execution_order)
        
        # Create agent plan
        plan = AgentPlan(
            upload_id=upload_id,
            agents_to_run=agents_to_run,
            execution_order=execution_order,
            parallel_groups=parallel_groups,
            estimated_duration=estimated_duration,
            priority_weights=priority_weights
        )
        
        return plan
        
    except Exception as e:
        print(f"DEBUG: Plan creation error: {str(e)}")
        print(f"DEBUG: Error type: {type(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Planning failed",
                "details": str(e)
            }
        )

def _determine_parallel_groups(execution_order: List[str], priority_weights: Dict[str, float]) -> List[List[str]]:
    """Determine which agents can run in parallel."""
    parallel_groups = []
    
    # Group agents by priority level
    priority_levels = {}
    for agent in execution_order:
        priority = priority_weights.get(agent, 0)
        if priority not in priority_levels:
            priority_levels[priority] = []
        priority_levels[priority].append(agent)
    
    # Create parallel groups for each priority level
    for priority in sorted(priority_levels.keys(), reverse=True):
        agents = priority_levels[priority]
        
        # Some agents can run in parallel, others cannot
        if len(agents) > 1:
            # Group compatible agents
            compatible_groups = _group_compatible_agents(agents)
            parallel_groups.extend(compatible_groups)
        else:
            parallel_groups.append(agents)
    
    return parallel_groups

def _group_compatible_agents(agents: List[str]) -> List[List[str]]:
    """Group agents that can run in parallel."""
    # Define agent compatibility
    compatibility = {
        "ContrastAgent": ["LanguageAgent", "ARIAAgent"],
        "SeizureSafeAgent": ["LanguageAgent", "ARIAAgent"],
        "LanguageAgent": ["ContrastAgent", "SeizureSafeAgent", "ARIAAgent"],
        "ARIAAgent": ["ContrastAgent", "SeizureSafeAgent", "LanguageAgent"],
        "StateExplorerAgent": [],  # Should run alone
        "TokenHarmonizerAgent": [],  # Should run after others
        "TriageAgent": []  # Should run last
    }
    
    groups = []
    remaining_agents = agents.copy()
    
    while remaining_agents:
        current_group = [remaining_agents.pop(0)]
        
        # Find compatible agents
        for agent in remaining_agents[:]:
            if _can_run_parallel(current_group[0], agent, compatibility):
                current_group.append(agent)
                remaining_agents.remove(agent)
        
        groups.append(current_group)
    
    return groups

def _can_run_parallel(agent1: str, agent2: str, compatibility: Dict[str, List[str]]) -> bool:
    """Check if two agents can run in parallel."""
    # TriageAgent and TokenHarmonizerAgent should run alone
    if agent1 in ["TriageAgent", "TokenHarmonizerAgent"] or agent2 in ["TriageAgent", "TokenHarmonizerAgent"]:
        return False
    
    # StateExplorerAgent should run alone
    if agent1 == "StateExplorerAgent" or agent2 == "StateExplorerAgent":
        return False
    
    # Check compatibility
    return agent2 in compatibility.get(agent1, []) or agent1 in compatibility.get(agent2, [])

def _calculate_estimated_duration(analysis_summary: AnalysisSummary, execution_order: List[str]) -> int:
    """Calculate estimated duration for agent execution."""
    # Base time per agent
    base_times = {
        "ContrastAgent": 30,
        "SeizureSafeAgent": 45,
        "LanguageAgent": 15,
        "ARIAAgent": 25,
        "StateExplorerAgent": 60,
        "TokenHarmonizerAgent": 20,
        "TriageAgent": 10
    }
    
    # Time multipliers based on issue count
    issue_multipliers = {
        "ContrastAgent": analysis_summary.criteria_summary.get("contrast", 0) * 0.1,
        "SeizureSafeAgent": analysis_summary.criteria_summary.get("seizure_safe", 0) * 0.2,
        "LanguageAgent": analysis_summary.criteria_summary.get("language", 0) * 0.05,
        "ARIAAgent": analysis_summary.criteria_summary.get("aria", 0) * 0.1,
        "StateExplorerAgent": analysis_summary.criteria_summary.get("state_explorer", 0) * 0.3,
        "TokenHarmonizerAgent": 0.1,  # Based on total issues
        "TriageAgent": 0.05  # Based on total issues
    }
    
    total_duration = 0
    
    for agent in execution_order:
        base_time = base_times.get(agent, 20)
        multiplier = issue_multipliers.get(agent, 0)
        
        # Calculate agent-specific duration
        agent_duration = base_time + (base_time * multiplier)
        total_duration += agent_duration
    
    # Add overhead for coordination
    total_duration += 30
    
    return min(total_duration, 600)  # Cap at 10 minutes

@router.get("/plan/{upload_id}")
async def get_agent_plan(upload_id: str):
    """Get the execution plan for an upload."""
    # In a real implementation, this would fetch from a database
    # For now, we'll create a new plan
    try:
        analysis_summary = await analyze_upload(upload_id)
        plan = await create_agent_plan(upload_id, analysis_summary)
        return plan
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Failed to get plan",
                "details": str(e)
            }
        )

@router.put("/plan/{upload_id}")
async def update_agent_plan(upload_id: str, plan: AgentPlan):
    """Update the execution plan for an upload."""
    # In a real implementation, this would update the database
    return {"message": "Plan updated successfully", "plan": plan}
