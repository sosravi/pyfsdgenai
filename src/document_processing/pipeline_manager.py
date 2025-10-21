"""
Pipeline Manager

This module implements the PipelineManager class for orchestrating document
processing workflows with AI agents.
"""

import uuid
import time
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

from src.agents.base_agent import BaseAgent, AgentResult, AgentStatus
from src.agents.pricing_extraction_agent import PricingExtractionAgent
from src.agents.terms_extraction_agent import TermsExtractionAgent
from src.agents.risk_assessment_agent import RiskAssessmentAgent

logger = logging.getLogger(__name__)


class PipelineManager:
    """Manages document processing pipelines with AI agents."""
    
    def __init__(self, max_concurrent_pipelines: int = 5):
        """
        Initialize PipelineManager.
        
        Args:
            max_concurrent_pipelines: Maximum number of concurrent pipelines
        """
        self.status = "idle"
        self.max_concurrent_pipelines = max_concurrent_pipelines
        self.pipelines = {}  # Store pipeline information
        self.executor = ThreadPoolExecutor(max_workers=max_concurrent_pipelines)
        
        # Initialize available agents
        self.available_agents = {
            "pricing": PricingExtractionAgent(),
            "terms": TermsExtractionAgent(),
            "risk": RiskAssessmentAgent()
        }
        
        logger.info(f"PipelineManager initialized with {len(self.available_agents)} agents")
    
    def start_processing(self, document_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Start document processing pipeline.
        
        Args:
            document_data: Document data including text content and metadata
            
        Returns:
            Dict containing pipeline start result
        """
        try:
            # Validate input data
            if not self._validate_document_data(document_data):
                return {
                    "success": False,
                    "error": "Invalid document data. Required fields: document_id, text_content"
                }
            
            # Generate pipeline ID
            pipeline_id = f"pipeline_{uuid.uuid4().hex[:8]}"
            
            # Initialize pipeline
            pipeline_info = {
                "pipeline_id": pipeline_id,
                "document_id": document_data["document_id"],
                "status": "processing",
                "progress": 0,
                "started_at": datetime.utcnow().isoformat() + "Z",
                "completed_at": None,
                "results": {},
                "errors": [],
                "agents_completed": 0,
                "total_agents": len(self.available_agents)
            }
            
            self.pipelines[pipeline_id] = pipeline_info
            
            # Start processing in background
            self.executor.submit(self._process_document, pipeline_id, document_data)
            
            logger.info(f"Pipeline started: {pipeline_id}")
            
            return {
                "success": True,
                "pipeline_id": pipeline_id,
                "status": "processing",
                "estimated_completion": self._estimate_completion_time()
            }
            
        except Exception as e:
            logger.error(f"Error starting pipeline: {str(e)}")
            return {
                "success": False,
                "error": f"Failed to start pipeline: {str(e)}"
            }
    
    def get_processing_status(self, pipeline_id: str) -> Dict[str, Any]:
        """
        Get processing status for a pipeline.
        
        Args:
            pipeline_id: ID of the pipeline
            
        Returns:
            Dict containing pipeline status
        """
        try:
            if pipeline_id not in self.pipelines:
                return {
                    "success": False,
                    "error": "Pipeline not found"
                }
            
            pipeline_info = self.pipelines[pipeline_id]
            
            return {
                "success": True,
                "pipeline_id": pipeline_id,
                "status": pipeline_info["status"],
                "progress": pipeline_info["progress"],
                "agents_completed": pipeline_info["agents_completed"],
                "total_agents": pipeline_info["total_agents"],
                "started_at": pipeline_info["started_at"],
                "completed_at": pipeline_info["completed_at"],
                "estimated_completion": self._estimate_completion_time()
            }
            
        except Exception as e:
            logger.error(f"Error getting pipeline status: {str(e)}")
            return {
                "success": False,
                "error": f"Failed to get pipeline status: {str(e)}"
            }
    
    def get_processing_results(self, pipeline_id: str) -> Dict[str, Any]:
        """
        Get processing results for a pipeline.
        
        Args:
            pipeline_id: ID of the pipeline
            
        Returns:
            Dict containing pipeline results
        """
        try:
            if pipeline_id not in self.pipelines:
                return {
                    "success": False,
                    "error": "Pipeline not found"
                }
            
            pipeline_info = self.pipelines[pipeline_id]
            
            if pipeline_info["status"] != "completed":
                return {
                    "success": False,
                    "error": "Pipeline not completed yet"
                }
            
            return {
                "success": True,
                "pipeline_id": pipeline_id,
                "results": pipeline_info["results"],
                "processing_time": self._calculate_processing_time(pipeline_info),
                "completed_at": pipeline_info["completed_at"]
            }
            
        except Exception as e:
            logger.error(f"Error getting pipeline results: {str(e)}")
            return {
                "success": False,
                "error": f"Failed to get pipeline results: {str(e)}"
            }
    
    def cancel_processing(self, pipeline_id: str) -> Dict[str, Any]:
        """
        Cancel a processing pipeline.
        
        Args:
            pipeline_id: ID of the pipeline to cancel
            
        Returns:
            Dict containing cancellation result
        """
        try:
            if pipeline_id not in self.pipelines:
                return {
                    "success": False,
                    "error": "Pipeline not found"
                }
            
            pipeline_info = self.pipelines[pipeline_id]
            
            if pipeline_info["status"] == "completed":
                return {
                    "success": False,
                    "error": "Pipeline already completed"
                }
            
            pipeline_info["status"] = "cancelled"
            pipeline_info["completed_at"] = datetime.utcnow().isoformat() + "Z"
            
            logger.info(f"Pipeline cancelled: {pipeline_id}")
            
            return {
                "success": True,
                "message": "Processing canceled successfully"
            }
            
        except Exception as e:
            logger.error(f"Error cancelling pipeline: {str(e)}")
            return {
                "success": False,
                "error": f"Failed to cancel pipeline: {str(e)}"
            }
    
    def list_pipelines(self, status: Optional[str] = None) -> Dict[str, Any]:
        """
        List all pipelines with optional status filtering.
        
        Args:
            status: Optional status filter
            
        Returns:
            Dict containing list of pipelines
        """
        try:
            pipelines = list(self.pipelines.values())
            
            # Apply status filter
            if status:
                pipelines = [p for p in pipelines if p["status"] == status]
            
            # Format response
            formatted_pipelines = []
            for pipeline in pipelines:
                formatted_pipelines.append({
                    "pipeline_id": pipeline["pipeline_id"],
                    "document_id": pipeline["document_id"],
                    "status": pipeline["status"],
                    "progress": pipeline["progress"],
                    "agents_completed": pipeline["agents_completed"],
                    "total_agents": pipeline["total_agents"],
                    "started_at": pipeline["started_at"],
                    "completed_at": pipeline["completed_at"]
                })
            
            return {
                "success": True,
                "pipelines": formatted_pipelines,
                "total": len(formatted_pipelines)
            }
            
        except Exception as e:
            logger.error(f"Error listing pipelines: {str(e)}")
            return {
                "success": False,
                "error": f"Failed to list pipelines: {str(e)}"
            }
    
    def _process_document(self, pipeline_id: str, document_data: Dict[str, Any]):
        """
        Process document with AI agents (runs in background).
        
        Args:
            pipeline_id: ID of the pipeline
            document_data: Document data to process
        """
        try:
            pipeline_info = self.pipelines[pipeline_id]
            text_content = document_data["text_content"]
            
            # Process with each agent
            agent_results = {}
            total_agents = len(self.available_agents)
            
            for i, (agent_name, agent) in enumerate(self.available_agents.items()):
                try:
                    # Update progress
                    pipeline_info["progress"] = int((i / total_agents) * 100)
                    
                    # Execute agent
                    agent_input = {"text": text_content}
                    result = agent.execute(agent_input)
                    
                    if result.success:
                        agent_results[agent_name] = result.data
                    else:
                        pipeline_info["errors"].append({
                            "agent": agent_name,
                            "error": result.error_message or "Agent execution failed"
                        })
                    
                    pipeline_info["agents_completed"] = i + 1
                    
                except Exception as e:
                    logger.error(f"Error executing agent {agent_name}: {str(e)}")
                    pipeline_info["errors"].append({
                        "agent": agent_name,
                        "error": str(e)
                    })
            
            # Update pipeline status
            pipeline_info["status"] = "completed"
            pipeline_info["progress"] = 100
            pipeline_info["completed_at"] = datetime.utcnow().isoformat() + "Z"
            pipeline_info["results"] = agent_results
            
            logger.info(f"Pipeline completed: {pipeline_id}")
            
        except Exception as e:
            logger.error(f"Error processing document: {str(e)}")
            pipeline_info["status"] = "failed"
            pipeline_info["completed_at"] = datetime.utcnow().isoformat() + "Z"
            pipeline_info["errors"].append({
                "error": f"Pipeline processing failed: {str(e)}"
            })
    
    def _validate_document_data(self, document_data: Dict[str, Any]) -> bool:
        """
        Validate document data structure.
        
        Args:
            document_data: Document data to validate
            
        Returns:
            True if valid, False otherwise
        """
        required_fields = ["document_id", "text_content"]
        return all(field in document_data for field in required_fields)
    
    def _estimate_completion_time(self) -> str:
        """
        Estimate completion time for processing.
        
        Returns:
            ISO formatted estimated completion time
        """
        # Simple estimation: 2 minutes from now
        estimated_time = datetime.utcnow().timestamp() + 120
        return datetime.fromtimestamp(estimated_time).isoformat() + "Z"
    
    def _calculate_processing_time(self, pipeline_info: Dict[str, Any]) -> float:
        """
        Calculate total processing time for a pipeline.
        
        Args:
            pipeline_info: Pipeline information
            
        Returns:
            Processing time in seconds
        """
        try:
            started_at = datetime.fromisoformat(pipeline_info["started_at"].replace("Z", ""))
            completed_at = datetime.fromisoformat(pipeline_info["completed_at"].replace("Z", ""))
            return (completed_at - started_at).total_seconds()
        except Exception:
            return 0.0
    
    def get_agent_status(self, agent_name: str) -> Optional[Dict[str, Any]]:
        """
        Get status of a specific agent.
        
        Args:
            agent_name: Name of the agent
            
        Returns:
            Agent status dict, or None if not found
        """
        if agent_name not in self.available_agents:
            return None
        
        return self.available_agents[agent_name].get_status()
    
    def get_all_agent_status(self) -> Dict[str, Any]:
        """
        Get status of all available agents.
        
        Returns:
            Dict containing status of all agents
        """
        agent_status = {}
        for name, agent in self.available_agents.items():
            agent_status[name] = agent.get_status()
        
        return {
            "success": True,
            "agents": agent_status,
            "total_agents": len(self.available_agents)
        }
    
    def shutdown(self):
        """Shutdown the pipeline manager and cleanup resources."""
        try:
            self.executor.shutdown(wait=True)
            logger.info("PipelineManager shutdown completed")
        except Exception as e:
            logger.error(f"Error during shutdown: {str(e)}")
