"""
Document Processing Test Fixtures

This module provides fixtures and utilities for document processing tests.
"""

import pytest
import tempfile
import os
from unittest.mock import Mock, patch
from typing import Dict, Any, List
from decimal import Decimal
from datetime import datetime


@pytest.fixture
def sample_contract_text():
    """Provide sample contract text for testing."""
    return """
    SERVICE AGREEMENT
    
    Contract ID: CONTRACT-2025-001
    Effective Date: January 1, 2025
    Expiration Date: December 31, 2025
    
    PARTIES:
    Company A (Client)
    Company B (Service Provider)
    
    TERMS AND CONDITIONS:
    1. Service Description: Software development and maintenance
    2. Payment Terms: Net 30 days
    3. Base Price: $50,000.00 per year
    4. Volume Discount: 5% for orders over $100,000
    5. Late Payment Fee: 1.5% per month
    6. Termination: Either party may terminate with 30 days notice
    7. Liability Limit: $1,000,000
    8. Force Majeure: Acts of God, war, natural disasters
    9. Governing Law: State of California
    10. Dispute Resolution: Arbitration in San Francisco
    
    SIGNATURES:
    Company A: John Doe, CEO
    Company B: Jane Smith, CTO
    
    Date: January 1, 2025
    """


@pytest.fixture
def sample_invoice_text():
    """Provide sample invoice text for testing."""
    return """
    INVOICE
    
    Invoice Number: INV-2025-001
    Invoice Date: January 15, 2025
    Due Date: February 14, 2025
    
    BILL TO:
    Company A
    123 Business Street
    City, State 12345
    
    DESCRIPTION:
    Software Development Services - January 2025
    
    QUANTITY: 1
    UNIT PRICE: $4,166.67
    TOTAL: $4,166.67
    
    PAYMENT TERMS: Net 30 days
    """


@pytest.fixture
def sample_pdf_content():
    """Provide sample PDF content for testing."""
    return b"Mock PDF content with contract data"


@pytest.fixture
def sample_docx_content():
    """Provide sample DOCX content for testing."""
    return b"Mock DOCX content with contract data"


@pytest.fixture
def sample_txt_content():
    """Provide sample TXT content for testing."""
    return b"Mock TXT content with contract data"


@pytest.fixture
def temp_pdf_file(sample_pdf_content):
    """Provide temporary PDF file for testing."""
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as temp_file:
        temp_file.write(sample_pdf_content)
        temp_file_path = temp_file.name
    
    yield temp_file_path
    
    # Cleanup
    if os.path.exists(temp_file_path):
        os.unlink(temp_file_path)


@pytest.fixture
def temp_docx_file(sample_docx_content):
    """Provide temporary DOCX file for testing."""
    with tempfile.NamedTemporaryFile(suffix=".docx", delete=False) as temp_file:
        temp_file.write(sample_docx_content)
        temp_file_path = temp_file.name
    
    yield temp_file_path
    
    # Cleanup
    if os.path.exists(temp_file_path):
        os.unlink(temp_file_path)


@pytest.fixture
def temp_txt_file(sample_txt_content):
    """Provide temporary TXT file for testing."""
    with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as temp_file:
        temp_file.write(sample_txt_content)
        temp_file_path = temp_file.name
    
    yield temp_file_path
    
    # Cleanup
    if os.path.exists(temp_file_path):
        os.unlink(temp_file_path)


@pytest.fixture
def mock_document_metadata():
    """Provide mock document metadata for testing."""
    return {
        "title": "Test Contract",
        "parties": ["Company A", "Company B"],
        "effective_date": "2025-01-01",
        "expiration_date": "2025-12-31",
        "value": Decimal("50000.00"),
        "currency": "USD",
        "document_type": "contract"
    }


@pytest.fixture
def mock_pricing_metadata():
    """Provide mock pricing metadata for testing."""
    return {
        "base_price": Decimal("50000.00"),
        "volume_discount": Decimal("5.00"),
        "payment_terms": "Net 30 days",
        "late_payment_fee": Decimal("1.50"),
        "currency": "USD"
    }


@pytest.fixture
def mock_terms_metadata():
    """Provide mock terms metadata for testing."""
    return {
        "termination_clause": "30 days notice",
        "liability_limit": Decimal("1000000.00"),
        "force_majeure": "Acts of God, war, natural disasters",
        "governing_law": "State of California",
        "dispute_resolution": "Arbitration in San Francisco"
    }


@pytest.fixture
def mock_agent_result():
    """Provide mock agent result for testing."""
    from src.agents.base_agent import AgentResult, AgentStatus
    
    return AgentResult(
        status=AgentStatus.COMPLETED,
        success=True,
        data={
            "pricing_items": [
                {
                    "description": "Software Development",
                    "quantity": 1,
                    "unit_price": 50000.00,
                    "total": 50000.00,
                    "currency": "USD"
                }
            ],
            "total_amount": 50000.00,
            "currency": "USD",
            "confidence": 0.95
        },
        execution_time=1.5,
        error_message=None
    )


@pytest.fixture
def mock_pipeline_data():
    """Provide mock pipeline data for testing."""
    return {
        "document_id": "doc_123",
        "text_content": "Sample contract text with pricing and terms",
        "metadata": {
            "type": "contract",
            "title": "Test Contract",
            "parties": ["Company A", "Company B"]
        }
    }


@pytest.fixture
def mock_processing_results():
    """Provide mock processing results for testing."""
    return {
        "pricing_analysis": {
            "total_value": 50000.00,
            "currency": "USD",
            "pricing_items": [
                {
                    "description": "Software Development",
                    "amount": 50000.00
                }
            ],
            "confidence": 0.95
        },
        "terms_analysis": {
            "risk_score": 0.3,
            "risk_factors": ["High liability limit"],
            "compliance_score": 0.85,
            "key_terms": ["Net 30", "Force Majeure"]
        },
        "compliance_check": {
            "passed": True,
            "issues": [],
            "recommendations": ["Consider liability insurance"]
        }
    }


@pytest.fixture
def mock_document_processor():
    """Provide mock document processor for testing."""
    processor = Mock()
    processor.upload_document.return_value = {
        "success": True,
        "document_id": "doc_123",
        "status": "uploaded",
        "file_size": 1024
    }
    processor.get_document_status.return_value = {
        "success": True,
        "document_id": "doc_123",
        "status": "processed",
        "created_at": "2025-01-01T00:00:00Z"
    }
    processor.delete_document.return_value = {
        "success": True,
        "message": "Document deleted successfully"
    }
    processor.list_documents.return_value = {
        "success": True,
        "documents": [
            {
                "document_id": "doc_123",
                "title": "Test Contract",
                "status": "processed",
                "created_at": "2025-01-01T00:00:00Z"
            }
        ]
    }
    return processor


@pytest.fixture
def mock_document_parser():
    """Provide mock document parser for testing."""
    parser = Mock()
    parser.parse_document.return_value = {
        "success": True,
        "text_content": "Sample contract text with pricing and terms",
        "metadata": {
            "format": "pdf",
            "pages": 1,
            "word_count": 50
        }
    }
    parser.extract_text_sections.return_value = {
        "parties": "Company A and Company B",
        "terms": "Net 30 days",
        "pricing": "$50,000.00",
        "signatures": "John Doe, Jane Smith"
    }
    return parser


@pytest.fixture
def mock_metadata_extractor():
    """Provide mock metadata extractor for testing."""
    extractor = Mock()
    extractor.extract_metadata.return_value = {
        "success": True,
        "contract_id": "CONTRACT-2025-001",
        "effective_date": "2025-01-01",
        "expiration_date": "2025-12-31",
        "parties": ["Company A", "Company B"],
        "value": Decimal("50000.00"),
        "currency": "USD"
    }
    extractor.extract_pricing_metadata.return_value = {
        "success": True,
        "base_price": Decimal("50000.00"),
        "volume_discount": Decimal("5.00"),
        "payment_terms": "Net 30 days",
        "late_payment_fee": Decimal("1.50")
    }
    extractor.extract_terms_metadata.return_value = {
        "success": True,
        "termination_clause": "30 days notice",
        "liability_limit": Decimal("1000000.00"),
        "force_majeure": "Acts of God, war, natural disasters",
        "governing_law": "State of California",
        "dispute_resolution": "Arbitration in San Francisco"
    }
    return extractor


@pytest.fixture
def mock_pipeline_manager():
    """Provide mock pipeline manager for testing."""
    manager = Mock()
    manager.start_processing.return_value = {
        "success": True,
        "pipeline_id": "pipeline_123",
        "status": "processing"
    }
    manager.get_processing_status.return_value = {
        "success": True,
        "pipeline_id": "pipeline_123",
        "status": "processing",
        "progress": 50
    }
    manager.get_processing_results.return_value = {
        "success": True,
        "pricing_analysis": {"total_value": 50000},
        "terms_analysis": {"risk_score": 0.3},
        "compliance_check": {"passed": True}
    }
    manager.cancel_processing.return_value = {
        "success": True,
        "message": "Processing canceled successfully"
    }
    manager.list_pipelines.return_value = {
        "success": True,
        "pipelines": [
            {
                "pipeline_id": "pipeline_123",
                "status": "processing",
                "progress": 50
            }
        ]
    }
    return manager


@pytest.fixture
def mock_ai_agents():
    """Provide mock AI agents for testing."""
    agents = {}
    
    # Mock pricing extraction agent
    pricing_agent = Mock()
    pricing_agent.execute.return_value = Mock(
        status="completed",
        success=True,
        data={
            "pricing_items": [
                {
                    "description": "Software Development",
                    "amount": 50000.00,
                    "currency": "USD"
                }
            ],
            "total_amount": 50000.00,
            "currency": "USD",
            "confidence": 0.95
        },
        execution_time=1.5
    )
    agents["pricing"] = pricing_agent
    
    # Mock terms extraction agent
    terms_agent = Mock()
    terms_agent.execute.return_value = Mock(
        status="completed",
        success=True,
        data={
            "terms": ["Net 30", "Force Majeure"],
            "risk_score": 0.3,
            "compliance_score": 0.85
        },
        execution_time=1.0
    )
    agents["terms"] = terms_agent
    
    # Mock risk assessment agent
    risk_agent = Mock()
    risk_agent.execute.return_value = Mock(
        status="completed",
        success=True,
        data={
            "risk_score": 0.3,
            "risk_factors": ["High liability limit"],
            "recommendations": ["Consider liability insurance"]
        },
        execution_time=1.2
    )
    agents["risk"] = risk_agent
    
    return agents


@pytest.fixture
def document_processing_test_data():
    """Provide comprehensive test data for document processing."""
    return {
        "contracts": [
            {
                "title": "Software Development Contract",
                "parties": ["TechCorp", "DevSolutions"],
                "value": Decimal("100000.00"),
                "currency": "USD",
                "terms": "Net 30 days",
                "risk_score": 0.2
            },
            {
                "title": "Consulting Services Agreement",
                "parties": ["BusinessCorp", "ConsultingLtd"],
                "value": Decimal("75000.00"),
                "currency": "USD",
                "terms": "Net 45 days",
                "risk_score": 0.4
            }
        ],
        "invoices": [
            {
                "invoice_number": "INV-001",
                "vendor": "TechCorp",
                "amount": Decimal("10000.00"),
                "currency": "USD",
                "due_date": "2025-02-15"
            },
            {
                "invoice_number": "INV-002",
                "vendor": "ConsultingLtd",
                "amount": Decimal("7500.00"),
                "currency": "USD",
                "due_date": "2025-02-20"
            }
        ]
    }
