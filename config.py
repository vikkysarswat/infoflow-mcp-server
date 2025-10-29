"""
Configuration management for InfoFlow MCP Server.
Handles loading and validating configuration from files and environment variables.
"""

import os
import json
from pathlib import Path
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, field_validator
from pydantic_settings import BaseSettings
from loguru import logger


class FilterConfig(BaseModel):
    """Configuration for content filtering."""
    
    relevance_threshold: float = Field(default=0.7, ge=0.0, le=1.0)
    quality_threshold: float = Field(default=0.6, ge=0.0, le=1.0)
    max_age_days: int = Field(default=30, ge=1)
    preferred_sources: List[str] = Field(default_factory=list)
    blocked_sources: List[str] = Field(default_factory=list)
    keywords: List[str] = Field(default_factory=list)


class SynthesisConfig(BaseModel):
    """Configuration for content synthesis."""
    
    max_summary_length: int = Field(default=500, ge=100)
    extract_key_points: bool = Field(default=True)
    include_sources: bool = Field(default=True)
    model: str = Field(default="gpt-4-turbo-preview")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)


class DecisionConfig(BaseModel):
    """Configuration for decision support."""
    
    include_pros_cons: bool = Field(default=True)
    include_recommendations: bool = Field(default=True)
    risk_analysis: bool = Field(default=True)
    urgency_ranking: bool = Field(default=True)
    confidence_threshold: float = Field(default=0.7, ge=0.0, le=1.0)


class CollectorConfig(BaseModel):
    """Configuration for data collectors."""
    
    rss_feeds: List[str] = Field(default_factory=list)
    news_apis: List[str] = Field(default_factory=list)
    social_platforms: List[str] = Field(default_factory=list)
    web_scraping_enabled: bool = Field(default=True)
    update_interval_minutes: int = Field(default=60, ge=5)


class StorageConfig(BaseModel):
    """Configuration for data storage."""
    
    type: str = Field(default="chromadb")  # chromadb, redis, sqlite
    path: Optional[str] = Field(default="./data/storage")
    redis_url: Optional[str] = Field(default=None)
    sqlite_path: Optional[str] = Field(default="./data/infoflow.db")
    max_items: int = Field(default=10000, ge=100)
    retention_days: int = Field(default=90, ge=1)


class UserPreferences(BaseModel):
    """User-specific preferences."""
    
    topics_of_interest: List[str] = Field(default_factory=list)
    preferred_content_types: List[str] = Field(default=["article", "news", "video"])
    notification_threshold: float = Field(default=0.8, ge=0.0, le=1.0)
    daily_digest_time: str = Field(default="09:00")
    risk_profile: str = Field(default="moderate")  # conservative, moderate, aggressive
    
    @field_validator('risk_profile')
    @classmethod
    def validate_risk_profile(cls, v: str) -> str:
        valid_profiles = ['conservative', 'moderate', 'aggressive']
        if v not in valid_profiles:
            raise ValueError(f"risk_profile must be one of {valid_profiles}")
        return v


class APIConfig(BaseModel):
    """API configuration for external services."""
    
    openai_api_key: Optional[str] = Field(default=None)
    anthropic_api_key: Optional[str] = Field(default=None)
    news_api_key: Optional[str] = Field(default=None)
    reddit_client_id: Optional[str] = Field(default=None)
    reddit_client_secret: Optional[str] = Field(default=None)


class InfoFlowConfig(BaseSettings):
    """Main configuration for InfoFlow MCP Server."""
    
    # Server Settings
    server_name: str = Field(default="InfoFlow MCP Server")
    version: str = Field(default="1.0.0")
    debug: bool = Field(default=False)
    log_level: str = Field(default="INFO")
    
    # Module Configurations
    filter: FilterConfig = Field(default_factory=FilterConfig)
    synthesis: SynthesisConfig = Field(default_factory=SynthesisConfig)
    decision: DecisionConfig = Field(default_factory=DecisionConfig)
    collector: CollectorConfig = Field(default_factory=CollectorConfig)
    storage: StorageConfig = Field(default_factory=StorageConfig)
    user: UserPreferences = Field(default_factory=UserPreferences)
    api: APIConfig = Field(default_factory=APIConfig)
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        env_nested_delimiter = "__"
        case_sensitive = False
    
    @classmethod
    def from_json_file(cls, file_path: str) -> "InfoFlowConfig":
        """Load configuration from a JSON file."""
        try:
            with open(file_path, 'r') as f:
                config_dict = json.load(f)
            return cls(**config_dict)
        except FileNotFoundError:
            logger.warning(f"Config file not found: {file_path}. Using defaults.")
            return cls()
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in config file: {e}")
            raise
    
    @classmethod
    def from_yaml_file(cls, file_path: str) -> "InfoFlowConfig":
        """Load configuration from a YAML file."""
        try:
            import yaml
            with open(file_path, 'r') as f:
                config_dict = yaml.safe_load(f)
            return cls(**config_dict)
        except FileNotFoundError:
            logger.warning(f"Config file not found: {file_path}. Using defaults.")
            return cls()
        except Exception as e:
            logger.error(f"Error loading YAML config: {e}")
            raise
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return self.model_dump()
    
    def save_to_json(self, file_path: str) -> None:
        """Save configuration to a JSON file."""
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)
        logger.info(f"Configuration saved to {file_path}")
    
    def validate_api_keys(self) -> Dict[str, bool]:
        """Validate that required API keys are present."""
        required_keys = {
            'openai': self.api.openai_api_key,
            'anthropic': self.api.anthropic_api_key,
        }
        
        results = {}
        for service, key in required_keys.items():
            if key and key.strip():
                results[service] = True
                logger.info(f"✓ {service} API key configured")
            else:
                results[service] = False
                logger.warning(f"✗ {service} API key not configured")
        
        return results


def load_config(config_path: Optional[str] = None) -> InfoFlowConfig:
    """
    Load configuration from file or environment variables.
    
    Priority order:
    1. Provided config file path
    2. CONFIG_PATH environment variable
    3. config.json in current directory
    4. Environment variables
    5. Default values
    """
    if config_path:
        if config_path.endswith('.yaml') or config_path.endswith('.yml'):
            return InfoFlowConfig.from_yaml_file(config_path)
        elif config_path.endswith('.json'):
            return InfoFlowConfig.from_json_file(config_path)
    
    # Try environment variable
    env_config_path = os.getenv('CONFIG_PATH')
    if env_config_path and Path(env_config_path).exists():
        if env_config_path.endswith(('.yaml', '.yml')):
            return InfoFlowConfig.from_yaml_file(env_config_path)
        elif env_config_path.endswith('.json'):
            return InfoFlowConfig.from_json_file(env_config_path)
    
    # Try default config.json
    default_config = Path('config.json')
    if default_config.exists():
        return InfoFlowConfig.from_json_file(str(default_config))
    
    # Fall back to environment variables and defaults
    logger.info("No config file found. Using environment variables and defaults.")
    return InfoFlowConfig()


# Create global config instance
config = load_config()
