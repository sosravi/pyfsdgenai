"""
PyFSD GenAI - Test Configuration and Fixtures

This module provides shared test configuration, fixtures, and utilities
for all test modules in the PyFSD GenAI project.

Following TDD principles:
- Red: Write failing tests first
- Green: Make tests pass with minimal code
- Refactor: Improve code while keeping tests green
"""

import asyncio
import os
import pytest
import tempfile
from typing import AsyncGenerator, Generator
from unittest.mock import Mock, patch

import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

try:
    from src.main import app
    from src.core.config import get_settings
    from src.core.database import get_db, Base
except ImportError:
    # Create minimal app for testing
    from fastapi import FastAPI
    app = FastAPI()
    
    # Create minimal settings
    class Settings:
        DATABASE_URL = "sqlite:///./test.db"
        REDIS_URL = "redis://localhost:6379/1"
        MONGODB_URL = "mongodb://localhost:27017/test_pyfsdgenai"
        DEBUG = True
        TESTING = True
    
    def get_settings():
        return Settings()
    
    # Create minimal database components
    from sqlalchemy.ext.declarative import declarative_base
    Base = declarative_base()
    
    def get_db():
        """Minimal get_db for testing."""
        yield None


# Test Configuration
@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def test_settings():
    """Test settings with overrides for testing environment."""
    settings = get_settings()
    
    # Override settings for testing
    settings.database_url = "sqlite:///./test.db"
    settings.redis_url = "redis://localhost:6379/1"  # Use different Redis DB
    settings.mongodb_url = "mongodb://localhost:27017/test_pyfsdgenai"
    settings.debug = True
    
    return settings


# Database Fixtures
@pytest.fixture(scope="function")
def test_db_engine(test_settings):
    """Create a test database engine."""
    engine = create_engine(
        test_settings.database_url,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def test_db_session(test_db_engine):
    """Create a test database session."""
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_db_engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture(scope="function")
def test_client(test_db_session):
    """Create a test client with database session override."""
    def override_get_db():
        try:
            yield test_db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as client:
        yield client
    
    app.dependency_overrides.clear()


# Mock Fixtures
@pytest.fixture
def mock_openai():
    """Mock OpenAI API calls."""
    with patch('openai.OpenAI') as mock:
        mock_instance = Mock()
        mock.return_value = mock_instance
        
        # Mock chat completion response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message = Mock()
        mock_response.choices[0].message.content = "Mocked AI response"
        
        mock_instance.chat.completions.create.return_value = mock_response
        yield mock_instance


@pytest.fixture
def mock_anthropic():
    """Mock Anthropic API calls."""
    with patch('anthropic.Anthropic') as mock:
        mock_instance = Mock()
        mock.return_value = mock_instance
        
        # Mock message response
        mock_response = Mock()
        mock_response.content = [Mock()]
        mock_response.content[0].text = "Mocked Anthropic response"
        
        mock_instance.messages.create.return_value = mock_response
        yield mock_instance


@pytest.fixture
def mock_redis():
    """Mock Redis connection."""
    with patch('redis.Redis') as mock:
        mock_instance = Mock()
        mock.return_value = mock_instance
        yield mock_instance


@pytest.fixture
def mock_mongodb():
    """Mock MongoDB connection."""
    with patch('pymongo.MongoClient') as mock:
        mock_instance = Mock()
        mock.return_value = mock_instance
        
        # Mock database and collection
        mock_db = Mock()
        mock_collection = Mock()
        mock_instance.__getitem__.return_value = mock_db
        mock_db.__getitem__.return_value = mock_collection
        
        yield mock_instance


# Test Data Fixtures
@pytest.fixture
def sample_contract_data():
    """Sample contract data for testing."""
    return {
        "contract_id": "TEST-001",
        "title": "Software License Agreement",
        "vendor": "Test Vendor Inc.",
        "amount": 50000.00,
        "currency": "USD",
        "start_date": "2024-01-01",
        "end_date": "2024-12-31",
        "terms": "Standard software license terms",
        "status": "active"
    }


@pytest.fixture
def sample_invoice_data():
    """Sample invoice data for testing."""
    return {
        "invoice_id": "INV-001",
        "contract_id": "TEST-001",
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
        "status": "pending"
    }


@pytest.fixture
def sample_document_data():
    """Sample document data for testing."""
    return {
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


# Async Test Fixtures
@pytest_asyncio.fixture
async def async_test_client():
    """Create an async test client."""
    from httpx import AsyncClient
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


# File System Fixtures
@pytest.fixture
def temp_upload_dir():
    """Create a temporary directory for file uploads."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir


@pytest.fixture
def sample_pdf_file(temp_upload_dir):
    """Create a sample PDF file for testing."""
    import io
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter
    
    pdf_path = os.path.join(temp_upload_dir, "sample.pdf")
    
    # Create a simple PDF
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    c.drawString(100, 750, "Sample Contract Document")
    c.drawString(100, 700, "This is a test PDF for PyFSD GenAI")
    c.save()
    
    with open(pdf_path, 'wb') as f:
        f.write(buffer.getvalue())
    
    return pdf_path


# Performance Testing Fixtures
@pytest.fixture
def performance_timer():
    """Timer fixture for performance testing."""
    import time
    
    class Timer:
        def __init__(self):
            self.start_time = None
            self.end_time = None
        
        def start(self):
            self.start_time = time.time()
        
        def stop(self):
            self.end_time = time.time()
        
        @property
        def elapsed(self):
            if self.start_time and self.end_time:
                return self.end_time - self.start_time
            return None
    
    return Timer()


# Test Utilities
class TestUtils:
    """Utility class for common test operations."""
    
    @staticmethod
    def assert_response_success(response, expected_status=200):
        """Assert that a response is successful."""
        assert response.status_code == expected_status
        assert response.json() is not None
    
    @staticmethod
    def assert_response_error(response, expected_status=400):
        """Assert that a response is an error."""
        assert response.status_code == expected_status
        assert "error" in response.json() or "detail" in response.json()
    
    @staticmethod
    def assert_database_record(session, model_class, **filters):
        """Assert that a database record exists."""
        record = session.query(model_class).filter_by(**filters).first()
        assert record is not None
        return record
    
    @staticmethod
    def assert_database_count(session, model_class, expected_count):
        """Assert the count of records in database."""
        actual_count = session.query(model_class).count()
        assert actual_count == expected_count


@pytest.fixture
def test_utils():
    """Provide test utilities."""
    return TestUtils


# Test Markers
def pytest_configure(config):
    """Configure pytest markers."""
    config.addinivalue_line(
        "markers", "unit: mark test as a unit test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )
    config.addinivalue_line(
        "markers", "api: mark test as an API test"
    )
    config.addinivalue_line(
        "markers", "database: mark test as a database test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )
    config.addinivalue_line(
        "markers", "performance: mark test as a performance test"
    )
    config.addinivalue_line(
        "markers", "edge_case: mark test as testing edge cases"
    )
    config.addinivalue_line(
        "markers", "regression: mark test as a regression test"
    )


# Test Collection Configuration
def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers based on test names."""
    for item in items:
        # Add markers based on test file location
        if "unit" in item.nodeid:
            item.add_marker(pytest.mark.unit)
        elif "integration" in item.nodeid:
            item.add_marker(pytest.mark.integration)
        elif "api" in item.nodeid:
            item.add_marker(pytest.mark.api)
        elif "database" in item.nodeid:
            item.add_marker(pytest.mark.database)
        
        # Add markers based on test name
        if "slow" in item.name.lower():
            item.add_marker(pytest.mark.slow)
        if "performance" in item.name.lower():
            item.add_marker(pytest.mark.performance)
        if "edge" in item.name.lower():
            item.add_marker(pytest.mark.edge_case)
        if "regression" in item.name.lower():
            item.add_marker(pytest.mark.regression)
