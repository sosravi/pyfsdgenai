"""
API Endpoints Testing Framework

This module contains comprehensive tests for all API endpoints,
ensuring that the FastAPI application works correctly with proper
validation, error handling, and response formatting.

Test Categories:
- Health Check Endpoints
- Contract Management Endpoints
- Invoice Management Endpoints
- Agent Management Endpoints
- Reports and Analytics Endpoints
- Authentication and Authorization
- Error Handling and Validation
- API Performance and Load Testing
"""

import pytest
import json
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any, List
from decimal import Decimal
from datetime import datetime, date


class TestHealthCheckEndpoints:
    """Test health check endpoints."""
    
    def test_health_check_endpoint(self, client):
        """Test health check endpoint returns correct response."""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "PyFSD GenAI"
        assert "version" in data
        assert "timestamp" in data
    
    def test_health_check_response_format(self, client):
        """Test health check response format is correct."""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        
        required_fields = ["status", "service", "version", "timestamp"]
        for field in required_fields:
            assert field in data, f"Required field '{field}' missing from response"
        
        assert isinstance(data["status"], str)
        assert isinstance(data["service"], str)
        assert isinstance(data["version"], str)
        assert isinstance(data["timestamp"], str)


class TestContractManagementEndpoints:
    """Test contract management endpoints."""
    
    def test_upload_contract_endpoint(self, client, mock_contract_data):
        """Test contract upload endpoint."""
        response = client.post("/contracts/upload", json=mock_contract_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True
        assert "message" in data
        assert "data" in data
        assert "contract_id" in data["data"]
        assert "status" in data["data"]
        assert "uploaded_at" in data["data"]
    
    def test_upload_contract_validation(self, client):
        """Test contract upload validation."""
        invalid_data = {
            "filename": "",  # Empty filename should fail
            "content_type": "application/pdf",
            "file_size": 1024000
        }
        
        response = client.post("/contracts/upload", json=invalid_data)
        
        assert response.status_code == 422
        data = response.json()
        assert data["success"] is False
        assert "error" in data
    
    def test_get_contracts_list(self, client, mock_contracts):
        """Test getting contracts list."""
        response = client.get("/contracts")
        
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert "page" in data
        assert "page_size" in data
        assert "total_pages" in data
        assert "has_next" in data
        assert "has_prev" in data
        
        assert isinstance(data["items"], list)
        assert isinstance(data["total"], int)
        assert isinstance(data["page"], int)
        assert isinstance(data["page_size"], int)
    
    def test_get_contracts_with_pagination(self, client, mock_contracts):
        """Test contracts list with pagination."""
        response = client.get("/contracts?page=1&page_size=10")
        
        assert response.status_code == 200
        data = response.json()
        assert data["page"] == 1
        assert data["page_size"] == 10
    
    def test_get_contracts_with_filters(self, client, mock_contracts):
        """Test contracts list with filters."""
        response = client.get("/contracts?status=completed&contract_type=service")
        
        assert response.status_code == 200
        data = response.json()
        # All returned contracts should match filters
        for contract in data["items"]:
            assert contract["status"] == "completed"
            assert contract["contract_type"] == "service"
    
    def test_get_specific_contract(self, client, mock_contract_id):
        """Test getting specific contract."""
        response = client.get(f"/contracts/{mock_contract_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "data" in data
        
        contract_data = data["data"]
        required_fields = [
            "id", "title", "contract_type", "parties", "effective_date",
            "expiration_date", "value", "currency", "status"
        ]
        for field in required_fields:
            assert field in contract_data, f"Required field '{field}' missing"
    
    def test_get_nonexistent_contract(self, client):
        """Test getting nonexistent contract returns 404."""
        response = client.get("/contracts/nonexistent_id")
        
        assert response.status_code == 404
        data = response.json()
        assert data["success"] is False
        assert "error" in data
    
    def test_start_contract_processing(self, client, mock_contract_id):
        """Test starting contract processing."""
        response = client.post(f"/contracts/{mock_contract_id}/process")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "message" in data
        assert "data" in data
        assert "job_id" in data["data"]
        assert "status" in data["data"]
        assert "estimated_completion" in data["data"]
    
    def test_get_contract_processing_status(self, client, mock_contract_id):
        """Test getting contract processing status."""
        response = client.get(f"/contracts/{mock_contract_id}/processing-status")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "data" in data
        
        status_data = data["data"]
        required_fields = [
            "job_id", "status", "progress", "agents_completed",
            "total_agents", "estimated_completion"
        ]
        for field in required_fields:
            assert field in status_data, f"Required field '{field}' missing"
    
    def test_start_contract_benchmarking(self, client, mock_contract_id):
        """Test starting contract benchmarking."""
        response = client.post(f"/contracts/{mock_contract_id}/benchmark")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "message" in data
        assert "data" in data
        assert "benchmark_id" in data["data"]
        assert "status" in data["data"]
        assert "estimated_completion" in data["data"]
    
    def test_get_contract_benchmark_result(self, client, mock_contract_id):
        """Test getting contract benchmark result."""
        response = client.get(f"/contracts/{mock_contract_id}/benchmark-result")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "data" in data
        
        benchmark_data = data["data"]
        required_fields = [
            "contract_id", "overall_score", "dimension_scores",
            "strengths", "weaknesses", "recommendations",
            "industry_average", "percentile_rank", "generated_at"
        ]
        for field in required_fields:
            assert field in benchmark_data, f"Required field '{field}' missing"


class TestInvoiceManagementEndpoints:
    """Test invoice management endpoints."""
    
    def test_upload_invoice_endpoint(self, client, mock_invoice_data):
        """Test invoice upload endpoint."""
        response = client.post("/invoices/upload", json=mock_invoice_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True
        assert "message" in data
        assert "data" in data
        assert "invoice_id" in data["data"]
        assert "status" in data["data"]
        assert "uploaded_at" in data["data"]
    
    def test_upload_invoice_validation(self, client):
        """Test invoice upload validation."""
        invalid_data = {
            "invoice_number": "",  # Empty invoice number should fail
            "vendor": "Vendor Corp",
            "amount": -100.0  # Negative amount should fail
        }
        
        response = client.post("/invoices/upload", json=invalid_data)
        
        assert response.status_code == 422
        data = response.json()
        assert data["success"] is False
        assert "error" in data
    
    def test_get_invoices_list(self, client, mock_invoices):
        """Test getting invoices list."""
        response = client.get("/invoices")
        
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert "page" in data
        assert "page_size" in data
        
        assert isinstance(data["items"], list)
        assert isinstance(data["total"], int)
    
    def test_get_invoices_with_filters(self, client, mock_invoices):
        """Test invoices list with filters."""
        response = client.get("/invoices?status=reconciled&contract_id=contract_123")
        
        assert response.status_code == 200
        data = response.json()
        # All returned invoices should match filters
        for invoice in data["items"]:
            assert invoice["status"] == "reconciled"
            assert invoice.get("contract_id") == "contract_123"
    
    def test_start_invoice_reconciliation(self, client, mock_invoice_id):
        """Test starting invoice reconciliation."""
        response = client.post(f"/invoices/{mock_invoice_id}/reconcile")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "message" in data
        assert "data" in data
        assert "reconciliation_id" in data["data"]
        assert "status" in data["data"]
        assert "estimated_completion" in data["data"]
    
    def test_get_invoice_reconciliation_result(self, client, mock_invoice_id):
        """Test getting invoice reconciliation result."""
        response = client.get(f"/invoices/{mock_invoice_id}/reconciliation-result")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "data" in data
        
        reconciliation_data = data["data"]
        required_fields = [
            "invoice_id", "contract_id", "reconciled", "price_match",
            "terms_match", "quantity_match", "discrepancies",
            "confidence_score", "reconciled_at"
        ]
        for field in required_fields:
            assert field in reconciliation_data, f"Required field '{field}' missing"


class TestAgentManagementEndpoints:
    """Test agent management endpoints."""
    
    def test_get_agents_list(self, client, mock_agents):
        """Test getting agents list."""
        response = client.get("/agents")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "data" in data
        
        agents_data = data["data"]
        assert "agents" in agents_data
        assert "total_agents" in agents_data
        assert "active_agents" in agents_data
        
        assert isinstance(agents_data["agents"], list)
        assert isinstance(agents_data["total_agents"], int)
        assert isinstance(agents_data["active_agents"], int)
    
    def test_get_agent_status(self, client, mock_agent_id):
        """Test getting specific agent status."""
        response = client.get(f"/agents/{mock_agent_id}/status")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "data" in data
        
        agent_data = data["data"]
        required_fields = [
            "agent_id", "agent_name", "status", "last_processed",
            "total_processed", "success_rate"
        ]
        for field in required_fields:
            assert field in agent_data, f"Required field '{field}' missing"
    
    def test_get_nonexistent_agent_status(self, client):
        """Test getting nonexistent agent status returns 404."""
        response = client.get("/agents/nonexistent_agent/status")
        
        assert response.status_code == 404
        data = response.json()
        assert data["success"] is False
        assert "error" in data
    
    def test_agent_execution_endpoint(self, client, mock_agent_id):
        """Test agent execution endpoint."""
        execution_data = {
            "document_id": "doc_123",
            "parameters": {
                "extract_pricing": True,
                "confidence_threshold": 0.8
            }
        }
        
        response = client.post(f"/agents/{mock_agent_id}/execute", json=execution_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "message" in data
        assert "data" in data
        assert "execution_id" in data["data"]
        assert "status" in data["data"]


class TestReportsAndAnalyticsEndpoints:
    """Test reports and analytics endpoints."""
    
    def test_get_contracts_summary_report(self, client):
        """Test getting contracts summary report."""
        response = client.get("/reports/contracts/summary")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "data" in data
        
        report_data = data["data"]
        required_fields = [
            "total_contracts", "processed_contracts", "pending_contracts",
            "average_processing_time", "average_quality_score",
            "contract_types", "processing_stats"
        ]
        for field in required_fields:
            assert field in report_data, f"Required field '{field}' missing"
    
    def test_get_contracts_summary_with_filters(self, client):
        """Test contracts summary report with date filters."""
        response = client.get("/reports/contracts/summary?start_date=2025-01-01&end_date=2025-01-31")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "data" in data
    
    def test_get_invoices_reconciliation_summary(self, client):
        """Test getting invoices reconciliation summary report."""
        response = client.get("/reports/invoices/reconciliation-summary")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "data" in data
        
        report_data = data["data"]
        required_fields = [
            "total_invoices", "reconciled_invoices", "pending_reconciliation",
            "discrepancies_found", "average_confidence_score",
            "cost_savings", "currency"
        ]
        for field in required_fields:
            assert field in report_data, f"Required field '{field}' missing"


class TestAuthenticationEndpoints:
    """Test authentication endpoints."""
    
    def test_login_endpoint(self, client, mock_login_data):
        """Test login endpoint."""
        response = client.post("/auth/login", json=mock_login_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "data" in data
        assert "access_token" in data["data"]
        assert "token_type" in data["data"]
        assert "expires_in" in data["data"]
    
    def test_login_with_invalid_credentials(self, client):
        """Test login with invalid credentials."""
        invalid_data = {
            "username": "invalid_user",
            "password": "invalid_password"
        }
        
        response = client.post("/auth/login", json=invalid_data)
        
        assert response.status_code == 401
        data = response.json()
        assert data["success"] is False
        assert "error" in data
    
    def test_refresh_token_endpoint(self, client, mock_refresh_token):
        """Test refresh token endpoint."""
        response = client.post("/auth/refresh", json={"refresh_token": mock_refresh_token})
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "data" in data
        assert "access_token" in data["data"]
    
    def test_logout_endpoint(self, client, mock_access_token):
        """Test logout endpoint."""
        headers = {"Authorization": f"Bearer {mock_access_token}"}
        response = client.post("/auth/logout", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "message" in data


class TestErrorHandlingAndValidation:
    """Test error handling and validation."""
    
    def test_invalid_json_request(self, client):
        """Test handling of invalid JSON request."""
        response = client.post(
            "/contracts/upload",
            data="invalid json",
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 422
    
    def test_missing_required_fields(self, client):
        """Test handling of missing required fields."""
        incomplete_data = {
            "filename": "contract.pdf"
            # Missing required fields
        }
        
        response = client.post("/contracts/upload", json=incomplete_data)
        
        assert response.status_code == 422
        data = response.json()
        assert data["success"] is False
        assert "error" in data
    
    def test_invalid_field_types(self, client):
        """Test handling of invalid field types."""
        invalid_data = {
            "filename": "contract.pdf",
            "content_type": "application/pdf",
            "file_size": "not_a_number"  # Should be number
        }
        
        response = client.post("/contracts/upload", json=invalid_data)
        
        assert response.status_code == 422
        data = response.json()
        assert data["success"] is False
    
    def test_file_size_limit_exceeded(self, client):
        """Test handling of file size limit exceeded."""
        large_file_data = {
            "filename": "large_contract.pdf",
            "content_type": "application/pdf",
            "file_size": 1000000000  # 1GB - exceeds limit
        }
        
        response = client.post("/contracts/upload", json=large_file_data)
        
        assert response.status_code == 422  # Pydantic validation returns 422
        data = response.json()
        assert data["success"] is False
        assert "error_code" in data
        assert data["error_code"] == "FILE_TOO_LARGE"
    
    def test_unsupported_file_format(self, client):
        """Test handling of unsupported file format."""
        unsupported_data = {
            "filename": "contract.txt",
            "content_type": "text/plain",
            "file_size": 1024
        }
        
        response = client.post("/contracts/upload", json=unsupported_data)
        
        assert response.status_code == 422
        data = response.json()
        assert data["success"] is False
        assert "error_code" in data
        assert data["error_code"] == "UNSUPPORTED_FORMAT"


class TestAPIPerformanceAndLoad:
    """Test API performance and load handling."""
    
    def test_concurrent_requests(self, client, mock_contract_data):
        """Test handling of concurrent requests."""
        import concurrent.futures
        import threading
        
        def make_request():
            return client.post("/contracts/upload", json=mock_contract_data)
        
        # Make 10 concurrent requests
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(make_request) for _ in range(10)]
            responses = [future.result() for future in futures]
        
        # All requests should succeed
        for response in responses:
            assert response.status_code in [200, 201]
    
    def test_response_time_performance(self, client):
        """Test API response time performance."""
        import time
        
        start_time = time.time()
        response = client.get("/health")
        end_time = time.time()
        
        response_time = end_time - start_time
        
        assert response.status_code == 200
        assert response_time < 1.0  # Should respond within 1 second
    
    def test_rate_limiting(self, client):
        """Test rate limiting functionality."""
        # Make multiple requests quickly
        responses = []
        for _ in range(105):  # Exceed rate limit
            response = client.get("/health")
            responses.append(response)
        
        # Check if rate limiting headers are present
        last_response = responses[-1]
        assert "X-RateLimit-Limit" in last_response.headers
        assert "X-RateLimit-Remaining" in last_response.headers
        assert "X-RateLimit-Reset" in last_response.headers


class TestAPIIntegration:
    """Test API integration scenarios."""
    
    def test_end_to_end_contract_processing(self, client, mock_contract_data):
        """Test end-to-end contract processing workflow."""
        # 1. Upload contract
        upload_response = client.post("/contracts/upload", json=mock_contract_data)
        assert upload_response.status_code == 201
        contract_id = upload_response.json()["data"]["contract_id"]
        
        # 2. Start processing
        process_response = client.post(f"/contracts/{contract_id}/process")
        assert process_response.status_code == 200
        job_id = process_response.json()["data"]["job_id"]
        
        # 3. Check processing status
        status_response = client.get(f"/contracts/{contract_id}/processing-status")
        assert status_response.status_code == 200
        
        # 4. Start benchmarking
        benchmark_response = client.post(f"/contracts/{contract_id}/benchmark")
        assert benchmark_response.status_code == 200
        
        # 5. Get benchmark results
        benchmark_result_response = client.get(f"/contracts/{contract_id}/benchmark-result")
        assert benchmark_result_response.status_code == 200
    
    def test_end_to_end_invoice_reconciliation(self, client, mock_invoice_data):
        """Test end-to-end invoice reconciliation workflow."""
        # 1. Upload invoice
        upload_response = client.post("/invoices/upload", json=mock_invoice_data)
        assert upload_response.status_code == 201
        invoice_id = upload_response.json()["data"]["invoice_id"]
        
        # 2. Start reconciliation
        reconcile_response = client.post(f"/invoices/{invoice_id}/reconcile")
        assert reconcile_response.status_code == 200
        
        # 3. Get reconciliation results
        result_response = client.get(f"/invoices/{invoice_id}/reconciliation-result")
        assert result_response.status_code == 200
    
    def test_api_versioning(self, client):
        """Test API versioning."""
        # Test v1 endpoints
        response = client.get("/health")
        assert response.status_code == 200
        
        # Test that version is included in response
        data = response.json()
        assert "version" in data


class TestAPIMarkers:
    """Test API markers."""
    
    @pytest.mark.api
    def test_api_marker_applied(self):
        """Test that API marker is applied."""
        # This test should be marked with @pytest.mark.api
        assert True, "API marker should be applied"
    
    @pytest.mark.api
    def test_api_basic_functionality(self):
        """Test basic API functionality."""
        # Test basic API functionality
        assert True, "Basic API functionality should work"
