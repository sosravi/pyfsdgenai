"""
PyFSD GenAI - Base Agent Class

This module defines the base agent class that all specialized AI agents
will inherit from, providing common functionality and interfaces.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging
import asyncio
from enum import Enum


class AgentStatus(Enum):
    """Agent execution status."""
    IDLE = "idle"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"


class BaseAgent(ABC):
    """
    Base class for all AI agents in the PyFSD GenAI system.
    
    This class provides common functionality and defines the interface
    that all specialized agents must implement.
    """
    
    def __init__(self, agent_id: str, agent_name: str, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the base agent.
        
        Args:
            agent_id: Unique identifier for the agent
            agent_name: Human-readable name for the agent
            config: Optional configuration dictionary
        """
        self.agent_id = agent_id
        self.agent_name = agent_name
        self.config = config or {}
        self.status = AgentStatus.IDLE
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None
        self.logger = logging.getLogger(f"agent.{agent_id}")
        
    @abstractmethod
    async def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process the input data and return results.
        
        Args:
            data: Input data dictionary containing contract/document information
            
        Returns:
            Dictionary containing processed results
            
        Raises:
            AgentProcessingError: If processing fails
        """
        pass
    
    @abstractmethod
    def validate_input(self, data: Dict[str, Any]) -> bool:
        """
        Validate input data before processing.
        
        Args:
            data: Input data to validate
            
        Returns:
            True if data is valid, False otherwise
        """
        pass
    
    @abstractmethod
    def extract_key_information(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract key information from the processed data.
        
        Args:
            data: Processed data dictionary
            
        Returns:
            Dictionary containing extracted key information
        """
        pass
    
    async def execute(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the agent processing workflow.
        
        Args:
            data: Input data for processing
            
        Returns:
            Dictionary containing processing results
        """
        try:
            # Validate input
            if not self.validate_input(data):
                raise ValueError("Invalid input data")
            
            # Update status
            self.status = AgentStatus.PROCESSING
            self.start_time = datetime.utcnow()
            
            # Process data
            result = await self.process(data)
            
            # Extract key information
            key_info = self.extract_key_information(result)
            
            # Update status
            self.status = AgentStatus.COMPLETED
            self.end_time = datetime.utcnow()
            
            # Log completion
            self.logger.info(f"Agent {self.agent_id} completed successfully")
            
            return {
                "agent_id": self.agent_id,
                "agent_name": self.agent_name,
                "status": self.status.value,
                "result": result,
                "key_information": key_info,
                "processing_time": self.get_processing_time(),
                "timestamp": self.end_time.isoformat()
            }
            
        except Exception as e:
            self.status = AgentStatus.FAILED
            self.end_time = datetime.utcnow()
            self.logger.error(f"Agent {self.agent_id} failed: {str(e)}")
            
            return {
                "agent_id": self.agent_id,
                "agent_name": self.agent_name,
                "status": self.status.value,
                "error": str(e),
                "processing_time": self.get_processing_time(),
                "timestamp": self.end_time.isoformat()
            }
    
    def get_processing_time(self) -> Optional[float]:
        """Get processing time in seconds."""
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return None
    
    def get_status(self) -> Dict[str, Any]:
        """Get current agent status."""
        return {
            "agent_id": self.agent_id,
            "agent_name": self.agent_name,
            "status": self.status.value,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "processing_time": self.get_processing_time()
        }
    
    def reset(self):
        """Reset agent state."""
        self.status = AgentStatus.IDLE
        self.start_time = None
        self.end_time = None


class AgentProcessingError(Exception):
    """Custom exception for agent processing errors."""
    pass


class AgentTimeoutError(Exception):
    """Custom exception for agent timeout errors."""
    pass
