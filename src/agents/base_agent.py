"""
Base Agent Classes for Document Processing

This module provides the base classes and interfaces for AI agents
used in document processing pipeline.
"""

from enum import Enum
from dataclasses import dataclass
from typing import Dict, Any, Optional, List
from datetime import datetime
from abc import ABC, abstractmethod


class AgentStatus(Enum):
    """Agent execution status."""
    IDLE = "idle"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class AgentResult:
    """Result of agent execution."""
    status: AgentStatus
    success: bool
    data: Dict[str, Any]
    execution_time: float
    error_message: Optional[str] = None
    timestamp: Optional[datetime] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()


class BaseAgent(ABC):
    """Abstract base class for all AI agents."""
    
    def __init__(self, agent_id: str, agent_name: str, agent_type: str):
        self.agent_id = agent_id
        self.agent_name = agent_name
        self.agent_type = agent_type
        self.status = AgentStatus.IDLE
        self.created_at = datetime.utcnow()
        self.last_executed = None
        self.execution_count = 0
        self.success_count = 0
        
    @abstractmethod
    def execute(self, input_data: Dict[str, Any]) -> AgentResult:
        """Execute the agent with given input data."""
        pass
    
    @abstractmethod
    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """Validate input data for the agent."""
        pass
    
    @abstractmethod
    def validate_output(self, output_data: Dict[str, Any]) -> bool:
        """Validate output data from the agent."""
        pass
    
    def get_status(self) -> Dict[str, Any]:
        """Get current agent status."""
        success_rate = self.success_count / self.execution_count if self.execution_count > 0 else 0
        
        return {
            "agent_id": self.agent_id,
            "agent_name": self.agent_name,
            "agent_type": self.agent_type,
            "status": self.status.value,
            "created_at": self.created_at.isoformat() + "Z",
            "last_executed": self.last_executed.isoformat() + "Z" if self.last_executed else None,
            "execution_count": self.execution_count,
            "success_count": self.success_count,
            "success_rate": success_rate
        }
    
    def reset_stats(self):
        """Reset agent execution statistics."""
        self.execution_count = 0
        self.success_count = 0
        self.last_executed = None
        self.status = AgentStatus.IDLE


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
            
            # Mock pricing extraction (in real implementation, use OpenAI API)
            text = input_data.get("text", "")
            
            # Simple pattern matching for demo
            pricing_items = []
            total_amount = 0.0
            
            # Look for price patterns
            import re
            price_patterns = [
                r'\$[\d,]+\.?\d*',
                r'[\d,]+\.?\d*\s*(?:USD|dollars?)',
                r'price[:\s]*\$?[\d,]+\.?\d*'
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
            
            result_data = {
                "pricing_items": pricing_items,
                "total_amount": total_amount,
                "currency": "USD",
                "confidence": 0.8 if pricing_items else 0.1
            }
            
            # Validate output
            if not self.validate_output(result_data):
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
            self.last_executed = datetime.utcnow()
            
            return AgentResult(
                status=AgentStatus.COMPLETED,
                success=True,
                data=result_data,
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
            
            # Mock terms extraction
            text = input_data.get("text", "")
            
            # Simple pattern matching for demo
            terms = []
            risk_score = 0.5
            compliance_score = 0.8
            
            # Look for common terms
            if "net 30" in text.lower():
                terms.append("Net 30")
            if "force majeure" in text.lower():
                terms.append("Force Majeure")
            if "termination" in text.lower():
                terms.append("Termination Clause")
            
            result_data = {
                "terms": terms,
                "risk_score": risk_score,
                "compliance_score": compliance_score
            }
            
            self.status = AgentStatus.COMPLETED
            self.success_count += 1
            self.last_executed = datetime.utcnow()
            
            return AgentResult(
                status=AgentStatus.COMPLETED,
                success=True,
                data=result_data,
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


class RiskAssessmentAgent(BaseAgent):
    """Agent for assessing risk in documents."""
    
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
            
            # Mock risk assessment
            text = input_data.get("text", "")
            
            # Simple risk scoring
            risk_factors = []
            risk_score = 0.3
            
            if "liability" in text.lower():
                risk_factors.append("High liability exposure")
                risk_score += 0.2
            
            if "termination" in text.lower():
                risk_factors.append("Termination risk")
                risk_score += 0.1
            
            recommendations = []
            if risk_score > 0.5:
                recommendations.append("Consider liability insurance")
            
            result_data = {
                "risk_score": min(risk_score, 1.0),
                "risk_factors": risk_factors,
                "recommendations": recommendations
            }
            
            self.status = AgentStatus.COMPLETED
            self.success_count += 1
            self.last_executed = datetime.utcnow()
            
            return AgentResult(
                status=AgentStatus.COMPLETED,
                success=True,
                data=result_data,
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