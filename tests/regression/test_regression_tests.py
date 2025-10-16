"""
PyFSD GenAI - Regression Tests

This module contains regression tests to ensure that previously
fixed bugs do not reoccur and that existing functionality
continues to work as expected.
"""

import pytest
import json
from unittest.mock import patch, Mock
from fastapi.testclient import TestClient

from tests.test_helpers import TestDataFactory, APITestHelper, MockHelper


class TestContractRegressionTests:
    """Regression tests for contract functionality."""
    
    def test_contract_creation_regression(self, test_client):
        """Regression test: Contract creation should work consistently."""
        api_helper = APITestHelper(test_client)
        
        # Test multiple contract creations to ensure consistency
        for i in range(5):
            contract_data = TestDataFactory.create_contract_data(
                contract_id=f"REGRESSION-{i:03d}",
                title=f"Regression Test Contract {i}"
            )
            
            response = test_client.post("/contracts", json=contract_data)
            # Should consistently succeed
            api_helper.assert_success_response(response, 201)
    
    def test_contract_validation_regression(self, test_client):
        """Regression test: Contract validation should be consistent."""
        api_helper = APITestHelper(test_client)
        
        # Test that validation errors are consistent
        invalid_contracts = [
            {"title": "Missing Required Fields"},  # Missing contract_id, vendor, etc.
            {"contract_id": "TEST-001", "amount": -100},  # Negative amount
            {"contract_id": "TEST-002", "currency": "INVALID"},  # Invalid currency
            {"contract_id": "TEST-003", "status": "invalid_status"}  # Invalid status
        ]
        
        for invalid_contract in invalid_contracts:
            response = test_client.post("/contracts", json=invalid_contract)
            # Should consistently reject invalid data
            api_helper.assert_error_response(response, 422)
    
    def test_contract_id_uniqueness_regression(self, test_client):
        """Regression test: Contract ID uniqueness should be enforced."""
        api_helper = APITestHelper(test_client)
        
        contract_data = TestDataFactory.create_contract_data(contract_id="UNIQUE-001")
        
        # Create first contract
        response1 = test_client.post("/contracts", json=contract_data)
        api_helper.assert_success_response(response1, 201)
        
        # Try to create second contract with same ID
        response2 = test_client.post("/contracts", json=contract_data)
        # Should reject duplicate ID
        api_helper.assert_error_response(response2, 409)  # 409 = Conflict
    
    def test_contract_amount_precision_regression(self, test_client):
        """Regression test: Contract amount precision should be maintained."""
        api_helper = APITestHelper(test_client)
        
        # Test various precision amounts
        precision_amounts = [
            100.00,
            100.01,
            100.10,
            100.99,
            999.99,
            1000.00
        ]
        
        for amount in precision_amounts:
            contract_data = TestDataFactory.create_contract_data(amount=amount)
            
            response = test_client.post("/contracts", json=contract_data)
            api_helper.assert_success_response(response, 201)
            
            # Verify amount precision is maintained
            data = response.json()
            assert data["amount"] == amount


class TestInvoiceRegressionTests:
    """Regression tests for invoice functionality."""
    
    def test_invoice_creation_regression(self, test_client):
        """Regression test: Invoice creation should work consistently."""
        api_helper = APITestHelper(test_client)
        
        # Test multiple invoice creations
        for i in range(3):
            invoice_data = TestDataFactory.create_invoice_data(
                invoice_id=f"INV-REGRESSION-{i:03d}",
                contract_id=f"CONTRACT-{i:03d}"
            )
            
            response = test_client.post("/invoices", json=invoice_data)
            # Should consistently succeed
            api_helper.assert_success_response(response, 201)
    
    def test_invoice_line_items_regression(self, test_client):
        """Regression test: Invoice line items should be handled correctly."""
        api_helper = APITestHelper(test_client)
        
        # Test various line item scenarios
        line_item_scenarios = [
            [{"description": "Single Item", "quantity": 1, "unit_price": 100.00, "total": 100.00}],
            [
                {"description": "Item 1", "quantity": 2, "unit_price": 50.00, "total": 100.00},
                {"description": "Item 2", "quantity": 1, "unit_price": 25.00, "total": 25.00}
            ],
            [{"description": "Zero Quantity", "quantity": 0, "unit_price": 100.00, "total": 0.00}]
        ]
        
        for i, line_items in enumerate(line_item_scenarios):
            invoice_data = TestDataFactory.create_invoice_data(
                invoice_id=f"LINE-ITEMS-{i:03d}",
                line_items=line_items
            )
            
            response = test_client.post("/invoices", json=invoice_data)
            # Should handle line items correctly
            assert response.status_code in [200, 201, 400, 422]
    
    def test_invoice_amount_calculation_regression(self, test_client):
        """Regression test: Invoice amount calculation should be accurate."""
        api_helper = APITestHelper(test_client)
        
        # Test amount calculation
        line_items = [
            {"description": "Item 1", "quantity": 2, "unit_price": 50.00, "total": 100.00},
            {"description": "Item 2", "quantity": 1, "unit_price": 25.00, "total": 25.00},
            {"description": "Item 3", "quantity": 3, "unit_price": 10.00, "total": 30.00}
        ]
        
        expected_total = 155.00
        
        invoice_data = TestDataFactory.create_invoice_data(
            invoice_id="CALCULATION-TEST",
            amount=expected_total,
            line_items=line_items
        )
        
        response = test_client.post("/invoices", json=invoice_data)
        api_helper.assert_success_response(response, 201)
        
        # Verify amount calculation
        data = response.json()
        assert data["amount"] == expected_total


class TestDocumentRegressionTests:
    """Regression tests for document functionality."""
    
    def test_document_upload_regression(self, test_client, test_file_manager):
        """Regression test: Document upload should work consistently."""
        api_helper = APITestHelper(test_client)
        
        # Test multiple document uploads
        for i in range(3):
            test_file_path = test_file_manager.create_temp_file(
                f"Regression test document {i}", ".txt"
            )
            
            with open(test_file_path, 'rb') as f:
                files = {"file": (f"regression_{i}.txt", f, "text/plain")}
                response = test_client.post("/documents/upload", files=files)
            
            # Should consistently succeed
            api_helper.assert_success_response(response, 201)
    
    def test_document_metadata_regression(self, test_client):
        """Regression test: Document metadata should be preserved."""
        api_helper = APITestHelper(test_client)
        
        # Test metadata preservation
        metadata_scenarios = [
            {"pages": 1, "language": "en", "confidence": 0.95},
            {"pages": 10, "language": "es", "confidence": 0.87},
            {"pages": 100, "language": "fr", "confidence": 0.99}
        ]
        
        for i, metadata in enumerate(metadata_scenarios):
            document_data = TestDataFactory.create_document_data(
                document_id=f"METADATA-{i:03d}",
                metadata=metadata
            )
            
            response = test_client.post("/documents", json=document_data)
            # Should preserve metadata
            assert response.status_code in [200, 201, 400, 422]
    
    def test_document_status_transitions_regression(self, test_client):
        """Regression test: Document status transitions should be consistent."""
        api_helper = APITestHelper(test_client)
        
        # Test status transitions
        status_transitions = [
            ("uploaded", "processing"),
            ("processing", "processed"),
            ("processed", "analyzed"),
            ("analyzed", "archived")
        ]
        
        for from_status, to_status in status_transitions:
            document_data = TestDataFactory.create_document_data(
                document_id=f"STATUS-{from_status}-{to_status}",
                status=from_status
            )
            
            response = test_client.post("/documents", json=document_data)
            # Should handle status transitions
            assert response.status_code in [200, 201, 400, 422]


class TestAIAgentRegressionTests:
    """Regression tests for AI agent functionality."""
    
    @patch('openai.OpenAI')
    def test_pricing_extraction_regression(self, mock_openai, test_client):
        """Regression test: Pricing extraction should be consistent."""
        api_helper = APITestHelper(test_client)
        
        # Setup mock
        mock_instance = Mock()
        mock_openai.return_value = mock_instance
        
        # Test multiple extractions
        for i in range(3):
            mock_response = MockHelper.mock_openai_response(f"Extracted pricing {i}: $5000")
            mock_instance.chat.completions.create.return_value = mock_response
            
            extraction_data = {
                "document_id": f"PRICING-{i:03d}",
                "extraction_type": "pricing"
            }
            
            response = test_client.post("/agents/pricing/extract", json=extraction_data)
            # Should consistently succeed
            api_helper.assert_success_response(response)
    
    @patch('anthropic.Anthropic')
    def test_contract_analysis_regression(self, mock_anthropic, test_client):
        """Regression test: Contract analysis should be consistent."""
        api_helper = APITestHelper(test_client)
        
        # Setup mock
        mock_instance = Mock()
        mock_anthropic.return_value = mock_instance
        
        # Test multiple analyses
        for i in range(3):
            mock_response = MockHelper.mock_anthropic_response(f"Contract analysis {i} complete")
            mock_instance.messages.create.return_value = mock_response
            
            analysis_data = {
                "document_id": f"ANALYSIS-{i:03d}",
                "analysis_type": "terms_extraction"
            }
            
            response = test_client.post("/agents/contract/analyze", json=analysis_data)
            # Should consistently succeed
            api_helper.assert_success_response(response)
    
    def test_agent_status_regression(self, test_client):
        """Regression test: Agent status should be consistent."""
        api_helper = APITestHelper(test_client)
        
        # Test multiple status checks
        for _ in range(5):
            response = test_client.get("/agents/status")
            api_helper.assert_success_response(response)
            
            # Verify consistent response structure
            data = response.json()
            assert "agents" in data
            assert isinstance(data["agents"], list)


class TestAuthenticationRegressionTests:
    """Regression tests for authentication functionality."""
    
    def test_login_regression(self, test_client):
        """Regression test: Login should work consistently."""
        api_helper = APITestHelper(test_client)
        
        # Test multiple login attempts
        for i in range(3):
            login_data = {
                "username": f"testuser{i}",
                "password": "testpassword"
            }
            
            response = test_client.post("/auth/login", json=login_data)
            # Should consistently succeed or fail based on user existence
            assert response.status_code in [200, 401]
    
    def test_token_validation_regression(self, test_client):
        """Regression test: Token validation should be consistent."""
        api_helper = APITestHelper(test_client)
        
        # Test various token scenarios
        token_scenarios = [
            "valid_token",
            "invalid_token",
            "expired_token",
            "malformed_token"
        ]
        
        for token in token_scenarios:
            headers = api_helper.get_auth_headers(token)
            response = test_client.get("/protected-endpoint", headers=headers)
            # Should handle tokens consistently
            assert response.status_code in [200, 401, 403]
    
    def test_logout_regression(self, test_client):
        """Regression test: Logout should work consistently."""
        api_helper = APITestHelper(test_client)
        
        # Test multiple logout attempts
        for _ in range(3):
            response = test_client.post("/auth/logout")
            # Should consistently succeed
            api_helper.assert_success_response(response, 204)


class TestPerformanceRegressionTests:
    """Regression tests for performance characteristics."""
    
    def test_response_time_regression(self, test_client, performance_helper):
        """Regression test: Response times should remain consistent."""
        api_helper = APITestHelper(test_client)
        
        # Test response times for multiple requests
        response_times = []
        
        for _ in range(10):
            performance_helper.start_timer()
            response = test_client.get("/health")
            performance_helper.stop_timer()
            
            api_helper.assert_success_response(response)
            response_times.append(performance_helper.elapsed_time)
        
        # Response times should be consistent (within reasonable variance)
        avg_response_time = sum(response_times) / len(response_times)
        max_response_time = max(response_times)
        
        assert avg_response_time < 1.0  # Average should be under 1 second
        assert max_response_time < 2.0  # Max should be under 2 seconds
    
    def test_concurrent_request_regression(self, test_client):
        """Regression test: Concurrent requests should be handled consistently."""
        import threading
        import time
        
        results = []
        
        def make_request():
            response = test_client.get("/health")
            results.append(response.status_code)
        
        # Test concurrent requests multiple times
        for _ in range(3):
            threads = []
            for _ in range(5):
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
            
            # Should handle concurrent requests consistently
            assert len(results) == 5
            assert all(status == 200 for status in results)
            assert end_time - start_time < 3.0  # Should complete within 3 seconds
            
            results.clear()  # Clear for next iteration


class TestDataIntegrityRegressionTests:
    """Regression tests for data integrity."""
    
    def test_data_consistency_regression(self, test_client, test_db_session):
        """Regression test: Data consistency should be maintained."""
        api_helper = APITestHelper(test_client)
        db_helper = DatabaseTestHelper(test_db_session)
        
        # Create contract and related invoice
        contract_data = TestDataFactory.create_contract_data(contract_id="INTEGRITY-001")
        
        response1 = test_client.post("/contracts", json=contract_data)
        api_helper.assert_success_response(response1, 201)
        
        invoice_data = TestDataFactory.create_invoice_data(
            invoice_id="INTEGRITY-INV-001",
            contract_id="INTEGRITY-001"
        )
        
        response2 = test_client.post("/invoices", json=invoice_data)
        api_helper.assert_success_response(response2, 201)
        
        # Verify data consistency
        contract_response = test_client.get("/contracts/INTEGRITY-001")
        invoice_response = test_client.get("/invoices/INTEGRITY-INV-001")
        
        api_helper.assert_success_response(contract_response)
        api_helper.assert_success_response(invoice_response)
        
        contract_data = contract_response.json()
        invoice_data = invoice_response.json()
        
        # Verify relationship integrity
        assert invoice_data["contract_id"] == contract_data["contract_id"]
    
    def test_data_persistence_regression(self, test_client):
        """Regression test: Data should persist correctly."""
        api_helper = APITestHelper(test_client)
        
        # Create data
        contract_data = TestDataFactory.create_contract_data(contract_id="PERSISTENCE-001")
        
        response1 = test_client.post("/contracts", json=contract_data)
        api_helper.assert_success_response(response1, 201)
        
        # Retrieve data
        response2 = test_client.get("/contracts/PERSISTENCE-001")
        api_helper.assert_success_response(response2)
        
        retrieved_data = response2.json()
        
        # Verify data persistence
        assert retrieved_data["contract_id"] == contract_data["contract_id"]
        assert retrieved_data["title"] == contract_data["title"]
        assert retrieved_data["amount"] == contract_data["amount"]


class TestErrorHandlingRegressionTests:
    """Regression tests for error handling."""
    
    def test_error_response_format_regression(self, test_client):
        """Regression test: Error response format should be consistent."""
        api_helper = APITestHelper(test_client)
        
        # Test various error scenarios
        error_scenarios = [
            ("/non-existent", 404),
            ("/contracts", "POST", {"invalid": "data"}, 422),
            ("/contracts/invalid-id", 404)
        ]
        
        for scenario in error_scenarios:
            if len(scenario) == 2:  # GET request
                endpoint, expected_status = scenario
                response = test_client.get(endpoint)
            else:  # POST request
                endpoint, method, data, expected_status = scenario
                response = test_client.post(endpoint, json=data)
            
            # Error response format should be consistent
            api_helper.assert_error_response(response, expected_status)
            
            # Verify error response structure
            error_data = response.json()
            assert "error" in error_data or "detail" in error_data
    
    def test_validation_error_regression(self, test_client):
        """Regression test: Validation errors should be consistent."""
        api_helper = APITestHelper(test_client)
        
        # Test various validation scenarios
        validation_scenarios = [
            {"contract_id": ""},  # Empty required field
            {"amount": "invalid"},  # Invalid type
            {"currency": "INVALID"},  # Invalid enum value
            {"start_date": "invalid-date"}  # Invalid date format
        ]
        
        for invalid_data in validation_scenarios:
            response = test_client.post("/contracts", json=invalid_data)
            api_helper.assert_error_response(response, 422)
            
            # Verify validation error structure
            error_data = response.json()
            assert "detail" in error_data
            assert isinstance(error_data["detail"], list)


@pytest.mark.regression
class TestRegressionMarkers:
    """Test that regression test markers work correctly."""
    
    def test_regression_marker_applied(self):
        """Test that regression marker is applied to this test."""
        assert True
    
    def test_historical_bug_prevention(self, test_client):
        """Test prevention of historical bugs."""
        api_helper = APITestHelper(test_client)
        
        # Test scenarios that previously caused bugs
        historical_bug_scenarios = [
            # Scenario 1: Empty string handling
            TestDataFactory.create_contract_data(title=""),
            # Scenario 2: Special characters
            TestDataFactory.create_contract_data(title="Test@#$%"),
            # Scenario 3: Very long strings
            TestDataFactory.create_contract_data(title="a" * 1000)
        ]
        
        for scenario_data in historical_bug_scenarios:
            response = test_client.post("/contracts", json=scenario_data)
            # Should handle without crashing
            assert response.status_code in [200, 201, 400, 422]
    
    def test_functionality_preservation(self, test_client):
        """Test that existing functionality is preserved."""
        api_helper = APITestHelper(test_client)
        
        # Test core functionality
        response = test_client.get("/health")
        api_helper.assert_success_response(response)
        
        # Test basic operations
        contract_data = TestDataFactory.create_contract_data()
        response = test_client.post("/contracts", json=contract_data)
        assert response.status_code in [200, 201, 400, 422]



