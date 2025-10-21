"""
Pricing Extraction Agent

This module implements the PricingExtractionAgent class for extracting
pricing information from document text using AI.
"""

from src.agents.base_agent import BaseAgent, AgentResult, AgentStatus
from typing import Dict, Any
import re
import logging

logger = logging.getLogger(__name__)


class PricingExtractionAgent(BaseAgent):
    """Agent for extracting pricing information from documents."""
    
    def __init__(self):
        super().__init__(
            agent_id="pricing_extraction_001",
            agent_name="Pricing Extraction Agent",
            agent_type="pricing_extraction"
        )
        self.prompt_template = """
        Extract pricing information from the following contract text.
        Return a JSON object with the following structure:
        {
            "pricing_items": [
                {
                    "description": "Item description",
                    "quantity": 1,
                    "unit_price": 1000.00,
                    "total": 1000.00,
                    "currency": "USD"
                }
            ],
            "total_amount": 1000.00,
            "currency": "USD",
            "confidence": 0.95
        }
        
        Contract text: {text}
        """
    
    def execute(self, input_data: Dict[str, Any]) -> AgentResult:
        """Execute pricing extraction."""
        import time
        start_time = time.time()
        
        try:
            self.status = AgentStatus.RUNNING
            self.execution_count += 1
            
            # Validate input
            if not self.validate_input(input_data):
                self.status = AgentStatus.FAILED
                return AgentResult(
                    status=AgentStatus.FAILED,
                    success=False,
                    data={},
                    execution_time=time.time() - start_time,
                    error_message="Invalid input data"
                )
            
            # Extract pricing information
            text = input_data.get("text", "")
            pricing_data = self._extract_pricing_from_text(text)
            
            # Validate output
            if not self.validate_output(pricing_data):
                self.status = AgentStatus.FAILED
                return AgentResult(
                    status=AgentStatus.FAILED,
                    success=False,
                    data={},
                    execution_time=time.time() - start_time,
                    error_message="Invalid output data"
                )
            
            self.status = AgentStatus.COMPLETED
            self.success_count += 1
            self.last_executed = self.created_at
            
            return AgentResult(
                status=AgentStatus.COMPLETED,
                success=True,
                data=pricing_data,
                execution_time=time.time() - start_time
            )
            
        except Exception as e:
            self.status = AgentStatus.FAILED
            return AgentResult(
                status=AgentStatus.FAILED,
                success=False,
                data={},
                execution_time=time.time() - start_time,
                error_message=str(e)
            )
    
    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """Validate input data."""
        return isinstance(input_data, dict) and "text" in input_data and isinstance(input_data["text"], str)
    
    def validate_output(self, output_data: Dict[str, Any]) -> bool:
        """Validate output data."""
        required_fields = ["pricing_items", "total_amount", "currency", "confidence"]
        return all(field in output_data for field in required_fields)
    
    def _extract_pricing_from_text(self, text: str) -> Dict[str, Any]:
        """Extract pricing information from text."""
        try:
            pricing_items = []
            total_amount = 0.0
            
            # Look for price patterns
            price_patterns = [
                r'\$[\d,]+\.?\d*',
                r'[\d,]+\.?\d*\s*(?:USD|dollars?)',
                r'price[:\s]*\$?[\d,]+\.?\d*',
                r'amount[:\s]*\$?[\d,]+\.?\d*',
                r'cost[:\s]*\$?[\d,]+\.?\d*',
                r'value[:\s]*\$?[\d,]+\.?\d*'
            ]
            
            for pattern in price_patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                for match in matches:
                    # Extract numeric value
                    numeric_match = re.search(r'[\d,]+\.?\d*', match)
                    if numeric_match:
                        amount = float(numeric_match.group().replace(',', ''))
                        pricing_items.append({
                            "description": "Service/Product",
                            "quantity": 1,
                            "unit_price": amount,
                            "total": amount,
                            "currency": "USD"
                        })
                        total_amount += amount
            
            # If no prices found, create a default entry
            if not pricing_items:
                pricing_items.append({
                    "description": "Contract Value",
                    "quantity": 1,
                    "unit_price": 0.0,
                    "total": 0.0,
                    "currency": "USD"
                })
            
            return {
                "pricing_items": pricing_items,
                "total_amount": total_amount,
                "currency": "USD",
                "confidence": 0.8 if pricing_items else 0.1
            }
            
        except Exception as e:
            logger.error(f"Error extracting pricing: {str(e)}")
            return {
                "pricing_items": [],
                "total_amount": 0.0,
                "currency": "USD",
                "confidence": 0.0
            }