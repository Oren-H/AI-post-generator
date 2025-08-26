"""Configuration management for the Instagram caption agent."""

import os
from typing import Optional
from dataclasses import dataclass
from dotenv import load_dotenv


@dataclass
class AgentConfig:
    """Configuration class for the Instagram caption agent."""
    
    openai_api_key: str
    openai_model: str = "gpt-4"
    max_text_length: int = 8000  # Limit for OpenAI context
    
    @classmethod
    def from_env(cls) -> "AgentConfig":
        """
        Create configuration from environment variables.
        
        Returns:
            AgentConfig: Configured instance
            
        Raises:
            ValueError: If required environment variables are missing or invalid
        """
        # Load environment variables from .env file if it exists
        load_dotenv()
        
        # Get OpenAI API key
        openai_api_key = os.getenv("OPENAI_API_KEY")
        if not openai_api_key:
            raise ValueError(
                "OPENAI_API_KEY environment variable is required. "
                "Please set it in your .env file or environment."
            )
        
        # Get optional configuration with defaults
        openai_model = os.getenv("OPENAI_MODEL", "gpt-4")
        max_text_length_str = os.getenv("MAX_TEXT_LENGTH", "8000")
        
        # Validate max_text_length
        try:
            max_text_length = int(max_text_length_str)
            if max_text_length <= 0:
                raise ValueError("MAX_TEXT_LENGTH must be a positive integer")
        except ValueError as e:
            if "invalid literal" in str(e):
                raise ValueError(f"MAX_TEXT_LENGTH must be a valid integer, got: {max_text_length_str}")
            raise
        
        return cls(
            openai_api_key=openai_api_key,
            openai_model=openai_model,
            max_text_length=max_text_length
        )
    
    def validate(self) -> None:
        """
        Validate the configuration.
        
        Raises:
            ValueError: If configuration is invalid
        """
        if not self.openai_api_key:
            raise ValueError("OpenAI API key cannot be empty")
        
        if not self.openai_model:
            raise ValueError("OpenAI model cannot be empty")
        
        if self.max_text_length <= 0:
            raise ValueError("Max text length must be positive")
        
        # Basic validation for OpenAI API key format
        if not self.openai_api_key.startswith("sk-"):
            raise ValueError(
                "OpenAI API key appears to be invalid. "
                "It should start with 'sk-'"
            )


def get_config() -> AgentConfig:
    """
    Get validated configuration instance.
    
    Returns:
        AgentConfig: Validated configuration
        
    Raises:
        ValueError: If configuration is invalid
    """
    config = AgentConfig.from_env()
    config.validate()
    return config