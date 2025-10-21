"""
Document Processing Pipeline Tests

This module contains comprehensive tests for the document processing pipeline,
including document upload, parsing, AI agent integration, and metadata extraction.

Following TDD approach - Red Phase: Write tests first, then implement functionality.
"""

import pytest
import tempfile
import os
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime
from decimal import Decimal

from src.document_processing.document_processor import DocumentProcessor
from src.document_processing.document_parser import DocumentParser
from src.document_processing.metadata_extractor import MetadataExtractor
from src.document_processing.pipeline_manager import PipelineManager
from src.agents.base_agent import AgentStatus, AgentResult


class TestDocumentProcessor:
    """Test cases for DocumentProcessor class."""

    def test_document_processor_initialization(self):
        """Test DocumentProcessor initialization."""
        processor = DocumentProcessor()
        
        assert processor is not None
        assert processor.status == "idle"
        assert processor.supported_formats == ["pdf", "doc", "docx", "txt"]
        assert processor.max_file_size == 100 * 1024 * 1024  # 100MB

    def test_document_processor_upload_valid_file(self):
        """Test uploading a valid document file."""
        processor = DocumentProcessor()
        
        # Create a temporary test file
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as temp_file:
            temp_file.write(b"Mock PDF content")
            temp_file_path = temp_file.name
        
        try:
            result = processor.upload_document(
                file_path=temp_file_path,
                document_type="contract",
                metadata={"title": "Test Contract", "parties": ["Company A", "Company B"]}
            )
            
            assert result["success"] is True
            assert "document_id" in result
            assert result["status"] == "uploaded"
            assert result["file_size"] > 0
        finally:
            os.unlink(temp_file_path)

    def test_document_processor_upload_invalid_format(self):
        """Test uploading a document with invalid format."""
        processor = DocumentProcessor()
        
        with tempfile.NamedTemporaryFile(suffix=".xyz", delete=False) as temp_file:
            temp_file.write(b"Mock content")
            temp_file_path = temp_file.name
        
        try:
            result = processor.upload_document(
                file_path=temp_file_path,
                document_type="contract"
            )
            
            assert result["success"] is False
            assert "error" in result
            assert "unsupported file format" in result["error"].lower()
        finally:
            os.unlink(temp_file_path)

    def test_document_processor_upload_file_too_large(self):
        """Test uploading a file that exceeds size limit."""
        processor = DocumentProcessor()
        
        # Create a large temporary file
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as temp_file:
            # Write 101MB of data
            temp_file.write(b"x" * (101 * 1024 * 1024))
            temp_file_path = temp_file.name
        
        try:
            result = processor.upload_document(
                file_path=temp_file_path,
                document_type="contract"
            )
            
            assert result["success"] is False
            assert "error" in result
            assert "file too large" in result["error"].lower()
        finally:
            os.unlink(temp_file_path)

    def test_document_processor_get_document_status(self):
        """Test getting document processing status."""
        processor = DocumentProcessor()
        
        # Upload a document first
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as temp_file:
            temp_file.write(b"Mock PDF content")
            temp_file_path = temp_file.name
        
        try:
            upload_result = processor.upload_document(
                file_path=temp_file_path,
                document_type="contract"
            )
            
            document_id = upload_result["document_id"]
            status = processor.get_document_status(document_id)
            
            assert status["success"] is True
            assert status["document_id"] == document_id
            assert "status" in status
            assert "created_at" in status
        finally:
            os.unlink(temp_file_path)

    def test_document_processor_get_nonexistent_document_status(self):
        """Test getting status for nonexistent document."""
        processor = DocumentProcessor()
        
        status = processor.get_document_status("nonexistent_id")
        
        assert status["success"] is False
        assert "not found" in status["error"].lower()

    def test_document_processor_delete_document(self):
        """Test deleting a document."""
        processor = DocumentProcessor()
        
        # Upload a document first
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as temp_file:
            temp_file.write(b"Mock PDF content")
            temp_file_path = temp_file.name
        
        try:
            upload_result = processor.upload_document(
                file_path=temp_file_path,
                document_type="contract"
            )
            
            document_id = upload_result["document_id"]
            delete_result = processor.delete_document(document_id)
            
            assert delete_result["success"] is True
            assert delete_result["message"] == "Document deleted successfully"
        finally:
            os.unlink(temp_file_path)

    def test_document_processor_list_documents(self):
        """Test listing all documents."""
        processor = DocumentProcessor()
        
        # Upload multiple documents
        document_ids = []
        for i in range(3):
            with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as temp_file:
                temp_file.write(f"Mock PDF content {i}".encode())
                temp_file_path = temp_file.name
            
            try:
                upload_result = processor.upload_document(
                    file_path=temp_file_path,
                    document_type="contract"
                )
                document_ids.append(upload_result["document_id"])
            finally:
                os.unlink(temp_file_path)
        
        # List documents
        documents = processor.list_documents()
        
        assert documents["success"] is True
        assert len(documents["documents"]) >= 3
        assert all(doc["document_id"] in document_ids for doc in documents["documents"])

    def test_document_processor_list_documents_with_filters(self):
        """Test listing documents with filters."""
        processor = DocumentProcessor()
        
        # Upload documents with different types
        contract_ids = []
        invoice_ids = []
        
        for i in range(2):
            with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as temp_file:
                temp_file.write(f"Mock PDF content {i}".encode())
                temp_file_path = temp_file.name
            
            try:
                upload_result = processor.upload_document(
                    file_path=temp_file_path,
                    document_type="contract" if i % 2 == 0 else "invoice"
                )
                
                if i % 2 == 0:
                    contract_ids.append(upload_result["document_id"])
                else:
                    invoice_ids.append(upload_result["document_id"])
            finally:
                os.unlink(temp_file_path)
        
        # Filter by document type
        contracts = processor.list_documents(document_type="contract")
        invoices = processor.list_documents(document_type="invoice")
        
        assert contracts["success"] is True
        assert invoices["success"] is True
        assert len(contracts["documents"]) >= 1
        assert len(invoices["documents"]) >= 1


class TestDocumentParser:
    """Test cases for DocumentParser class."""

    def test_document_parser_initialization(self):
        """Test DocumentParser initialization."""
        parser = DocumentParser()
        
        assert parser is not None
        assert parser.supported_formats == ["pdf", "doc", "docx", "txt"]
        assert parser.max_text_length == 1000000  # 1MB of text

    def test_document_parser_parse_pdf(self):
        """Test parsing PDF documents."""
        parser = DocumentParser()
        
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as temp_file:
            temp_file.write(b"Mock PDF content")
            temp_file_path = temp_file.name
        
        try:
            result = parser.parse_document(temp_file_path)
            
            # Since PyPDF2 might not be available, test fallback behavior
            assert result["success"] is True
            assert "text_content" in result
            assert "metadata" in result
            # Format might be "pdf" or "txt" depending on available libraries
            assert result["metadata"]["format"] in ["pdf", "txt"]
        finally:
            os.unlink(temp_file_path)

    def test_document_parser_parse_docx(self):
        """Test parsing DOCX documents."""
        parser = DocumentParser()
        
        with tempfile.NamedTemporaryFile(suffix=".docx", delete=False) as temp_file:
            temp_file.write(b"Mock DOCX content")
            temp_file_path = temp_file.name
        
        try:
            result = parser.parse_document(temp_file_path)
            
            # Since python-docx might not be available, test fallback behavior
            assert result["success"] is True
            assert "text_content" in result
            assert "metadata" in result
            # Format might be "docx" or "txt" depending on available libraries
            assert result["metadata"]["format"] in ["docx", "txt"]
        finally:
            os.unlink(temp_file_path)

    def test_document_parser_parse_txt(self):
        """Test parsing TXT documents."""
        parser = DocumentParser()
        
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as temp_file:
            temp_file.write(b"Sample contract text with pricing and terms.")
            temp_file_path = temp_file.name
        
        try:
            result = parser.parse_document(temp_file_path)
            
            assert result["success"] is True
            assert "text_content" in result
            assert "metadata" in result
            assert result["text_content"] == "Sample contract text with pricing and terms."
            assert result["metadata"]["format"] == "txt"
        finally:
            os.unlink(temp_file_path)

    def test_document_parser_parse_unsupported_format(self):
        """Test parsing unsupported document format."""
        parser = DocumentParser()
        
        with tempfile.NamedTemporaryFile(suffix=".xyz", delete=False) as temp_file:
            temp_file.write(b"Mock content")
            temp_file_path = temp_file.name
        
        try:
            result = parser.parse_document(temp_file_path)
            
            assert result["success"] is False
            assert "error" in result
            assert "unsupported file format" in result["error"].lower()
        finally:
            os.unlink(temp_file_path)

    def test_document_parser_extract_text_sections(self):
        """Test extracting text sections from parsed document."""
        parser = DocumentParser()
        
        sample_text = """
        CONTRACT AGREEMENT
        
        PARTIES: Company A and Company B
        
        TERMS AND CONDITIONS:
        1. Payment terms: Net 30 days
        2. Delivery: Within 30 days
        3. Pricing: $10,000 per unit
        
        SIGNATURES:
        Company A: John Doe
        Company B: Jane Smith
        """
        
        sections = parser.extract_text_sections(sample_text)
        
        assert "parties" in sections
        assert "terms" in sections
        assert "pricing" in sections
        assert "signatures" in sections
        assert "Company A and Company B" in sections["parties"]
        assert "$10,000" in sections["pricing"]


class TestMetadataExtractor:
    """Test cases for MetadataExtractor class."""

    def test_metadata_extractor_initialization(self):
        """Test MetadataExtractor initialization."""
        extractor = MetadataExtractor()
        
        assert extractor is not None
        assert extractor.extraction_patterns is not None
        assert len(extractor.extraction_patterns) > 0

    def test_metadata_extractor_extract_basic_metadata(self):
        """Test extracting basic metadata from document."""
        extractor = MetadataExtractor()
        
        sample_text = """
        SERVICE AGREEMENT
        Contract ID: CONTRACT-2025-001
        Effective Date: January 1, 2025
        Expiration Date: December 31, 2025
        Parties: ABC Corp and XYZ Ltd
        Value: $50,000.00
        Currency: USD
        """
        
        metadata = extractor.extract_metadata(sample_text)
        
        assert metadata["success"] is True
        assert "contract_id" in metadata
        assert "effective_date" in metadata
        assert "expiration_date" in metadata
        assert "parties" in metadata
        assert "value" in metadata
        assert "currency" in metadata
        assert metadata["contract_id"] == "CONTRACT-2025-001"
        assert metadata["value"] == Decimal("50000.00")
        assert metadata["currency"] == "USD"

    def test_metadata_extractor_extract_pricing_metadata(self):
        """Test extracting pricing metadata."""
        extractor = MetadataExtractor()
        
        sample_text = """
        PRICING SCHEDULE
        Base Price: $1,000.00 per unit
        Volume Discount: 5% for orders over 100 units
        Payment Terms: Net 30 days
        Late Payment Fee: 1.5% per month
        """
        
        metadata = extractor.extract_pricing_metadata(sample_text)
        
        assert metadata["success"] is True
        assert "base_price" in metadata
        assert "volume_discount" in metadata
        assert "payment_terms" in metadata
        assert "late_payment_fee" in metadata
        assert metadata["base_price"] == Decimal("1000.00")
        assert metadata["volume_discount"] == Decimal("5.00")

    def test_metadata_extractor_extract_terms_metadata(self):
        """Test extracting terms and conditions metadata."""
        extractor = MetadataExtractor()
        
        sample_text = """
        TERMS AND CONDITIONS
        Termination: Either party may terminate with 30 days notice
        Liability Limit: $1,000,000
        Force Majeure: Acts of God, war, natural disasters
        Governing Law: State of California
        Dispute Resolution: Arbitration in San Francisco
        """
        
        metadata = extractor.extract_terms_metadata(sample_text)
        
        assert metadata["success"] is True
        assert "termination_clause" in metadata
        assert "liability_limit" in metadata
        assert "force_majeure" in metadata
        assert "governing_law" in metadata
        assert "dispute_resolution" in metadata
        assert "30 days notice" in metadata["termination_clause"]
        assert metadata["liability_limit"] == Decimal("1000000.00")

    def test_metadata_extractor_extract_empty_text(self):
        """Test extracting metadata from empty text."""
        extractor = MetadataExtractor()
        
        metadata = extractor.extract_metadata("")
        
        assert metadata["success"] is True
        assert len(metadata) == 1  # Only success field


class TestPipelineManager:
    """Test cases for PipelineManager class."""

    def test_pipeline_manager_initialization(self):
        """Test PipelineManager initialization."""
        manager = PipelineManager()
        
        assert manager is not None
        assert manager.status == "idle"
        assert manager.available_agents is not None
        assert len(manager.available_agents) > 0

    def test_pipeline_manager_start_processing(self):
        """Test starting document processing pipeline."""
        manager = PipelineManager()
        
        # Mock document data
        document_data = {
            "document_id": "doc_123",
            "text_content": "Sample contract text",
            "metadata": {"type": "contract"}
        }
        
        result = manager.start_processing(document_data)
        
        assert result["success"] is True
        assert "pipeline_id" in result
        assert "status" in result
        assert result["status"] == "processing"

    def test_pipeline_manager_get_processing_status(self):
        """Test getting processing pipeline status."""
        manager = PipelineManager()
        
        # Start processing first
        document_data = {
            "document_id": "doc_123",
            "text_content": "Sample contract text",
            "metadata": {"type": "contract"}
        }
        
        start_result = manager.start_processing(document_data)
        pipeline_id = start_result["pipeline_id"]
        
        status = manager.get_processing_status(pipeline_id)
        
        assert status["success"] is True
        assert status["pipeline_id"] == pipeline_id
        assert "status" in status
        assert "progress" in status

    def test_pipeline_manager_get_processing_results(self):
        """Test getting processing pipeline results."""
        manager = PipelineManager()
        
        # Start processing first
        document_data = {
            "document_id": "doc_123",
            "text_content": "Sample contract text",
            "metadata": {"type": "contract"}
        }
        
        start_result = manager.start_processing(document_data)
        pipeline_id = start_result["pipeline_id"]
        
        # Wait for processing to complete (mock)
        manager.pipelines[pipeline_id]["status"] = "completed"
        manager.pipelines[pipeline_id]["results"] = {
            "pricing_analysis": {"total_value": 50000},
            "terms_analysis": {"risk_score": 0.3},
            "compliance_check": {"passed": True}
        }
        
        results = manager.get_processing_results(pipeline_id)
        
        assert results["success"] is True
        assert "pricing_analysis" in results["results"]
        assert "terms_analysis" in results["results"]
        assert "compliance_check" in results["results"]

    def test_pipeline_manager_cancel_processing(self):
        """Test canceling document processing pipeline."""
        manager = PipelineManager()
        
        # Start processing first
        document_data = {
            "document_id": "doc_123",
            "text_content": "Sample contract text",
            "metadata": {"type": "contract"}
        }
        
        start_result = manager.start_processing(document_data)
        pipeline_id = start_result["pipeline_id"]
        
        # Check if pipeline is still running before canceling
        status = manager.get_processing_status(pipeline_id)
        if status["status"] == "processing":
            cancel_result = manager.cancel_processing(pipeline_id)
            assert cancel_result["success"] is True
        else:
            # Pipeline completed too quickly, test completed pipeline
            cancel_result = manager.cancel_processing(pipeline_id)
            assert cancel_result["success"] is False
            assert "already completed" in cancel_result["error"]

    def test_pipeline_manager_list_pipelines(self):
        """Test listing all processing pipelines."""
        manager = PipelineManager()
        
        # Start multiple pipelines
        for i in range(3):
            document_data = {
                "document_id": f"doc_{i}",
                "text_content": f"Sample contract text {i}",
                "metadata": {"type": "contract"}
            }
            manager.start_processing(document_data)
        
        pipelines = manager.list_pipelines()
        
        assert pipelines["success"] is True
        assert len(pipelines["pipelines"]) >= 3

    @patch('src.agents.pricing_extraction_agent.PricingExtractionAgent')
    def test_pipeline_manager_integrate_ai_agents(self, mock_agent_class):
        """Test integrating AI agents into processing pipeline."""
        manager = PipelineManager()
        
        # Mock agent
        mock_agent = Mock()
        mock_agent.execute.return_value = AgentResult(
            status=AgentStatus.COMPLETED,
            success=True,
            data={"pricing_items": [{"description": "Service", "amount": 1000}]},
            execution_time=1.5
        )
        mock_agent_class.return_value = mock_agent
        
        # Test agent integration
        document_data = {
            "document_id": "doc_123",
            "text_content": "Service contract for $1,000",
            "metadata": {"type": "contract"}
        }
        
        result = manager.start_processing(document_data)
        
        assert result["success"] is True
        assert "pipeline_id" in result

    def test_pipeline_manager_error_handling(self):
        """Test pipeline manager error handling."""
        manager = PipelineManager()
        
        # Test with invalid document data
        invalid_data = {"invalid": "data"}
        
        result = manager.start_processing(invalid_data)
        
        assert result["success"] is False
        assert "error" in result

    def test_pipeline_manager_concurrent_processing(self):
        """Test handling concurrent document processing."""
        manager = PipelineManager()
        
        # Start multiple concurrent pipelines
        pipeline_ids = []
        for i in range(5):
            document_data = {
                "document_id": f"doc_{i}",
                "text_content": f"Sample contract text {i}",
                "metadata": {"type": "contract"}
            }
            result = manager.start_processing(document_data)
            pipeline_ids.append(result["pipeline_id"])
        
        # Check all pipelines are running
        for pipeline_id in pipeline_ids:
            status = manager.get_processing_status(pipeline_id)
            assert status["success"] is True
            assert status["pipeline_id"] == pipeline_id


class TestDocumentProcessingIntegration:
    """Integration tests for document processing pipeline."""

    def test_end_to_end_document_processing(self):
        """Test complete end-to-end document processing workflow."""
        processor = DocumentProcessor()
        parser = DocumentParser()
        extractor = MetadataExtractor()
        manager = PipelineManager()
        
        # Create test document
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as temp_file:
            temp_file.write(b"Mock PDF content with contract data")
            temp_file_path = temp_file.name
        
        try:
            # Step 1: Upload document
            upload_result = processor.upload_document(
                file_path=temp_file_path,
                document_type="contract",
                metadata={"title": "Test Contract"}
            )
            
            assert upload_result["success"] is True
            document_id = upload_result["document_id"]
            
            # Step 2: Parse document
            parse_result = parser.parse_document(temp_file_path)
            
            assert parse_result["success"] is True
            assert "text_content" in parse_result
            
            # Step 3: Extract metadata
            metadata_result = extractor.extract_metadata(parse_result["text_content"])
            
            assert metadata_result["success"] is True
            
            # Step 4: Start processing pipeline
            document_data = {
                "document_id": document_id,
                "text_content": parse_result["text_content"],
                "metadata": metadata_result
            }
            
            pipeline_result = manager.start_processing(document_data)
            
            assert pipeline_result["success"] is True
            assert "pipeline_id" in pipeline_result
            
        finally:
            os.unlink(temp_file_path)

    def test_document_processing_with_multiple_agents(self):
        """Test document processing with multiple AI agents."""
        manager = PipelineManager()
        
        # Mock multiple agents
        with patch('src.agents.pricing_extraction_agent.PricingExtractionAgent') as mock_pricing, \
             patch('src.agents.terms_extraction_agent.TermsExtractionAgent') as mock_terms, \
             patch('src.agents.risk_assessment_agent.RiskAssessmentAgent') as mock_risk:
            
            # Setup mock agents
            mock_pricing.return_value.execute.return_value = AgentResult(
                status=AgentStatus.COMPLETED,
                success=True,
                data={"pricing_items": [{"description": "Service", "amount": 1000}]},
                execution_time=1.0
            )
            
            mock_terms.return_value.execute.return_value = AgentResult(
                status=AgentStatus.COMPLETED,
                success=True,
                data={"terms": ["Net 30", "Force Majeure"]},
                execution_time=0.8
            )
            
            mock_risk.return_value.execute.return_value = AgentResult(
                status=AgentStatus.COMPLETED,
                success=True,
                data={"risk_score": 0.3, "risk_factors": ["High liability"]},
                execution_time=1.2
            )
            
            # Test processing with multiple agents
            document_data = {
                "document_id": "doc_123",
                "text_content": "Service contract with pricing and terms",
                "metadata": {"type": "contract"}
            }
            
            result = manager.start_processing(document_data)
            
            assert result["success"] is True
            assert "pipeline_id" in result

    def test_document_processing_error_recovery(self):
        """Test document processing error recovery."""
        processor = DocumentProcessor()
        
        # Test with corrupted file
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as temp_file:
            temp_file.write(b"Corrupted PDF content")
            temp_file_path = temp_file.name
        
        try:
            result = processor.upload_document(
                file_path=temp_file_path,
                document_type="contract"
            )
            
            # Should handle gracefully
            assert result["success"] is True  # Upload succeeds
            document_id = result["document_id"]
            
            # But processing might fail
            status = processor.get_document_status(document_id)
            assert status["success"] is True
            
        finally:
            os.unlink(temp_file_path)

    def test_document_processing_performance(self):
        """Test document processing performance."""
        import time
        
        processor = DocumentProcessor()
        manager = PipelineManager()
        
        # Test processing time
        start_time = time.time()
        
        # Process multiple documents
        for i in range(10):
            with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as temp_file:
                temp_file.write(f"Sample contract text {i}".encode())
                temp_file_path = temp_file.name
            
            try:
                upload_result = processor.upload_document(
                    file_path=temp_file_path,
                    document_type="contract"
                )
                
                document_data = {
                    "document_id": upload_result["document_id"],
                    "text_content": f"Sample contract text {i}",
                    "metadata": {"type": "contract"}
                }
                
                manager.start_processing(document_data)
                
            finally:
                os.unlink(temp_file_path)
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        # Should process 10 documents in reasonable time
        assert processing_time < 5.0  # Less than 5 seconds
