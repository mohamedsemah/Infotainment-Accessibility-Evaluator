"""
Anthropic Claude client for LLM-1 Discovery stage.
Provides JSON-strict responses with retry logic.
"""

import asyncio
import json
import logging
import os
from typing import Dict, Any, Optional

import httpx
from anthropic import AsyncAnthropic

from ..models import CandidateIssue, FileSpan

logger = logging.getLogger(__name__)


class ClaudeClient:
    """Client for Anthropic Claude API with JSON-strict responses."""
    
    def __init__(self, model: str = "claude-opus-4-1-20250805"):
        self.model = model
        self.api_key = os.getenv("ANTHROPIC_API_KEY")
        self.client = None
        
        if self.api_key:
            self.client = AsyncAnthropic(api_key=self.api_key)
    
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
            raise Exception("Anthropic API key not configured")
        
        # Convert user payload to string
        if isinstance(user_payload, dict):
            user_message = json.dumps(user_payload, indent=2)
        else:
            user_message = str(user_payload)
        
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = await self.client.messages.create(
                    model=self.model,
                    max_tokens=1500,
                    temperature=0.1,
                    system=system_prompt,
                    messages=[{"role": "user", "content": user_message}],
                    response_format={"type": "json_object"}
                )
                
                # Extract content from response
                content = response.content[0].text
                
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
    
    async def discover_issues(self, code_chunks: list, file_paths: list) -> list:
        """
        Discover accessibility issues in code chunks.
        
        Args:
            code_chunks: List of code chunks to analyze
            file_paths: List of corresponding file paths
            
        Returns:
            List of CandidateIssue objects
        """
        system_prompt = """You are an accessibility auditor. Output ONLY a JSON array of CandidateIssue items. No prose.
Each item keys: id, rule_id, title, description, evidence[{file_path,start_line,end_line,code_snippet}], tags, confidence, llm_model.
Do not propose fixes or final verdicts."""
        
        user_payload = {
            "code_chunks": code_chunks,
            "file_paths": file_paths,
            "instruction": "Scan the provided code chunk(s) for WCAG 2.2 candidate issues. When unsure about exact rule_id, use 'TBD'. Return ONLY valid JSON (no markdown)."
        }
        
        try:
            response = await self.chat_json(system_prompt, user_payload)
            
            # Parse response into CandidateIssue objects
            candidates = []
            if isinstance(response, list):
                for item in response:
                    try:
                        # Convert evidence to FileSpan objects
                        evidence = []
                        for ev in item.get('evidence', []):
                            evidence.append(FileSpan(
                                file_path=ev['file_path'],
                                start_line=ev['start_line'],
                                end_line=ev['end_line'],
                                code_snippet=ev['code_snippet']
                            ))
                        
                        candidate = CandidateIssue(
                            rule_id=item.get('rule_id', 'TBD'),
                            title=item.get('title', ''),
                            description=item.get('description', ''),
                            evidence=evidence,
                            tags=item.get('tags', []),
                            llm_model=self.model,
                            confidence=item.get('confidence', 'medium')
                        )
                        candidates.append(candidate)
                    except Exception as e:
                        logger.warning(f"Failed to parse candidate issue: {e}")
                        continue
            
            return candidates
            
        except Exception as e:
            logger.error(f"Failed to discover issues: {e}")
            return []
    
    def is_available(self) -> bool:
        """Check if the client is properly configured."""
        return self.client is not None and self.api_key is not None
