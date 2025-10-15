"""
PyFSD GenAI - Base Agent Module

This module contains the base agent class and related enums for all AI agents.
"""

from enum import Enum
from typing import Dict, Any, Optional, List
from datetime import datetime
from dataclasses import dataclass
import json


class AgentStatus(Enum):
    """Enumeration of possible agent statuses."""
    IDLE = "idle"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class AgentResult:
    """Result object returned by agent operations."""
    status: AgentStatus
    success: bool
    data: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    confidence: Optional[float] = None
    execution_time: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None


class BaseAgent:
    """Base class for all AI agents."""
    
    def __init__(
        self,
        agent_type: str,
        model_name: str = "gpt-4-turbo-preview",
        max_retries: int = 3,
        timeout_seconds: int = 300
    ):
        """
        Initialize the base agent.
        
        Args:
            agent_type: Type identifier for the agent
            model_name: Name of the AI model to use
            max_retries: Maximum number of retry attempts
            timeout_seconds: Timeout for operations in seconds
        """
        self.agent_type = agent_type
        self.model_name = model_name
        self.max_retries = max_retries
        self.timeout_seconds = timeout_seconds
        self.status = AgentStatus.IDLE
        self.created_at = datetime.utcnow()
        self.last_execution = None
    
    def get_status(self) -> AgentStatus:
        """Get the current status of the agent."""
        return self.status
    
    def get_agent_info(self) -> Dict[str, Any]:
        """Get information about the agent."""
        return {
            "agent_type": self.agent_type,
            "status": self.status,
            "model_name": self.model_name,
            "max_retries": self.max_retries,
            "timeout_seconds": self.timeout_seconds,
            "created_at": self.created_at.isoformat(),
            "last_execution": self.last_execution.isoformat() if self.last_execution else None
        }
    
    def _set_status(self, status: AgentStatus):
        """Set the agent status."""
        self.status = status
    
    def _create_result(
        self,
        status: AgentStatus,
        success: bool,
        data: Optional[Dict[str, Any]] = None,
        error_message: Optional[str] = None,
        confidence: Optional[float] = None,
        execution_time: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> AgentResult:
        """Create an AgentResult object."""
        return AgentResult(
            status=status,
            success=success,
            data=data,
            error_message=error_message,
            confidence=confidence,
            execution_time=execution_time,
            metadata=metadata
        )
    
    def _validate_input(self, input_data: Any, input_name: str = "input") -> bool:
        """Validate input data."""
        if input_data is None:
            raise ValueError(f"{input_name} cannot be None")
        
        if isinstance(input_data, str) and not input_data.strip():
            raise ValueError(f"{input_name} cannot be empty")
        
        return True
    
    def _parse_json_response(self, response_text: str) -> Dict[str, Any]:
        """Parse JSON response from AI model."""
        try:
            return json.loads(response_text)
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse JSON response: {str(e)}")
    
    def _format_timestamp(self) -> str:
        """Get current timestamp as ISO string."""
        return datetime.utcnow().isoformat()
    
    def _calculate_execution_time(self, start_time: datetime) -> float:
        """Calculate execution time in seconds."""
        return (datetime.utcnow() - start_time).total_seconds()
    
    def _retry_operation(self, operation, *args, **kwargs):
        """Retry an operation with exponential backoff."""
        last_exception = None
        
        for attempt in range(self.max_retries + 1):
            try:
                return operation(*args, **kwargs)
            except Exception as e:
                last_exception = e
                if attempt < self.max_retries:
                    # Exponential backoff: wait 2^attempt seconds
                    import time
                    time.sleep(2 ** attempt)
                    continue
                else:
                    break
        
        raise last_exception