"""
Terms Extraction Agent

This module implements the TermsExtractionAgent class for extracting
terms and conditions from document text using AI.
"""

from src.agents.base_agent import BaseAgent, AgentResult, AgentStatus
from typing import Dict, Any
import re
import logging

logger = logging.getLogger(__name__)


class TermsExtractionAgent(BaseAgent):
    """Agent for extracting terms and conditions from documents."""
    
    def __init__(self):
        super().__init__(
            agent_id="terms_extraction_001",
            agent_name="Terms Extraction Agent",
            agent_type="terms_extraction"
        )
    
    def execute(self, input_data: Dict[str, Any]) -> AgentResult:
        """Execute terms extraction."""
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
            
            # Extract terms information
            text = input_data.get("text", "")
            terms_data = self._extract_terms_from_text(text)
            
            # Validate output
            if not self.validate_output(terms_data):
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
                data=terms_data,
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
        required_fields = ["terms", "risk_score", "compliance_score"]
        return all(field in output_data for field in required_fields)
    
    def _extract_terms_from_text(self, text: str) -> Dict[str, Any]:
        """Extract terms and conditions from text."""
        try:
            terms = []
            risk_score = 0.5
            compliance_score = 0.8
            
            # Look for common terms
            term_patterns = {
                "Net 30": r'net\s*30',
                "Net 45": r'net\s*45',
                "Net 60": r'net\s*60',
                "Force Majeure": r'force\s*majeure',
                "Termination Clause": r'termination',
                "Liability Limit": r'liability',
                "Payment Terms": r'payment',
                "Delivery Terms": r'delivery',
                "Warranty": r'warranty',
                "Indemnification": r'indemnif'
            }
            
            for term_name, pattern in term_patterns.items():
                if re.search(pattern, text, re.IGNORECASE):
                    terms.append(term_name)
            
            # Calculate risk score based on terms found
            high_risk_terms = ["Termination Clause", "Liability Limit", "Indemnification"]
            risk_factors = sum(1 for term in terms if term in high_risk_terms)
            risk_score = min(0.3 + (risk_factors * 0.2), 1.0)
            
            # Calculate compliance score
            compliance_terms = ["Payment Terms", "Delivery Terms", "Warranty"]
            compliance_factors = sum(1 for term in terms if term in compliance_terms)
            compliance_score = min(0.6 + (compliance_factors * 0.1), 1.0)
            
            return {
                "terms": terms,
                "risk_score": risk_score,
                "compliance_score": compliance_score
            }
            
        except Exception as e:
            logger.error(f"Error extracting terms: {str(e)}")
            return {
                "terms": [],
                "risk_score": 0.5,
                "compliance_score": 0.5
            }
