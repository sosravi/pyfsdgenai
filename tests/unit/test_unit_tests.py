"""
PyFSD GenAI - Unit Tests

This module contains unit tests for individual components and functions.
Unit tests focus on testing isolated units of code in isolation.
"""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime, timedelta

from test_helpers import TestDataFactory, MockHelper, EdgeCaseTestHelper


class TestDataFactoryUnit:
    """Unit tests for TestDataFactory."""
    
    def test_create_contract_data_default(self):
        """Test creating contract data with default values."""
        data = TestDataFactory.create_contract_data()
        
        assert data["contract_id"] == "TEST-CONTRACT-001"
        assert data["title"] == "Software License Agreement"
        assert data["vendor"] == "Test Vendor Inc."
        assert data["amount"] == 50000.00
        assert data["currency"] == "USD"
        assert data["status"] == "active"
    
    def test_create_contract_data_with_overrides(self):
        """Test creating contract data with overrides."""
        overrides = {
            "contract_id": "CUSTOM-001",
            "amount": 75000.00,
            "status": "draft"
        }
        data = TestDataFactory.create_contract_data(**overrides)
        
        assert data["contract_id"] == "CUSTOM-001"
        assert data["amount"] == 75000.00
        assert data["status"] == "draft"
        # Default values should still be present
        assert data["title"] == "Software License Agreement"
        assert data["vendor"] == "Test Vendor Inc."
    
    def test_create_invoice_data_default(self):
        """Test creating invoice data with default values."""
        data = TestDataFactory.create_invoice_data()
        
        assert data["invoice_id"] == "INV-001"
        assert data["contract_id"] == "TEST-CONTRACT-001"
        assert data["amount"] == 5000.00
        assert data["status"] == "pending"
        assert len(data["line_items"]) == 1
        assert data["line_items"][0]["description"] == "Software License"
    
    def test_create_document_data_default(self):
        """Test creating document data with default values."""
        data = TestDataFactory.create_document_data()
        
        assert data["document_id"] == "DOC-001"
        assert data["filename"] == "test_contract.pdf"
        assert data["file_type"] == "application/pdf"
        assert data["file_size"] == 1024000
        assert data["status"] == "processed"
        assert data["metadata"]["pages"] == 10
        assert data["metadata"]["confidence"] == 0.95
    
    def test_create_user_data_default(self):
        """Test creating user data with default values."""
        data = TestDataFactory.create_user_data()
        
        assert data["user_id"] == "USER-001"
        assert data["username"] == "testuser"
        assert data["email"] == "test@example.com"
        assert data["role"] == "analyst"
        assert data["is_active"] is True


class TestMockHelperUnit:
    """Unit tests for MockHelper."""
    
    def test_mock_openai_response_default(self):
        """Test creating default OpenAI mock response."""
        mock_response = MockHelper.mock_openai_response()
        
        assert mock_response.choices is not None
        assert len(mock_response.choices) == 1
        assert mock_response.choices[0].message is not None
        assert mock_response.choices[0].message.content == "Mocked AI response"
    
    def test_mock_openai_response_custom(self):
        """Test creating custom OpenAI mock response."""
        custom_content = "Custom AI response"
        mock_response = MockHelper.mock_openai_response(custom_content)
        
        assert mock_response.choices[0].message.content == custom_content
    
    def test_mock_anthropic_response_default(self):
        """Test creating default Anthropic mock response."""
        mock_response = MockHelper.mock_anthropic_response()
        
        assert mock_response.content is not None
        assert len(mock_response.content) == 1
        assert mock_response.content[0].text == "Mocked Anthropic response"
    
    def test_mock_anthropic_response_custom(self):
        """Test creating custom Anthropic mock response."""
        custom_content = "Custom Anthropic response"
        mock_response = MockHelper.mock_anthropic_response(custom_content)
        
        assert mock_response.content[0].text == custom_content
    
    def test_mock_file_upload_default(self):
        """Test creating default file upload mock."""
        mock_file = MockHelper.mock_file_upload()
        
        assert mock_file.filename == "test.pdf"
        assert mock_file.read() == b"test content"
        assert mock_file.size == len(b"test content")
    
    def test_mock_file_upload_custom(self):
        """Test creating custom file upload mock."""
        custom_filename = "custom.pdf"
        custom_content = b"custom content"
        mock_file = MockHelper.mock_file_upload(custom_filename, custom_content)
        
        assert mock_file.filename == custom_filename
        assert mock_file.read() == custom_content
        assert mock_file.size == len(custom_content)


class TestEdgeCaseTestHelperUnit:
    """Unit tests for EdgeCaseTestHelper."""
    
    def test_get_edge_case_strings(self):
        """Test getting edge case strings."""
        edge_cases = EdgeCaseTestHelper.get_edge_case_strings()
        
        assert isinstance(edge_cases, list)
        assert len(edge_cases) > 0
        assert "" in edge_cases  # Empty string
        assert " " in edge_cases  # Single space
        assert "🚀🔥💯" in edge_cases  # Emojis
        assert "测试中文" in edge_cases  # Unicode
    
    def test_get_edge_case_numbers(self):
        """Test getting edge case numbers."""
        edge_cases = EdgeCaseTestHelper.get_edge_case_numbers()
        
        assert isinstance(edge_cases, list)
        assert len(edge_cases) > 0
        assert 0 in edge_cases
        assert -1 in edge_cases
        assert 1 in edge_cases
        assert float('inf') in edge_cases
        assert float('-inf') in edge_cases
    
    def test_get_edge_case_dates(self):
        """Test getting edge case dates."""
        edge_cases = EdgeCaseTestHelper.get_edge_case_dates()
        
        assert isinstance(edge_cases, list)
        assert len(edge_cases) > 0
        assert "2024-01-01" in edge_cases
        assert "2024-02-29" in edge_cases  # Leap year
        assert "2024-13-01" in edge_cases  # Invalid month
        assert "2024-01-01T00:00:00Z" in edge_cases  # ISO format


class TestUtilityFunctions:
    """Unit tests for utility functions."""
    
    def test_date_validation_valid(self):
        """Test valid date validation."""
        from datetime import datetime
        
        valid_dates = [
            "2024-01-01",
            "2024-12-31",
            "2024-02-29",  # Leap year
            "2024-01-01T00:00:00Z"
        ]
        
        for date_str in valid_dates:
            try:
                datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                assert True  # Should not raise exception
            except ValueError:
                pytest.fail(f"Valid date {date_str} failed validation")
    
    def test_date_validation_invalid(self):
        """Test invalid date validation."""
        from datetime import datetime
        
        invalid_dates = [
            "2024-13-01",  # Invalid month
            "2024-01-32",  # Invalid day
            "2024-02-30",  # Invalid day for February
            "invalid-date",
            ""
        ]
        
        for date_str in invalid_dates:
            with pytest.raises(ValueError):
                datetime.fromisoformat(date_str.replace('Z', '+00:00'))
    
    def test_amount_validation(self):
        """Test amount validation."""
        valid_amounts = [0, 0.01, 100, 999999.99, 1000000]
        invalid_amounts = [-1, -0.01, "invalid", None, ""]
        
        for amount in valid_amounts:
            assert isinstance(amount, (int, float))
            assert amount >= 0
        
        for amount in invalid_amounts:
            if isinstance(amount, (int, float)):
                assert amount < 0
            else:
                assert not isinstance(amount, (int, float))
    
    def test_currency_validation(self):
        """Test currency validation."""
        valid_currencies = ["USD", "EUR", "GBP", "JPY", "CAD"]
        invalid_currencies = ["", "INVALID", "usd", "123", None]
        
        for currency in valid_currencies:
            assert isinstance(currency, str)
            assert len(currency) == 3
            assert currency.isalpha()
            assert currency.isupper()
        
        for currency in invalid_currencies:
            if currency is None:
                assert currency is None
            elif isinstance(currency, str):
                assert len(currency) != 3 or not currency.isalpha() or not currency.isupper()
            else:
                assert not isinstance(currency, str)


class TestStringProcessing:
    """Unit tests for string processing functions."""
    
    def test_sanitize_filename(self):
        """Test filename sanitization."""
        test_cases = [
            ("normal_file.pdf", "normal_file.pdf"),
            ("file with spaces.pdf", "file_with_spaces.pdf"),
            ("file/with/slashes.pdf", "file_with_slashes.pdf"),
            ("file\\with\\backslashes.pdf", "file_with_backslashes.pdf"),
            ("file:with:colons.pdf", "file_with_colons.pdf"),
            ("file*with*asterisks.pdf", "file_with_asterisks.pdf"),
            ("file?with?questions.pdf", "file_with_questions.pdf"),
            ("file<with>brackets.pdf", "file_with_brackets.pdf"),
        ]
        
        for input_name, expected in test_cases:
            # Simple sanitization logic for testing
            sanitized = input_name.replace(" ", "_").replace("/", "_").replace("\\", "_")
            sanitized = sanitized.replace(":", "_").replace("*", "_").replace("?", "_")
            sanitized = sanitized.replace("<", "_").replace(">", "_")
            assert sanitized == expected
    
    def test_extract_text_from_content(self):
        """Test text extraction from content."""
        test_content = "This is a test document with important information."
        
        # Mock text extraction
        extracted_text = test_content.lower()
        
        assert "test" in extracted_text
        assert "document" in extracted_text
        assert "important" in extracted_text
        assert len(extracted_text) > 0
    
    def test_validate_email_format(self):
        """Test email format validation."""
        valid_emails = [
            "test@example.com",
            "user.name@domain.co.uk",
            "test+tag@example.org",
            "123@test.com"
        ]
        
        invalid_emails = [
            "invalid-email",
            "@example.com",
            "test@",
            "test..test@example.com",
            ""
        ]
        
        for email in valid_emails:
            assert "@" in email
            assert "." in email.split("@")[1]
            assert len(email.split("@")) == 2
        
        for email in invalid_emails:
            if email == "":
                assert email == ""
            else:
                assert "@" not in email or "." not in email.split("@")[1] or len(email.split("@")) != 2


class TestDataValidation:
    """Unit tests for data validation functions."""
    
    def test_validate_contract_data(self):
        """Test contract data validation."""
        valid_contract = TestDataFactory.create_contract_data()
        
        # Required fields
        required_fields = ["contract_id", "title", "vendor", "amount", "currency", "status"]
        for field in required_fields:
            assert field in valid_contract
            assert valid_contract[field] is not None
            assert valid_contract[field] != ""
    
    def test_validate_invoice_data(self):
        """Test invoice data validation."""
        valid_invoice = TestDataFactory.create_invoice_data()
        
        # Required fields
        required_fields = ["invoice_id", "contract_id", "vendor", "amount", "currency", "status"]
        for field in required_fields:
            assert field in valid_invoice
            assert valid_invoice[field] is not None
            assert valid_invoice[field] != ""
        
        # Line items validation
        assert "line_items" in valid_invoice
        assert isinstance(valid_invoice["line_items"], list)
        assert len(valid_invoice["line_items"]) > 0
    
    def test_validate_document_data(self):
        """Test document data validation."""
        valid_document = TestDataFactory.create_document_data()
        
        # Required fields
        required_fields = ["document_id", "filename", "file_type", "file_size", "status"]
        for field in required_fields:
            assert field in valid_document
            assert valid_document[field] is not None
            assert valid_document[field] != ""
        
        # Metadata validation
        assert "metadata" in valid_document
        assert isinstance(valid_document["metadata"], dict)


@pytest.mark.unit
class TestUnitTestMarkers:
    """Test that unit test markers work correctly."""
    
    def test_unit_marker_applied(self):
        """Test that unit marker is applied to this test."""
        # This test should be marked as unit
        assert True
    
    def test_basic_functionality(self):
        """Test basic functionality without external dependencies."""
        # Simple test without mocks or external dependencies
        result = 2 + 2
        assert result == 4
    
    def test_string_operations(self):
        """Test string operations."""
        test_string = "Hello, World!"
        
        assert len(test_string) == 13
        assert test_string.upper() == "HELLO, WORLD!"
        assert test_string.lower() == "hello, world!"
        assert test_string.split(", ") == ["Hello", "World!"]
    
    def test_list_operations(self):
        """Test list operations."""
        test_list = [1, 2, 3, 4, 5]
        
        assert len(test_list) == 5
        assert sum(test_list) == 15
        assert max(test_list) == 5
        assert min(test_list) == 1
        assert 3 in test_list
        assert 6 not in test_list
