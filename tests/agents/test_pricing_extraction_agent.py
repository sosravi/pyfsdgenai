"""
PyFSD GenAI - AI Agent Tests

This module contains tests for AI agents following TDD principles.
We write tests first (Red phase), then implement agents to make tests pass (Green phase).
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from decimal import Decimal
from typing import Dict, List, Any

from src.agents.pricing_extraction_agent import PricingExtractionAgent
from src.agents.base_agent import AgentStatus, AgentResult
from src.models.database_models import Document, AgentExecution


class TestPricingExtractionAgent:
    """Tests for PricingExtractionAgent."""
    
    def test_agent_initialization(self):
        """Test agent initialization."""
        agent = PricingExtractionAgent()
        
        assert agent.agent_type == "pricing_extraction"
        assert agent.status == AgentStatus.IDLE
        assert agent.model_name == "gpt-4-turbo-preview"
        assert agent.max_retries == 3
        assert agent.timeout_seconds == 300
    
    def test_agent_initialization_with_custom_params(self):
        """Test agent initialization with custom parameters."""
        agent = PricingExtractionAgent(
            model_name="gpt-3.5-turbo",
            max_retries=5,
            timeout_seconds=600
        )
        
        assert agent.model_name == "gpt-3.5-turbo"
        assert agent.max_retries == 5
        assert agent.timeout_seconds == 600
    
    @patch('src.agents.pricing_extraction_agent.OpenAI')
    def test_extract_pricing_from_text_success(self, mock_openai):
        """Test successful pricing extraction from text."""
        # Mock OpenAI response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = '''
        {
            "pricing_items": [
                {
                    "description": "Software License",
                    "quantity": 1,
                    "unit_price": 5000.00,
                    "total": 5000.00,
                    "currency": "USD"
                },
                {
                    "description": "Support Services",
                    "quantity": 12,
                    "unit_price": 500.00,
                    "total": 6000.00,
                    "currency": "USD"
                }
            ],
            "total_amount": 11000.00,
            "currency": "USD",
            "confidence": 0.95
        }
        '''
        
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        agent = PricingExtractionAgent()
        text = "Software License: $5,000. Support Services: $500/month for 12 months."
        
        result = agent.extract_pricing_from_text(text)
        
        assert result.status == AgentStatus.COMPLETED
        assert result.success is True
        assert result.confidence == 0.95
        assert len(result.data["pricing_items"]) == 2
        assert result.data["total_amount"] == 11000.00
        assert result.data["currency"] == "USD"
    
    @patch('src.agents.pricing_extraction_agent.OpenAI')
    def test_extract_pricing_from_text_no_pricing_found(self, mock_openai):
        """Test pricing extraction when no pricing is found."""
        # Mock OpenAI response for no pricing found
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = '''
        {
            "pricing_items": [],
            "total_amount": 0.00,
            "currency": "USD",
            "confidence": 0.85,
            "message": "No pricing information found in the text"
        }
        '''
        
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        agent = PricingExtractionAgent()
        text = "This is a general description without any pricing information."
        
        result = agent.extract_pricing_from_text(text)
        
        assert result.status == AgentStatus.COMPLETED
        assert result.success is True
        assert result.confidence == 0.85
        assert len(result.data["pricing_items"]) == 0
        assert result.data["total_amount"] == 0.00
    
    @patch('src.agents.pricing_extraction_agent.OpenAI')
    def test_extract_pricing_from_text_api_error(self, mock_openai):
        """Test pricing extraction with API error."""
        # Mock OpenAI API error
        mock_client = Mock()
        mock_client.chat.completions.create.side_effect = Exception("API Error")
        mock_openai.return_value = mock_client
        
        agent = PricingExtractionAgent()
        text = "Software License: $5,000."
        
        result = agent.extract_pricing_from_text(text)
        
        assert result.status == AgentStatus.FAILED
        assert result.success is False
        assert "API Error" in result.error_message
    
    @patch('src.agents.pricing_extraction_agent.OpenAI')
    def test_extract_pricing_from_text_invalid_json(self, mock_openai):
        """Test pricing extraction with invalid JSON response."""
        # Mock OpenAI response with invalid JSON
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Invalid JSON response"
        
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        agent = PricingExtractionAgent()
        text = "Software License: $5,000."
        
        result = agent.extract_pricing_from_text(text)
        
        assert result.status == AgentStatus.FAILED
        assert result.success is False
        assert "JSON" in result.error_message or "parse" in result.error_message.lower()
    
    def test_extract_pricing_from_text_empty_input(self):
        """Test pricing extraction with empty input."""
        agent = PricingExtractionAgent()
        
        result = agent.extract_pricing_from_text("")
        
        assert result.status == AgentStatus.FAILED
        assert result.success is False
        assert "empty" in result.error_message.lower() or "invalid" in result.error_message.lower()
    
    def test_extract_pricing_from_text_none_input(self):
        """Test pricing extraction with None input."""
        agent = PricingExtractionAgent()
        
        result = agent.extract_pricing_from_text(None)
        
        assert result.status == AgentStatus.FAILED
        assert result.success is False
        assert "none" in result.error_message.lower() or "invalid" in result.error_message.lower()
    
    @patch('src.agents.pricing_extraction_agent.OpenAI')
    def test_extract_pricing_from_document_success(self, mock_openai):
        """Test successful pricing extraction from document."""
        # Mock OpenAI response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = '''
        {
            "pricing_items": [
                {
                    "description": "Annual Software License",
                    "quantity": 1,
                    "unit_price": 10000.00,
                    "total": 10000.00,
                    "currency": "USD"
                }
            ],
            "total_amount": 10000.00,
            "currency": "USD",
            "confidence": 0.92
        }
        '''
        
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        agent = PricingExtractionAgent()
        
        # Mock document
        document = Mock()
        document.document_id = "DOC-001"
        document.extracted_text = "Annual Software License: $10,000 per year."
        
        result = agent.extract_pricing_from_document(document)
        
        assert result.status == AgentStatus.COMPLETED
        assert result.success is True
        assert result.confidence == 0.92
        assert len(result.data["pricing_items"]) == 1
        assert result.data["total_amount"] == 10000.00
    
    @patch('src.agents.pricing_extraction_agent.OpenAI')
    def test_extract_pricing_from_document_no_text(self, mock_openai):
        """Test pricing extraction from document with no extracted text."""
        agent = PricingExtractionAgent()
        
        # Mock document with no extracted text
        document = Mock()
        document.document_id = "DOC-001"
        document.extracted_text = None
        
        result = agent.extract_pricing_from_document(document)
        
        assert result.status == AgentStatus.FAILED
        assert result.success is False
        assert "no text" in result.error_message.lower() or "extracted" in result.error_message.lower()
    
    @patch('src.agents.pricing_extraction_agent.OpenAI')
    def test_extract_pricing_with_retry_success(self, mock_openai):
        """Test pricing extraction with retry mechanism - success on retry."""
        # Mock OpenAI responses - first fails, second succeeds
        mock_response_fail = Mock()
        mock_response_fail.choices = [Mock()]
        mock_response_fail.choices[0].message.content = "Invalid JSON"
        
        mock_response_success = Mock()
        mock_response_success.choices = [Mock()]
        mock_response_success.choices[0].message.content = '''
        {
            "pricing_items": [
                {
                    "description": "Software License",
                    "quantity": 1,
                    "unit_price": 5000.00,
                    "total": 5000.00,
                    "currency": "USD"
                }
            ],
            "total_amount": 5000.00,
            "currency": "USD",
            "confidence": 0.90
        }
        '''
        
        mock_client = Mock()
        mock_client.chat.completions.create.side_effect = [
            Exception("API Error"),  # First call fails
            mock_response_success    # Second call succeeds
        ]
        mock_openai.return_value = mock_client
        
        agent = PricingExtractionAgent(max_retries=2)
        text = "Software License: $5,000."
        
        result = agent.extract_pricing_from_text(text)
        
        assert result.status == AgentStatus.COMPLETED
        assert result.success is True
        assert result.confidence == 0.90
        assert mock_client.chat.completions.create.call_count == 2
    
    @patch('src.agents.pricing_extraction_agent.OpenAI')
    def test_extract_pricing_with_retry_all_fail(self, mock_openai):
        """Test pricing extraction with retry mechanism - all retries fail."""
        # Mock OpenAI API error for all calls
        mock_client = Mock()
        mock_client.chat.completions.create.side_effect = Exception("API Error")
        mock_openai.return_value = mock_client
        
        agent = PricingExtractionAgent(max_retries=2)
        text = "Software License: $5,000."
        
        result = agent.extract_pricing_from_text(text)
        
        assert result.status == AgentStatus.FAILED
        assert result.success is False
        assert "API Error" in result.error_message
        assert mock_client.chat.completions.create.call_count == 3  # Initial + 2 retries
    
    def test_validate_pricing_data_valid(self):
        """Test validation of valid pricing data."""
        agent = PricingExtractionAgent()
        
        valid_data = {
            "pricing_items": [
                {
                    "description": "Software License",
                    "quantity": 1,
                    "unit_price": 5000.00,
                    "total": 5000.00,
                    "currency": "USD"
                }
            ],
            "total_amount": 5000.00,
            "currency": "USD",
            "confidence": 0.95
        }
        
        is_valid = agent.validate_pricing_data(valid_data)
        assert is_valid is True
    
    def test_validate_pricing_data_invalid_missing_fields(self):
        """Test validation of pricing data with missing fields."""
        agent = PricingExtractionAgent()
        
        invalid_data = {
            "pricing_items": [
                {
                    "description": "Software License",
                    "quantity": 1,
                    # Missing unit_price and total
                    "currency": "USD"
                }
            ],
            "total_amount": 5000.00,
            "currency": "USD",
            "confidence": 0.95
        }
        
        is_valid = agent.validate_pricing_data(invalid_data)
        assert is_valid is False
    
    def test_validate_pricing_data_invalid_negative_amounts(self):
        """Test validation of pricing data with negative amounts."""
        agent = PricingExtractionAgent()
        
        invalid_data = {
            "pricing_items": [
                {
                    "description": "Software License",
                    "quantity": 1,
                    "unit_price": -5000.00,  # Negative price
                    "total": -5000.00,
                    "currency": "USD"
                }
            ],
            "total_amount": -5000.00,
            "currency": "USD",
            "confidence": 0.95
        }
        
        is_valid = agent.validate_pricing_data(invalid_data)
        assert is_valid is False
    
    def test_validate_pricing_data_invalid_currency(self):
        """Test validation of pricing data with invalid currency."""
        agent = PricingExtractionAgent()
        
        invalid_data = {
            "pricing_items": [
                {
                    "description": "Software License",
                    "quantity": 1,
                    "unit_price": 5000.00,
                    "total": 5000.00,
                    "currency": "INVALID"  # Invalid currency code
                }
            ],
            "total_amount": 5000.00,
            "currency": "INVALID",
            "confidence": 0.95
        }
        
        is_valid = agent.validate_pricing_data(invalid_data)
        assert is_valid is False
    
    def test_validate_pricing_data_invalid_confidence(self):
        """Test validation of pricing data with invalid confidence."""
        agent = PricingExtractionAgent()
        
        invalid_data = {
            "pricing_items": [
                {
                    "description": "Software License",
                    "quantity": 1,
                    "unit_price": 5000.00,
                    "total": 5000.00,
                    "currency": "USD"
                }
            ],
            "total_amount": 5000.00,
            "currency": "USD",
            "confidence": 1.5  # Invalid confidence > 1.0
        }
        
        is_valid = agent.validate_pricing_data(invalid_data)
        assert is_valid is False
    
    def test_format_pricing_output(self):
        """Test formatting of pricing output."""
        agent = PricingExtractionAgent()
        
        raw_data = {
            "pricing_items": [
                {
                    "description": "Software License",
                    "quantity": 1,
                    "unit_price": 5000.00,
                    "total": 5000.00,
                    "currency": "USD"
                }
            ],
            "total_amount": 5000.00,
            "currency": "USD",
            "confidence": 0.95
        }
        
        formatted = agent.format_pricing_output(raw_data)
        
        assert "pricing_items" in formatted
        assert "total_amount" in formatted
        assert "currency" in formatted
        assert "confidence" in formatted
        assert "extraction_timestamp" in formatted
        assert "agent_type" in formatted
        assert formatted["agent_type"] == "pricing_extraction"
    
    def test_get_agent_status(self):
        """Test getting agent status."""
        agent = PricingExtractionAgent()
        
        assert agent.get_status() == AgentStatus.IDLE
        
        agent.status = AgentStatus.RUNNING
        assert agent.get_status() == AgentStatus.RUNNING
    
    def test_get_agent_info(self):
        """Test getting agent information."""
        agent = PricingExtractionAgent()
        
        info = agent.get_agent_info()
        
        assert info["agent_type"] == "pricing_extraction"
        assert info["status"] == AgentStatus.IDLE
        assert info["model_name"] == "gpt-4-turbo-preview"
        assert info["max_retries"] == 3
        assert info["timeout_seconds"] == 300


class TestPricingExtractionAgentIntegration:
    """Integration tests for PricingExtractionAgent."""
    
    @patch('src.agents.pricing_extraction_agent.OpenAI')
    def test_end_to_end_pricing_extraction(self, mock_openai):
        """Test end-to-end pricing extraction workflow."""
        # Mock OpenAI response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = '''
        {
            "pricing_items": [
                {
                    "description": "Enterprise Software License",
                    "quantity": 1,
                    "unit_price": 25000.00,
                    "total": 25000.00,
                    "currency": "USD"
                },
                {
                    "description": "Annual Support",
                    "quantity": 1,
                    "unit_price": 5000.00,
                    "total": 5000.00,
                    "currency": "USD"
                }
            ],
            "total_amount": 30000.00,
            "currency": "USD",
            "confidence": 0.98
        }
        '''
        
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        agent = PricingExtractionAgent()
        
        # Test with complex contract text
        contract_text = """
        SOFTWARE LICENSE AGREEMENT
        
        Enterprise Software License: $25,000 one-time fee
        Annual Support: $5,000 per year
        
        Total Contract Value: $30,000
        """
        
        result = agent.extract_pricing_from_text(contract_text)
        
        assert result.status == AgentStatus.COMPLETED
        assert result.success is True
        assert result.confidence == 0.98
        assert len(result.data["pricing_items"]) == 2
        assert result.data["total_amount"] == 30000.00
        assert result.data["currency"] == "USD"
        
        # Verify individual pricing items
        items = result.data["pricing_items"]
        assert items[0]["description"] == "Enterprise Software License"
        assert items[0]["unit_price"] == 25000.00
        assert items[1]["description"] == "Annual Support"
        assert items[1]["unit_price"] == 5000.00
    
    @patch('src.agents.pricing_extraction_agent.OpenAI')
    def test_multiple_currency_handling(self, mock_openai):
        """Test handling of multiple currencies in pricing extraction."""
        # Mock OpenAI response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = '''
        {
            "pricing_items": [
                {
                    "description": "Software License",
                    "quantity": 1,
                    "unit_price": 5000.00,
                    "total": 5000.00,
                    "currency": "USD"
                },
                {
                    "description": "Support Services",
                    "quantity": 1,
                    "unit_price": 4000.00,
                    "total": 4000.00,
                    "currency": "EUR"
                }
            ],
            "total_amount": 9000.00,
            "currency": "MIXED",
            "confidence": 0.85,
            "note": "Multiple currencies detected"
        }
        '''
        
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        agent = PricingExtractionAgent()
        
        text = "Software License: $5,000 USD. Support Services: €4,000 EUR."
        
        result = agent.extract_pricing_from_text(text)
        
        assert result.status == AgentStatus.COMPLETED
        assert result.success is True
        assert result.data["currency"] == "MIXED"
        assert len(result.data["pricing_items"]) == 2
        assert result.data["pricing_items"][0]["currency"] == "USD"
        assert result.data["pricing_items"][1]["currency"] == "EUR"


@pytest.mark.agent
class TestAgentMarkers:
    """Test that agent test markers work correctly."""
    
    def test_agent_marker_applied(self):
        """Test that agent marker is applied to this test."""
        assert True
    
    def test_agent_basic_functionality(self):
        """Test basic agent functionality."""
        agent = PricingExtractionAgent()
        assert agent.agent_type == "pricing_extraction"
        assert agent.status == AgentStatus.IDLE
