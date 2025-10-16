"""
PyFSD GenAI - Basic Test Suite

This module contains basic tests for the PyFSD GenAI application
to ensure core functionality works as expected.
"""

import pytest
from fastapi.testclient import TestClient
from src.main import app
from src.models.schemas import Contract, Invoice, DocumentType, ContractType


class TestMainApplication:
    """Test cases for the main application."""
    
    def setup_method(self):
        """Set up test client."""
        self.client = TestClient(app)
    
    def test_root_endpoint(self):
        """Test the root endpoint."""
        response = self.client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "PyFSD GenAI - AI-Powered Procurement Intelligence Platform"
        assert data["version"] == "1.0.0"
        assert data["status"] == "running"
    
    def test_health_check(self):
        """Test the health check endpoint."""
        response = self.client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "PyFSD GenAI"
        assert data["version"] == "1.0.0"


class TestDataModels:
    """Test cases for data models."""
    
    def test_contract_creation(self):
        """Test contract model creation."""
        contract = Contract(
            title="Test Contract",
            contract_type=ContractType.SERVICE,
            parties=["Company A", "Company B"]
        )
        
        assert contract.title == "Test Contract"
        assert contract.contract_type == ContractType.SERVICE
        assert contract.parties == ["Company A", "Company B"]
        assert contract.currency == "USD"  # Default value
    
    def test_invoice_creation(self):
        """Test invoice model creation."""
        invoice = Invoice(
            invoice_number="INV-001",
            vendor="Test Vendor",
            amount=1000.00,
            invoice_date="2025-01-01T00:00:00"
        )
        
        assert invoice.invoice_number == "INV-001"
        assert invoice.vendor == "Test Vendor"
        assert invoice.amount == 1000.00
        assert invoice.currency == "USD"  # Default value
        assert invoice.reconciled is False  # Default value
    
    def test_document_type_enum(self):
        """Test document type enum values."""
        assert DocumentType.PDF == "pdf"
        assert DocumentType.DOCX == "docx"
        assert DocumentType.TXT == "txt"
        assert DocumentType.HTML == "html"
        assert DocumentType.XML == "xml"


class TestAgentBase:
    """Test cases for base agent functionality."""
    
    def test_agent_status_enum(self):
        """Test agent status enum values."""
        from src.agents.base_agent import AgentStatus
        
        assert AgentStatus.IDLE == "idle"
        assert AgentStatus.PROCESSING == "processing"
        assert AgentStatus.COMPLETED == "completed"
        assert AgentStatus.FAILED == "failed"
        assert AgentStatus.TIMEOUT == "timeout"


if __name__ == "__main__":
    pytest.main([__file__])



