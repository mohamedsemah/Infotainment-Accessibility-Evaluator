"""
OpenAI GPT client for LLM-4 Fixes stage.
Provides JSON-strict responses for fix suggestions.
"""

import asyncio
import json
import logging
import os
from typing import Dict, Any, Optional

import httpx
from openai import AsyncOpenAI

from ..models import FixSuggestion

logger = logging.getLogger(__name__)


class OpenAIClient:
    """Client for OpenAI API with JSON-strict responses."""
    
    def __init__(self, model: str = "gpt-5"):
        self.model = model
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.client = None
        
        if self.api_key:
            self.client = AsyncOpenAI(api_key=self.api_key)
    
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
        if not self.client:
            raise Exception("OpenAI API key not configured")
        
        # Convert user payload to string
        if isinstance(user_payload, dict):
            user_message = json.dumps(user_payload, indent=2)
        else:
            user_message = str(user_payload)
        
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = await self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_message}
                    ],
                    max_tokens=2500,
                    temperature=0.2,
                    response_format={"type": "json_object"}
                )
                
                # Extract content from response
                content = response.choices[0].message.content
                
                # Parse JSON response
                try:
                    return json.loads(content)
                except json.JSONDecodeError as e:
                    if attempt < max_retries - 1:
                        logger.warning(f"JSON parse error on attempt {attempt + 1}: {e}")
                        # Retry with explicit JSON instruction
                        system_prompt += "\n\nIMPORTANT: Return ONLY valid JSON. No markdown, no prose, no explanations."
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
    
    async def generate_fixes(self, validation_decision: dict, code_spans: list) -> FixSuggestion:
        """
        Generate fix suggestions for a failed validation decision.
        
        Args:
            validation_decision: The validation decision that failed
            code_spans: Code spans to fix
            
        Returns:
            FixSuggestion object
        """
        system_prompt = """You are a senior accessibility engineer. Propose minimal, safe unified diff patches.
Output ONLY JSON: {patch_unified_diff, summary, side_effects, test_suggestions, llm_model}."""
        
        user_payload = {
            "validation_decision": validation_decision,
            "code_spans": code_spans,
            "instruction": "Given the decision (failed) and code span(s), produce minimal unified diff(s) to fix the issue. Keep context lines accurate. Include 1-3 test_suggestions (axe-core rule refs acceptable)."
        }
        
        try:
            response = await self.chat_json(system_prompt, user_payload)
            
            # Parse response into FixSuggestion object
            fix = FixSuggestion(
                candidate_id=validation_decision.get('candidate_id'),
                rule_id=validation_decision.get('rule_id', ''),
                patch_unified_diff=response.get('patch_unified_diff', ''),
                summary=response.get('summary', ''),
                side_effects=response.get('side_effects', []),
                test_suggestions=response.get('test_suggestions', []),
                llm_model=self.model
            )
            
            return fix
            
        except Exception as e:
            logger.error(f"Failed to generate fixes: {e}")
            # Return a default fix suggestion
            return FixSuggestion(
                candidate_id=validation_decision.get('candidate_id'),
                rule_id=validation_decision.get('rule_id', ''),
                patch_unified_diff="",
                summary=f"Fix generation failed due to error: {str(e)}",
                side_effects=["Manual review required"],
                test_suggestions=["Manual testing recommended"],
                llm_model=self.model
            )
    
    def is_available(self) -> bool:
        """Check if the client is properly configured."""
        return self.client is not None and self.api_key is not None
