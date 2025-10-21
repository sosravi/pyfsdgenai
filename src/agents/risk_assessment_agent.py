"""
Risk Assessment Agent

This module implements the RiskAssessmentAgent class for assessing
risk factors in document text using AI.
"""

from src.agents.base_agent import BaseAgent, AgentResult, AgentStatus
from typing import Dict, Any
import re
import logging

logger = logging.getLogger(__name__)


class RiskAssessmentAgent(BaseAgent):
    """Agent for assessing risk factors in documents."""
    
    def __init__(self):
        super().__init__(
            agent_id="risk_assessment_001",
            agent_name="Risk Assessment Agent",
            agent_type="risk_assessment"
        )
    
    def execute(self, input_data: Dict[str, Any]) -> AgentResult:
        """Execute risk assessment."""
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
            
            # Assess risk factors
            text = input_data.get("text", "")
            risk_data = self._assess_risk_from_text(text)
            
            # Validate output
            if not self.validate_output(risk_data):
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
                data=risk_data,
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
        required_fields = ["risk_score", "risk_factors", "recommendations"]
        return all(field in output_data for field in required_fields)
    
    def _assess_risk_from_text(self, text: str) -> Dict[str, Any]:
        """Assess risk factors from text."""
        try:
            risk_factors = []
            risk_score = 0.3
            recommendations = []
            
            # Risk factor patterns
            risk_patterns = {
                "High liability exposure": r'liability.*limit.*\$?[\d,]+',
                "Termination risk": r'termination.*notice',
                "Payment risk": r'late.*payment.*fee',
                "Force majeure": r'force\s*majeure',
                "Indemnification": r'indemnif',
                "Penalty clauses": r'penalty.*\$?[\d,]+',
                "High value contract": r'\$[\d,]+.*(?:million|thousand)',
                "Long term contract": r'(?:year|month).*(?:term|duration)',
                "Exclusive agreement": r'exclusive',
                "Non-compete": r'non.?compete'
            }
            
            # Check for risk factors
            for risk_factor, pattern in risk_patterns.items():
                if re.search(pattern, text, re.IGNORECASE):
                    risk_factors.append(risk_factor)
            
            # Calculate risk score based on factors found
            high_risk_factors = ["High liability exposure", "Penalty clauses", "High value contract"]
            medium_risk_factors = ["Termination risk", "Payment risk", "Long term contract"]
            
            high_risk_count = sum(1 for factor in risk_factors if factor in high_risk_factors)
            medium_risk_count = sum(1 for factor in risk_factors if factor in medium_risk_factors)
            
            risk_score = 0.3 + (high_risk_count * 0.2) + (medium_risk_count * 0.1)
            risk_score = min(risk_score, 1.0)
            
            # Generate recommendations based on risk factors
            if "High liability exposure" in risk_factors:
                recommendations.append("Consider liability insurance")
            
            if "Termination risk" in risk_factors:
                recommendations.append("Review termination clauses")
            
            if "Payment risk" in risk_factors:
                recommendations.append("Implement payment monitoring")
            
            if "High value contract" in risk_factors:
                recommendations.append("Conduct thorough due diligence")
            
            if risk_score > 0.7:
                recommendations.append("Consider legal review")
            
            if not recommendations:
                recommendations.append("Contract appears low risk")
            
            return {
                "risk_score": risk_score,
                "risk_factors": risk_factors,
                "recommendations": recommendations
            }
            
        except Exception as e:
            logger.error(f"Error assessing risk: {str(e)}")
            return {
                "risk_score": 0.5,
                "risk_factors": ["Assessment error"],
                "recommendations": ["Manual review recommended"]
            }
