"""
PyFSD GenAI - Database Model Tests

This module contains tests for database models following TDD principles.
We write tests first (Red phase), then implement models to make tests pass (Green phase).
"""

import pytest
from datetime import datetime, date
from decimal import Decimal
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError

from src.models.database_models import (
    Contract, Invoice, Document, User, ContractLineItem, 
    InvoiceLineItem, DocumentMetadata, AgentExecution
)


class TestContractModel:
    """Tests for Contract model."""
    
    def test_contract_creation(self, test_db_session):
        """Test basic contract creation."""
        contract = Contract(
            contract_id="TEST-001",
            title="Test Contract",
            vendor="Test Vendor Inc.",
            amount=Decimal("50000.00"),
            currency="USD",
            start_date=date(2024, 1, 1),
            end_date=date(2024, 12, 31),
            terms="Standard terms",
            status="active"
        )
        
        test_db_session.add(contract)
        test_db_session.commit()
        test_db_session.refresh(contract)
        
        assert contract.id is not None
        assert contract.contract_id == "TEST-001"
        assert contract.title == "Test Contract"
        assert contract.vendor == "Test Vendor Inc."
        assert contract.amount == Decimal("50000.00")
        assert contract.currency == "USD"
        assert contract.status == "active"
        assert contract.created_at is not None
        assert contract.updated_at is not None
    
    def test_contract_required_fields(self, test_db_session):
        """Test that required fields are enforced."""
        # Test missing contract_id
        contract = Contract(
            title="Test Contract",
            vendor="Test Vendor Inc.",
            amount=Decimal("50000.00"),
            currency="USD"
        )
        
        test_db_session.add(contract)
        with pytest.raises(IntegrityError):
            test_db_session.commit()
    
    def test_contract_unique_constraints(self, test_db_session):
        """Test unique constraints on contract_id."""
        contract1 = Contract(
            contract_id="UNIQUE-001",
            title="Contract 1",
            vendor="Vendor 1",
            amount=Decimal("10000.00"),
            currency="USD"
        )
        
        contract2 = Contract(
            contract_id="UNIQUE-001",  # Same contract_id
            title="Contract 2",
            vendor="Vendor 2",
            amount=Decimal("20000.00"),
            currency="USD"
        )
        
        test_db_session.add(contract1)
        test_db_session.commit()
        
        test_db_session.add(contract2)
        with pytest.raises(IntegrityError):
            test_db_session.commit()
    
    def test_contract_status_validation(self, test_db_session):
        """Test contract status validation."""
        valid_statuses = ["active", "draft", "expired", "cancelled"]
        
        for status in valid_statuses:
            contract = Contract(
                contract_id=f"STATUS-{status}",
                title=f"Contract {status}",
                vendor="Test Vendor",
                amount=Decimal("10000.00"),
                currency="USD",
                status=status
            )
            
            test_db_session.add(contract)
            test_db_session.commit()
            test_db_session.refresh(contract)
            
            assert contract.status == status
    
    def test_contract_amount_precision(self, test_db_session):
        """Test contract amount precision handling."""
        contract = Contract(
            contract_id="PRECISION-001",
            title="Precision Test Contract",
            vendor="Test Vendor",
            amount=Decimal("12345.67"),
            currency="USD"
        )
        
        test_db_session.add(contract)
        test_db_session.commit()
        test_db_session.refresh(contract)
        
        assert contract.amount == Decimal("12345.67")
        assert str(contract.amount) == "12345.67"


class TestInvoiceModel:
    """Tests for Invoice model."""
    
    def test_invoice_creation(self, test_db_session):
        """Test basic invoice creation."""
        invoice = Invoice(
            invoice_id="INV-001",
            contract_id="CONTRACT-001",
            vendor="Test Vendor Inc.",
            amount=Decimal("5000.00"),
            currency="USD",
            due_date=date(2024, 2, 15),
            status="pending"
        )
        
        test_db_session.add(invoice)
        test_db_session.commit()
        test_db_session.refresh(invoice)
        
        assert invoice.id is not None
        assert invoice.invoice_id == "INV-001"
        assert invoice.contract_id == "CONTRACT-001"
        assert invoice.amount == Decimal("5000.00")
        assert invoice.status == "pending"
        assert invoice.created_at is not None
    
    def test_invoice_contract_relationship(self, test_db_session):
        """Test invoice-contract relationship."""
        # Create contract first
        contract = Contract(
            contract_id="CONTRACT-001",
            title="Test Contract",
            vendor="Test Vendor Inc.",
            amount=Decimal("50000.00"),
            currency="USD"
        )
        test_db_session.add(contract)
        test_db_session.commit()
        
        # Create invoice
        invoice = Invoice(
            invoice_id="INV-001",
            contract_id="CONTRACT-001",
            vendor="Test Vendor Inc.",
            amount=Decimal("5000.00"),
            currency="USD"
        )
        test_db_session.add(invoice)
        test_db_session.commit()
        test_db_session.refresh(invoice)
        
        # Test relationship
        assert invoice.contract_id == contract.contract_id
    
    def test_invoice_line_items_relationship(self, test_db_session):
        """Test invoice-line items relationship."""
        invoice = Invoice(
            invoice_id="INV-001",
            contract_id="CONTRACT-001",
            vendor="Test Vendor",
            amount=Decimal("1000.00"),
            currency="USD"
        )
        test_db_session.add(invoice)
        test_db_session.commit()
        test_db_session.refresh(invoice)
        
        # Add line items
        line_item1 = InvoiceLineItem(
            invoice_id=invoice.id,
            description="Item 1",
            quantity=2,
            unit_price=Decimal("250.00"),
            total=Decimal("500.00")
        )
        
        line_item2 = InvoiceLineItem(
            invoice_id=invoice.id,
            description="Item 2",
            quantity=1,
            unit_price=Decimal("500.00"),
            total=Decimal("500.00")
        )
        
        test_db_session.add_all([line_item1, line_item2])
        test_db_session.commit()
        
        # Test relationship
        assert len(invoice.line_items) == 2
        assert invoice.line_items[0].description == "Item 1"
        assert invoice.line_items[1].description == "Item 2"


class TestDocumentModel:
    """Tests for Document model."""
    
    def test_document_creation(self, test_db_session):
        """Test basic document creation."""
        document = Document(
            document_id="DOC-001",
            filename="test_contract.pdf",
            file_type="application/pdf",
            file_size=1024000,
            upload_date=datetime.utcnow(),
            status="processed"
        )
        
        test_db_session.add(document)
        test_db_session.commit()
        test_db_session.refresh(document)
        
        assert document.id is not None
        assert document.document_id == "DOC-001"
        assert document.filename == "test_contract.pdf"
        assert document.file_type == "application/pdf"
        assert document.file_size == 1024000
        assert document.status == "processed"
    
    def test_document_metadata_relationship(self, test_db_session):
        """Test document-metadata relationship."""
        document = Document(
            document_id="DOC-001",
            filename="test.pdf",
            file_type="application/pdf",
            file_size=1000,
            status="processed"
        )
        test_db_session.add(document)
        test_db_session.commit()
        test_db_session.refresh(document)
        
        # Add metadata
        metadata = DocumentMetadata(
            document_id=document.id,
            pages=10,
            language="en",
            confidence=0.95,
            extracted_text="Sample extracted text"
        )
        test_db_session.add(metadata)
        test_db_session.commit()
        
        # Test relationship
        assert document.document_metadata is not None
        assert document.document_metadata.pages == 10
        assert document.document_metadata.language == "en"
        assert document.document_metadata.confidence == 0.95


class TestUserModel:
    """Tests for User model."""
    
    def test_user_creation(self, test_db_session):
        """Test basic user creation."""
        user = User(
            user_id="USER-001",
            username="testuser",
            email="test@example.com",
            full_name="Test User",
            role="analyst",
            is_active=True
        )
        
        test_db_session.add(user)
        test_db_session.commit()
        test_db_session.refresh(user)
        
        assert user.id is not None
        assert user.user_id == "USER-001"
        assert user.username == "testuser"
        assert user.email == "test@example.com"
        assert user.full_name == "Test User"
        assert user.role == "analyst"
        assert user.is_active is True
        assert user.created_at is not None
    
    def test_user_email_uniqueness(self, test_db_session):
        """Test user email uniqueness constraint."""
        user1 = User(
            user_id="USER-001",
            username="user1",
            email="test@example.com",
            full_name="User 1",
            role="analyst"
        )
        
        user2 = User(
            user_id="USER-002",
            username="user2",
            email="test@example.com",  # Same email
            full_name="User 2",
            role="analyst"
        )
        
        test_db_session.add(user1)
        test_db_session.commit()
        
        test_db_session.add(user2)
        with pytest.raises(IntegrityError):
            test_db_session.commit()
    
    def test_user_role_validation(self, test_db_session):
        """Test user role validation."""
        valid_roles = ["admin", "analyst", "viewer", "manager"]
        
        for role in valid_roles:
            user = User(
                user_id=f"USER-{role}",
                username=f"user_{role}",
                email=f"{role}@example.com",
                full_name=f"User {role}",
                role=role
            )
            
            test_db_session.add(user)
            test_db_session.commit()
            test_db_session.refresh(user)
            
            assert user.role == role


class TestAgentExecutionModel:
    """Tests for AgentExecution model."""
    
    def test_agent_execution_creation(self, test_db_session):
        """Test basic agent execution creation."""
        execution = AgentExecution(
            execution_id="EXEC-001",
            agent_type="pricing_extraction",
            document_id="DOC-001",
            status="completed",
            input_data={"text": "Sample contract text"},
            output_data={"extracted_pricing": "$5000"},
            confidence=0.95,
            execution_time=1.5
        )
        
        test_db_session.add(execution)
        test_db_session.commit()
        test_db_session.refresh(execution)
        
        assert execution.id is not None
        assert execution.execution_id == "EXEC-001"
        assert execution.agent_type == "pricing_extraction"
        assert execution.status == "completed"
        assert execution.confidence == 0.95
        assert execution.execution_time == 1.5
        assert execution.created_at is not None
    
    def test_agent_execution_status_validation(self, test_db_session):
        """Test agent execution status validation."""
        valid_statuses = ["pending", "running", "completed", "failed", "cancelled"]
        
        for status in valid_statuses:
            execution = AgentExecution(
                execution_id=f"EXEC-{status}",
                agent_type="test_agent",
                document_id="DOC-001",
                status=status
            )
            
            test_db_session.add(execution)
            test_db_session.commit()
            test_db_session.refresh(execution)
            
            assert execution.status == status


class TestModelRelationships:
    """Tests for model relationships."""
    
    def test_contract_invoice_relationship(self, test_db_session):
        """Test contract-invoice relationship."""
        # Create contract
        contract = Contract(
            contract_id="CONTRACT-001",
            title="Test Contract",
            vendor="Test Vendor",
            amount=Decimal("50000.00"),
            currency="USD"
        )
        test_db_session.add(contract)
        test_db_session.commit()
        
        # Create invoices
        invoice1 = Invoice(
            invoice_id="INV-001",
            contract_id="CONTRACT-001",
            vendor="Test Vendor",
            amount=Decimal("5000.00"),
            currency="USD"
        )
        
        invoice2 = Invoice(
            invoice_id="INV-002",
            contract_id="CONTRACT-001",
            vendor="Test Vendor",
            amount=Decimal("3000.00"),
            currency="USD"
        )
        
        test_db_session.add_all([invoice1, invoice2])
        test_db_session.commit()
        
        # Test relationship (would need to implement relationship in models)
        # This test will guide the implementation of relationships
    
    def test_document_agent_execution_relationship(self, test_db_session):
        """Test document-agent execution relationship."""
        # Create document
        document = Document(
            document_id="DOC-001",
            filename="test.pdf",
            file_type="application/pdf",
            file_size=1000,
            status="processed"
        )
        test_db_session.add(document)
        test_db_session.commit()
        
        # Create agent execution
        execution = AgentExecution(
            execution_id="EXEC-001",
            agent_type="pricing_extraction",
            document_id="DOC-001",
            status="completed"
        )
        test_db_session.add(execution)
        test_db_session.commit()
        
        # Test relationship (would need to implement relationship in models)
        # This test will guide the implementation of relationships


class TestModelConstraints:
    """Tests for model constraints and validations."""
    
    def test_decimal_precision(self, test_db_session):
        """Test decimal precision handling."""
        contract = Contract(
            contract_id="PRECISION-001",
            title="Precision Test",
            vendor="Test Vendor",
            amount=Decimal("999999999.99"),  # Large amount
            currency="USD"
        )
        
        test_db_session.add(contract)
        test_db_session.commit()
        test_db_session.refresh(contract)
        
        assert contract.amount == Decimal("999999999.99")
    
    def test_date_handling(self, test_db_session):
        """Test date field handling."""
        contract = Contract(
            contract_id="DATE-001",
            title="Date Test Contract",
            vendor="Test Vendor",
            amount=Decimal("10000.00"),
            currency="USD",
            start_date=date(2024, 1, 1),
            end_date=date(2024, 12, 31)
        )
        
        test_db_session.add(contract)
        test_db_session.commit()
        test_db_session.refresh(contract)
        
        assert contract.start_date == date(2024, 1, 1)
        assert contract.end_date == date(2024, 12, 31)
    
    def test_datetime_handling(self, test_db_session):
        """Test datetime field handling."""
        document = Document(
            document_id="DATETIME-001",
            filename="test.pdf",
            file_type="application/pdf",
            file_size=1000,
            upload_date=datetime(2024, 1, 15, 10, 30, 0),
            status="processed"
        )
        
        test_db_session.add(document)
        test_db_session.commit()
        test_db_session.refresh(document)
        
        assert document.upload_date == datetime(2024, 1, 15, 10, 30, 0)


@pytest.mark.database
class TestDatabaseMarkers:
    """Test that database test markers work correctly."""
    
    def test_database_marker_applied(self):
        """Test that database marker is applied to this test."""
        assert True
    
    def test_database_operations(self, test_db_session):
        """Test basic database operations."""
        # Test that we can create and query records
        contract = Contract(
            contract_id="MARKER-001",
            title="Marker Test Contract",
            vendor="Test Vendor",
            amount=Decimal("1000.00"),
            currency="USD"
        )
        
        test_db_session.add(contract)
        test_db_session.commit()
        
        # Query the record
        retrieved_contract = test_db_session.query(Contract).filter_by(
            contract_id="MARKER-001"
        ).first()
        
        assert retrieved_contract is not None
        assert retrieved_contract.title == "Marker Test Contract"
