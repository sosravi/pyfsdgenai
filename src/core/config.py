"""
PyFSD GenAI - Core Configuration Module

This module handles application configuration, environment variables,
and settings management for the PyFSD GenAI platform.
"""

from pydantic_settings import BaseSettings
from typing import List, Optional
import os


class Settings(BaseSettings):
    """Application settings and configuration."""
    
    # Application Settings
    app_name: str = "PyFSD GenAI"
    app_version: str = "1.0.0"
    debug: bool = False
    log_level: str = "INFO"
    
    # Database Configuration
    database_url: str = "postgresql://user:password@localhost:5432/pyfsdgenai"
    mongodb_url: str = "mongodb://localhost:27017/pyfsdgenai"
    redis_url: str = "redis://localhost:6379/0"
    
    # AI/ML Configuration
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    default_llm_provider: str = "openai"
    default_model: str = "gpt-4-turbo-preview"
    
    # Document Processing
    max_file_size_mb: int = 100
    supported_formats: List[str] = ["pdf", "docx", "txt", "html", "xml"]
    ocr_enabled: bool = True
    ocr_language: str = "eng"
    
    # Security
    secret_key: str = "your-secret-key-change-in-production"
    access_token_expire_minutes: int = 30
    algorithm: str = "HS256"
    
    # API Configuration
    api_v1_str: str = "/api/v1"
    project_name: str = "PyFSD GenAI"
    allowed_hosts: List[str] = ["localhost", "127.0.0.1"]
    
    # Agent Configuration
    max_concurrent_agents: int = 20
    agent_timeout_seconds: int = 300
    agent_retry_attempts: int = 3
    
    # Performance
    max_concurrent_requests: int = 50
    request_timeout_seconds: int = 30
    cache_ttl_seconds: int = 3600
    
    # Monitoring
    enable_metrics: bool = True
    metrics_port: int = 9090
    health_check_interval: int = 60
    
    # File Storage
    storage_provider: str = "local"
    aws_s3_bucket: Optional[str] = None
    azure_storage_container: Optional[str] = None
    gcp_storage_bucket: Optional[str] = None
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get application settings."""
    return settings

