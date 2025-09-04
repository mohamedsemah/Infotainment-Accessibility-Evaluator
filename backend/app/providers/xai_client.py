"""
XAI Grok client for LLM-3 Validation stage.
Provides JSON-strict responses for validation decisions.
"""

import asyncio
import json
import logging
import os
from typing import Dict, Any, Optional

import httpx

from ..models import ValidationDecision

logger = logging.getLogger(__name__)


class XAIClient:
    """Client for XAI Grok API with JSON-strict responses."""
    
    def __init__(self, model: str = "grok-4"):
        self.model = model
        self.api_key = os.getenv("XAI_API_KEY")
        self.base_url = "https://api.x.ai/v1"
    
    async def chat_json(self, system_prompt: str, user_payload: dict) -> dict:
        """
        Send a chat request with JSON-only response format.
        
        Args:
            system_prompt: System prompt for the conversation
            user_payload: User message content
            
        Returns:
            Parsed JSON response
            
        Raises:
            Exception: If API call fails or JSON parsing fails
        """
        if not self.api_key:
            raise Exception("XAI API key not configured")
        
        # Convert user payload to string
        if isinstance(user_payload, dict):
            user_message = json.dumps(user_payload, indent=2)
        else:
            user_message = str(user_payload)
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            "max_tokens": 600,
            "temperature": 0.0
            # Note: Omitting presence_penalty and frequency_penalty as requested
        }
        
        max_retries = 3
        for attempt in range(max_retries):
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        f"{self.base_url}/chat/completions",
                        headers=headers,
                        json=payload,
                        timeout=30.0
                    )
                    response.raise_for_status()
                    
                    data = response.json()
                    content = data["choices"][0]["message"]["content"]
                    
                    # Parse JSON response
                    try:
                        return json.loads(content)
                    except json.JSONDecodeError as e:
                        if attempt < max_retries - 1:
                            logger.warning(f"JSON parse error on attempt {attempt + 1}: {e}")
                            # Retry with explicit JSON instruction
                            system_prompt += "\n\nIMPORTANT: Return ONLY valid JSON. No markdown, no prose, no explanations."
                            payload["messages"][0]["content"] = system_prompt
                            continue
                        else:
                            raise Exception(f"Failed to parse JSON response after {max_retries} attempts: {e}")
                
            except httpx.HTTPError as e:
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt + 0.1  # Exponential backoff with jitter
                    logger.warning(f"HTTP error on attempt {attempt + 1}: {e}. Retrying in {wait_time}s")
                    await asyncio.sleep(wait_time)
                    continue
                else:
                    raise Exception(f"HTTP error after {max_retries} attempts: {e}")
            
            except Exception as e:
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt + 0.1
                    logger.warning(f"Error on attempt {attempt + 1}: {e}. Retrying in {wait_time}s")
                    await asyncio.sleep(wait_time)
                    continue
                else:
                    raise Exception(f"Request failed after {max_retries} attempts: {e}")
        
        raise Exception("Max retries exceeded")
    
    async def validate_decision(self, candidate_issue: dict, metrics: list, 
                              rule_config: dict) -> ValidationDecision:
        """
        Validate a candidate issue against WCAG thresholds.
        
        Args:
            candidate_issue: The candidate issue to validate
            metrics: List of computed metrics
            rule_config: WCAG rule configuration
            
        Returns:
            ValidationDecision object
        """
        system_prompt = """You are a standards adjudicator. Use ONLY the provided thresholds. Decide pass/fail and severity.
Output ONLY a JSON object: {candidate_id, rule_id, passed, severity, reasoning, metrics_used, llm_model}."""
        
        user_payload = {
            "candidate_issue": candidate_issue,
            "metrics": [m.dict() if hasattr(m, 'dict') else m for m in metrics],
            "rule_config": rule_config,
            "instruction": "Compare the provided metrics with the rule_config. Pick the correct threshold variant if applicable (e.g., large vs normal text). Return valid JSON. No extra commentary."
        }
        
        try:
            response = await self.chat_json(system_prompt, user_payload)
            
            # Parse response into ValidationDecision object
            decision = ValidationDecision(
                candidate_id=candidate_issue.get('id'),
                rule_id=response.get('rule_id', candidate_issue.get('rule_id', '')),
                passed=response.get('passed', False),
                severity=response.get('severity', 'minor'),
                reasoning=response.get('reasoning', ''),
                metrics_used=response.get('metrics_used', {}),
                llm_model=self.model
            )
            
            return decision
            
        except Exception as e:
            logger.error(f"Failed to validate decision: {e}")
            # Return a default failed decision
            return ValidationDecision(
                candidate_id=candidate_issue.get('id'),
                rule_id=candidate_issue.get('rule_id', ''),
                passed=False,
                severity='moderate',
                reasoning=f"Validation failed due to error: {str(e)}",
                metrics_used={},
                llm_model=self.model
            )
    
    def is_available(self) -> bool:
        """Check if the client is properly configured."""
        return self.api_key is not None
