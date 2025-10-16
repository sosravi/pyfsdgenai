"""
Functionality Validation Test Data Fixtures

This module provides comprehensive test data for functionality validation scenarios.
Includes workflow data, performance metrics, security scenarios, and validation datasets.
"""

import pytest
from datetime import datetime, date
from decimal import Decimal
from typing import Dict, List, Any
import json


@pytest.fixture
def end_to_end_workflow_data():
    """End-to-end workflow test data."""
    return {
        "contract_management_workflow": {
            "steps": [
                {
                    "step": "create_contract",
                    "data": {
                        "contract_id": "E2E-CONTRACT-001",
                        "title": "End-to-End Test Contract",
                        "vendor": "Test Vendor Inc.",
                        "amount": Decimal("50000.00"),
                        "currency": "USD",
                        "start_date": date(2024, 1, 1),
                        "end_date": date(2024, 12, 31),
                        "status": "draft"
                    },
                    "expected_result": {"status": "created", "contract_id": "E2E-CONTRACT-001"}
                },
                {
                    "step": "review_contract",
                    "data": {"contract_id": "E2E-CONTRACT-001", "reviewer": "admin"},
                    "expected_result": {"status": "under_review"}
                },
                {
                    "step": "approve_contract",
                    "data": {"contract_id": "E2E-CONTRACT-001", "approver": "admin"},
                    "expected_result": {"status": "approved"}
                },
                {
                    "step": "activate_contract",
                    "data": {"contract_id": "E2E-CONTRACT-001"},
                    "expected_result": {"status": "active"}
                }
            ],
            "expected_duration": 30.0,
            "expected_success": True
        },
        "invoice_processing_workflow": {
            "steps": [
                {
                    "step": "create_invoice",
                    "data": {
                        "invoice_id": "E2E-INVOICE-001",
                        "contract_id": "E2E-CONTRACT-001",
                        "vendor": "Test Vendor Inc.",
                        "amount": Decimal("25000.00"),
                        "currency": "USD",
                        "due_date": date(2024, 6, 30),
                        "status": "draft"
                    },
                    "expected_result": {"status": "created", "invoice_id": "E2E-INVOICE-001"}
                },
                {
                    "step": "add_line_items",
                    "data": {
                        "invoice_id": "E2E-INVOICE-001",
                        "line_items": [
                            {
                                "description": "Software License",
                                "quantity": 1,
                                "unit_price": Decimal("15000.00"),
                                "total": Decimal("15000.00"),
                                "currency": "USD"
                            },
                            {
                                "description": "Implementation Services",
                                "quantity": 100,
                                "unit_price": Decimal("100.00"),
                                "total": Decimal("10000.00"),
                                "currency": "USD"
                            }
                        ]
                    },
                    "expected_result": {"line_items_added": 2, "total_amount": Decimal("25000.00")}
                },
                {
                    "step": "calculate_totals",
                    "data": {"invoice_id": "E2E-INVOICE-001"},
                    "expected_result": {"total_amount": Decimal("25000.00"), "tax_amount": Decimal("0.00")}
                },
                {
                    "step": "submit_invoice",
                    "data": {"invoice_id": "E2E-INVOICE-001"},
                    "expected_result": {"status": "submitted"}
                }
            ],
            "expected_duration": 15.0,
            "expected_success": True
        },
        "document_processing_workflow": {
            "steps": [
                {
                    "step": "upload_document",
                    "data": {
                        "document_id": "E2E-DOCUMENT-001",
                        "filename": "contract_agreement.pdf",
                        "file_path": "/documents/contract_agreement.pdf",
                        "file_size": 2048000,
                        "mime_type": "application/pdf",
                        "status": "uploaded"
                    },
                    "expected_result": {"status": "uploaded", "document_id": "E2E-DOCUMENT-001"}
                },
                {
                    "step": "extract_text",
                    "data": {"document_id": "E2E-DOCUMENT-001"},
                    "expected_result": {"text_extracted": True, "confidence": 0.95}
                },
                {
                    "step": "analyze_content",
                    "data": {"document_id": "E2E-DOCUMENT-001", "analysis_type": "contract_analysis"},
                    "expected_result": {"analysis_complete": True, "key_terms_found": 15}
                },
                {
                    "step": "store_results",
                    "data": {"document_id": "E2E-DOCUMENT-001"},
                    "expected_result": {"status": "processed", "metadata_stored": True}
                }
            ],
            "expected_duration": 45.0,
            "expected_success": True
        }
    }


@pytest.fixture
def data_flow_scenarios():
    """Data flow validation scenarios."""
    return {
        "contract_data_flow": {
            "input": {
                "raw_data": {
                    "title": "Software License Agreement",
                    "vendor": "TechCorp Inc.",
                    "amount": "50000.00",
                    "currency": "USD",
                    "start_date": "2024-01-01",
                    "end_date": "2024-12-31"
                }
            },
            "processing": {
                "validation": {
                    "required_fields": True,
                    "data_types": True,
                    "business_rules": True
                },
                "transformation": {
                    "amount_conversion": Decimal("50000.00"),
                    "date_parsing": [date(2024, 1, 1), date(2024, 12, 31)],
                    "currency_validation": "USD"
                },
                "enrichment": {
                    "contract_id_generation": "CONTRACT-001",
                    "status_assignment": "draft",
                    "timestamp_creation": datetime.now()
                }
            },
            "output": {
                "contract_id": "CONTRACT-001",
                "title": "Software License Agreement",
                "vendor": "TechCorp Inc.",
                "amount": Decimal("50000.00"),
                "currency": "USD",
                "start_date": date(2024, 1, 1),
                "end_date": date(2024, 12, 31),
                "status": "draft",
                "created_at": datetime.now()
            },
            "expected_integrity": True
        },
        "invoice_calculation_flow": {
            "input": {
                "line_items": [
                    {"description": "License", "quantity": 1, "unit_price": 10000.00},
                    {"description": "Support", "quantity": 12, "unit_price": 500.00}
                ],
                "tax_rate": 0.1
            },
            "processing": {
                "line_item_totals": [
                    {"total": 10000.00},
                    {"total": 6000.00}
                ],
                "subtotal_calculation": 16000.00,
                "tax_calculation": 1600.00,
                "total_calculation": 17600.00
            },
            "output": {
                "subtotal": Decimal("16000.00"),
                "tax_amount": Decimal("1600.00"),
                "total_amount": Decimal("17600.00")
            },
            "expected_accuracy": True
        }
    }


@pytest.fixture
def business_logic_scenarios():
    """Business logic validation scenarios."""
    return {
        "contract_validation_rules": {
            "amount_validation": [
                {"amount": Decimal("1000.00"), "expected_valid": True},
                {"amount": Decimal("0.00"), "expected_valid": False},
                {"amount": Decimal("-1000.00"), "expected_valid": False},
                {"amount": Decimal("999999999999999.99"), "expected_valid": True}
            ],
            "currency_validation": [
                {"currency": "USD", "expected_valid": True},
                {"currency": "EUR", "expected_valid": True},
                {"currency": "GBP", "expected_valid": True},
                {"currency": "INVALID", "expected_valid": False},
                {"currency": "US", "expected_valid": False}
            ],
            "date_validation": [
                {"start_date": date(2024, 1, 1), "end_date": date(2024, 12, 31), "expected_valid": True},
                {"start_date": date(2024, 12, 31), "end_date": date(2024, 1, 1), "expected_valid": False},
                {"start_date": date(2024, 1, 1), "end_date": date(2024, 1, 1), "expected_valid": True}
            ]
        },
        "invoice_calculation_rules": {
            "line_item_calculations": [
                {
                    "quantity": 2,
                    "unit_price": Decimal("50.00"),
                    "expected_total": Decimal("100.00")
                },
                {
                    "quantity": 0,
                    "unit_price": Decimal("50.00"),
                    "expected_total": Decimal("0.00")
                },
                {
                    "quantity": 1,
                    "unit_price": Decimal("0.00"),
                    "expected_total": Decimal("0.00")
                }
            ],
            "total_calculations": [
                {
                    "line_items": [
                        {"total": Decimal("100.00")},
                        {"total": Decimal("50.00")}
                    ],
                    "expected_total": Decimal("150.00")
                },
                {
                    "line_items": [],
                    "expected_total": Decimal("0.00")
                }
            ]
        },
        "status_transition_rules": {
            "contract_status_transitions": [
                {"from": "draft", "to": "under_review", "expected_valid": True},
                {"from": "under_review", "to": "approved", "expected_valid": True},
                {"from": "approved", "to": "active", "expected_valid": True},
                {"from": "draft", "to": "active", "expected_valid": False},
                {"from": "active", "to": "draft", "expected_valid": False}
            ],
            "invoice_status_transitions": [
                {"from": "draft", "to": "submitted", "expected_valid": True},
                {"from": "submitted", "to": "paid", "expected_valid": True},
                {"from": "paid", "to": "draft", "expected_valid": False},
                {"from": "draft", "to": "paid", "expected_valid": False}
            ]
        }
    }


@pytest.fixture
def integration_scenarios():
    """Integration validation scenarios."""
    return {
        "database_integration": {
            "contract_operations": {
                "create": {
                    "data": {"contract_id": "INT-CONTRACT-001", "title": "Integration Test Contract"},
                    "expected_result": {"id": 1, "contract_id": "INT-CONTRACT-001"}
                },
                "read": {
                    "contract_id": "INT-CONTRACT-001",
                    "expected_result": {"contract_id": "INT-CONTRACT-001", "title": "Integration Test Contract"}
                },
                "update": {
                    "contract_id": "INT-CONTRACT-001",
                    "data": {"title": "Updated Integration Test Contract"},
                    "expected_result": {"title": "Updated Integration Test Contract"}
                },
                "delete": {
                    "contract_id": "INT-CONTRACT-001",
                    "expected_result": {"deleted": True}
                }
            },
            "invoice_operations": {
                "create_with_contract": {
                    "data": {
                        "invoice_id": "INT-INVOICE-001",
                        "contract_id": "INT-CONTRACT-001",
                        "amount": Decimal("1000.00")
                    },
                    "expected_result": {"invoice_id": "INT-INVOICE-001", "contract_id": "INT-CONTRACT-001"}
                }
            }
        },
        "agent_integration": {
            "pricing_extraction": {
                "valid_input": {
                    "text": "Software License: $5,000.00 per year",
                    "expected_output": {
                        "pricing_items": [
                            {
                                "description": "Software License",
                                "quantity": 1,
                                "unit_price": 5000.00,
                                "total": 5000.00,
                                "currency": "USD"
                            }
                        ],
                        "total_amount": 5000.00,
                        "currency": "USD",
                        "confidence": 0.95
                    }
                },
                "invalid_input": {
                    "text": "",
                    "expected_output": {"error": "invalid_input"}
                },
                "complex_input": {
                    "text": "Software License: $5,000.00, Support: $1,200.00 per year, Implementation: $2,500.00 one-time",
                    "expected_output": {
                        "pricing_items": [
                            {"description": "Software License", "unit_price": 5000.00, "currency": "USD"},
                            {"description": "Support", "unit_price": 1200.00, "currency": "USD"},
                            {"description": "Implementation", "unit_price": 2500.00, "currency": "USD"}
                        ],
                        "total_amount": 8700.00,
                        "currency": "USD"
                    }
                }
            }
        },
        "api_integration": {
            "contract_endpoints": {
                "create_contract": {
                    "endpoint": "/contracts",
                    "method": "POST",
                    "data": {"contract_id": "API-CONTRACT-001", "title": "API Test Contract"},
                    "expected_status": 201
                },
                "get_contract": {
                    "endpoint": "/contracts/API-CONTRACT-001",
                    "method": "GET",
                    "expected_status": 200
                },
                "update_contract": {
                    "endpoint": "/contracts/API-CONTRACT-001",
                    "method": "PUT",
                    "data": {"title": "Updated API Test Contract"},
                    "expected_status": 200
                },
                "delete_contract": {
                    "endpoint": "/contracts/API-CONTRACT-001",
                    "method": "DELETE",
                    "expected_status": 204
                }
            },
            "invoice_endpoints": {
                "create_invoice": {
                    "endpoint": "/invoices",
                    "method": "POST",
                    "data": {
                        "invoice_id": "API-INVOICE-001",
                        "contract_id": "API-CONTRACT-001",
                        "amount": Decimal("1000.00")
                    },
                    "expected_status": 201
                },
                "list_invoices": {
                    "endpoint": "/invoices",
                    "method": "GET",
                    "expected_status": 200
                }
            }
        }
    }


@pytest.fixture
def user_workflow_scenarios():
    """User workflow validation scenarios."""
    return {
        "admin_workflows": {
            "contract_management": {
                "user_role": "admin",
                "permissions": ["create", "read", "update", "delete", "approve"],
                "workflow_steps": [
                    {"action": "create_contract", "expected_success": True},
                    {"action": "review_contract", "expected_success": True},
                    {"action": "approve_contract", "expected_success": True},
                    {"action": "activate_contract", "expected_success": True}
                ]
            },
            "user_management": {
                "user_role": "admin",
                "permissions": ["create_user", "update_user", "delete_user", "assign_roles"],
                "workflow_steps": [
                    {"action": "create_user", "expected_success": True},
                    {"action": "assign_role", "expected_success": True},
                    {"action": "update_permissions", "expected_success": True}
                ]
            }
        },
        "user_workflows": {
            "invoice_processing": {
                "user_role": "user",
                "permissions": ["create", "read", "update"],
                "workflow_steps": [
                    {"action": "create_invoice", "expected_success": True},
                    {"action": "add_line_items", "expected_success": True},
                    {"action": "submit_invoice", "expected_success": True},
                    {"action": "approve_invoice", "expected_success": False}  # No permission
                ]
            },
            "document_handling": {
                "user_role": "user",
                "permissions": ["upload", "read", "process"],
                "workflow_steps": [
                    {"action": "upload_document", "expected_success": True},
                    {"action": "process_document", "expected_success": True},
                    {"action": "view_results", "expected_success": True},
                    {"action": "delete_document", "expected_success": False}  # No permission
                ]
            }
        },
        "viewer_workflows": {
            "read_only_access": {
                "user_role": "viewer",
                "permissions": ["read"],
                "workflow_steps": [
                    {"action": "view_contracts", "expected_success": True},
                    {"action": "view_invoices", "expected_success": True},
                    {"action": "view_documents", "expected_success": True},
                    {"action": "create_contract", "expected_success": False},  # No permission
                    {"action": "update_invoice", "expected_success": False}  # No permission
                ]
            }
        }
    }


@pytest.fixture
def error_handling_scenarios():
    """Error handling validation scenarios."""
    return {
        "validation_errors": {
            "missing_required_fields": {
                "input": {"title": "Test Contract"},  # Missing required fields
                "expected_error": "validation_error",
                "expected_status": 422,
                "expected_message": "Missing required fields"
            },
            "invalid_data_types": {
                "input": {"contract_id": "TEST-001", "amount": "invalid_amount"},
                "expected_error": "type_error",
                "expected_status": 422,
                "expected_message": "Invalid data type"
            },
            "business_rule_violations": {
                "input": {"contract_id": "TEST-001", "amount": Decimal("-1000.00")},
                "expected_error": "business_rule_violation",
                "expected_status": 422,
                "expected_message": "Amount must be positive"
            }
        },
        "database_errors": {
            "constraint_violations": {
                "input": {"contract_id": "DUPLICATE-001"},  # Duplicate contract_id
                "expected_error": "constraint_violation",
                "expected_status": 409,
                "expected_message": "Contract ID already exists"
            },
            "foreign_key_violations": {
                "input": {"invoice_id": "TEST-INV-001", "contract_id": "NON-EXISTENT"},
                "expected_error": "foreign_key_violation",
                "expected_status": 400,
                "expected_message": "Referenced contract does not exist"
            }
        },
        "agent_errors": {
            "invalid_input": {
                "input": "",
                "expected_error": "agent_error",
                "expected_status": 400,
                "expected_message": "Invalid input for agent processing"
            },
            "processing_failure": {
                "input": "corrupted_document_content",
                "expected_error": "processing_error",
                "expected_status": 500,
                "expected_message": "Agent processing failed"
            }
        },
        "system_errors": {
            "service_unavailable": {
                "operation": "external_api_call",
                "expected_error": "service_unavailable",
                "expected_status": 503,
                "expected_message": "External service unavailable"
            },
            "timeout_errors": {
                "operation": "long_running_process",
                "expected_error": "timeout_error",
                "expected_status": 408,
                "expected_message": "Operation timeout"
            }
        }
    }


@pytest.fixture
def performance_scenarios():
    """Performance validation scenarios."""
    return {
        "response_time_scenarios": {
            "contract_operations": {
                "create_contract": {"max_response_time": 2.0, "iterations": 10},
                "get_contract": {"max_response_time": 0.5, "iterations": 50},
                "update_contract": {"max_response_time": 1.5, "iterations": 20},
                "delete_contract": {"max_response_time": 1.0, "iterations": 10}
            },
            "invoice_operations": {
                "create_invoice": {"max_response_time": 3.0, "iterations": 15},
                "calculate_totals": {"max_response_time": 0.2, "iterations": 100},
                "list_invoices": {"max_response_time": 1.0, "iterations": 30}
            },
            "document_operations": {
                "upload_document": {"max_response_time": 5.0, "iterations": 5},
                "process_document": {"max_response_time": 30.0, "iterations": 3},
                "extract_text": {"max_response_time": 10.0, "iterations": 5}
            }
        },
        "throughput_scenarios": {
            "api_endpoints": {
                "get_contracts": {"min_requests_per_second": 100, "duration": 10},
                "get_invoices": {"min_requests_per_second": 80, "duration": 10},
                "health_check": {"min_requests_per_second": 500, "duration": 10}
            },
            "database_operations": {
                "select_queries": {"min_queries_per_second": 1000, "duration": 10},
                "insert_queries": {"min_queries_per_second": 100, "duration": 10},
                "update_queries": {"min_queries_per_second": 50, "duration": 10}
            }
        },
        "memory_usage_scenarios": {
            "document_processing": {
                "max_memory_mb": 500,
                "iterations": 5,
                "operation": "process_large_document"
            },
            "batch_operations": {
                "max_memory_mb": 200,
                "iterations": 10,
                "operation": "process_multiple_contracts"
            }
        },
        "concurrent_user_scenarios": {
            "contract_management": {
                "concurrent_users": 50,
                "operation": "create_contract",
                "max_response_time": 5.0,
                "duration": 30
            },
            "invoice_processing": {
                "concurrent_users": 30,
                "operation": "create_invoice",
                "max_response_time": 3.0,
                "duration": 30
            }
        }
    }


@pytest.fixture
def security_scenarios():
    """Security validation scenarios."""
    return {
        "authentication_scenarios": {
            "valid_credentials": {
                "username": "admin",
                "password": "secure_password_123",
                "expected_result": "authenticated",
                "expected_token": "jwt_token"
            },
            "invalid_credentials": {
                "username": "admin",
                "password": "wrong_password",
                "expected_result": "authentication_failed",
                "expected_status": 401
            },
            "missing_credentials": {
                "username": "",
                "password": "",
                "expected_result": "authentication_failed",
                "expected_status": 401
            }
        },
        "authorization_scenarios": {
            "admin_access": {
                "user_role": "admin",
                "resource": "admin_endpoint",
                "expected_access": "granted",
                "expected_status": 200
            },
            "user_access": {
                "user_role": "user",
                "resource": "admin_endpoint",
                "expected_access": "denied",
                "expected_status": 403
            },
            "viewer_access": {
                "user_role": "viewer",
                "resource": "create_contract",
                "expected_access": "denied",
                "expected_status": 403
            }
        },
        "input_validation_scenarios": {
            "sql_injection": {
                "input": "'; DROP TABLE contracts; --",
                "expected_behavior": "sanitized_or_rejected",
                "expected_status": 400
            },
            "xss_attack": {
                "input": "<script>alert('xss')</script>",
                "expected_behavior": "sanitized_or_rejected",
                "expected_status": 400
            },
            "path_traversal": {
                "input": "../../../etc/passwd",
                "expected_behavior": "rejected",
                "expected_status": 400
            }
        },
        "data_encryption_scenarios": {
            "password_storage": {
                "password": "user_password_123",
                "expected_behavior": "hashed_and_encrypted",
                "algorithm": "bcrypt"
            },
            "sensitive_data": {
                "data": "credit_card_number_1234567890123456",
                "expected_behavior": "encrypted_at_rest",
                "algorithm": "AES-256"
            }
        }
    }


@pytest.fixture
def data_consistency_scenarios():
    """Data consistency validation scenarios."""
    return {
        "referential_integrity": {
            "contract_invoice_relationship": {
                "contract": {"contract_id": "CONS-CONTRACT-001", "title": "Consistency Test Contract"},
                "invoices": [
                    {"invoice_id": "CONS-INV-001", "contract_id": "CONS-CONTRACT-001", "amount": Decimal("1000.00")},
                    {"invoice_id": "CONS-INV-002", "contract_id": "CONS-CONTRACT-001", "amount": Decimal("2000.00")}
                ],
                "expected_consistency": True
            },
            "orphaned_records": {
                "invoice_without_contract": {
                    "invoice_id": "ORPHAN-INV-001",
                    "contract_id": "NON-EXISTENT-CONTRACT",
                    "expected_consistency": False
                }
            }
        },
        "data_accuracy": {
            "calculation_accuracy": {
                "invoice_calculation": {
                    "line_items": [
                        {"quantity": 2, "unit_price": Decimal("50.00"), "expected_total": Decimal("100.00")},
                        {"quantity": 1, "unit_price": Decimal("25.00"), "expected_total": Decimal("25.00")}
                    ],
                    "expected_grand_total": Decimal("125.00"),
                    "tolerance": Decimal("0.01")
                },
                "tax_calculation": {
                    "subtotal": Decimal("1000.00"),
                    "tax_rate": Decimal("0.1"),
                    "expected_tax": Decimal("100.00"),
                    "expected_total": Decimal("1100.00")
                }
            }
        },
        "transaction_consistency": {
            "atomic_operations": {
                "contract_with_invoice": {
                    "operations": [
                        {"type": "create_contract", "data": {"contract_id": "TXN-CONTRACT-001"}},
                        {"type": "create_invoice", "data": {"invoice_id": "TXN-INV-001", "contract_id": "TXN-CONTRACT-001"}}
                    ],
                    "expected_atomicity": True,
                    "rollback_scenario": "invoice_creation_fails"
                }
            }
        }
    }


@pytest.fixture
def validation_thresholds():
    """Validation thresholds configuration."""
    return {
        "performance_thresholds": {
            "max_response_time": 5.0,
            "min_throughput": 100,
            "max_memory_usage": 500,
            "max_cpu_usage": 80.0
        },
        "accuracy_thresholds": {
            "min_success_rate": 0.95,
            "max_error_rate": 0.05,
            "data_precision": 0.99,
            "calculation_accuracy": 0.999
        },
        "security_thresholds": {
            "max_failed_attempts": 3,
            "session_timeout": 3600,
            "password_strength": "strong",
            "encryption_strength": "AES-256"
        },
        "consistency_thresholds": {
            "referential_integrity": 1.0,
            "data_accuracy": 0.99,
            "transaction_atomicity": 1.0
        }
    }


@pytest.fixture
def validation_test_data():
    """Comprehensive validation test data."""
    return {
        "contracts": [
            {
                "contract_id": "VAL-CONTRACT-001",
                "title": "Validation Test Contract 1",
                "vendor": "Test Vendor A",
                "amount": Decimal("10000.00"),
                "currency": "USD",
                "start_date": date(2024, 1, 1),
                "end_date": date(2024, 12, 31),
                "status": "active"
            },
            {
                "contract_id": "VAL-CONTRACT-002",
                "title": "Validation Test Contract 2",
                "vendor": "Test Vendor B",
                "amount": Decimal("25000.00"),
                "currency": "EUR",
                "start_date": date(2024, 2, 1),
                "end_date": date(2024, 11, 30),
                "status": "pending"
            }
        ],
        "invoices": [
            {
                "invoice_id": "VAL-INVOICE-001",
                "contract_id": "VAL-CONTRACT-001",
                "vendor": "Test Vendor A",
                "amount": Decimal("5000.00"),
                "currency": "USD",
                "due_date": date(2024, 6, 30),
                "status": "pending"
            },
            {
                "invoice_id": "VAL-INVOICE-002",
                "contract_id": "VAL-CONTRACT-002",
                "vendor": "Test Vendor B",
                "amount": Decimal("12500.00"),
                "currency": "EUR",
                "due_date": date(2024, 7, 31),
                "status": "paid"
            }
        ],
        "documents": [
            {
                "document_id": "VAL-DOCUMENT-001",
                "filename": "validation_test_contract.pdf",
                "file_path": "/documents/validation/validation_test_contract.pdf",
                "file_size": 1024000,
                "mime_type": "application/pdf",
                "status": "processed"
            },
            {
                "document_id": "VAL-DOCUMENT-002",
                "filename": "validation_test_invoice.pdf",
                "file_path": "/documents/validation/validation_test_invoice.pdf",
                "file_size": 512000,
                "mime_type": "application/pdf",
                "status": "uploaded"
            }
        ],
        "users": [
            {
                "username": "validation_admin",
                "email": "validation.admin@example.com",
                "full_name": "Validation Admin User",
                "role": "admin",
                "is_active": True
            },
            {
                "username": "validation_user",
                "email": "validation.user@example.com",
                "full_name": "Validation Regular User",
                "role": "user",
                "is_active": True
            }
        ]
    }


