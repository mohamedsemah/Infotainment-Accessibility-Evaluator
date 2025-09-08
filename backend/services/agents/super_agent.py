"""
SuperAgent - Coordinates and manages Special Agents for accessibility evaluation.
"""

import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime

from models.schemas import AgentPlan, AgentResult, Finding, Cluster, ProgressEvent
from services.agents.special.contrast_agent import ContrastAgent
from services.agents.special.seizure_safe_agent import SeizureSafeAgent
from services.agents.special.language_agent import LanguageAgent
from services.agents.special.aria_agent import ARIAAgent
from services.agents.special.state_explorer_agent import StateExplorerAgent
from services.agents.special.triage_agent import TriageAgent
from services.agents.special.token_harmonizer_agent import TokenHarmonizerAgent

# Perceivable Agents
from services.agents.special.alt_text_agent import AltTextAgent
from services.agents.special.media_agent import MediaAgent
from services.agents.special.layout_agent import LayoutAgent
from services.agents.special.sensory_agent import SensoryAgent

# Operable Agents
from services.agents.special.keyboard_navigation_agent import KeyboardNavigationAgent
from services.agents.special.focus_agent import FocusAgent
from services.agents.special.timing_agent import TimingAgent
from services.agents.special.gesture_agent import GestureAgent
from services.agents.special.navigation_consistency_agent import NavigationConsistencyAgent

# Understandable Agents
from services.agents.special.predictability_agent import PredictabilityAgent
from services.agents.special.error_prevention_agent import ErrorPreventionAgent
from services.agents.special.readability_agent import ReadabilityAgent
from services.agents.special.input_assistance_agent import InputAssistanceAgent

# Robust Agents
from services.agents.special.semantic_structure_agent import SemanticStructureAgent
from services.agents.special.compatibility_agent import CompatibilityAgent
from services.agents.special.assistive_tech_simulation_agent import AssistiveTechSimulationAgent
from utils.id_gen import generate_agent_id

class SuperAgent:
    """SuperAgent coordinates and manages Special Agents."""
    
    def __init__(self, connection_manager=None):
        self.connection_manager = connection_manager
        self.agents = {
            # Original agents
            'ContrastAgent': ContrastAgent(),
            'SeizureSafeAgent': SeizureSafeAgent(),
            'LanguageAgent': LanguageAgent(),
            'ARIAAgent': ARIAAgent(),
            'StateExplorerAgent': StateExplorerAgent(),
            'TriageAgent': TriageAgent(),
            'TokenHarmonizerAgent': TokenHarmonizerAgent(),
            
            # Perceivable Agents
            'AltTextAgent': AltTextAgent(),
            'MediaAgent': MediaAgent(),
            'LayoutAgent': LayoutAgent(),
            'SensoryAgent': SensoryAgent(),
            
            # Operable Agents
            'KeyboardNavigationAgent': KeyboardNavigationAgent(),
            'FocusAgent': FocusAgent(),
            'TimingAgent': TimingAgent(),
            'GestureAgent': GestureAgent(),
            'NavigationConsistencyAgent': NavigationConsistencyAgent(),
            
            # Understandable Agents
            'PredictabilityAgent': PredictabilityAgent(),
            'ErrorPreventionAgent': ErrorPreventionAgent(),
            'ReadabilityAgent': ReadabilityAgent(),
            'InputAssistanceAgent': InputAssistanceAgent(),
            
            # Robust Agents
            'SemanticStructureAgent': SemanticStructureAgent(),
            'CompatibilityAgent': CompatibilityAgent(),
            'AssistiveTechSimulationAgent': AssistiveTechSimulationAgent()
        }
        self.results = {}
        self.all_findings = []
    
    async def execute_plan(self, plan: AgentPlan, upload_path: str) -> Dict[str, Any]:
        """Execute an agent plan."""
        execution_results = {
            'plan': plan,
            'results': {},
            'all_findings': [],
            'clusters': [],
            'patches': [],
            'success': True,
            'errors': []
        }
        
        try:
            # Execute agents in parallel groups
            for group in plan.parallel_groups:
                await self._execute_agent_group(group, upload_path, plan.upload_id, execution_results)
            
            # Collect all findings and set agent names
            self.all_findings = []
            for agent_name, result in execution_results['results'].items():
                print(f"DEBUG: Agent {agent_name} found {len(result.findings)} findings")
                for i, finding in enumerate(result.findings):
                    print(f"DEBUG: Finding {i+1}: {finding.details} (WCAG: {finding.wcag_criterion})")
                    finding.agent = agent_name
                self.all_findings.extend(result.findings)
            
            print(f"DEBUG: Total findings collected: {len(self.all_findings)}")
            
            # Set all_findings in execution_results - convert to dicts for JSON serialization
            execution_results['all_findings'] = [finding.dict() for finding in self.all_findings]
            print(f"DEBUG: execution_results['all_findings'] length: {len(execution_results['all_findings'])}")
            
            # Debug: Check if findings are now dictionaries
            if execution_results['all_findings']:
                print(f"DEBUG: First finding type: {type(execution_results['all_findings'][0])}")
                print(f"DEBUG: First finding keys: {list(execution_results['all_findings'][0].keys()) if isinstance(execution_results['all_findings'][0], dict) else 'Not a dict'}")
            
            # Run TriageAgent to cluster findings
            if self.all_findings:
                triage_agent = self.agents['TriageAgent']
                clusters = await triage_agent.analyze(self.all_findings, plan.upload_id)
                execution_results['clusters'] = clusters
                
                # Run TokenHarmonizerAgent to generate patches
                if clusters:
                    token_agent = self.agents['TokenHarmonizerAgent']
                    patches = await token_agent.analyze(clusters, upload_path)
                    execution_results['patches'] = patches
            
        except Exception as e:
            execution_results['success'] = False
            execution_results['errors'].append(str(e))
            await self._send_progress_event(
                plan.upload_id,
                "error",
                f"Execution failed: {str(e)}",
                0.0
            )
        
        return execution_results
    
    async def _execute_agent_group(self, agent_names: List[str], upload_path: str, upload_id: str, execution_results: Dict[str, Any]):
        """Execute a group of agents in parallel."""
        tasks = []
        
        for agent_name in agent_names:
            if agent_name in self.agents:
                task = asyncio.create_task(
                    self._execute_single_agent(agent_name, upload_path, upload_id, execution_results)
                )
                tasks.append(task)
        
        # Wait for all agents in the group to complete
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
    
    async def _execute_single_agent(self, agent_name: str, upload_path: str, upload_id: str, execution_results: Dict[str, Any]):
        """Execute a single agent."""
        try:
            agent = self.agents[agent_name]
            agent_id = generate_agent_id()
            
            await self._send_progress_event(
                upload_id,
                "agent_start",
                f"Starting {agent_name}",
                0.0,
                agent_name
            )
            
            start_time = datetime.now()
            
            # Execute agent
            print(f"DEBUG: Executing {agent_name} on {upload_path}")
            if agent_name == 'TriageAgent':
                # TriageAgent needs findings from other agents
                findings = execution_results.get('all_findings', [])
                print(f"DEBUG: TriageAgent analyzing {len(findings)} findings")
                result = await agent.analyze(findings, upload_id)
            elif agent_name == 'TokenHarmonizerAgent':
                # TokenHarmonizerAgent needs clusters
                clusters = execution_results.get('clusters', [])
                print(f"DEBUG: TokenHarmonizerAgent analyzing {len(clusters)} clusters")
                result = await agent.analyze(clusters, upload_path)
            else:
                # Other agents analyze the upload
                print(f"DEBUG: {agent_name} analyzing upload path: {upload_path}")
                result = await agent.analyze(upload_path)
            
            print(f"DEBUG: {agent_name} returned {len(result) if isinstance(result, list) else 'non-list'} results")
            
            end_time = datetime.now()
            processing_time = (end_time - start_time).total_seconds()
            
            # Create agent result
            agent_result = AgentResult(
                agent_name=agent_name,
                findings=result if isinstance(result, list) else [],
                processing_time=processing_time,
                success=True
            )
            
            execution_results['results'][agent_name] = agent_result
            
            await self._send_progress_event(
                upload_id,
                "agent_complete",
                f"Completed {agent_name}",
                1.0,
                agent_name
            )
            
        except Exception as e:
            # Create error result
            agent_result = AgentResult(
                agent_name=agent_name,
                findings=[],
                processing_time=0.0,
                success=False,
                error_message=str(e)
            )
            
            execution_results['results'][agent_name] = agent_result
            execution_results['errors'].append(f"{agent_name}: {str(e)}")
            
            await self._send_progress_event(
                upload_id,
                "agent_error",
                f"Error in {agent_name}: {str(e)}",
                0.0,
                agent_name
            )
    
    async def _send_progress_event(self, upload_id: str, event_type: str, message: str, progress: float, agent_name: str = None):
        """Send progress event via WebSocket."""
        if self.connection_manager:
            event = ProgressEvent(
                event_type=event_type,
                upload_id=upload_id,
                agent_name=agent_name,
                progress=progress,
                message=message
            )
            
            await self.connection_manager.send_progress(event)
    
    async def get_agent_status(self, agent_name: str) -> Dict[str, Any]:
        """Get status of a specific agent."""
        if agent_name not in self.agents:
            return {"error": "Agent not found"}
        
        agent = self.agents[agent_name]
        
        return {
            "name": agent_name,
            "status": "ready",
            "last_run": None,
            "findings_count": len(getattr(agent, 'findings', [])),
            "clusters_count": len(getattr(agent, 'clusters', [])),
            "patches_count": len(getattr(agent, 'patches', []))
        }
    
    async def get_all_agents_status(self) -> Dict[str, Any]:
        """Get status of all agents."""
        status = {}
        
        for agent_name in self.agents.keys():
            status[agent_name] = await self.get_agent_status(agent_name)
        
        return status
    
    async def reset_agent(self, agent_name: str) -> bool:
        """Reset a specific agent."""
        if agent_name not in self.agents:
            return False
        
        # Reset agent state
        agent = self.agents[agent_name]
        if hasattr(agent, 'findings'):
            agent.findings = []
        if hasattr(agent, 'clusters'):
            agent.clusters = []
        if hasattr(agent, 'patches'):
            agent.patches = []
        
        return True
    
    async def reset_all_agents(self) -> bool:
        """Reset all agents."""
        for agent_name in self.agents.keys():
            await self.reset_agent(agent_name)
        
        return True
    
    async def get_agent_capabilities(self) -> Dict[str, Any]:
        """Get capabilities of all agents."""
        capabilities = {
            # Original agents
            'ContrastAgent': {
                'description': 'Evaluates color contrast compliance',
                'criteria': ['1.4.3', '1.4.6', '1.4.11'],
                'input_types': ['html', 'css', 'qml'],
                'output_types': ['findings', 'suggestions']
            },
            'SeizureSafeAgent': {
                'description': 'Evaluates seizure safety compliance',
                'criteria': ['2.3.1', '2.3.2', '2.3.3'],
                'input_types': ['html', 'css', 'qml', 'js'],
                'output_types': ['findings', 'suggestions']
            },
            'LanguageAgent': {
                'description': 'Evaluates language attribute compliance',
                'criteria': ['3.1.1', '3.1.2'],
                'input_types': ['html', 'qml'],
                'output_types': ['findings', 'suggestions']
            },
            'ARIAAgent': {
                'description': 'Evaluates ARIA attribute compliance',
                'criteria': ['4.1.2', '4.1.3'],
                'input_types': ['html', 'qml'],
                'output_types': ['findings', 'suggestions']
            },
            'StateExplorerAgent': {
                'description': 'Explores UI states for accessibility',
                'criteria': ['1.4.13', '2.4.7', '2.4.11', '2.4.12'],
                'input_types': ['html', 'css', 'qml'],
                'output_types': ['findings', 'suggestions']
            },
            'TriageAgent': {
                'description': 'Normalizes and clusters findings',
                'criteria': ['all'],
                'input_types': ['findings'],
                'output_types': ['clusters']
            },
            'TokenHarmonizerAgent': {
                'description': 'Recommends design token fixes',
                'criteria': ['all'],
                'input_types': ['clusters'],
                'output_types': ['patches']
            },
            
            # Perceivable Agents
            'AltTextAgent': {
                'description': 'Detects missing or inadequate alt text',
                'criteria': ['1.1.1'],
                'input_types': ['html'],
                'output_types': ['findings', 'suggestions']
            },
            'MediaAgent': {
                'description': 'Detects media accessibility issues',
                'criteria': ['1.2.1', '1.2.2', '1.2.3'],
                'input_types': ['html'],
                'output_types': ['findings', 'suggestions']
            },
            'LayoutAgent': {
                'description': 'Detects layout and structure issues',
                'criteria': ['1.3.1', '1.3.2'],
                'input_types': ['html'],
                'output_types': ['findings', 'suggestions']
            },
            'SensoryAgent': {
                'description': 'Detects sensory accessibility issues',
                'criteria': ['1.4.1', '1.4.2'],
                'input_types': ['html'],
                'output_types': ['findings', 'suggestions']
            },
            
            # Operable Agents
            'KeyboardNavigationAgent': {
                'description': 'Detects keyboard navigation issues',
                'criteria': ['2.1.1', '2.1.2'],
                'input_types': ['html'],
                'output_types': ['findings', 'suggestions']
            },
            'FocusAgent': {
                'description': 'Detects focus management issues',
                'criteria': ['2.4.7'],
                'input_types': ['html'],
                'output_types': ['findings', 'suggestions']
            },
            'TimingAgent': {
                'description': 'Detects timing-related issues',
                'criteria': ['2.2.1', '2.2.2'],
                'input_types': ['html'],
                'output_types': ['findings', 'suggestions']
            },
            'GestureAgent': {
                'description': 'Detects gesture accessibility issues',
                'criteria': ['2.5.1', '2.5.2'],
                'input_types': ['html'],
                'output_types': ['findings', 'suggestions']
            },
            'NavigationConsistencyAgent': {
                'description': 'Detects navigation consistency issues',
                'criteria': ['3.2.3'],
                'input_types': ['html'],
                'output_types': ['findings', 'suggestions']
            },
            
            # Understandable Agents
            'PredictabilityAgent': {
                'description': 'Detects predictability issues',
                'criteria': ['3.2.1', '3.2.2'],
                'input_types': ['html'],
                'output_types': ['findings', 'suggestions']
            },
            'ErrorPreventionAgent': {
                'description': 'Detects error prevention issues',
                'criteria': ['3.3.4', '3.3.6'],
                'input_types': ['html'],
                'output_types': ['findings', 'suggestions']
            },
            'ReadabilityAgent': {
                'description': 'Detects readability issues',
                'criteria': ['3.1.5'],
                'input_types': ['html'],
                'output_types': ['findings', 'suggestions']
            },
            'InputAssistanceAgent': {
                'description': 'Detects input assistance issues',
                'criteria': ['3.3.5'],
                'input_types': ['html'],
                'output_types': ['findings', 'suggestions']
            },
            
            # Robust Agents
            'SemanticStructureAgent': {
                'description': 'Detects semantic structure issues',
                'criteria': ['4.1.1'],
                'input_types': ['html'],
                'output_types': ['findings', 'suggestions']
            },
            'CompatibilityAgent': {
                'description': 'Detects compatibility issues',
                'criteria': ['4.1.2'],
                'input_types': ['html'],
                'output_types': ['findings', 'suggestions']
            },
            'AssistiveTechSimulationAgent': {
                'description': 'Simulates assistive technology behavior',
                'criteria': ['4.1.3'],
                'input_types': ['html'],
                'output_types': ['findings', 'suggestions']
            }
        }
        
        return capabilities
    
    async def validate_plan(self, plan: AgentPlan) -> Dict[str, Any]:
        """Validate an agent plan."""
        validation = {
            'valid': True,
            'errors': [],
            'warnings': []
        }
        
        # Check if all agents exist
        for agent_name in plan.agents_to_run:
            if agent_name not in self.agents:
                validation['valid'] = False
                validation['errors'].append(f"Unknown agent: {agent_name}")
        
        # Check for required agents
        required_agents = ['TriageAgent']
        for required_agent in required_agents:
            if required_agent not in plan.agents_to_run:
                validation['warnings'].append(f"Recommended agent not included: {required_agent}")
        
        # Check execution order
        if 'TriageAgent' in plan.agents_to_run:
            triage_index = plan.agents_to_run.index('TriageAgent')
            if triage_index != len(plan.agents_to_run) - 1:
                validation['warnings'].append("TriageAgent should be last in execution order")
        
        return validation
