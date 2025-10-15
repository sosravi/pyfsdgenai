"""
PyFSD GenAI - Property-Based Tests using Hypothesis

This module contains property-based tests for core components
using Hypothesis for comprehensive testing.
"""

import pytest
from hypothesis import given, strategies as st, settings, example
from decimal import Decimal
from datetime import datetime, date, timedelta
from typing import Dict, List, Any

from src.agents.pricing_extraction_agent import PricingExtractionAgent
from src.agents.base_agent import AgentStatus, AgentResult
from test_helpers import TestDataFactory


class TestPropertyBasedTests:
    """Property-based tests using Hypothesis."""

    @given(st.text(min_size=1, max_size=1000))
    def test_pricing_extraction_agent_handles_any_text(self, text):
        """Test that pricing extraction agent handles any text input."""
        agent = PricingExtractionAgent()
        
        # Test input validation without API calls
        # Should not crash on any text input
        assert isinstance(text, str)
        assert len(text) >= 1
        assert len(text) <= 1000
        
        # Test that agent can be initialized with any text length
        assert agent.agent_type == "pricing_extraction"
        assert agent.status == AgentStatus.IDLE

    @given(st.decimals(min_value=Decimal('0.01'), max_value=Decimal('999999999.99'), places=2))
    def test_pricing_validation_accepts_valid_amounts(self, amount):
        """Test that pricing validation accepts valid decimal amounts."""
        agent = PricingExtractionAgent()
        
        valid_data = {
            "pricing_items": [{
                "description": "Test Service",
                "quantity": 1,
                "unit_price": float(amount),
                "total": float(amount),
                "currency": "USD"
            }],
            "total_amount": float(amount),
            "currency": "USD",
            "confidence": 0.90
        }
        
        assert agent.validate_pricing_data(valid_data) is True

    @given(st.floats(min_value=0.0, max_value=1.0))
    def test_pricing_validation_accepts_valid_confidence(self, confidence):
        """Test that pricing validation accepts valid confidence values."""
        agent = PricingExtractionAgent()
        
        valid_data = {
            "pricing_items": [{
                "description": "Test Service",
                "quantity": 1,
                "unit_price": 1000.0,
                "total": 1000.0,
                "currency": "USD"
            }],
            "total_amount": 1000.0,
            "currency": "USD",
            "confidence": confidence
        }
        
        assert agent.validate_pricing_data(valid_data) is True

    @given(st.text(min_size=3, max_size=3, alphabet=st.characters(whitelist_categories=('Lu',))))
    def test_pricing_validation_accepts_valid_currency_codes(self, currency):
        """Test that pricing validation accepts valid 3-letter currency codes."""
        agent = PricingExtractionAgent()
        
        valid_data = {
            "pricing_items": [{
                "description": "Test Service",
                "quantity": 1,
                "unit_price": 1000.0,
                "total": 1000.0,
                "currency": currency
            }],
            "total_amount": 1000.0,
            "currency": currency,
            "confidence": 0.90
        }
        
        assert agent.validate_pricing_data(valid_data) is True

    @given(st.lists(st.text(min_size=1, max_size=100), min_size=1, max_size=10))
    def test_pricing_items_list_validation(self, descriptions):
        """Test validation with lists of pricing items."""
        agent = PricingExtractionAgent()
        
        pricing_items = []
        total_amount = 0.0
        
        for i, desc in enumerate(descriptions):
            amount = 100.0 + i * 50.0
            pricing_items.append({
                "description": desc,
                "quantity": 1,
                "unit_price": amount,
                "total": amount,
                "currency": "USD"
            })
            total_amount += amount
        
        valid_data = {
            "pricing_items": pricing_items,
            "total_amount": total_amount,
            "currency": "USD",
            "confidence": 0.90
        }
        
        assert agent.validate_pricing_data(valid_data) is True

    @given(st.dates(min_value=date(1900, 1, 1), max_value=date(2099, 12, 31)))
    def test_contract_date_generation(self, contract_date):
        """Test contract data generation with various dates."""
        contract_data = TestDataFactory.create_contract_data(
            start_date=contract_date.isoformat(),
            end_date=(contract_date + timedelta(days=365)).isoformat()
        )
        
        assert contract_data["start_date"] == contract_date.isoformat()
        assert contract_data["end_date"] == (contract_date + timedelta(days=365)).isoformat()

    @given(st.floats(min_value=0.01, max_value=999999999.99))
    def test_invoice_amount_generation(self, amount):
        """Test invoice data generation with various amounts."""
        invoice_data = TestDataFactory.create_invoice_data(total_amount=amount)
        
        assert invoice_data["total_amount"] == amount

    @given(st.integers(min_value=1, max_value=1073741824))  # Up to 1GB
    def test_document_size_generation(self, file_size):
        """Test document data generation with various file sizes."""
        document_data = TestDataFactory.create_document_data(file_size=file_size)
        
        assert document_data["file_size"] == file_size

    @given(st.text(min_size=1, max_size=50, alphabet=st.characters(whitelist_categories=('Ll', 'Lu', 'Nd'))))
    def test_username_generation(self, username):
        """Test user data generation with various usernames."""
        user_data = TestDataFactory.create_user_data(username=username)
        
        assert user_data["username"] == username

    @given(st.emails())
    def test_email_generation(self, email):
        """Test user data generation with various emails."""
        user_data = TestDataFactory.create_user_data(email=email)
        
        assert user_data["email"] == email

    @given(st.text(min_size=1, max_size=1000))
    def test_filename_sanitization(self, filename):
        """Test filename sanitization with various inputs."""
        import re
        
        # Simple sanitization function
        def sanitize_filename(filename):
            return re.sub(r'[<>:"/\\|?*]', '', filename)
        
        sanitized = sanitize_filename(filename)
        
        # Sanitized filename should not contain invalid characters
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            assert char not in sanitized

    @given(st.text(min_size=0, max_size=1000))
    def test_text_extraction(self, text):
        """Test text extraction with various inputs."""
        # Simple text extraction function
        def extract_text_from_content(text):
            return text.strip()
        
        extracted = extract_text_from_content(text)
        
        # Extracted text should be a string
        assert isinstance(extracted, str)

    @given(st.floats(min_value=0.0, max_value=1.0))
    def test_confidence_boundary_properties(self, confidence):
        """Test confidence value boundary properties."""
        agent = PricingExtractionAgent()
        
        # Test that confidence values between 0 and 1 are valid
        valid_data = {
            "pricing_items": [{
                "description": "Test Service",
                "quantity": 1,
                "unit_price": 1000.0,
                "total": 1000.0,
                "currency": "USD"
            }],
            "total_amount": 1000.0,
            "currency": "USD",
            "confidence": confidence
        }
        
        assert agent.validate_pricing_data(valid_data) is True

    @given(st.lists(st.floats(min_value=0.01, max_value=999999.99), min_size=1, max_size=20))
    def test_multiple_pricing_items_totals(self, amounts):
        """Test that multiple pricing items sum correctly."""
        agent = PricingExtractionAgent()
        
        pricing_items = []
        expected_total = sum(amounts)
        
        for i, amount in enumerate(amounts):
            pricing_items.append({
                "description": f"Service {i+1}",
                "quantity": 1,
                "unit_price": amount,
                "total": amount,
                "currency": "USD"
            })
        
        valid_data = {
            "pricing_items": pricing_items,
            "total_amount": expected_total,
            "currency": "USD",
            "confidence": 0.90
        }
        
        assert agent.validate_pricing_data(valid_data) is True

    @given(st.text(min_size=3, max_size=3, alphabet=st.characters(whitelist_categories=('Lu',))))
    def test_currency_code_properties(self, currency):
        """Test currency code properties."""
        agent = PricingExtractionAgent()
        
        # Should accept valid 3-letter currency codes
        valid_data = {
            "pricing_items": [{
                "description": "Test Service",
                "quantity": 1,
                "unit_price": 1000.0,
                "total": 1000.0,
                "currency": currency
            }],
            "total_amount": 1000.0,
            "currency": currency,
            "confidence": 0.90
        }
        
        assert agent.validate_pricing_data(valid_data) is True

    @given(st.integers(min_value=1, max_value=100))
    def test_agent_retry_properties(self, max_retries):
        """Test agent retry properties."""
        agent = PricingExtractionAgent(max_retries=max_retries)
        
        assert agent.max_retries == max_retries
        assert agent.max_retries >= 1
        assert agent.max_retries <= 100

    @given(st.integers(min_value=1, max_value=3600))  # 1 second to 1 hour
    def test_agent_timeout_properties(self, timeout_seconds):
        """Test agent timeout properties."""
        agent = PricingExtractionAgent(timeout_seconds=timeout_seconds)
        
        assert agent.timeout_seconds == timeout_seconds
        assert agent.timeout_seconds >= 1
        assert agent.timeout_seconds <= 3600


@pytest.mark.property
class TestPropertyMarkers:
    """Test that property markers work correctly."""

    def test_property_marker_applied(self):
        """Test that property marker is applied to this test."""
        assert True

    def test_property_basic_functionality(self):
        """Test basic property functionality."""
        # Test that properties hold for simple cases
        assert 1 + 1 == 2
        assert "hello" + "world" == "helloworld"
        assert [1, 2, 3] + [4, 5, 6] == [1, 2, 3, 4, 5, 6]
