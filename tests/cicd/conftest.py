"""
CI/CD Pipeline Test Fixtures

This module provides fixtures and utilities for CI/CD pipeline testing.
"""

import pytest
import json
import yaml
from pathlib import Path
from unittest.mock import Mock, patch
from typing import Dict, Any


@pytest.fixture
def cicd_pipeline_config():
    """Provide CI/CD pipeline configuration."""
    config_path = Path("config/cicd_pipeline_config.json")
    
    if config_path.exists():
        with open(config_path, 'r') as f:
            return json.load(f)
    else:
        return {
            "required_jobs": [
                "unit-testing",
                "regression-testing",
                "functionality-validation",
                "security-validation",
                "code-quality",
                "documentation-validation",
                "performance-testing"
            ],
            "thresholds": {
                "coverage": 95.0,
                "security_score": 90.0,
                "performance_score": 85.0
            }
        }


@pytest.fixture
def github_workflow_content():
    """Provide GitHub workflow content."""
    workflow_path = Path(".github/workflows/ci-cd-pipeline.yml")
    
    if workflow_path.exists():
        with open(workflow_path, 'r') as f:
            return yaml.safe_load(f)
    else:
        return {
            "name": "Test Workflow",
            "on": {"push": {"branches": ["main"]}},
            "jobs": {
                "test": {
                    "runs-on": "ubuntu-latest",
                    "steps": [
                        {"name": "Checkout code", "uses": "actions/checkout@v4"}
                    ]
                }
            }
        }


@pytest.fixture
def mock_pipeline_execution_results():
    """Provide mock pipeline execution results."""
    return {
        "unit-testing": {
            "status": "success",
            "execution_time": 45.2,
            "coverage": 96.2,
            "tests_run": 150,
            "tests_passed": 148,
            "tests_failed": 2
        },
        "regression-testing": {
            "status": "success",
            "execution_time": 120.5,
            "tests_run": 45,
            "tests_passed": 45,
            "tests_failed": 0
        },
        "functionality-validation": {
            "status": "success",
            "execution_time": 30.8,
            "validations_run": 17,
            "validations_passed": 17,
            "validations_failed": 0
        },
        "security-validation": {
            "status": "success",
            "execution_time": 60.0,
            "vulnerabilities": 0,
            "high_issues": 0,
            "medium_issues": 0,
            "low_issues": 2
        },
        "code-quality": {
            "status": "success",
            "execution_time": 25.0,
            "lint_errors": 0,
            "type_errors": 0
        }
    }


@pytest.fixture
def mock_security_results():
    """Provide mock security validation results."""
    return {
        "bandit_scan": {
            "high_issues": 0,
            "medium_issues": 0,
            "low_issues": 2,
            "score": 95.0
        },
        "safety_check": {
            "vulnerabilities": 0,
            "score": 100.0
        },
        "pip_audit": {
            "vulnerabilities": 0,
            "score": 100.0
        },
        "secrets_detection": {
            "secrets_found": 0,
            "score": 100.0
        }
    }


@pytest.fixture
def mock_performance_results():
    """Provide mock performance testing results."""
    return {
        "unit_tests": {
            "execution_time": 45.2,
            "threshold": 60.0,
            "status": "pass"
        },
        "regression_tests": {
            "execution_time": 120.5,
            "threshold": 180.0,
            "status": "pass"
        },
        "functionality_validation": {
            "execution_time": 30.8,
            "threshold": 45.0,
            "status": "pass"
        },
        "load_tests": {
            "response_time": 150.0,
            "threshold": 200.0,
            "status": "pass"
        }
    }


@pytest.fixture
def mock_integration_results():
    """Provide mock integration test results."""
    return {
        "unit_tests": {
            "status": "success",
            "test_count": 150,
            "test_files": ["test_models.py", "test_agents.py"],
            "integration_method": "pytest"
        },
        "regression_tests": {
            "status": "success",
            "test_count": 45,
            "test_files": ["test_regression_framework.py"],
            "integration_method": "pytest"
        },
        "functionality_validation": {
            "status": "success",
            "validation_count": 17,
            "validation_files": ["test_functionality_validation.py"],
            "integration_method": "pytest"
        },
        "security_tools": {
            "status": "success",
            "tools_integrated": 4,
            "total_tools": 4,
            "tool_status": {
                "bandit": "available",
                "safety": "available",
                "pip_audit": "available",
                "detect_secrets": "available"
            }
        },
        "deployment_processes": {
            "status": "success",
            "environments_configured": 2,
            "total_environments": 2,
            "environment_status": {
                "staging": "accessible",
                "production": "accessible"
            }
        }
    }


@pytest.fixture
def mock_pipeline_metrics():
    """Provide mock pipeline metrics."""
    return {
        "timestamp": 1640995200.0,
        "execution_time": 120.5,
        "success_rate": 0.95,
        "failure_rate": 0.05,
        "coverage": 96.2,
        "security_score": 92.5,
        "performance_score": 88.7
    }


@pytest.fixture
def mock_pipeline_alerts():
    """Provide mock pipeline alerts."""
    return [
        {
            "type": "performance",
            "severity": "medium",
            "message": "Performance score 88.7 below threshold",
            "timestamp": 1640995200.0
        }
    ]


@pytest.fixture
def mock_pipeline_report():
    """Provide mock pipeline report."""
    return {
        "summary": {
            "pipeline_status": "success",
            "total_jobs": 7,
            "successful_jobs": 7,
            "failed_jobs": 0,
            "execution_time": 125.5,
            "coverage": 96.2,
            "security_score": 92.5,
            "performance_score": 88.7
        },
        "test_results": {
            "unit_tests": {
                "total": 150,
                "passed": 148,
                "failed": 2,
                "skipped": 0,
                "coverage": 96.2
            },
            "regression_tests": {
                "total": 45,
                "passed": 45,
                "failed": 0,
                "skipped": 0,
                "coverage": 100.0
            },
            "functionality_validation": {
                "total": 17,
                "passed": 17,
                "failed": 0,
                "skipped": 0,
                "coverage": 100.0
            }
        },
        "security_results": {
            "bandit_scan": {
                "high_issues": 0,
                "medium_issues": 0,
                "low_issues": 2,
                "score": 95.0
            },
            "safety_check": {
                "vulnerabilities": 0,
                "score": 100.0
            },
            "pip_audit": {
                "vulnerabilities": 0,
                "score": 100.0
            },
            "secrets_detection": {
                "secrets_found": 0,
                "score": 100.0
            }
        },
        "performance_results": {
            "unit_tests": {
                "execution_time": 45.2,
                "threshold": 60.0,
                "status": "pass"
            },
            "regression_tests": {
                "execution_time": 120.5,
                "threshold": 180.0,
                "status": "pass"
            },
            "functionality_validation": {
                "execution_time": 30.8,
                "threshold": 45.0,
                "status": "pass"
            }
        },
        "recommendations": [
            "Consider optimizing unit test execution time",
            "Add more comprehensive security scanning",
            "Implement performance monitoring for production deployments"
        ]
    }


@pytest.fixture
def mock_subprocess_result():
    """Provide mock subprocess result."""
    result = Mock()
    result.returncode = 0
    result.stdout = "Mock output"
    result.stderr = ""
    return result


@pytest.fixture
def mock_requests_response():
    """Provide mock requests response."""
    response = Mock()
    response.status_code = 200
    response.json.return_value = {"status": "healthy"}
    return response


@pytest.fixture
def temp_config_file(tmp_path):
    """Provide temporary configuration file."""
    config_file = tmp_path / "test_config.json"
    config_data = {
        "test": True,
        "thresholds": {
            "coverage": 95.0,
            "security_score": 90.0
        }
    }
    
    with open(config_file, 'w') as f:
        json.dump(config_data, f)
    
    return config_file


@pytest.fixture
def temp_workflow_file(tmp_path):
    """Provide temporary workflow file."""
    workflow_file = tmp_path / "test_workflow.yml"
    workflow_data = {
        "name": "Test Workflow",
        "on": {"push": {"branches": ["main"]}},
        "jobs": {
            "test": {
                "runs-on": "ubuntu-latest",
                "steps": [
                    {"name": "Checkout code", "uses": "actions/checkout@v4"}
                ]
            }
        }
    }
    
    with open(workflow_file, 'w') as f:
        yaml.dump(workflow_data, f)
    
    return workflow_file


