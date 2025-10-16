"""
Phase 1.1 - Development Environment Setup Tests

This module contains tests for validating the development environment setup
following TDD principles. These tests define the expected behavior before
implementing the environment configuration.
"""

import pytest
import os
import subprocess
import sys
from pathlib import Path


class TestDevelopmentEnvironment:
    """Test cases for development environment setup."""
    
    def test_docker_compose_file_exists(self):
        """Test that docker-compose.yml file exists."""
        docker_compose_path = Path("docker-compose.yml")
        assert docker_compose_path.exists(), "docker-compose.yml file should exist"
        
    def test_docker_compose_configuration(self):
        """Test that docker-compose.yml has required services."""
        with open("docker-compose.yml", "r") as f:
            content = f.read()
            
        # Check for required services
        assert "app:" in content, "App service should be defined"
        assert "db:" in content, "Database service should be defined"
        assert "mongo:" in content, "MongoDB service should be defined"
        assert "redis:" in content, "Redis service should be defined"
        
    def test_environment_file_template_exists(self):
        """Test that environment configuration template exists."""
        env_template_path = Path("config.env.example")
        assert env_template_path.exists(), "config.env.example should exist"
        
    def test_requirements_file_exists(self):
        """Test that requirements.txt file exists."""
        requirements_path = Path("requirements.txt")
        assert requirements_path.exists(), "requirements.txt should exist"
        
    def test_python_version_compatibility(self):
        """Test Python version compatibility."""
        python_version = sys.version_info
        assert python_version.major == 3, "Python 3 is required"
        assert python_version.minor >= 9, "Python 3.9+ is required"
        
    def test_required_packages_available(self):
        """Test that required packages can be imported."""
        required_packages = [
            "fastapi",
            "pydantic",
            "sqlalchemy",
            "pytest",
            "docker"
        ]
        
        for package in required_packages:
            try:
                __import__(package)
            except ImportError:
                pytest.fail(f"Required package {package} is not available")
                
    def test_docker_daemon_running(self):
        """Test that Docker daemon is running."""
        try:
            result = subprocess.run(
                ["docker", "version"], 
                capture_output=True, 
                text=True, 
                timeout=10
            )
            assert result.returncode == 0, "Docker daemon should be running"
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pytest.fail("Docker daemon is not running or Docker is not installed")
            
    def test_docker_compose_command_available(self):
        """Test that docker-compose command is available."""
        try:
            result = subprocess.run(
                ["docker-compose", "--version"], 
                capture_output=True, 
                text=True, 
                timeout=10
            )
            assert result.returncode == 0, "docker-compose command should be available"
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pytest.fail("docker-compose command is not available")
            
    def test_application_structure_exists(self):
        """Test that application source structure exists."""
        required_dirs = [
            "src",
            "src/agents",
            "src/api", 
            "src/core",
            "src/models",
            "src/utils"
        ]
        
        for dir_path in required_dirs:
            assert Path(dir_path).exists(), f"Directory {dir_path} should exist"
            
    def test_main_application_file_exists(self):
        """Test that main application file exists."""
        main_file_path = Path("src/main.py")
        assert main_file_path.exists(), "src/main.py should exist"
        
    def test_configuration_file_exists(self):
        """Test that configuration file exists."""
        config_file_path = Path("src/core/config.py")
        assert config_file_path.exists(), "src/core/config.py should exist"


class TestEnvironmentConfiguration:
    """Test cases for environment configuration."""
    
    def test_environment_variables_defined(self):
        """Test that required environment variables are defined in template."""
        env_template_path = Path("config.env.example")
        with open(env_template_path, "r") as f:
            content = f.read()
            
        required_vars = [
            "APP_NAME",
            "APP_VERSION", 
            "DATABASE_URL",
            "MONGODB_URL",
            "REDIS_URL",
            "OPENAI_API_KEY",
            "SECRET_KEY"
        ]
        
        for var in required_vars:
            assert f"{var}=" in content, f"Environment variable {var} should be defined"
            
    def test_database_url_format(self):
        """Test that database URL format is correct."""
        env_template_path = Path("config.env.example")
        with open(env_template_path, "r") as f:
            content = f.read()
            
        # Check for PostgreSQL URL format
        assert "postgresql://" in content, "PostgreSQL URL format should be used"
        
    def test_redis_url_format(self):
        """Test that Redis URL format is correct."""
        env_template_path = Path("config.env.example")
        with open(env_template_path, "r") as f:
            content = f.read()
            
        # Check for Redis URL format
        assert "redis://" in content, "Redis URL format should be used"


class TestDockerServices:
    """Test cases for Docker services configuration."""
    
    def test_app_service_configuration(self):
        """Test app service configuration."""
        with open("docker-compose.yml", "r") as f:
            content = f.read()
            
        # Check app service configuration
        assert "build: ." in content, "App service should build from Dockerfile"
        assert "ports:" in content, "App service should expose ports"
        assert "8000:8000" in content, "App service should expose port 8000"
        
    def test_database_service_configuration(self):
        """Test database service configuration."""
        with open("docker-compose.yml", "r") as f:
            content = f.read()
            
        # Check database service configuration
        assert "postgres:15" in content, "PostgreSQL 15 should be used"
        assert "POSTGRES_DB=" in content, "Database name should be configured"
        assert "POSTGRES_USER=" in content, "Database user should be configured"
        assert "POSTGRES_PASSWORD=" in content, "Database password should be configured"
        
    def test_mongodb_service_configuration(self):
        """Test MongoDB service configuration."""
        with open("docker-compose.yml", "r") as f:
            content = f.read()
            
        # Check MongoDB service configuration
        assert "mongo:7" in content, "MongoDB 7 should be used"
        assert "MONGO_INITDB_ROOT_USERNAME=" in content, "MongoDB root username should be configured"
        assert "MONGO_INITDB_ROOT_PASSWORD=" in content, "MongoDB root password should be configured"
        
    def test_redis_service_configuration(self):
        """Test Redis service configuration."""
        with open("docker-compose.yml", "r") as f:
            content = f.read()
            
        # Check Redis service configuration
        assert "redis:7-alpine" in content, "Redis 7 Alpine should be used"
        assert "6379:6379" in content, "Redis should expose port 6379"


class TestApplicationHealth:
    """Test cases for application health checks."""
    
    def test_health_endpoint_accessible(self):
        """Test that health endpoint is accessible."""
        # This test will be implemented after the application is running
        # For now, we'll test the endpoint definition
        main_file_path = Path("src/main.py")
        with open(main_file_path, "r") as f:
            content = f.read()
            
        assert "@app.get(\"/health\")" in content, "Health endpoint should be defined"
        assert "health_check" in content, "Health check function should be defined"
        
    def test_root_endpoint_accessible(self):
        """Test that root endpoint is accessible."""
        main_file_path = Path("src/main.py")
        with open(main_file_path, "r") as f:
            content = f.read()
            
        assert "@app.get(\"/\")" in content, "Root endpoint should be defined"
        assert "root" in content, "Root function should be defined"


if __name__ == "__main__":
    pytest.main([__file__])



