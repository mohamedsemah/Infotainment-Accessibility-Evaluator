"""
DeepSeek client for LLM-2 Metrics stage.
Provides JSON-strict responses for metric computation.
"""

import asyncio
import json
import logging
import os
from typing import Dict, Any, Optional

import httpx

from ..models import Metric, FileSpan

logger = logging.getLogger(__name__)


class DeepSeekClient:
    """Client for DeepSeek API with JSON-strict responses."""
    
    def __init__(self, model: str = "deepseek-chat"):
        self.model = model
        self.api_key = os.getenv("DEEPSEEK_API_KEY")
        self.base_url = "https://api.deepseek.com/v1"
    
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
            raise Exception("DeepSeek API key not configured")
        
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
            "temperature": 0.0,
            "response_format": {"type": "json_object"}
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
    
    async def compute_metrics(self, candidate_issue: dict, code_spans: list, 
                            required_metrics: list) -> list:
        """
        Compute required metrics for a candidate issue.
        
        Args:
            candidate_issue: The candidate issue to analyze
            code_spans: Code spans to analyze
            required_metrics: List of metric names to compute
            
        Returns:
            List of Metric objects
        """
        system_prompt = """You compute metrics required by the provided WCAG config. Output ONLY a JSON object: {name, scope_id, value, unit?, notes?}.
If a metric cannot be computed from the spans, set value to null and include a brief notes."""
        
        user_payload = {
            "candidate_issue": candidate_issue,
            "code_spans": code_spans,
            "required_metrics": required_metrics,
            "instruction": "Given the candidate and code spans, compute ONLY the requested metric(s). Be concise and deterministic. Return valid JSON."
        }
        
        try:
            response = await self.chat_json(system_prompt, user_payload)
            
            # Parse response into Metric objects
            metrics = []
            if isinstance(response, dict):
                # Single metric response
                metric = Metric(
                    name=response.get('name', ''),
                    scope_id=response.get('scope_id', ''),
                    value=response.get('value'),
                    unit=response.get('unit'),
                    computed_from=[],  # Will be filled by caller
                    notes=response.get('notes'),
                    llm_model=self.model
                )
                metrics.append(metric)
            elif isinstance(response, list):
                # Multiple metrics response
                for item in response:
                    metric = Metric(
                        name=item.get('name', ''),
                        scope_id=item.get('scope_id', ''),
                        value=item.get('value'),
                        unit=item.get('unit'),
                        computed_from=[],  # Will be filled by caller
                        notes=item.get('notes'),
                        llm_model=self.model
                    )
                    metrics.append(metric)
            
            return metrics
            
        except Exception as e:
            logger.error(f"Failed to compute metrics: {e}")
            return []
    
    def is_available(self) -> bool:
        """Check if the client is properly configured."""
        return self.api_key is not None
