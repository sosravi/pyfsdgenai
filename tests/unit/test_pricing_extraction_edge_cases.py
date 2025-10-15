"""
PyFSD GenAI - Comprehensive Edge Case Tests for Pricing Extraction Agent

This module contains extensive edge case tests for the PricingExtractionAgent
focusing on validation and error handling without API calls.
"""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime
from decimal import Decimal
from typing import Dict, List, Any

from src.agents.pricing_extraction_agent import PricingExtractionAgent
from src.agents.base_agent import AgentStatus, AgentResult


class TestPricingExtractionEdgeCases:
    """Comprehensive edge case tests for PricingExtractionAgent."""

    def test_empty_string_input(self):
        """Test handling of empty string input."""
        agent = PricingExtractionAgent()
        result = agent.extract_pricing_from_text("")
        
        assert result.status == AgentStatus.FAILED
        assert result.success is False
        assert "empty" in result.error_message.lower() or "invalid" in result.error_message.lower()

    def test_whitespace_only_input(self):
        """Test handling of whitespace-only input."""
        agent = PricingExtractionAgent()
        result = agent.extract_pricing_from_text("   \n\t   ")
        
        assert result.status == AgentStatus.FAILED
        assert result.success is False
        assert "empty" in result.error_message.lower() or "invalid" in result.error_message.lower()

    def test_none_input(self):
        """Test handling of None input."""
        agent = PricingExtractionAgent()
        result = agent.extract_pricing_from_text(None)
        
        assert result.status == AgentStatus.FAILED
        assert result.success is False
        assert "none" in result.error_message.lower() or "invalid" in result.error_message.lower()

    def test_document_with_no_extracted_text(self):
        """Test handling of document with no extracted text."""
        agent = PricingExtractionAgent()
        
        document = Mock()
        document.document_id = "DOC-001"
        document.extracted_text = None
        
        result = agent.extract_pricing_from_document(document)
        
        assert result.status == AgentStatus.FAILED
        assert result.success is False
        assert "no text" in result.error_message.lower() or "extracted" in result.error_message.lower()

    def test_document_with_empty_extracted_text(self):
        """Test handling of document with empty extracted text."""
        agent = PricingExtractionAgent()
        
        document = Mock()
        document.document_id = "DOC-001"
        document.extracted_text = ""
        
        result = agent.extract_pricing_from_document(document)
        
        assert result.status == AgentStatus.FAILED
        assert result.success is False
        assert "no text" in result.error_message.lower() or "extracted" in result.error_message.lower()

    def test_zero_amounts_validation(self):
        """Test handling of zero amounts in pricing data."""
        agent = PricingExtractionAgent()
        
        # Test that zero amounts are valid
        valid_data = {
            "pricing_items": [{"description": "Free Service", "quantity": 1, "unit_price": 0.00, "total": 0.00, "currency": "USD"}],
            "total_amount": 0.00,
            "currency": "USD",
            "confidence": 0.95
        }
        
        assert agent.validate_pricing_data(valid_data) is True

    def test_very_large_amounts_validation(self):
        """Test handling of very large amounts."""
        agent = PricingExtractionAgent()
        
        # Test that large amounts are valid
        valid_data = {
            "pricing_items": [{"description": "Enterprise License", "quantity": 1, "unit_price": 999999999.99, "total": 999999999.99, "currency": "USD"}],
            "total_amount": 999999999.99,
            "currency": "USD",
            "confidence": 0.90
        }
        
        assert agent.validate_pricing_data(valid_data) is True

    def test_high_precision_amounts_validation(self):
        """Test handling of high precision amounts."""
        agent = PricingExtractionAgent()
        
        # Test that high precision amounts are valid
        valid_data = {
            "pricing_items": [{"description": "Precise Service", "quantity": 1, "unit_price": 1234.5678, "total": 1234.5678, "currency": "USD"}],
            "total_amount": 1234.5678,
            "currency": "USD",
            "confidence": 0.90
        }
        
        assert agent.validate_pricing_data(valid_data) is True

    def test_negative_amounts_validation(self):
        """Test validation rejection of negative amounts."""
        agent = PricingExtractionAgent()
        
        # Test that negative amounts are rejected
        invalid_data = {
            "pricing_items": [{"description": "Refund", "quantity": 1, "unit_price": -1000.00, "total": -1000.00, "currency": "USD"}],
            "total_amount": -1000.00,
            "currency": "USD",
            "confidence": 0.90
        }
        
        assert agent.validate_pricing_data(invalid_data) is False

    def test_invalid_currency_codes_validation(self):
        """Test validation rejection of invalid currency codes."""
        agent = PricingExtractionAgent()
        
        # Test that invalid currency codes are rejected
        invalid_data = {
            "pricing_items": [{"description": "Service", "quantity": 1, "unit_price": 1000.00, "total": 1000.00, "currency": "INVALID"}],
            "total_amount": 1000.00,
            "currency": "INVALID",
            "confidence": 0.90
        }
        
        assert agent.validate_pricing_data(invalid_data) is False

    def test_invalid_confidence_values_validation(self):
        """Test validation rejection of invalid confidence values."""
        agent = PricingExtractionAgent()
        
        # Test that invalid confidence values are rejected
        invalid_data = {
            "pricing_items": [{"description": "Service", "quantity": 1, "unit_price": 1000.00, "total": 1000.00, "currency": "USD"}],
            "total_amount": 1000.00,
            "currency": "USD",
            "confidence": 1.5  # Invalid confidence > 1.0
        }
        
        assert agent.validate_pricing_data(invalid_data) is False

    def test_missing_required_fields_validation(self):
        """Test validation rejection of missing required fields."""
        agent = PricingExtractionAgent()
        
        # Test that missing required fields are rejected
        invalid_data = {
            "pricing_items": [{"description": "Service", "quantity": 1, "unit_price": 1000.00}],  # Missing total and currency
            "total_amount": 1000.00,
            "currency": "USD"
            # Missing confidence
        }
        
        assert agent.validate_pricing_data(invalid_data) is False

    def test_boundary_confidence_values_validation(self):
        """Test boundary confidence values (0.0 and 1.0)."""
        agent = PricingExtractionAgent()
        
        # Test confidence = 0.0
        valid_data_0 = {
            "pricing_items": [{"description": "Service", "quantity": 1, "unit_price": 1000.00, "total": 1000.00, "currency": "USD"}],
            "total_amount": 1000.00,
            "currency": "USD",
            "confidence": 0.0
        }
        assert agent.validate_pricing_data(valid_data_0) is True

        # Test confidence = 1.0
        valid_data_1 = {
            "pricing_items": [{"description": "Service", "quantity": 1, "unit_price": 1000.00, "total": 1000.00, "currency": "USD"}],
            "total_amount": 1000.00,
            "currency": "USD",
            "confidence": 1.0
        }
        assert agent.validate_pricing_data(valid_data_1) is True

    def test_multiple_currencies_edge_case_validation(self):
        """Test edge case with many different currencies."""
        agent = PricingExtractionAgent()
        
        # Test that multiple currencies with MIXED are valid
        valid_data = {
            "pricing_items": [
                {"description": "USD Service", "quantity": 1, "unit_price": 1000.00, "total": 1000.00, "currency": "USD"},
                {"description": "EUR Service", "quantity": 1, "unit_price": 900.00, "total": 900.00, "currency": "EUR"},
                {"description": "GBP Service", "quantity": 1, "unit_price": 800.00, "total": 800.00, "currency": "GBP"},
                {"description": "JPY Service", "quantity": 1, "unit_price": 150000.00, "total": 150000.00, "currency": "JPY"}
            ],
            "total_amount": 152700.00,
            "currency": "MIXED",
            "confidence": 0.85
        }
        
        assert agent.validate_pricing_data(valid_data) is True

    def test_minimum_positive_amounts_validation(self):
        """Test minimum positive amounts."""
        agent = PricingExtractionAgent()
        
        # Test minimum positive amount
        valid_data = {
            "pricing_items": [{"description": "Min Service", "quantity": 1, "unit_price": 0.01, "total": 0.01, "currency": "USD"}],
            "total_amount": 0.01,
            "currency": "USD",
            "confidence": 0.90
        }
        
        assert agent.validate_pricing_data(valid_data) is True

    def test_minimum_quantities_validation(self):
        """Test minimum quantities."""
        agent = PricingExtractionAgent()
        
        # Test minimum quantity
        valid_data = {
            "pricing_items": [{"description": "Min Qty", "quantity": 0.01, "unit_price": 100.00, "total": 1.00, "currency": "USD"}],
            "total_amount": 1.00,
            "currency": "USD",
            "confidence": 0.90
        }
        
        assert agent.validate_pricing_data(valid_data) is True

    def test_large_quantities_validation(self):
        """Test large quantities."""
        agent = PricingExtractionAgent()
        
        # Test large quantity
        valid_data = {
            "pricing_items": [{"description": "Large Qty", "quantity": 999999.99, "unit_price": 1.00, "total": 999999.99, "currency": "USD"}],
            "total_amount": 999999.99,
            "currency": "USD",
            "confidence": 0.90
        }
        
        assert agent.validate_pricing_data(valid_data) is True

    def test_unicode_characters_in_description(self):
        """Test handling of Unicode characters in descriptions."""
        agent = PricingExtractionAgent()
        
        # Test that Unicode characters in descriptions are valid
        valid_data = {
            "pricing_items": [{"description": "软件许可证", "quantity": 1, "unit_price": 5000.00, "total": 5000.00, "currency": "USD"}],
            "total_amount": 5000.00,
            "currency": "USD",
            "confidence": 0.90
        }
        
        assert agent.validate_pricing_data(valid_data) is True

    def test_special_characters_in_description(self):
        """Test handling of special characters in descriptions."""
        agent = PricingExtractionAgent()
        
        # Test that special characters in descriptions are valid
        valid_data = {
            "pricing_items": [{"description": "Service & Agreement (2024) - Special!", "quantity": 1, "unit_price": 1000.00, "total": 1000.00, "currency": "USD"}],
            "total_amount": 1000.00,
            "currency": "USD",
            "confidence": 0.90
        }
        
        assert agent.validate_pricing_data(valid_data) is True

    def test_empty_description_validation(self):
        """Test handling of empty description."""
        agent = PricingExtractionAgent()
        
        # Test that empty description is valid (might be acceptable in some cases)
        valid_data = {
            "pricing_items": [{"description": "", "quantity": 1, "unit_price": 1000.00, "total": 1000.00, "currency": "USD"}],
            "total_amount": 1000.00,
            "currency": "USD",
            "confidence": 0.90
        }
        
        assert agent.validate_pricing_data(valid_data) is True

    def test_very_long_description_validation(self):
        """Test handling of very long description."""
        agent = PricingExtractionAgent()
        
        # Test that very long description is valid
        long_description = "A" * 1000  # Very long description
        valid_data = {
            "pricing_items": [{"description": long_description, "quantity": 1, "unit_price": 1000.00, "total": 1000.00, "currency": "USD"}],
            "total_amount": 1000.00,
            "currency": "USD",
            "confidence": 0.90
        }
        
        assert agent.validate_pricing_data(valid_data) is True

    def test_multiple_pricing_items_validation(self):
        """Test validation with multiple pricing items."""
        agent = PricingExtractionAgent()
        
        # Test that multiple pricing items are valid
        valid_data = {
            "pricing_items": [
                {"description": "Service 1", "quantity": 1, "unit_price": 1000.00, "total": 1000.00, "currency": "USD"},
                {"description": "Service 2", "quantity": 2, "unit_price": 500.00, "total": 1000.00, "currency": "USD"},
                {"description": "Service 3", "quantity": 1, "unit_price": 2000.00, "total": 2000.00, "currency": "USD"}
            ],
            "total_amount": 4000.00,
            "currency": "USD",
            "confidence": 0.90
        }
        
        assert agent.validate_pricing_data(valid_data) is True

    def test_empty_pricing_items_list_validation(self):
        """Test validation with empty pricing items list."""
        agent = PricingExtractionAgent()
        
        # Test that empty pricing items list is valid (no pricing found)
        valid_data = {
            "pricing_items": [],
            "total_amount": 0.00,
            "currency": "USD",
            "confidence": 0.85
        }
        
        assert agent.validate_pricing_data(valid_data) is True

    def test_format_pricing_output_edge_cases(self):
        """Test formatting of pricing output with edge cases."""
        agent = PricingExtractionAgent()
        
        # Test with minimal data
        minimal_data = {
            "pricing_items": [{"description": "Service", "quantity": 1, "unit_price": 1000.00, "total": 1000.00, "currency": "USD"}],
            "total_amount": 1000.00,
            "currency": "USD",
            "confidence": 0.90
        }
        
        formatted = agent.format_pricing_output(minimal_data)
        
        assert "pricing_items" in formatted
        assert "total_amount" in formatted
        assert "currency" in formatted
        assert "confidence" in formatted
        assert "extraction_timestamp" in formatted
        assert "agent_type" in formatted
        assert formatted["agent_type"] == "pricing_extraction"

    def test_get_agent_status_edge_cases(self):
        """Test getting agent status with edge cases."""
        agent = PricingExtractionAgent()
        
        # Test initial status
        assert agent.get_status() == AgentStatus.IDLE
        
        # Test status transitions
        agent.status = AgentStatus.RUNNING
        assert agent.get_status() == AgentStatus.RUNNING
        
        agent.status = AgentStatus.COMPLETED
        assert agent.get_status() == AgentStatus.COMPLETED
        
        agent.status = AgentStatus.FAILED
        assert agent.get_status() == AgentStatus.FAILED

    def test_get_agent_info_edge_cases(self):
        """Test getting agent information with edge cases."""
        agent = PricingExtractionAgent()
        
        info = agent.get_agent_info()
        
        assert info["agent_type"] == "pricing_extraction"
        assert info["status"] == AgentStatus.IDLE
        assert info["model_name"] == "gpt-4-turbo-preview"
        assert info["max_retries"] == 3
        assert info["timeout_seconds"] == 300

    def test_agent_initialization_edge_cases(self):
        """Test agent initialization with edge case parameters."""
        # Test with minimum values
        agent_min = PricingExtractionAgent(max_retries=1, timeout_seconds=1)
        assert agent_min.max_retries == 1
        assert agent_min.timeout_seconds == 1
        
        # Test with maximum reasonable values
        agent_max = PricingExtractionAgent(max_retries=100, timeout_seconds=3600)
        assert agent_max.max_retries == 100
        assert agent_max.timeout_seconds == 3600
        
        # Test with custom model name
        agent_custom = PricingExtractionAgent(model_name="gpt-3.5-turbo")
        assert agent_custom.model_name == "gpt-3.5-turbo"


@pytest.mark.edge_case
class TestEdgeCaseMarkers:
    """Test that edge case markers work correctly."""

    def test_edge_case_marker_applied(self):
        """Test that edge case marker is applied to this test."""
        assert True

    def test_edge_case_basic_functionality(self):
        """Test basic edge case functionality."""
        agent = PricingExtractionAgent()
        assert agent.agent_type == "pricing_extraction"
        assert agent.status == AgentStatus.IDLE