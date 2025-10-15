"""
Regression Test Data Fixtures

This module provides comprehensive test data for regression testing scenarios.
Includes baseline data, performance metrics, API responses, and database schemas.
"""

import pytest
from datetime import datetime, date
from decimal import Decimal
from typing import Dict, List, Any
import json


@pytest.fixture
def baseline_performance_metrics():
    """Baseline performance metrics for regression testing."""
    return {
        "execution_time": 1.0,  # seconds
        "memory_usage": 100.0,  # MB
        "cpu_usage": 50.0,     # percentage
        "disk_io": 10.0,       # MB/s
        "network_io": 5.0,     # MB/s
        "database_queries": 25, # count
        "cache_hits": 80.0,    # percentage
        "response_time": 0.5    # seconds
    }


@pytest.fixture
def regression_performance_metrics():
    """Performance metrics showing regressions."""
    return {
        "execution_time": 2.5,  # 150% increase
        "memory_usage": 200.0, # 100% increase
        "cpu_usage": 80.0,     # 60% increase
        "disk_io": 25.0,       # 150% increase
        "network_io": 15.0,    # 200% increase
        "database_queries": 50, # 100% increase
        "cache_hits": 60.0,    # 25% decrease
        "response_time": 1.5    # 200% increase
    }


@pytest.fixture
def baseline_api_responses():
    """Baseline API responses for regression testing."""
    return {
        "GET /api/contracts": {
            "status_code": 200,
            "response_time": 0.3,
            "data": {
                "contracts": [
                    {"id": 1, "contract_id": "C-001", "title": "Test Contract", "amount": 1000.00},
                    {"id": 2, "contract_id": "C-002", "title": "Another Contract", "amount": 2000.00}
                ],
                "total": 2,
                "page": 1,
                "per_page": 10
            }
        },
        "POST /api/contracts": {
            "status_code": 201,
            "response_time": 0.5,
            "data": {
                "id": 3,
                "contract_id": "C-003",
                "title": "New Contract",
                "amount": 1500.00,
                "created_at": "2024-01-01T00:00:00Z"
            }
        },
        "GET /api/invoices": {
            "status_code": 200,
            "response_time": 0.4,
            "data": {
                "invoices": [
                    {"id": 1, "invoice_id": "I-001", "contract_id": "C-001", "amount": 1000.00},
                    {"id": 2, "invoice_id": "I-002", "contract_id": "C-002", "amount": 2000.00}
                ],
                "total": 2
            }
        }
    }


@pytest.fixture
def regression_api_responses():
    """API responses showing regressions."""
    return {
        "GET /api/contracts": {
            "status_code": 200,
            "response_time": 1.2,  # 300% increase
            "data": {
                "contracts": [
                    {"id": 1, "contract_id": "C-001", "title": "Test Contract"},  # Missing amount
                    {"id": 2, "contract_id": "C-002", "title": "Another Contract", "amount": 2000.00}
                ],
                "total": 2,
                "page": 1,
                "per_page": 10
            }
        },
        "POST /api/contracts": {
            "status_code": 201,
            "response_time": 2.0,  # 300% increase
            "data": {
                "id": 3,
                "contract_id": "C-003",
                "title": "New Contract",
                "amount": 1500.00,
                "created_at": "2024-01-01T00:00:00Z"
            }
        },
        "GET /api/invoices": {
            "status_code": 200,
            "response_time": 1.5,  # 275% increase
            "data": {
                "invoices": [
                    {"id": 1, "invoice_id": "I-001", "contract_id": "C-001", "amount": 1000.00},
                    {"id": 2, "invoice_id": "I-002", "contract_id": "C-002", "amount": 2000.00}
                ],
                "total": 2
            }
        }
    }


@pytest.fixture
def baseline_database_schema():
    """Baseline database schema for regression testing."""
    return {
        "tables": {
            "contracts": {
                "columns": {
                    "id": {"type": "INTEGER", "nullable": False, "primary_key": True},
                    "contract_id": {"type": "VARCHAR(100)", "nullable": False, "unique": True},
                    "title": {"type": "VARCHAR(255)", "nullable": False},
                    "vendor": {"type": "VARCHAR(255)", "nullable": False},
                    "amount": {"type": "NUMERIC(15,2)", "nullable": False},
                    "currency": {"type": "VARCHAR(3)", "nullable": False, "default": "USD"},
                    "start_date": {"type": "DATE", "nullable": True},
                    "end_date": {"type": "DATE", "nullable": True},
                    "status": {"type": "VARCHAR(50)", "nullable": False, "default": "active"},
                    "created_at": {"type": "TIMESTAMP", "nullable": False},
                    "updated_at": {"type": "TIMESTAMP", "nullable": False}
                },
                "indexes": ["contract_id", "vendor", "status"],
                "constraints": ["unique_contract_id"]
            },
            "invoices": {
                "columns": {
                    "id": {"type": "INTEGER", "nullable": False, "primary_key": True},
                    "invoice_id": {"type": "VARCHAR(100)", "nullable": False, "unique": True},
                    "contract_id": {"type": "VARCHAR(100)", "nullable": False},
                    "vendor": {"type": "VARCHAR(255)", "nullable": False},
                    "amount": {"type": "NUMERIC(15,2)", "nullable": False},
                    "currency": {"type": "VARCHAR(3)", "nullable": False, "default": "USD"},
                    "due_date": {"type": "DATE", "nullable": True},
                    "status": {"type": "VARCHAR(50)", "nullable": False, "default": "pending"},
                    "created_at": {"type": "TIMESTAMP", "nullable": False},
                    "updated_at": {"type": "TIMESTAMP", "nullable": False}
                },
                "indexes": ["invoice_id", "contract_id", "vendor", "status"],
                "constraints": ["unique_invoice_id", "fk_contract_id"]
            },
            "documents": {
                "columns": {
                    "id": {"type": "INTEGER", "nullable": False, "primary_key": True},
                    "document_id": {"type": "VARCHAR(100)", "nullable": False, "unique": True},
                    "filename": {"type": "VARCHAR(255)", "nullable": False},
                    "file_path": {"type": "VARCHAR(500)", "nullable": False},
                    "file_size": {"type": "BIGINT", "nullable": False},
                    "mime_type": {"type": "VARCHAR(100)", "nullable": False},
                    "status": {"type": "VARCHAR(50)", "nullable": False, "default": "uploaded"},
                    "created_at": {"type": "TIMESTAMP", "nullable": False},
                    "updated_at": {"type": "TIMESTAMP", "nullable": False}
                },
                "indexes": ["document_id", "filename", "status"],
                "constraints": ["unique_document_id"]
            }
        },
        "relationships": [
            {"from": "invoices.contract_id", "to": "contracts.contract_id", "type": "foreign_key"}
        ]
    }


@pytest.fixture
def regression_database_schema():
    """Database schema showing regressions."""
    return {
        "tables": {
            "contracts": {
                "columns": {
                    "id": {"type": "INTEGER", "nullable": False, "primary_key": True},
                    "contract_id": {"type": "VARCHAR(100)", "nullable": False, "unique": True},
                    "title": {"type": "VARCHAR(255)", "nullable": False},
                    "vendor": {"type": "VARCHAR(255)", "nullable": False},
                    # Missing amount column - regression!
                    "currency": {"type": "VARCHAR(3)", "nullable": False, "default": "USD"},
                    "start_date": {"type": "DATE", "nullable": True},
                    "end_date": {"type": "DATE", "nullable": True},
                    "status": {"type": "VARCHAR(50)", "nullable": False, "default": "active"},
                    "created_at": {"type": "TIMESTAMP", "nullable": False},
                    "updated_at": {"type": "TIMESTAMP", "nullable": False}
                },
                "indexes": ["contract_id", "vendor", "status"],
                "constraints": ["unique_contract_id"]
            },
            "invoices": {
                "columns": {
                    "id": {"type": "INTEGER", "nullable": False, "primary_key": True},
                    "invoice_id": {"type": "VARCHAR(100)", "nullable": False, "unique": True},
                    "contract_id": {"type": "VARCHAR(100)", "nullable": False},
                    "vendor": {"type": "VARCHAR(255)", "nullable": False},
                    "amount": {"type": "NUMERIC(15,2)", "nullable": False},
                    "currency": {"type": "VARCHAR(3)", "nullable": False, "default": "USD"},
                    "due_date": {"type": "DATE", "nullable": True},
                    "status": {"type": "VARCHAR(50)", "nullable": False, "default": "pending"},
                    "created_at": {"type": "TIMESTAMP", "nullable": False},
                    "updated_at": {"type": "TIMESTAMP", "nullable": False}
                },
                "indexes": ["invoice_id", "contract_id", "vendor", "status"],
                "constraints": ["unique_invoice_id", "fk_contract_id"]
            },
            "documents": {
                "columns": {
                    "id": {"type": "INTEGER", "nullable": False, "primary_key": True},
                    "document_id": {"type": "VARCHAR(100)", "nullable": False, "unique": True},
                    "filename": {"type": "VARCHAR(255)", "nullable": False},
                    "file_path": {"type": "VARCHAR(500)", "nullable": False},
                    "file_size": {"type": "BIGINT", "nullable": False},
                    "mime_type": {"type": "VARCHAR(100)", "nullable": False},
                    "status": {"type": "VARCHAR(50)", "nullable": False, "default": "uploaded"},
                    "created_at": {"type": "TIMESTAMP", "nullable": False},
                    "updated_at": {"type": "TIMESTAMP", "nullable": False}
                },
                "indexes": ["document_id", "filename", "status"],
                "constraints": ["unique_document_id"]
            }
        },
        "relationships": [
            {"from": "invoices.contract_id", "to": "contracts.contract_id", "type": "foreign_key"}
        ]
    }


@pytest.fixture
def baseline_test_results():
    """Baseline test results for regression testing."""
    return {
        "unit_tests": {
            "total": 100,
            "passed": 95,
            "failed": 5,
            "skipped": 0,
            "execution_time": 30.0,
            "coverage": 85.0
        },
        "integration_tests": {
            "total": 50,
            "passed": 45,
            "failed": 5,
            "skipped": 0,
            "execution_time": 60.0,
            "coverage": 75.0
        },
        "regression_tests": {
            "total": 25,
            "passed": 25,
            "failed": 0,
            "skipped": 0,
            "execution_time": 15.0,
            "coverage": 90.0
        },
        "overall": {
            "total": 175,
            "passed": 165,
            "failed": 10,
            "skipped": 0,
            "execution_time": 105.0,
            "coverage": 83.3
        }
    }


@pytest.fixture
def regression_test_results():
    """Test results showing regressions."""
    return {
        "unit_tests": {
            "total": 100,
            "passed": 80,  # 15 fewer passing tests
            "failed": 20,   # 15 more failing tests
            "skipped": 0,
            "execution_time": 45.0,  # 50% increase
            "coverage": 75.0  # 10% decrease
        },
        "integration_tests": {
            "total": 50,
            "passed": 40,  # 5 fewer passing tests
            "failed": 10,  # 5 more failing tests
            "skipped": 0,
            "execution_time": 90.0,  # 50% increase
            "coverage": 65.0  # 10% decrease
        },
        "regression_tests": {
            "total": 25,
            "passed": 20,  # 5 fewer passing tests
            "failed": 5,   # 5 more failing tests
            "skipped": 0,
            "execution_time": 25.0,  # 67% increase
            "coverage": 80.0  # 10% decrease
        },
        "overall": {
            "total": 175,
            "passed": 140,  # 25 fewer passing tests
            "failed": 35,   # 25 more failing tests
            "skipped": 0,
            "execution_time": 160.0,  # 52% increase
            "coverage": 73.3  # 10% decrease
        }
    }


@pytest.fixture
def regression_thresholds():
    """Regression detection thresholds."""
    return {
        "performance": {
            "execution_time": 50.0,    # 50% increase threshold
            "memory_usage": 100.0,     # 100% increase threshold
            "cpu_usage": 75.0,         # 75% increase threshold
            "disk_io": 100.0,          # 100% increase threshold
            "network_io": 150.0,        # 150% increase threshold
            "database_queries": 100.0, # 100% increase threshold
            "cache_hits": 20.0,        # 20% decrease threshold
            "response_time": 100.0     # 100% increase threshold
        },
        "test_coverage": {
            "minimum_coverage": 80.0,   # Minimum coverage threshold
            "coverage_decrease": 5.0,  # 5% decrease threshold
            "test_failure_increase": 10.0,  # 10% increase threshold
            "execution_time_increase": 50.0  # 50% increase threshold
        },
        "api_behavior": {
            "response_time_increase": 100.0,  # 100% increase threshold
            "status_code_change": True,       # Any status code change
            "data_structure_change": True,    # Any data structure change
            "missing_fields": True           # Any missing fields
        },
        "database_schema": {
            "missing_tables": True,           # Any missing tables
            "missing_columns": True,         # Any missing columns
            "missing_indexes": True,         # Any missing indexes
            "missing_constraints": True,     # Any missing constraints
            "data_type_changes": True        # Any data type changes
        }
    }


@pytest.fixture
def regression_test_data():
    """Comprehensive regression test data."""
    return {
        "contracts": [
            {
                "contract_id": "REG-C-001",
                "title": "Regression Test Contract 1",
                "vendor": "Test Vendor A",
                "amount": Decimal("10000.00"),
                "currency": "USD",
                "start_date": date(2024, 1, 1),
                "end_date": date(2024, 12, 31),
                "status": "active"
            },
            {
                "contract_id": "REG-C-002",
                "title": "Regression Test Contract 2",
                "vendor": "Test Vendor B",
                "amount": Decimal("25000.00"),
                "currency": "EUR",
                "start_date": date(2024, 2, 1),
                "end_date": date(2024, 11, 30),
                "status": "active"
            },
            {
                "contract_id": "REG-C-003",
                "title": "Regression Test Contract 3",
                "vendor": "Test Vendor C",
                "amount": Decimal("50000.00"),
                "currency": "GBP",
                "start_date": date(2024, 3, 1),
                "end_date": date(2024, 10, 31),
                "status": "pending"
            }
        ],
        "invoices": [
            {
                "invoice_id": "REG-I-001",
                "contract_id": "REG-C-001",
                "vendor": "Test Vendor A",
                "amount": Decimal("5000.00"),
                "currency": "USD",
                "due_date": date(2024, 6, 30),
                "status": "pending"
            },
            {
                "invoice_id": "REG-I-002",
                "contract_id": "REG-C-002",
                "vendor": "Test Vendor B",
                "amount": Decimal("12500.00"),
                "currency": "EUR",
                "due_date": date(2024, 7, 31),
                "status": "paid"
            }
        ],
        "documents": [
            {
                "document_id": "REG-D-001",
                "filename": "regression_test_contract.pdf",
                "file_path": "/documents/regression/regression_test_contract.pdf",
                "file_size": 1024000,  # 1MB
                "mime_type": "application/pdf",
                "status": "processed"
            },
            {
                "document_id": "REG-D-002",
                "filename": "regression_test_invoice.pdf",
                "file_path": "/documents/regression/regression_test_invoice.pdf",
                "file_size": 512000,   # 512KB
                "mime_type": "application/pdf",
                "status": "uploaded"
            }
        ],
        "users": [
            {
                "username": "regression_test_user",
                "email": "regression.test@example.com",
                "full_name": "Regression Test User",
                "role": "admin",
                "is_active": True
            }
        ]
    }


@pytest.fixture
def regression_scenarios():
    """Various regression scenarios for testing."""
    return {
        "performance_regression": {
            "description": "Performance degradation in API endpoints",
            "baseline": {"response_time": 0.5, "memory_usage": 100.0},
            "current": {"response_time": 2.0, "memory_usage": 250.0},
            "expected_regressions": ["response_time", "memory_usage"]
        },
        "api_behavior_regression": {
            "description": "API response structure changes",
            "baseline": {"data": {"result": "success", "count": 10}},
            "current": {"data": {"result": "success", "count": 5, "new_field": "value"}},
            "expected_regressions": ["data_structure_change"]
        },
        "database_schema_regression": {
            "description": "Missing database columns",
            "baseline": {"columns": ["id", "name", "amount"]},
            "current": {"columns": ["id", "name"]},  # Missing amount
            "expected_regressions": ["missing_column"]
        },
        "test_coverage_regression": {
            "description": "Decreasing test coverage",
            "baseline": {"coverage": 85.0, "passed": 95},
            "current": {"coverage": 75.0, "passed": 80},
            "expected_regressions": ["coverage_decrease", "test_failure_increase"]
        }
    }


@pytest.fixture
def regression_notification_config():
    """Configuration for regression notifications."""
    return {
        "email": {
            "enabled": True,
            "recipients": ["dev-team@example.com", "qa-team@example.com"],
            "template": "regression_alert_email.html",
            "subject": "Regression Alert: {severity} - {type}"
        },
        "slack": {
            "enabled": True,
            "webhook_url": "https://hooks.slack.com/services/...",
            "channel": "#alerts",
            "template": "regression_alert_slack.json"
        },
        "teams": {
            "enabled": False,
            "webhook_url": "",
            "template": "regression_alert_teams.json"
        },
        "severity_thresholds": {
            "high": ["email", "slack"],
            "medium": ["slack"],
            "low": []
        }
    }
