"""
PyFSD GenAI - Pricing Extraction Agent

This module contains the pricing extraction agent that uses AI to extract
pricing information from contract text and documents.
"""

import json
import re
from typing import Dict, Any, Optional, List
from datetime import datetime
from decimal import Decimal

from openai import OpenAI
from src.agents.base_agent import BaseAgent, AgentStatus, AgentResult
from src.core.config import get_settings


class PricingExtractionAgent(BaseAgent):
    """AI agent for extracting pricing information from text and documents."""
    
    def __init__(
        self,
        model_name: str = "gpt-4-turbo-preview",
        max_retries: int = 3,
        timeout_seconds: int = 300
    ):
        """
        Initialize the pricing extraction agent.
        
        Args:
            model_name: Name of the AI model to use
            max_retries: Maximum number of retry attempts
            timeout_seconds: Timeout for operations in seconds
        """
        super().__init__(
            agent_type="pricing_extraction",
            model_name=model_name,
            max_retries=max_retries,
            timeout_seconds=timeout_seconds
        )
        
        # Initialize OpenAI client
        settings = get_settings()
        api_key = settings.openai_api_key or "test-key-for-testing"
        self.client = OpenAI(api_key=api_key)
        
        # Pricing extraction prompt template
        self.prompt_template = """You are an expert pricing extraction agent. Your task is to extract pricing information from contract text and return it in a structured JSON format.

Extract the following information:
1. Individual pricing items with description, quantity, unit price, total, and currency
2. Total contract amount
3. Currency used
4. Confidence level (0.0 to 1.0)

Return ONLY valid JSON in this exact format:
{{"pricing_items": [{{"description": "Item description", "quantity": 1, "unit_price": 1000.00, "total": 1000.00, "currency": "USD"}}], "total_amount": 1000.00, "currency": "USD", "confidence": 0.95}}

If no pricing information is found, return:
{{"pricing_items": [], "total_amount": 0.00, "currency": "USD", "confidence": 0.0, "message": "No pricing information found in the text"}}

Text to analyze:
{text}"""
    
    def extract_pricing_from_text(self, text: str) -> AgentResult:
        """
        Extract pricing information from text.
        
        Args:
            text: Text to extract pricing from
            
        Returns:
            AgentResult containing extracted pricing data
        """
        start_time = datetime.utcnow()
        
        try:
            # Validate input
            self._validate_input(text, "text")
            
            # Set status to running
            self._set_status(AgentStatus.RUNNING)
            
            # Prepare prompt
            prompt = self.prompt_template.format(text=text)
            
            # Call OpenAI API with retry mechanism
            def call_openai():
                response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=[
                        {"role": "system", "content": "You are a pricing extraction expert. Return only valid JSON."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.1,
                    max_tokens=2000
                )
                return response
            
            response = self._retry_operation(call_openai)
            
            # Extract response content
            response_text = response.choices[0].message.content.strip()
            
            # Parse JSON response
            pricing_data = self._parse_json_response(response_text)
            
            # Validate extracted data
            if not self.validate_pricing_data(pricing_data):
                raise ValueError("Extracted pricing data failed validation")
            
            # Format output
            formatted_data = self.format_pricing_output(pricing_data)
            
            # Calculate execution time
            execution_time = self._calculate_execution_time(start_time)
            
            # Update last execution time
            self.last_execution = datetime.utcnow()
            
            # Set status to completed
            self._set_status(AgentStatus.COMPLETED)
            
            return self._create_result(
                status=AgentStatus.COMPLETED,
                success=True,
                data=formatted_data,
                confidence=pricing_data.get("confidence", 0.0),
                execution_time=execution_time
            )
            
        except Exception as e:
            # Set status to failed
            self._set_status(AgentStatus.FAILED)
            
            # Calculate execution time
            execution_time = self._calculate_execution_time(start_time)
            
            return self._create_result(
                status=AgentStatus.FAILED,
                success=False,
                error_message=str(e),
                execution_time=execution_time
            )
    
    def extract_pricing_from_document(self, document) -> AgentResult:
        """
        Extract pricing information from a document object.
        
        Args:
            document: Document object with extracted_text attribute
            
        Returns:
            AgentResult containing extracted pricing data
        """
        try:
            # Check if document has extracted text
            if not hasattr(document, 'extracted_text') or not document.extracted_text:
                return self._create_result(
                    status=AgentStatus.FAILED,
                    success=False,
                    error_message="Document has no extracted text available"
                )
            
            # Extract pricing from the document's text
            return self.extract_pricing_from_text(document.extracted_text)
            
        except Exception as e:
            return self._create_result(
                status=AgentStatus.FAILED,
                success=False,
                error_message=str(e)
            )
    
    def validate_pricing_data(self, data: Dict[str, Any]) -> bool:
        """
        Validate extracted pricing data.
        
        Args:
            data: Pricing data to validate
            
        Returns:
            True if data is valid, False otherwise
        """
        try:
            # Check required fields
            required_fields = ["pricing_items", "total_amount", "currency", "confidence"]
            for field in required_fields:
                if field not in data:
                    return False
            
            # Validate pricing_items
            if not isinstance(data["pricing_items"], list):
                return False
            
            # Validate each pricing item
            for item in data["pricing_items"]:
                if not isinstance(item, dict):
                    return False
                
                # Check required item fields
                item_fields = ["description", "quantity", "unit_price", "total", "currency"]
                for field in item_fields:
                    if field not in item:
                        return False
                
                # Validate numeric fields
                numeric_fields = ["quantity", "unit_price", "total"]
                for field in numeric_fields:
                    if not isinstance(item[field], (int, float)) or item[field] < 0:
                        return False
                
                # Validate currency
                if not isinstance(item["currency"], str) or len(item["currency"]) != 3:
                    return False
            
            # Validate total_amount
            if not isinstance(data["total_amount"], (int, float)) or data["total_amount"] < 0:
                return False
            
            # Validate currency (allow MIXED for multiple currencies)
            if not isinstance(data["currency"], str) or (len(data["currency"]) != 3 and data["currency"] != "MIXED"):
                return False
            
            # Validate confidence
            confidence = data["confidence"]
            if not isinstance(confidence, (int, float)) or confidence < 0 or confidence > 1:
                return False
            
            return True
            
        except Exception:
            return False
    
    def format_pricing_output(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format pricing output with additional metadata.
        
        Args:
            raw_data: Raw pricing data from AI model
            
        Returns:
            Formatted pricing data with metadata
        """
        formatted = raw_data.copy()
        
        # Add metadata
        formatted["extraction_timestamp"] = self._format_timestamp()
        formatted["agent_type"] = self.agent_type
        formatted["model_used"] = self.model_name
        
        return formatted
    
    def get_supported_currencies(self) -> List[str]:
        """Get list of supported currency codes."""
        return [
            "USD", "EUR", "GBP", "JPY", "CAD", "AUD", "CHF", "CNY", "SEK", "NOK",
            "DKK", "PLN", "CZK", "HUF", "RUB", "BRL", "INR", "KRW", "SGD", "HKD"
        ]
    
    def is_valid_currency(self, currency: str) -> bool:
        """Check if currency code is valid."""
        return currency.upper() in self.get_supported_currencies()
    
    def extract_currency_from_text(self, text: str) -> Optional[str]:
        """Extract currency code from text."""
        # Common currency patterns
        currency_patterns = [
            r'\$(\d+(?:,\d{3})*(?:\.\d{2})?)',  # USD
            r'€(\d+(?:,\d{3})*(?:\.\d{2})?)',   # EUR
            r'£(\d+(?:,\d{3})*(?:\.\d{2})?)',   # GBP
            r'¥(\d+(?:,\d{3})*(?:\.\d{2})?)',   # JPY
            r'(\d+(?:,\d{3})*(?:\.\d{2})?)\s*(USD|EUR|GBP|JPY|CAD|AUD)',  # Explicit currency codes
        ]
        
        for pattern in currency_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                # Return the first currency found
                if len(matches[0]) == 2:  # Pattern with explicit currency code
                    return matches[0][1].upper()
                else:  # Pattern with currency symbol
                    if '$' in pattern:
                        return 'USD'
                    elif '€' in pattern:
                        return 'EUR'
                    elif '£' in pattern:
                        return 'GBP'
                    elif '¥' in pattern:
                        return 'JPY'
        
        return None
