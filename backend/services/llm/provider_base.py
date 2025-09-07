"""
Base class for LLM providers.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from models.schemas import LLMRequest, LLMResponse

class LLMProvider(ABC):
    """Base class for LLM providers."""
    
    def __init__(self):
        self.api_key = None
        self.base_url = None
        self.model = None
        self.max_tokens = 1000
        self.temperature = 0.1
    
    @abstractmethod
    async def generate_response(self, request: LLMRequest) -> LLMResponse:
        """Generate a response from the LLM."""
        pass
    
    @abstractmethod
    async def generate_contrast_suggestions(self, foreground_color: str, background_color: str, target_ratio: float) -> Dict[str, Any]:
        """Generate contrast improvement suggestions."""
        pass
    
    @abstractmethod
    async def generate_aria_suggestions(self, element_type: str, current_attributes: Dict[str, str]) -> Dict[str, Any]:
        """Generate ARIA improvement suggestions."""
        pass
    
    @abstractmethod
    async def generate_animation_suggestions(self, animation_type: str, current_frequency: float) -> Dict[str, Any]:
        """Generate animation safety suggestions."""
        pass
    
    @abstractmethod
    async def generate_language_suggestions(self, current_lang: str, content_language: str) -> Dict[str, Any]:
        """Generate language attribute suggestions."""
        pass
    
    @abstractmethod
    async def generate_state_suggestions(self, element_type: str, current_states: Dict[str, bool]) -> Dict[str, Any]:
        """Generate state handling suggestions."""
        pass
    
    def set_api_key(self, api_key: str):
        """Set API key for the provider."""
        self.api_key = api_key
    
    def set_base_url(self, base_url: str):
        """Set base URL for the provider."""
        self.base_url = base_url
    
    def set_model(self, model: str):
        """Set model for the provider."""
        self.model = model
    
    def set_max_tokens(self, max_tokens: int):
        """Set maximum tokens for responses."""
        self.max_tokens = max_tokens
    
    def set_temperature(self, temperature: float):
        """Set temperature for responses."""
        self.temperature = temperature
    
    def is_configured(self) -> bool:
        """Check if the provider is properly configured."""
        return self.api_key is not None and self.model is not None
    
    async def test_connection(self) -> bool:
        """Test connection to the LLM provider."""
        try:
            test_request = LLMRequest(
                prompt="Test connection",
                max_tokens=10,
                temperature=0.1
            )
            response = await self.generate_response(test_request)
            return response is not None
        except Exception:
            return False
