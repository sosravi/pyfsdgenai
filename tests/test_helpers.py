"""
PyFSD GenAI - Test Utilities and Helpers

This module provides utility functions and helper classes for testing
across the PyFSD GenAI project.
"""

import json
import os
import tempfile
from typing import Any, Dict, List, Optional, Union
from unittest.mock import Mock, patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session


class TestDataFactory:
    """Factory class for creating test data."""
    
    @staticmethod
    def create_contract_data(**overrides) -> Dict[str, Any]:
        """Create contract test data with optional overrides."""
        default_data = {
            "contract_id": "TEST-CONTRACT-001",
            "title": "Software License Agreement",
            "vendor": "Test Vendor Inc.",
            "amount": 50000.00,
            "currency": "USD",
            "start_date": "2024-01-01",
            "end_date": "2024-12-31",
            "terms": "Standard software license terms",
            "status": "active",
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z"
        }
        default_data.update(overrides)
        return default_data
    
    @staticmethod
    def create_invoice_data(**overrides) -> Dict[str, Any]:
        """Create invoice test data with optional overrides."""
        default_data = {
            "invoice_id": "INV-001",
            "contract_id": "TEST-CONTRACT-001",
            "vendor": "Test Vendor Inc.",
            "amount": 5000.00,
            "currency": "USD",
            "due_date": "2024-02-15",
            "line_items": [
                {
                    "description": "Software License",
                    "quantity": 1,
                    "unit_price": 5000.00,
                    "total": 5000.00
                }
            ],
            "status": "pending",
            "created_at": "2024-01-15T10:30:00Z"
        }
        default_data.update(overrides)
        return default_data
    
    @staticmethod
    def create_document_data(**overrides) -> Dict[str, Any]:
        """Create document test data with optional overrides."""
        default_data = {
            "document_id": "DOC-001",
            "filename": "test_contract.pdf",
            "file_type": "application/pdf",
            "file_size": 1024000,
            "upload_date": "2024-01-15T10:30:00Z",
            "status": "processed",
            "metadata": {
                "pages": 10,
                "language": "en",
                "confidence": 0.95
            }
        }
        default_data.update(overrides)
        return default_data
    
    @staticmethod
    def create_user_data(**overrides) -> Dict[str, Any]:
        """Create user test data with optional overrides."""
        default_data = {
            "user_id": "USER-001",
            "username": "testuser",
            "email": "test@example.com",
            "full_name": "Test User",
            "role": "analyst",
            "is_active": True,
            "created_at": "2024-01-01T00:00:00Z"
        }
        default_data.update(overrides)
        return default_data


class APITestHelper:
    """Helper class for API testing."""
    
    def __init__(self, client: TestClient):
        self.client = client
    
    def assert_success_response(self, response, expected_status: int = 200) -> Dict[str, Any]:
        """Assert successful response and return JSON data."""
        assert response.status_code == expected_status
        data = response.json()
        assert data is not None
        return data
    
    def assert_error_response(self, response, expected_status: int = 400) -> Dict[str, Any]:
        """Assert error response and return JSON data."""
        assert response.status_code == expected_status
        data = response.json()
        assert "error" in data or "detail" in data
        return data
    
    def assert_validation_error(self, response, field_name: str) -> Dict[str, Any]:
        """Assert validation error for specific field."""
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data
        
        # Check if field error exists
        errors = data["detail"]
        field_errors = [error for error in errors if error.get("loc", [None])[-1] == field_name]
        assert len(field_errors) > 0, f"Expected validation error for field '{field_name}'"
        
        return data
    
    def get_auth_headers(self, token: str) -> Dict[str, str]:
        """Get authorization headers."""
        return {"Authorization": f"Bearer {token}"}
    
    def create_test_file(self, content: str = "Test file content", filename: str = "test.txt") -> bytes:
        """Create test file content."""
        return content.encode('utf-8')


class DatabaseTestHelper:
    """Helper class for database testing."""
    
    def __init__(self, session: Session):
        self.session = session
    
    def assert_record_exists(self, model_class, **filters) -> Any:
        """Assert that a record exists and return it."""
        record = self.session.query(model_class).filter_by(**filters).first()
        assert record is not None, f"Record not found with filters: {filters}"
        return record
    
    def assert_record_count(self, model_class, expected_count: int):
        """Assert the count of records."""
        actual_count = self.session.query(model_class).count()
        assert actual_count == expected_count, f"Expected {expected_count} records, got {actual_count}"
    
    def assert_record_attributes(self, record, **attributes):
        """Assert that a record has specific attributes."""
        for attr_name, expected_value in attributes.items():
            actual_value = getattr(record, attr_name)
            assert actual_value == expected_value, f"Attribute '{attr_name}' expected {expected_value}, got {actual_value}"
    
    def create_test_record(self, model_class, **data) -> Any:
        """Create a test record."""
        record = model_class(**data)
        self.session.add(record)
        self.session.commit()
        self.session.refresh(record)
        return record


class MockHelper:
    """Helper class for creating mocks."""
    
    @staticmethod
    def mock_openai_response(content: str = "Mocked AI response") -> Mock:
        """Create a mock OpenAI response."""
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message = Mock()
        mock_response.choices[0].message.content = content
        return mock_response
    
    @staticmethod
    def mock_anthropic_response(content: str = "Mocked Anthropic response") -> Mock:
        """Create a mock Anthropic response."""
        mock_response = Mock()
        mock_response.content = [Mock()]
        mock_response.content[0].text = content
        return mock_response
    
    @staticmethod
    def mock_file_upload(filename: str = "test.pdf", content: bytes = b"test content") -> Mock:
        """Create a mock file upload."""
        mock_file = Mock()
        mock_file.filename = filename
        mock_file.read.return_value = content
        mock_file.size = len(content)
        return mock_file


class PerformanceTestHelper:
    """Helper class for performance testing."""
    
    def __init__(self):
        import time
        self.start_time = None
        self.end_time = None
    
    def start_timer(self):
        """Start performance timer."""
        import time
        self.start_time = time.time()
    
    def stop_timer(self) -> float:
        """Stop performance timer and return elapsed time."""
        import time
        self.end_time = time.time()
        return self.elapsed_time
    
    @property
    def elapsed_time(self) -> float:
        """Get elapsed time."""
        if self.start_time and self.end_time:
            return self.end_time - self.start_time
        return 0.0
    
    def assert_performance(self, max_time: float):
        """Assert that operation completed within time limit."""
        elapsed = self.elapsed_time
        assert elapsed <= max_time, f"Operation took {elapsed:.3f}s, expected <= {max_time}s"


class EdgeCaseTestHelper:
    """Helper class for edge case testing."""
    
    @staticmethod
    def get_edge_case_strings() -> List[str]:
        """Get edge case strings for testing."""
        return [
            "",  # Empty string
            " ",  # Single space
            "  ",  # Multiple spaces
            "\n",  # Newline
            "\t",  # Tab
            "a" * 1000,  # Very long string
            "🚀🔥💯",  # Emojis
            "测试中文",  # Unicode characters
            "test@example.com",  # Email format
            "https://example.com",  # URL format
            "SELECT * FROM users;",  # SQL injection attempt
            "<script>alert('xss')</script>",  # XSS attempt
        ]
    
    @staticmethod
    def get_edge_case_numbers() -> List[Union[int, float]]:
        """Get edge case numbers for testing."""
        return [
            0,  # Zero
            -1,  # Negative
            1,  # One
            999999999,  # Large integer
            -999999999,  # Large negative integer
            0.0,  # Zero float
            -0.0,  # Negative zero
            0.1,  # Small decimal
            0.0000001,  # Very small decimal
            float('inf'),  # Infinity
            float('-inf'),  # Negative infinity
            float('nan'),  # Not a number
        ]
    
    @staticmethod
    def get_edge_case_dates() -> List[str]:
        """Get edge case dates for testing."""
        return [
            "2024-01-01",  # Valid date
            "2024-12-31",  # End of year
            "2024-02-29",  # Leap year
            "2023-02-29",  # Invalid leap year
            "2024-13-01",  # Invalid month
            "2024-01-32",  # Invalid day
            "2024/01/01",  # Different format
            "01-01-2024",  # Different format
            "2024-01-01T00:00:00Z",  # ISO format
            "2024-01-01T23:59:59.999Z",  # End of day
        ]


class TestFileManager:
    """Helper class for managing test files."""
    
    def __init__(self):
        self.temp_files = []
    
    def create_temp_file(self, content: str = "test content", suffix: str = ".txt") -> str:
        """Create a temporary file and return its path."""
        import tempfile
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix=suffix) as f:
            f.write(content)
            temp_path = f.name
        
        self.temp_files.append(temp_path)
        return temp_path
    
    def create_temp_pdf(self, content: str = "Sample PDF content") -> str:
        """Create a temporary PDF file."""
        import io
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import letter
        
        temp_path = self.create_temp_file(suffix=".pdf")
        
        # Create a simple PDF
        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=letter)
        c.drawString(100, 750, content)
        c.save()
        
        with open(temp_path, 'wb') as f:
            f.write(buffer.getvalue())
        
        return temp_path
    
    def cleanup(self):
        """Clean up all temporary files."""
        import os
        
        for temp_file in self.temp_files:
            try:
                if os.path.exists(temp_file):
                    os.unlink(temp_file)
            except Exception:
                pass  # Ignore cleanup errors
        
        self.temp_files.clear()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cleanup()


# Pytest fixtures for helpers
@pytest.fixture
def test_data_factory():
    """Provide test data factory."""
    return TestDataFactory


@pytest.fixture
def api_helper(test_client):
    """Provide API test helper."""
    return APITestHelper(test_client)


@pytest.fixture
def db_helper(test_db_session):
    """Provide database test helper."""
    return DatabaseTestHelper(test_db_session)


@pytest.fixture
def mock_helper():
    """Provide mock helper."""
    return MockHelper


@pytest.fixture
def performance_helper():
    """Provide performance test helper."""
    return PerformanceTestHelper()


@pytest.fixture
def edge_case_helper():
    """Provide edge case test helper."""
    return EdgeCaseTestHelper


@pytest.fixture
def test_file_manager():
    """Provide test file manager."""
    manager = TestFileManager()
    yield manager
    manager.cleanup()

