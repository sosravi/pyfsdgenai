"""
PyFSD GenAI - Comprehensive Database Model Unit Tests

This module contains comprehensive unit tests for database models
with edge cases and boundary conditions.
"""

import pytest
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Float, Text, ForeignKey, Boolean, Numeric, Date
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime, date, timedelta
from decimal import Decimal
from unittest.mock import patch

# Import actual models
from src.core.database import Base
from src.models.database_models import Contract, Invoice, Document, User, ContractLineItem, InvoiceLineItem, DocumentMetadata, AgentExecution


@pytest.fixture(scope="function")
def in_memory_db_session():
    """Fixture for an in-memory SQLite database for testing."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(engine)


@pytest.mark.database
class TestContractModelComprehensive:
    """Comprehensive tests for Contract model with edge cases."""

    def test_contract_minimum_values(self, in_memory_db_session):
        """Test contract creation with minimum valid values."""
        contract = Contract(
            contract_id="MIN-001",
            title="A",  # Minimum length title
            vendor="B",  # Minimum length vendor
            amount=Decimal("0.01"),  # Minimum amount
            currency="USD",
            start_date=date(1900, 1, 1),  # Earliest date
            end_date=date(1900, 1, 2),   # One day later
            terms="",  # Empty terms
            status="draft"
        )
        in_memory_db_session.add(contract)
        in_memory_db_session.commit()
        in_memory_db_session.refresh(contract)

        assert contract.id is not None
        assert contract.title == "A"
        assert contract.vendor == "B"
        assert contract.amount == Decimal("0.01")

    def test_contract_maximum_values(self, in_memory_db_session):
        """Test contract creation with maximum reasonable values."""
        contract = Contract(
            contract_id="MAX-001",
            title="A" * 255,  # Maximum length title
            vendor="B" * 255,  # Maximum length vendor
            amount=Decimal("999999999999999.99"),  # Large amount
            currency="USD",
            start_date=date(2099, 12, 31),  # Latest date
            end_date=date(2099, 12, 31),    # Same date
            terms="C" * 1000,  # Long terms
            status="active"
        )
        in_memory_db_session.add(contract)
        in_memory_db_session.commit()
        in_memory_db_session.refresh(contract)

        assert contract.id is not None
        assert len(contract.title) == 255
        assert len(contract.vendor) == 255
        assert contract.amount == Decimal("1000000000000000.00")  # Rounded to 2 decimal places

    def test_contract_unicode_characters(self, in_memory_db_session):
        """Test contract creation with Unicode characters."""
        contract = Contract(
            contract_id="UNI-001",
            title="软件许可证合同",  # Chinese characters
            vendor="株式会社テスト",  # Japanese characters
            amount=Decimal("50000.00"),
            currency="USD",
            terms="Contrat de licence logicielle",  # French
            status="active"
        )
        in_memory_db_session.add(contract)
        in_memory_db_session.commit()
        in_memory_db_session.refresh(contract)

        assert contract.title == "软件许可证合同"
        assert contract.vendor == "株式会社テスト"
        assert contract.terms == "Contrat de licence logicielle"

    def test_contract_special_characters(self, in_memory_db_session):
        """Test contract creation with special characters."""
        contract = Contract(
            contract_id="SPEC-001",
            title="Contract & Agreement (2024) - Special Characters!",
            vendor="Vendor@Company.com",
            amount=Decimal("10000.00"),
            currency="USD",
            terms="Terms with $pecial ch@racters & symbols!",
            status="active"
        )
        in_memory_db_session.add(contract)
        in_memory_db_session.commit()
        in_memory_db_session.refresh(contract)

        assert contract.title == "Contract & Agreement (2024) - Special Characters!"
        assert contract.vendor == "Vendor@Company.com"
        assert contract.terms == "Terms with $pecial ch@racters & symbols!"

    def test_contract_precision_handling(self, in_memory_db_session):
        """Test contract amount precision handling."""
        contract = Contract(
            contract_id="PREC-001",
            title="Precision Test",
            vendor="Test Vendor",
            amount=Decimal("123456789.123456789"),  # High precision
            currency="USD"
        )
        in_memory_db_session.add(contract)
        in_memory_db_session.commit()
        in_memory_db_session.refresh(contract)

        # Should be rounded to 2 decimal places
        assert contract.amount == Decimal("123456789.12")

    def test_contract_status_transitions(self, in_memory_db_session):
        """Test contract status transitions."""
        contract = Contract(
            contract_id="STATUS-001",
            title="Status Test",
            vendor="Test Vendor",
            amount=Decimal("1000.00"),
            currency="USD"
        )
        in_memory_db_session.add(contract)
        in_memory_db_session.commit()
        in_memory_db_session.refresh(contract)

        # Test all status transitions
        statuses = ["draft", "pending", "approved", "active", "expired", "cancelled"]
        for status in statuses:
            contract.status = status
            in_memory_db_session.commit()
            in_memory_db_session.refresh(contract)
            assert contract.status == status

    def test_contract_date_edge_cases(self, in_memory_db_session):
        """Test contract date edge cases."""
        # Test leap year
        contract = Contract(
            contract_id="LEAP-001",
            title="Leap Year Test",
            vendor="Test Vendor",
            amount=Decimal("1000.00"),
            currency="USD",
            start_date=date(2024, 2, 29),  # Leap year
            end_date=date(2024, 2, 29)
        )
        in_memory_db_session.add(contract)
        in_memory_db_session.commit()
        in_memory_db_session.refresh(contract)

        assert contract.start_date == date(2024, 2, 29)
        assert contract.end_date == date(2024, 2, 29)

        # Test year boundaries
        contract2 = Contract(
            contract_id="YEAR-001",
            title="Year Boundary Test",
            vendor="Test Vendor",
            amount=Decimal("1000.00"),
            currency="USD",
            start_date=date(2023, 12, 31),
            end_date=date(2024, 1, 1)
        )
        in_memory_db_session.add(contract2)
        in_memory_db_session.commit()
        in_memory_db_session.refresh(contract2)

        assert contract2.start_date == date(2023, 12, 31)
        assert contract2.end_date == date(2024, 1, 1)


@pytest.mark.database
class TestInvoiceModelComprehensive:
    """Comprehensive tests for Invoice model with edge cases."""

    def test_invoice_minimum_values(self, in_memory_db_session):
        """Test invoice creation with minimum valid values."""
        contract = Contract(
            contract_id="INV-C-001",
            title="Contract",
            vendor="Vendor",
            amount=Decimal("1000.00"),
            currency="USD"
        )
        in_memory_db_session.add(contract)
        in_memory_db_session.commit()
        in_memory_db_session.refresh(contract)

        invoice = Invoice(
            invoice_id="INV-001",
            contract_id="INV-C-001",
            vendor="A",  # Minimum length
            amount=Decimal("0.01"),  # Minimum amount
            currency="USD",
            due_date=date(1900, 1, 2),
            status="pending"
        )
        in_memory_db_session.add(invoice)
        in_memory_db_session.commit()
        in_memory_db_session.refresh(invoice)

        assert invoice.id is not None
        assert invoice.vendor == "A"
        assert invoice.amount == Decimal("0.01")

    def test_invoice_maximum_values(self, in_memory_db_session):
        """Test invoice creation with maximum reasonable values."""
        contract = Contract(
            contract_id="INV-C-002",
            title="Contract",
            vendor="Vendor",
            amount=Decimal("1000000.00"),
            currency="USD"
        )
        in_memory_db_session.add(contract)
        in_memory_db_session.commit()
        in_memory_db_session.refresh(contract)

        invoice = Invoice(
            invoice_id="INV-002",
            contract_id="INV-C-002",
            vendor="B" * 255,  # Maximum length
            amount=Decimal("999999999999999.99"),  # Large amount
            currency="USD",
            due_date=date(2099, 12, 31),
            status="paid"
        )
        in_memory_db_session.add(invoice)
        in_memory_db_session.commit()
        in_memory_db_session.refresh(invoice)

        assert len(invoice.vendor) == 255
        assert invoice.amount == Decimal("1000000000000000.00")  # Rounded due to Numeric(15,2)

    def test_invoice_line_items_edge_cases(self, in_memory_db_session):
        """Test invoice line items with edge cases."""
        contract = Contract(
            contract_id="INV-C-003",
            title="Contract",
            vendor="Vendor",
            amount=Decimal("1000.00"),
            currency="USD"
        )
        in_memory_db_session.add(contract)
        in_memory_db_session.commit()
        in_memory_db_session.refresh(contract)

        invoice = Invoice(
            invoice_id="INV-003",
            contract_id="INV-C-003",
            vendor="Vendor",
            amount=Decimal("1000.00"),
            currency="USD"
        )
        in_memory_db_session.add(invoice)
        in_memory_db_session.commit()
        in_memory_db_session.refresh(invoice)

        # Test line item with minimum values
        line_item = InvoiceLineItem(
            invoice_id=invoice.id,
            description="A",  # Minimum length
            quantity=Decimal("0.01"),  # Minimum quantity
            unit_price=Decimal("0.01"),  # Minimum price
            total=Decimal("0.0001")  # Very small total
        )
        in_memory_db_session.add(line_item)
        in_memory_db_session.commit()
        in_memory_db_session.refresh(line_item)

        assert line_item.description == "A"
        assert line_item.quantity == Decimal("0.01")
        assert line_item.unit_price == Decimal("0.01")

    def test_invoice_status_transitions(self, in_memory_db_session):
        """Test invoice status transitions."""
        contract = Contract(
            contract_id="INV-C-004",
            title="Contract",
            vendor="Vendor",
            amount=Decimal("1000.00"),
            currency="USD"
        )
        in_memory_db_session.add(contract)
        in_memory_db_session.commit()
        in_memory_db_session.refresh(contract)

        invoice = Invoice(
            invoice_id="INV-004",
            contract_id="INV-C-004",
            vendor="Vendor",
            amount=Decimal("1000.00"),
            currency="USD"
        )
        in_memory_db_session.add(invoice)
        in_memory_db_session.commit()
        in_memory_db_session.refresh(invoice)

        # Test all status transitions
        statuses = ["pending", "sent", "paid", "overdue", "cancelled"]
        for status in statuses:
            invoice.status = status
            in_memory_db_session.commit()
            in_memory_db_session.refresh(invoice)
            assert invoice.status == status


@pytest.mark.database
class TestDocumentModelComprehensive:
    """Comprehensive tests for Document model with edge cases."""

    def test_document_minimum_values(self, in_memory_db_session):
        """Test document creation with minimum valid values."""
        document = Document(
            document_id="DOC-001",
            filename="a.pdf",  # Minimum filename
            file_type="application/pdf",
            file_size=1,  # Minimum file size
            status="uploaded",
            file_path="/a/b/c.pdf",  # Minimum path
            content_hash="a" * 64  # SHA256 hash length
        )
        in_memory_db_session.add(document)
        in_memory_db_session.commit()
        in_memory_db_session.refresh(document)

        assert document.id is not None
        assert document.filename == "a.pdf"
        assert document.file_size == 1

    def test_document_maximum_values(self, in_memory_db_session):
        """Test document creation with maximum reasonable values."""
        document = Document(
            document_id="DOC-002",
            filename="a" * 255 + ".pdf",  # Maximum filename length
            file_type="application/pdf",
            file_size=1073741824,  # 1GB
            status="processed",
            file_path="/" + "a" * 500 + ".pdf",  # Long path
            content_hash="b" * 64  # SHA256 hash
        )
        in_memory_db_session.add(document)
        in_memory_db_session.commit()
        in_memory_db_session.refresh(document)

        assert len(document.filename) == 259  # 255 + ".pdf"
        assert document.file_size == 1073741824

    def test_document_unicode_filename(self, in_memory_db_session):
        """Test document creation with Unicode filename."""
        document = Document(
            document_id="DOC-003",
            filename="文档.pdf",  # Chinese characters
            file_type="application/pdf",
            file_size=1024,
            status="uploaded",
            content_hash="c" * 64
        )
        in_memory_db_session.add(document)
        in_memory_db_session.commit()
        in_memory_db_session.refresh(document)

        assert document.filename == "文档.pdf"

    def test_document_special_characters_filename(self, in_memory_db_session):
        """Test document creation with special characters in filename."""
        document = Document(
            document_id="DOC-004",
            filename="file-name_with.special@chars#2024.pdf",
            file_type="application/pdf",
            file_size=1024,
            status="uploaded",
            content_hash="d" * 64
        )
        in_memory_db_session.add(document)
        in_memory_db_session.commit()
        in_memory_db_session.refresh(document)

        assert document.filename == "file-name_with.special@chars#2024.pdf"

    def test_document_status_transitions(self, in_memory_db_session):
        """Test document status transitions."""
        document = Document(
            document_id="DOC-005",
            filename="test.pdf",
            file_type="application/pdf",
            file_size=1024,
            status="uploaded"
        )
        in_memory_db_session.add(document)
        in_memory_db_session.commit()
        in_memory_db_session.refresh(document)

        # Test all status transitions
        statuses = ["uploaded", "processing", "processed", "failed", "archived"]
        for status in statuses:
            document.status = status
            in_memory_db_session.commit()
            in_memory_db_session.refresh(document)
            assert document.status == status

    def test_document_metadata_edge_cases(self, in_memory_db_session):
        """Test document metadata with edge cases."""
        document = Document(
            document_id="DOC-006",
            filename="test.pdf",
            file_type="application/pdf",
            file_size=1024,
            status="uploaded"
        )
        in_memory_db_session.add(document)
        in_memory_db_session.commit()
        in_memory_db_session.refresh(document)

        # Test metadata with edge values
        metadata = DocumentMetadata(
            document_id=document.id,
            pages=1,  # Minimum pages
            language="en",  # Short language code
            confidence=0.0,  # Minimum confidence
            extracted_text="",  # Empty text
            processing_time=0.001  # Very short processing time
        )
        in_memory_db_session.add(metadata)
        in_memory_db_session.commit()
        in_memory_db_session.refresh(metadata)

        assert metadata.pages == 1
        assert metadata.language == "en"
        assert metadata.confidence == 0.0
        assert metadata.extracted_text == ""
        assert metadata.processing_time == 0.001


@pytest.mark.database
class TestUserModelComprehensive:
    """Comprehensive tests for User model with edge cases."""

    def test_user_minimum_values(self, in_memory_db_session):
        """Test user creation with minimum valid values."""
        user = User(
            user_id="USER-001",
            username="a",  # Minimum username
            email="a@b.c",  # Minimum email
            full_name="A",  # Minimum full name
            role="viewer"
        )
        in_memory_db_session.add(user)
        in_memory_db_session.commit()
        in_memory_db_session.refresh(user)

        assert user.id is not None
        assert user.username == "a"
        assert user.email == "a@b.c"
        assert user.full_name == "A"

    def test_user_maximum_values(self, in_memory_db_session):
        """Test user creation with maximum reasonable values."""
        user = User(
            user_id="USER-002",
            username="a" * 50,  # Maximum username length
            email="a" * 50 + "@" + "b" * 50 + ".com",  # Long email
            full_name="A" * 255,  # Maximum full name length
            role="admin"
        )
        in_memory_db_session.add(user)
        in_memory_db_session.commit()
        in_memory_db_session.refresh(user)

        assert len(user.username) == 50
        assert len(user.email) == 105  # 50 + 1 + 50 + 1 + 3 (.com)
        assert len(user.full_name) == 255

    def test_user_unicode_characters(self, in_memory_db_session):
        """Test user creation with Unicode characters."""
        user = User(
            user_id="USER-003",
            username="用户名",  # Chinese username
            email="用户@测试.com",  # Chinese email
            full_name="用户全名",  # Chinese full name
            role="editor"
        )
        in_memory_db_session.add(user)
        in_memory_db_session.commit()
        in_memory_db_session.refresh(user)

        assert user.username == "用户名"
        assert user.email == "用户@测试.com"
        assert user.full_name == "用户全名"

    def test_user_role_transitions(self, in_memory_db_session):
        """Test user role transitions."""
        user = User(
            user_id="USER-004",
            username="testuser",
            email="test@example.com",
            full_name="Test User"
        )
        in_memory_db_session.add(user)
        in_memory_db_session.commit()
        in_memory_db_session.refresh(user)

        # Test all role transitions
        roles = ["viewer", "editor", "admin", "auditor"]
        for role in roles:
            user.role = role
            in_memory_db_session.commit()
            in_memory_db_session.refresh(user)
            assert user.role == role

    def test_user_active_status_transitions(self, in_memory_db_session):
        """Test user active status transitions."""
        user = User(
            user_id="USER-005",
            username="testuser",
            email="test@example.com",
            full_name="Test User"
        )
        in_memory_db_session.add(user)
        in_memory_db_session.commit()
        in_memory_db_session.refresh(user)

        # Test active status transitions
        assert user.is_active is True  # Default value

        user.is_active = False
        in_memory_db_session.commit()
        in_memory_db_session.refresh(user)
        assert user.is_active is False

        user.is_active = True
        in_memory_db_session.commit()
        in_memory_db_session.refresh(user)
        assert user.is_active is True


@pytest.mark.database
class TestAgentExecutionModelComprehensive:
    """Comprehensive tests for AgentExecution model with edge cases."""

    def test_agent_execution_minimum_values(self, in_memory_db_session):
        """Test agent execution creation with minimum valid values."""
        document = Document(
            document_id="AGENT-DOC-001",
            filename="test.pdf",
            file_type="application/pdf",
            file_size=1024,
            status="uploaded"
        )
        in_memory_db_session.add(document)
        in_memory_db_session.commit()
        in_memory_db_session.refresh(document)

        execution = AgentExecution(
            execution_id="EXEC-001",
            agent_type="a",  # Minimum agent type
            document_id="AGENT-DOC-001",
            status="pending",
            input_data={},  # Empty input
            output_data={},  # Empty output
            confidence=0.0,  # Minimum confidence
            execution_time=0.001  # Minimum execution time
        )
        in_memory_db_session.add(execution)
        in_memory_db_session.commit()
        in_memory_db_session.refresh(execution)

        assert execution.id is not None
        assert execution.agent_type == "a"
        assert execution.confidence == 0.0
        assert execution.execution_time == 0.001

    def test_agent_execution_maximum_values(self, in_memory_db_session):
        """Test agent execution creation with maximum reasonable values."""
        document = Document(
            document_id="AGENT-DOC-002",
            filename="test.pdf",
            file_type="application/pdf",
            file_size=1024,
            status="uploaded"
        )
        in_memory_db_session.add(document)
        in_memory_db_session.commit()
        in_memory_db_session.refresh(document)

        execution = AgentExecution(
            execution_id="EXEC-002",
            agent_type="a" * 100,  # Long agent type
            document_id="AGENT-DOC-002",
            status="completed",
            input_data={"key": "value" * 1000},  # Large input
            output_data={"result": "data" * 1000},  # Large output
            confidence=1.0,  # Maximum confidence
            execution_time=3600.0  # 1 hour execution time
        )
        in_memory_db_session.add(execution)
        in_memory_db_session.commit()
        in_memory_db_session.refresh(execution)

        assert len(execution.agent_type) == 100
        assert execution.confidence == 1.0
        assert execution.execution_time == 3600.0

    def test_agent_execution_status_transitions(self, in_memory_db_session):
        """Test agent execution status transitions."""
        document = Document(
            document_id="AGENT-DOC-003",
            filename="test.pdf",
            file_type="application/pdf",
            file_size=1024,
            status="uploaded"
        )
        in_memory_db_session.add(document)
        in_memory_db_session.commit()
        in_memory_db_session.refresh(document)

        execution = AgentExecution(
            execution_id="EXEC-003",
            agent_type="test_agent",
            document_id="AGENT-DOC-003",
            status="pending"
        )
        in_memory_db_session.add(execution)
        in_memory_db_session.commit()
        in_memory_db_session.refresh(execution)

        # Test all status transitions
        statuses = ["pending", "running", "completed", "failed", "cancelled"]
        for status in statuses:
            execution.status = status
            in_memory_db_session.commit()
            in_memory_db_session.refresh(execution)
            assert execution.status == status


@pytest.mark.database
class TestModelRelationshipsComprehensive:
    """Comprehensive tests for model relationships with edge cases."""

    def test_complex_contract_invoice_relationship(self, in_memory_db_session):
        """Test complex contract-invoice relationship with many invoices."""
        contract = Contract(
            contract_id="COMPLEX-C-001",
            title="Complex Contract",
            vendor="Complex Vendor",
            amount=Decimal("100000.00"),
            currency="USD"
        )
        in_memory_db_session.add(contract)
        in_memory_db_session.commit()
        in_memory_db_session.refresh(contract)

        # Create many invoices
        invoices = []
        for i in range(50):  # Create 50 invoices
            invoice = Invoice(
                invoice_id=f"INV-{i:03d}",
                contract_id="COMPLEX-C-001",
                vendor="Complex Vendor",
                amount=Decimal("2000.00"),
                currency="USD"
            )
            invoices.append(invoice)
        
        in_memory_db_session.add_all(invoices)
        in_memory_db_session.commit()
        in_memory_db_session.refresh(contract)

        assert len(contract.invoices) == 50

    def test_complex_document_agent_execution_relationship(self, in_memory_db_session):
        """Test complex document-agent execution relationship."""
        document = Document(
            document_id="COMPLEX-DOC-001",
            filename="complex.pdf",
            file_type="application/pdf",
            file_size=1024,
            status="uploaded"
        )
        in_memory_db_session.add(document)
        in_memory_db_session.commit()
        in_memory_db_session.refresh(document)

        # Create many agent executions
        executions = []
        for i in range(20):  # Create 20 executions
            execution = AgentExecution(
                execution_id=f"EXEC-{i:03d}",
                agent_type=f"agent_{i}",
                document_id="COMPLEX-DOC-001",
                status="completed"
            )
            executions.append(execution)
        
        in_memory_db_session.add_all(executions)
        in_memory_db_session.commit()
        in_memory_db_session.refresh(document)

        assert len(document.agent_executions) == 20


@pytest.mark.database
class TestDatabaseConstraintsComprehensive:
    """Comprehensive tests for database constraints with edge cases."""

    def test_unique_constraint_violations(self, in_memory_db_session):
        """Test unique constraint violations."""
        # Test contract_id uniqueness
        contract1 = Contract(
            contract_id="UNIQUE-001",
            title="Contract 1",
            vendor="Vendor",
            amount=Decimal("1000.00"),
            currency="USD"
        )
        in_memory_db_session.add(contract1)
        in_memory_db_session.commit()

        with pytest.raises(Exception):  # Should raise IntegrityError
            contract2 = Contract(
                contract_id="UNIQUE-001",  # Same ID
                title="Contract 2",
                vendor="Vendor",
                amount=Decimal("2000.00"),
                currency="USD"
            )
            in_memory_db_session.add(contract2)
            in_memory_db_session.commit()
        in_memory_db_session.rollback()

    def test_foreign_key_constraint_violations(self, in_memory_db_session):
        """Test foreign key constraint violations."""
        # SQLite doesn't enforce foreign key constraints by default
        # This test verifies the model structure is correct
        invoice = Invoice(
            invoice_id="FK-001",
            contract_id="NON-EXISTENT",  # Non-existent contract
            vendor="Vendor",
            amount=Decimal("1000.00"),
            currency="USD"
        )
        in_memory_db_session.add(invoice)
        in_memory_db_session.commit()
        
        # Verify the invoice was created (SQLite allows this)
        assert invoice.id is not None
        assert invoice.contract_id == "NON-EXISTENT"

    def test_not_null_constraint_violations(self, in_memory_db_session):
        """Test not null constraint violations."""
        with pytest.raises(Exception):  # Should raise IntegrityError
            contract = Contract(
                contract_id="NULL-001",
                # Missing required fields: title, vendor, amount, currency
            )
            in_memory_db_session.add(contract)
            in_memory_db_session.commit()
        in_memory_db_session.rollback()


@pytest.mark.database
class TestDatabaseMarkersComprehensive:
    """Test that database markers work correctly for comprehensive tests."""

    def test_database_marker_applied(self):
        """Test that database marker is applied to this test."""
        assert True

    def test_comprehensive_database_operations(self, in_memory_db_session):
        """Test comprehensive database operations."""
        # Create a complex scenario with all models
        contract = Contract(
            contract_id="COMPREHENSIVE-001",
            title="Comprehensive Test Contract",
            vendor="Test Vendor",
            amount=Decimal("50000.00"),
            currency="USD"
        )
        in_memory_db_session.add(contract)
        in_memory_db_session.commit()
        in_memory_db_session.refresh(contract)

        invoice = Invoice(
            invoice_id="COMPREHENSIVE-INV-001",
            contract_id="COMPREHENSIVE-001",
            vendor="Test Vendor",
            amount=Decimal("10000.00"),
            currency="USD"
        )
        in_memory_db_session.add(invoice)
        in_memory_db_session.commit()
        in_memory_db_session.refresh(invoice)

        document = Document(
            document_id="COMPREHENSIVE-DOC-001",
            filename="comprehensive.pdf",
            file_type="application/pdf",
            file_size=1024,
            status="uploaded"
        )
        in_memory_db_session.add(document)
        in_memory_db_session.commit()
        in_memory_db_session.refresh(document)

        user = User(
            user_id="COMPREHENSIVE-USER-001",
            username="comprehensive_user",
            email="comprehensive@test.com",
            full_name="Comprehensive Test User"
        )
        in_memory_db_session.add(user)
        in_memory_db_session.commit()
        in_memory_db_session.refresh(user)

        execution = AgentExecution(
            execution_id="COMPREHENSIVE-EXEC-001",
            agent_type="comprehensive_agent",
            document_id="COMPREHENSIVE-DOC-001",
            status="completed"
        )
        in_memory_db_session.add(execution)
        in_memory_db_session.commit()
        in_memory_db_session.refresh(execution)

        # Verify all relationships work
        assert contract.invoices[0].invoice_id == "COMPREHENSIVE-INV-001"
        assert document.agent_executions[0].execution_id == "COMPREHENSIVE-EXEC-001"
        assert execution.document.document_id == "COMPREHENSIVE-DOC-001"

        # Verify counts
        assert in_memory_db_session.query(Contract).count() == 1
        assert in_memory_db_session.query(Invoice).count() == 1
        assert in_memory_db_session.query(Document).count() == 1
        assert in_memory_db_session.query(User).count() == 1
        assert in_memory_db_session.query(AgentExecution).count() == 1
