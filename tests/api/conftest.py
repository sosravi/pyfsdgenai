"""
API Test Fixtures

This module provides fixtures and utilities for API testing.
"""

import pytest
import json
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
from typing import Dict, Any, List
from decimal import Decimal
from datetime import datetime, date


@pytest.fixture
def client():
    """Provide FastAPI test client."""
    from src.main import app, rate_limiter
    # Reset rate limiter for each test
    rate_limiter.requests = {}
    return TestClient(app)


@pytest.fixture
def mock_contract_data():
    """Provide mock contract upload data."""
    return {
        "filename": "service_agreement.pdf",
        "content_type": "application/pdf",
        "file_size": 1024000,
        "document_type": "pdf",
        "contract_type": "service",
        "title": "Service Agreement",
        "parties": ["Company A", "Company B"],
        "effective_date": "2025-01-01T00:00:00Z",
        "expiration_date": "2025-12-31T23:59:59Z",
        "value": 100000.00,
        "currency": "USD"
    }


@pytest.fixture
def mock_invoice_data():
    """Provide mock invoice upload data."""
    return {
        "invoice_number": "INV-001",
        "vendor": "Vendor Corp",
        "amount": 5000.00,
        "currency": "USD",
        "invoice_date": "2025-01-01T00:00:00Z",
        "due_date": "2025-01-31T23:59:59Z",
        "contract_id": "contract_123"
    }


@pytest.fixture
def mock_login_data():
    """Provide mock login data."""
    return {
        "username": "test_user",
        "password": "test_password"
    }


@pytest.fixture
def mock_contract_id():
    """Provide mock contract ID."""
    return "contract_123"


@pytest.fixture
def mock_invoice_id():
    """Provide mock invoice ID."""
    return "invoice_789"


@pytest.fixture
def mock_agent_id():
    """Provide mock agent ID."""
    return "pricing_agent_1"


@pytest.fixture
def mock_access_token():
    """Provide mock access token."""
    return "mock_access_token_123"


@pytest.fixture
def mock_refresh_token():
    """Provide mock refresh token."""
    return "mock_refresh_token_456"


@pytest.fixture
def mock_contracts():
    """Provide mock contracts list."""
    return [
        {
            "id": "contract_123",
            "title": "Service Agreement",
            "contract_type": "service",
            "parties": ["Company A", "Company B"],
            "status": "completed",
            "created_at": "2025-01-01T00:00:00Z"
        },
        {
            "id": "contract_456",
            "title": "Supply Contract",
            "contract_type": "supply",
            "parties": ["Company C", "Company D"],
            "status": "pending",
            "created_at": "2025-01-02T00:00:00Z"
        }
    ]


@pytest.fixture
def mock_invoices():
    """Provide mock invoices list."""
    return [
        {
            "id": "invoice_789",
            "invoice_number": "INV-001",
            "vendor": "Vendor Corp",
            "amount": 5000.00,
            "status": "reconciled",
            "reconciled": True,
            "created_at": "2025-01-01T00:00:00Z"
        },
        {
            "id": "invoice_101",
            "invoice_number": "INV-002",
            "vendor": "Another Vendor",
            "amount": 7500.00,
            "status": "pending",
            "reconciled": False,
            "created_at": "2025-01-02T00:00:00Z"
        }
    ]


@pytest.fixture
def mock_agents():
    """Provide mock agents list."""
    return [
        {
            "agent_id": "pricing_agent_1",
            "agent_name": "Pricing Structure Agent",
            "category": "pricing",
            "status": "active",
            "description": "Extracts pricing structures and rates"
        },
        {
            "agent_id": "terms_agent_1",
            "agent_name": "Terms & Conditions Agent",
            "category": "terms",
            "status": "active",
            "description": "Analyzes contractual terms and conditions"
        },
        {
            "agent_id": "risk_agent_1",
            "agent_name": "Risk Assessment Agent",
            "category": "risk",
            "status": "active",
            "description": "Assesses contract risk factors"
        }
    ]


@pytest.fixture
def mock_contract_processing_status():
    """Provide mock contract processing status."""
    return {
        "job_id": "job_456",
        "status": "processing",
        "progress": 75,
        "agents_completed": 15,
        "total_agents": 20,
        "estimated_completion": "2025-01-01T00:02:00Z"
    }


@pytest.fixture
def mock_contract_benchmark_result():
    """Provide mock contract benchmark result."""
    return {
        "contract_id": "contract_123",
        "overall_score": 8.5,
        "dimension_scores": {
            "pricing": 9.0,
            "terms": 8.0,
            "risk": 8.5,
            "compliance": 9.0
        },
        "strengths": [
            "Competitive pricing",
            "Clear payment terms",
            "Strong compliance framework"
        ],
        "weaknesses": [
            "Limited termination flexibility",
            "High liability exposure"
        ],
        "recommendations": [
            "Negotiate better termination terms",
            "Consider liability insurance"
        ],
        "industry_average": 7.2,
        "percentile_rank": 85.5,
        "generated_at": "2025-01-01T00:03:00Z"
    }


@pytest.fixture
def mock_invoice_reconciliation_result():
    """Provide mock invoice reconciliation result."""
    return {
        "invoice_id": "invoice_789",
        "contract_id": "contract_123",
        "reconciled": True,
        "price_match": True,
        "terms_match": True,
        "quantity_match": True,
        "discrepancies": [],
        "confidence_score": 0.95,
        "reconciled_at": "2025-01-01T00:02:00Z"
    }


@pytest.fixture
def mock_contracts_summary_report():
    """Provide mock contracts summary report."""
    return {
        "total_contracts": 150,
        "processed_contracts": 145,
        "pending_contracts": 5,
        "average_processing_time": 4.2,
        "average_quality_score": 8.1,
        "contract_types": {
            "service": 80,
            "supply": 45,
            "software": 25
        },
        "processing_stats": {
            "success_rate": 0.97,
            "error_rate": 0.03
        }
    }


@pytest.fixture
def mock_invoices_reconciliation_summary():
    """Provide mock invoices reconciliation summary."""
    return {
        "total_invoices": 500,
        "reconciled_invoices": 480,
        "pending_reconciliation": 20,
        "discrepancies_found": 15,
        "average_confidence_score": 0.94,
        "cost_savings": 25000.00,
        "currency": "USD"
    }


@pytest.fixture
def mock_agent_status():
    """Provide mock agent status."""
    return {
        "agent_id": "pricing_agent_1",
        "agent_name": "Pricing Structure Agent",
        "status": "idle",
        "last_processed": "2025-01-01T00:00:00Z",
        "total_processed": 150,
        "success_rate": 0.98
    }


@pytest.fixture
def mock_agent_execution_result():
    """Provide mock agent execution result."""
    return {
        "execution_id": "exec_789",
        "status": "completed",
        "result": {
            "pricing_items": [
                {
                    "description": "Software License",
                    "quantity": 1,
                    "unit_price": 5000.00,
                    "total": 5000.00,
                    "currency": "USD"
                }
            ],
            "total_amount": 5000.00,
            "currency": "USD",
            "confidence": 0.95
        },
        "execution_time": 2.5,
        "completed_at": "2025-01-01T00:02:30Z"
    }


@pytest.fixture
def mock_auth_response():
    """Provide mock authentication response."""
    return {
        "access_token": "mock_access_token_123",
        "token_type": "bearer",
        "expires_in": 3600,
        "refresh_token": "mock_refresh_token_456"
    }


@pytest.fixture
def mock_error_response():
    """Provide mock error response."""
    return {
        "success": False,
        "message": "Error description",
        "error": "Detailed error message",
        "error_code": "ERROR_CODE",
        "timestamp": "2025-01-01T00:00:00Z"
    }


@pytest.fixture
def mock_rate_limit_headers():
    """Provide mock rate limit headers."""
    return {
        "X-RateLimit-Limit": "100",
        "X-RateLimit-Remaining": "95",
        "X-RateLimit-Reset": "1640995200"
    }


@pytest.fixture
def mock_webhook_payload():
    """Provide mock webhook payload."""
    return {
        "event": "contract.processing.completed",
        "data": {
            "contract_id": "contract_123",
            "job_id": "job_456",
            "processing_time": 4.2,
            "quality_score": 8.5
        },
        "timestamp": "2025-01-01T00:00:00Z"
    }


@pytest.fixture
def mock_database_session():
    """Provide mock database session."""
    session = Mock()
    session.add = Mock()
    session.commit = Mock()
    session.rollback = Mock()
    session.close = Mock()
    return session


@pytest.fixture
def mock_file_upload():
    """Provide mock file upload."""
    return {
        "filename": "test_contract.pdf",
        "content": b"Mock PDF content",
        "content_type": "application/pdf",
        "size": 1024
    }


@pytest.fixture
def mock_processing_job():
    """Provide mock processing job."""
    return {
        "job_id": "job_456",
        "contract_id": "contract_123",
        "status": "processing",
        "progress": 0,
        "agents_completed": 0,
        "total_agents": 20,
        "estimated_completion": "2025-01-01T00:05:00Z",
        "created_at": "2025-01-01T00:00:00Z"
    }


@pytest.fixture
def mock_benchmark_job():
    """Provide mock benchmark job."""
    return {
        "benchmark_id": "bench_202",
        "contract_id": "contract_123",
        "status": "processing",
        "estimated_completion": "2025-01-01T00:03:00Z",
        "created_at": "2025-01-01T00:00:00Z"
    }


@pytest.fixture
def mock_reconciliation_job():
    """Provide mock reconciliation job."""
    return {
        "reconciliation_id": "recon_101",
        "invoice_id": "invoice_789",
        "contract_id": "contract_123",
        "status": "processing",
        "estimated_completion": "2025-01-01T00:02:00Z",
        "created_at": "2025-01-01T00:00:00Z"
    }
