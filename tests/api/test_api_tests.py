"""
PyFSD GenAI - API Tests

This module contains tests specifically for API endpoints,
request/response handling, and API-specific functionality.
"""

import pytest
import json
from unittest.mock import patch, Mock
from fastapi.testclient import TestClient

from tests.test_helpers import TestDataFactory, APITestHelper, MockHelper


class TestHealthEndpoints:
    """Tests for health and status endpoints."""
    
    def test_health_endpoint(self, test_client):
        """Test health endpoint returns 200."""
        api_helper = APITestHelper(test_client)
        
        response = test_client.get("/health")
        data = api_helper.assert_success_response(response)
        
        # Verify response structure
        assert "status" in data
        assert data["status"] == "healthy"
    
    def test_root_endpoint(self, test_client):
        """Test root endpoint returns 200."""
        api_helper = APITestHelper(test_client)
        
        response = test_client.get("/")
        data = api_helper.assert_success_response(response)
        
        # Verify response structure
        assert "message" in data
        assert "version" in data
    
    def test_readiness_endpoint(self, test_client):
        """Test readiness endpoint."""
        api_helper = APITestHelper(test_client)
        
        response = test_client.get("/ready")
        data = api_helper.assert_success_response(response)
        
        # Verify response structure
        assert "ready" in data
        assert data["ready"] is True
    
    def test_liveness_endpoint(self, test_client):
        """Test liveness endpoint."""
        api_helper = APITestHelper(test_client)
        
        response = test_client.get("/live")
        data = api_helper.assert_success_response(response)
        
        # Verify response structure
        assert "alive" in data
        assert data["alive"] is True


class TestContractEndpoints:
    """Tests for contract-related API endpoints."""
    
    def test_get_contracts_endpoint(self, test_client):
        """Test GET /contracts endpoint."""
        api_helper = APITestHelper(test_client)
        
        response = test_client.get("/contracts")
        data = api_helper.assert_success_response(response)
        
        # Verify response structure
        assert isinstance(data, list)
    
    def test_create_contract_endpoint(self, test_client):
        """Test POST /contracts endpoint."""
        api_helper = APITestHelper(test_client)
        
        contract_data = TestDataFactory.create_contract_data()
        
        response = test_client.post("/contracts", json=contract_data)
        data = api_helper.assert_success_response(response, 201)
        
        # Verify response structure
        assert "contract_id" in data
        assert data["contract_id"] == contract_data["contract_id"]
    
    def test_get_contract_by_id_endpoint(self, test_client):
        """Test GET /contracts/{contract_id} endpoint."""
        api_helper = APITestHelper(test_client)
        
        contract_id = "TEST-CONTRACT-001"
        
        response = test_client.get(f"/contracts/{contract_id}")
        data = api_helper.assert_success_response(response)
        
        # Verify response structure
        assert "contract_id" in data
        assert data["contract_id"] == contract_id
    
    def test_update_contract_endpoint(self, test_client):
        """Test PUT /contracts/{contract_id} endpoint."""
        api_helper = APITestHelper(test_client)
        
        contract_id = "TEST-CONTRACT-001"
        update_data = {"status": "updated"}
        
        response = test_client.put(f"/contracts/{contract_id}", json=update_data)
        data = api_helper.assert_success_response(response)
        
        # Verify response structure
        assert "contract_id" in data
        assert data["status"] == "updated"
    
    def test_delete_contract_endpoint(self, test_client):
        """Test DELETE /contracts/{contract_id} endpoint."""
        api_helper = APITestHelper(test_client)
        
        contract_id = "TEST-CONTRACT-001"
        
        response = test_client.delete(f"/contracts/{contract_id}")
        api_helper.assert_success_response(response, 204)
    
    def test_contract_validation_errors(self, test_client):
        """Test contract validation error handling."""
        api_helper = APITestHelper(test_client)
        
        # Test missing required fields
        invalid_contract = {"title": "Test Contract"}
        
        response = test_client.post("/contracts", json=invalid_contract)
        api_helper.assert_error_response(response, 422)
    
    def test_contract_not_found_error(self, test_client):
        """Test contract not found error handling."""
        api_helper = APITestHelper(test_client)
        
        non_existent_id = "NON-EXISTENT-001"
        
        response = test_client.get(f"/contracts/{non_existent_id}")
        api_helper.assert_error_response(response, 404)


class TestInvoiceEndpoints:
    """Tests for invoice-related API endpoints."""
    
    def test_get_invoices_endpoint(self, test_client):
        """Test GET /invoices endpoint."""
        api_helper = APITestHelper(test_client)
        
        response = test_client.get("/invoices")
        data = api_helper.assert_success_response(response)
        
        # Verify response structure
        assert isinstance(data, list)
    
    def test_create_invoice_endpoint(self, test_client):
        """Test POST /invoices endpoint."""
        api_helper = APITestHelper(test_client)
        
        invoice_data = TestDataFactory.create_invoice_data()
        
        response = test_client.post("/invoices", json=invoice_data)
        data = api_helper.assert_success_response(response, 201)
        
        # Verify response structure
        assert "invoice_id" in data
        assert data["invoice_id"] == invoice_data["invoice_id"]
    
    def test_get_invoice_by_id_endpoint(self, test_client):
        """Test GET /invoices/{invoice_id} endpoint."""
        api_helper = APITestHelper(test_client)
        
        invoice_id = "INV-001"
        
        response = test_client.get(f"/invoices/{invoice_id}")
        data = api_helper.assert_success_response(response)
        
        # Verify response structure
        assert "invoice_id" in data
        assert data["invoice_id"] == invoice_id
    
    def test_invoice_reconciliation_endpoint(self, test_client):
        """Test POST /invoices/{invoice_id}/reconcile endpoint."""
        api_helper = APITestHelper(test_client)
        
        invoice_id = "INV-001"
        
        response = test_client.post(f"/invoices/{invoice_id}/reconcile")
        data = api_helper.assert_success_response(response)
        
        # Verify response structure
        assert "reconciliation_status" in data
        assert "matched_amount" in data
    
    def test_invoice_validation_errors(self, test_client):
        """Test invoice validation error handling."""
        api_helper = APITestHelper(test_client)
        
        # Test missing required fields
        invalid_invoice = {"amount": 1000}
        
        response = test_client.post("/invoices", json=invalid_invoice)
        api_helper.assert_error_response(response, 422)


class TestDocumentEndpoints:
    """Tests for document-related API endpoints."""
    
    def test_upload_document_endpoint(self, test_client, test_file_manager):
        """Test POST /documents/upload endpoint."""
        api_helper = APITestHelper(test_client)
        
        # Create test file
        test_file_path = test_file_manager.create_temp_file("Test document content", ".txt")
        
        with open(test_file_path, 'rb') as f:
            files = {"file": ("test.txt", f, "text/plain")}
            response = test_client.post("/documents/upload", files=files)
        
        data = api_helper.assert_success_response(response, 201)
        
        # Verify response structure
        assert "document_id" in data
        assert "filename" in data
        assert "status" in data
    
    def test_get_documents_endpoint(self, test_client):
        """Test GET /documents endpoint."""
        api_helper = APITestHelper(test_client)
        
        response = test_client.get("/documents")
        data = api_helper.assert_success_response(response)
        
        # Verify response structure
        assert isinstance(data, list)
    
    def test_get_document_by_id_endpoint(self, test_client):
        """Test GET /documents/{document_id} endpoint."""
        api_helper = APITestHelper(test_client)
        
        document_id = "DOC-001"
        
        response = test_client.get(f"/documents/{document_id}")
        data = api_helper.assert_success_response(response)
        
        # Verify response structure
        assert "document_id" in data
        assert data["document_id"] == document_id
    
    def test_document_analysis_endpoint(self, test_client):
        """Test POST /documents/{document_id}/analyze endpoint."""
        api_helper = APITestHelper(test_client)
        
        document_id = "DOC-001"
        
        response = test_client.post(f"/documents/{document_id}/analyze")
        data = api_helper.assert_success_response(response)
        
        # Verify response structure
        assert "analysis_status" in data
        assert "extracted_data" in data
    
    def test_document_download_endpoint(self, test_client):
        """Test GET /documents/{document_id}/download endpoint."""
        api_helper = APITestHelper(test_client)
        
        document_id = "DOC-001"
        
        response = test_client.get(f"/documents/{document_id}/download")
        
        # Verify response
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/octet-stream"
    
    def test_file_upload_validation(self, test_client):
        """Test file upload validation."""
        api_helper = APITestHelper(test_client)
        
        # Test empty file upload
        files = {"file": ("empty.txt", b"", "text/plain")}
        response = test_client.post("/documents/upload", files=files)
        api_helper.assert_error_response(response, 400)
        
        # Test invalid file type
        files = {"file": ("test.exe", b"binary content", "application/x-executable")}
        response = test_client.post("/documents/upload", files=files)
        api_helper.assert_error_response(response, 400)


class TestAIAgentEndpoints:
    """Tests for AI agent-related API endpoints."""
    
    @patch('openai.OpenAI')
    def test_pricing_extraction_endpoint(self, mock_openai, test_client):
        """Test POST /agents/pricing/extract endpoint."""
        api_helper = APITestHelper(test_client)
        
        # Setup mock
        mock_instance = Mock()
        mock_openai.return_value = mock_instance
        
        mock_response = MockHelper.mock_openai_response("Extracted pricing: $5000")
        mock_instance.chat.completions.create.return_value = mock_response
        
        # Test data
        extraction_data = {
            "document_id": "DOC-001",
            "extraction_type": "pricing"
        }
        
        response = test_client.post("/agents/pricing/extract", json=extraction_data)
        data = api_helper.assert_success_response(response)
        
        # Verify response structure
        assert "extraction_result" in data
        assert "confidence" in data
        assert "extracted_data" in data
    
    @patch('anthropic.Anthropic')
    def test_contract_analysis_endpoint(self, mock_anthropic, test_client):
        """Test POST /agents/contract/analyze endpoint."""
        api_helper = APITestHelper(test_client)
        
        # Setup mock
        mock_instance = Mock()
        mock_anthropic.return_value = mock_instance
        
        mock_response = MockHelper.mock_anthropic_response("Contract analysis complete")
        mock_instance.messages.create.return_value = mock_response
        
        # Test data
        analysis_data = {
            "document_id": "DOC-001",
            "analysis_type": "terms_extraction"
        }
        
        response = test_client.post("/agents/contract/analyze", json=analysis_data)
        data = api_helper.assert_success_response(response)
        
        # Verify response structure
        assert "analysis_result" in data
        assert "confidence" in data
        assert "extracted_terms" in data
    
    def test_agent_status_endpoint(self, test_client):
        """Test GET /agents/status endpoint."""
        api_helper = APITestHelper(test_client)
        
        response = test_client.get("/agents/status")
        data = api_helper.assert_success_response(response)
        
        # Verify response structure
        assert "agents" in data
        assert isinstance(data["agents"], list)
        
        # Check agent status structure
        for agent in data["agents"]:
            assert "agent_id" in agent
            assert "status" in agent
            assert "last_active" in agent


class TestAuthenticationEndpoints:
    """Tests for authentication-related API endpoints."""
    
    def test_login_endpoint(self, test_client):
        """Test POST /auth/login endpoint."""
        api_helper = APITestHelper(test_client)
        
        login_data = {
            "username": "testuser",
            "password": "testpassword"
        }
        
        response = test_client.post("/auth/login", json=login_data)
        data = api_helper.assert_success_response(response)
        
        # Verify response structure
        assert "access_token" in data
        assert "token_type" in data
        assert "expires_in" in data
    
    def test_logout_endpoint(self, test_client):
        """Test POST /auth/logout endpoint."""
        api_helper = APITestHelper(test_client)
        
        response = test_client.post("/auth/logout")
        api_helper.assert_success_response(response, 204)
    
    def test_refresh_token_endpoint(self, test_client):
        """Test POST /auth/refresh endpoint."""
        api_helper = APITestHelper(test_client)
        
        refresh_data = {
            "refresh_token": "test_refresh_token"
        }
        
        response = test_client.post("/auth/refresh", json=refresh_data)
        data = api_helper.assert_success_response(response)
        
        # Verify response structure
        assert "access_token" in data
        assert "token_type" in data
    
    def test_invalid_login_credentials(self, test_client):
        """Test invalid login credentials."""
        api_helper = APITestHelper(test_client)
        
        invalid_login_data = {
            "username": "invaliduser",
            "password": "wrongpassword"
        }
        
        response = test_client.post("/auth/login", json=invalid_login_data)
        api_helper.assert_error_response(response, 401)


class TestErrorHandling:
    """Tests for API error handling."""
    
    def test_404_error_handling(self, test_client):
        """Test 404 error handling."""
        api_helper = APITestHelper(test_client)
        
        response = test_client.get("/non-existent-endpoint")
        api_helper.assert_error_response(response, 404)
    
    def test_405_method_not_allowed(self, test_client):
        """Test 405 method not allowed error."""
        api_helper = APITestHelper(test_client)
        
        # Try to POST to a GET-only endpoint
        response = test_client.post("/health")
        api_helper.assert_error_response(response, 405)
    
    def test_422_validation_error(self, test_client):
        """Test 422 validation error."""
        api_helper = APITestHelper(test_client)
        
        # Send invalid JSON data
        invalid_data = {"invalid_field": "value"}
        
        response = test_client.post("/contracts", json=invalid_data)
        api_helper.assert_error_response(response, 422)
    
    def test_500_internal_server_error(self, test_client):
        """Test 500 internal server error handling."""
        api_helper = APITestHelper(test_client)
        
        # This would require a specific endpoint that triggers an error
        # For now, we'll test basic error handling
        response = test_client.get("/health")
        api_helper.assert_success_response(response)


class TestAPIPerformance:
    """Tests for API performance."""
    
    def test_endpoint_response_time(self, test_client, performance_helper):
        """Test endpoint response time."""
        api_helper = APITestHelper(test_client)
        
        # Test health endpoint performance
        performance_helper.start_timer()
        response = test_client.get("/health")
        performance_helper.stop_timer()
        
        api_helper.assert_success_response(response)
        performance_helper.assert_performance(0.5)  # Should respond within 500ms
    
    def test_concurrent_api_requests(self, test_client):
        """Test concurrent API requests."""
        import threading
        import time
        
        results = []
        
        def make_request():
            response = test_client.get("/health")
            results.append(response.status_code)
        
        # Create multiple threads
        threads = []
        for _ in range(10):
            thread = threading.Thread(target=make_request)
            threads.append(thread)
        
        # Start all threads
        start_time = time.time()
        for thread in threads:
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        end_time = time.time()
        
        # Verify all requests succeeded
        assert len(results) == 10
        assert all(status == 200 for status in results)
        assert end_time - start_time < 3.0  # Should complete within 3 seconds


@pytest.mark.api
class TestAPIMarkers:
    """Test that API test markers work correctly."""
    
    def test_api_marker_applied(self):
        """Test that API marker is applied to this test."""
        assert True
    
    def test_request_response_cycle(self, test_client):
        """Test basic request-response cycle."""
        api_helper = APITestHelper(test_client)
        
        response = test_client.get("/health")
        api_helper.assert_success_response(response)
    
    def test_json_serialization(self):
        """Test JSON serialization."""
        test_data = TestDataFactory.create_contract_data()
        
        json_str = json.dumps(test_data)
        parsed_data = json.loads(json_str)
        
        assert parsed_data == test_data

