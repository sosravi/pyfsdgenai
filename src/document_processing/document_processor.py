"""
Document Processor

This module implements the DocumentProcessor class for handling document uploads,
storage, and basic document management operations.
"""

import os
import uuid
import shutil
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class DocumentProcessor:
    """Handles document upload, storage, and basic management operations."""
    
    def __init__(self, storage_path: str = "documents", max_file_size: int = 100 * 1024 * 1024):
        """
        Initialize DocumentProcessor.
        
        Args:
            storage_path: Path to store uploaded documents
            max_file_size: Maximum file size in bytes (default: 100MB)
        """
        self.storage_path = Path(storage_path)
        self.max_file_size = max_file_size
        self.supported_formats = ["pdf", "doc", "docx", "txt"]
        self.status = "idle"
        self.documents = {}  # In-memory storage for demo
        
        # Create storage directory if it doesn't exist
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"DocumentProcessor initialized with storage path: {self.storage_path}")
    
    def upload_document(self, file_path: str, document_type: str, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Upload a document for processing.
        
        Args:
            file_path: Path to the document file
            document_type: Type of document (contract, invoice, etc.)
            metadata: Optional metadata for the document
            
        Returns:
            Dict containing upload result
        """
        try:
            file_path = Path(file_path)
            
            # Validate file exists
            if not file_path.exists():
                return {
                    "success": False,
                    "error": "File does not exist"
                }
            
            # Validate file format
            file_extension = file_path.suffix.lower().lstrip('.')
            if file_extension not in self.supported_formats:
                return {
                    "success": False,
                    "error": f"Unsupported file format: {file_extension}. Supported formats: {', '.join(self.supported_formats)}"
                }
            
            # Validate file size
            file_size = file_path.stat().st_size
            if file_size > self.max_file_size:
                return {
                    "success": False,
                    "error": f"File too large: {file_size} bytes. Maximum allowed: {self.max_file_size} bytes"
                }
            
            # Generate unique document ID
            document_id = f"doc_{uuid.uuid4().hex[:8]}"
            
            # Create document storage directory
            doc_storage_path = self.storage_path / document_id
            doc_storage_path.mkdir(exist_ok=True)
            
            # Copy file to storage
            stored_file_path = doc_storage_path / f"{document_id}.{file_extension}"
            shutil.copy2(file_path, stored_file_path)
            
            # Store document metadata
            document_info = {
                "document_id": document_id,
                "original_filename": file_path.name,
                "stored_path": str(stored_file_path),
                "file_size": file_size,
                "file_format": file_extension,
                "document_type": document_type,
                "metadata": metadata or {},
                "status": "uploaded",
                "created_at": datetime.utcnow().isoformat() + "Z",
                "updated_at": datetime.utcnow().isoformat() + "Z"
            }
            
            self.documents[document_id] = document_info
            
            logger.info(f"Document uploaded successfully: {document_id}")
            
            return {
                "success": True,
                "document_id": document_id,
                "status": "uploaded",
                "file_size": file_size,
                "file_format": file_extension,
                "created_at": document_info["created_at"]
            }
            
        except Exception as e:
            logger.error(f"Error uploading document: {str(e)}")
            return {
                "success": False,
                "error": f"Upload failed: {str(e)}"
            }
    
    def get_document_status(self, document_id: str) -> Dict[str, Any]:
        """
        Get the status of a document.
        
        Args:
            document_id: ID of the document
            
        Returns:
            Dict containing document status
        """
        try:
            if document_id not in self.documents:
                return {
                    "success": False,
                    "error": "Document not found"
                }
            
            document_info = self.documents[document_id]
            
            return {
                "success": True,
                "document_id": document_id,
                "status": document_info["status"],
                "created_at": document_info["created_at"],
                "updated_at": document_info["updated_at"],
                "file_size": document_info["file_size"],
                "file_format": document_info["file_format"],
                "document_type": document_info["document_type"]
            }
            
        except Exception as e:
            logger.error(f"Error getting document status: {str(e)}")
            return {
                "success": False,
                "error": f"Failed to get document status: {str(e)}"
            }
    
    def delete_document(self, document_id: str) -> Dict[str, Any]:
        """
        Delete a document.
        
        Args:
            document_id: ID of the document to delete
            
        Returns:
            Dict containing deletion result
        """
        try:
            if document_id not in self.documents:
                return {
                    "success": False,
                    "error": "Document not found"
                }
            
            document_info = self.documents[document_id]
            
            # Delete stored file
            stored_path = Path(document_info["stored_path"])
            if stored_path.exists():
                stored_path.unlink()
            
            # Delete document directory
            doc_storage_path = self.storage_path / document_id
            if doc_storage_path.exists():
                shutil.rmtree(doc_storage_path)
            
            # Remove from memory
            del self.documents[document_id]
            
            logger.info(f"Document deleted successfully: {document_id}")
            
            return {
                "success": True,
                "message": "Document deleted successfully"
            }
            
        except Exception as e:
            logger.error(f"Error deleting document: {str(e)}")
            return {
                "success": False,
                "error": f"Failed to delete document: {str(e)}"
            }
    
    def list_documents(self, document_type: Optional[str] = None, status: Optional[str] = None) -> Dict[str, Any]:
        """
        List all documents with optional filtering.
        
        Args:
            document_type: Filter by document type
            status: Filter by document status
            
        Returns:
            Dict containing list of documents
        """
        try:
            documents = list(self.documents.values())
            
            # Apply filters
            if document_type:
                documents = [doc for doc in documents if doc["document_type"] == document_type]
            
            if status:
                documents = [doc for doc in documents if doc["status"] == status]
            
            # Format response
            formatted_documents = []
            for doc in documents:
                formatted_documents.append({
                    "document_id": doc["document_id"],
                    "original_filename": doc["original_filename"],
                    "document_type": doc["document_type"],
                    "status": doc["status"],
                    "file_size": doc["file_size"],
                    "file_format": doc["file_format"],
                    "created_at": doc["created_at"],
                    "updated_at": doc["updated_at"]
                })
            
            return {
                "success": True,
                "documents": formatted_documents,
                "total": len(formatted_documents)
            }
            
        except Exception as e:
            logger.error(f"Error listing documents: {str(e)}")
            return {
                "success": False,
                "error": f"Failed to list documents: {str(e)}"
            }
    
    def get_document_path(self, document_id: str) -> Optional[str]:
        """
        Get the storage path of a document.
        
        Args:
            document_id: ID of the document
            
        Returns:
            Path to the stored document file, or None if not found
        """
        if document_id not in self.documents:
            return None
        
        document_info = self.documents[document_id]
        stored_path = Path(document_info["stored_path"])
        
        if stored_path.exists():
            return str(stored_path)
        
        return None
    
    def update_document_status(self, document_id: str, status: str) -> bool:
        """
        Update the status of a document.
        
        Args:
            document_id: ID of the document
            status: New status
            
        Returns:
            True if updated successfully, False otherwise
        """
        try:
            if document_id not in self.documents:
                return False
            
            self.documents[document_id]["status"] = status
            self.documents[document_id]["updated_at"] = datetime.utcnow().isoformat() + "Z"
            
            logger.info(f"Document status updated: {document_id} -> {status}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating document status: {str(e)}")
            return False
    
    def get_document_metadata(self, document_id: str) -> Optional[Dict[str, Any]]:
        """
        Get metadata for a document.
        
        Args:
            document_id: ID of the document
            
        Returns:
            Document metadata, or None if not found
        """
        if document_id not in self.documents:
            return None
        
        return self.documents[document_id]["metadata"]
    
    def add_document_metadata(self, document_id: str, metadata: Dict[str, Any]) -> bool:
        """
        Add metadata to a document.
        
        Args:
            document_id: ID of the document
            metadata: Metadata to add
            
        Returns:
            True if added successfully, False otherwise
        """
        try:
            if document_id not in self.documents:
                return False
            
            self.documents[document_id]["metadata"].update(metadata)
            self.documents[document_id]["updated_at"] = datetime.utcnow().isoformat() + "Z"
            
            logger.info(f"Document metadata updated: {document_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding document metadata: {str(e)}")
            return False
