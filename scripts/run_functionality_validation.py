#!/usr/bin/env python3
"""
Functionality Validation Automation Script

This script automates the execution of functionality validation tests and generates reports.
It integrates with the functionality validation framework to provide comprehensive
validation testing and reporting capabilities.
"""

import sys
import os
import json
import time
import argparse
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from testing.functionality_validation import (
    EndToEndValidator,
    DataFlowValidator,
    BusinessLogicValidator,
    IntegrationValidator,
    UserWorkflowValidator,
    ErrorHandlingValidator,
    PerformanceValidator,
    SecurityValidator,
    DataConsistencyValidator,
    ValidationReporter,
    ValidationDataManager,
    ValidationThresholdManager,
    ValidationAutomation,
    ValidationIntegrator
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('functionality_validation.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class FunctionalityValidationRunner:
    """Main functionality validation runner."""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config = self._load_config(config_path)
        self.validators = self._initialize_validators()
        self.reporter = ValidationReporter()
        self.data_manager = ValidationDataManager()
        self.threshold_manager = ValidationThresholdManager()
        self.automation = ValidationAutomation()
        self.integrator = ValidationIntegrator()
        
    def _load_config(self, config_path: Optional[str]) -> Dict[str, Any]:
        """Load configuration from file or use defaults."""
        if config_path and os.path.exists(config_path):
            with open(config_path, 'r') as f:
                return json.load(f)
        else:
            return self._get_default_config()
            
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration."""
        return {
            "thresholds": {
                "performance": {
                    "max_response_time": 5.0,
                    "min_throughput": 100,
                    "max_memory_usage": 500
                },
                "accuracy": {
                    "min_success_rate": 0.95,
                    "max_error_rate": 0.05,
                    "data_precision": 0.99
                },
                "security": {
                    "max_failed_attempts": 3,
                    "session_timeout": 3600,
                    "password_strength": "strong"
                }
            },
            "validations": {
                "end_to_end": True,
                "data_flow": True,
                "business_logic": True,
                "integration": True,
                "user_workflow": True,
                "error_handling": True,
                "performance": True,
                "security": True,
                "data_consistency": True
            },
            "automation": {
                "enabled": True,
                "schedule": "daily",
                "time": "03:00",
                "notifications": ["email", "slack"]
            }
        }
        
    def _initialize_validators(self) -> Dict[str, Any]:
        """Initialize validation validators."""
        return {
            "end_to_end": EndToEndValidator(),
            "data_flow": DataFlowValidator(),
            "business_logic": BusinessLogicValidator(),
            "integration": IntegrationValidator(),
            "user_workflow": UserWorkflowValidator(),
            "error_handling": ErrorHandlingValidator(),
            "performance": PerformanceValidator(),
            "security": SecurityValidator(),
            "data_consistency": DataConsistencyValidator()
        }
        
    def run_functionality_validations(self) -> Dict[str, Any]:
        """Run comprehensive functionality validations."""
        logger.info("Starting functionality validation execution")
        
        start_time = time.time()
        results = {
            "timestamp": datetime.now().isoformat(),
            "validations": {},
            "summary": {}
        }
        
        try:
            # Load validation data
            validation_data = self._load_validation_data()
            if not validation_data:
                logger.error("No validation data found - cannot run validations")
                return results
                
            # Run each validation type
            validation_config = self.config.get("validations", {})
            
            for validation_type, enabled in validation_config.items():
                if enabled and validation_type in self.validators:
                    logger.info(f"Running {validation_type} validation")
                    validation_result = self._run_validation(validation_type, validation_data)
                    results["validations"][validation_type] = validation_result
                    
            # Generate summary
            results["summary"] = self._generate_summary(results["validations"])
            
            # Configure automation if enabled
            if self.config.get("automation", {}).get("enabled", False):
                self._configure_automation()
                
            execution_time = time.time() - start_time
            logger.info(f"Functionality validations completed in {execution_time:.2f} seconds")
            
        except Exception as e:
            logger.error(f"Error during functionality validation execution: {e}")
            results["error"] = str(e)
            
        return results
        
    def _load_validation_data(self) -> Optional[Dict[str, Any]]:
        """Load validation test data."""
        # Try to load from data manager
        validation_data = self.data_manager.get_validation_dataset("comprehensive")
        if validation_data:
            logger.info("Loaded validation data from dataset")
            return validation_data
            
        # Generate mock validation data for testing
        validation_data = self._generate_mock_validation_data()
        logger.info("Generated mock validation data for testing")
        return validation_data
        
    def _generate_mock_validation_data(self) -> Dict[str, Any]:
        """Generate mock validation data for testing."""
        return {
            "end_to_end_workflow": {
                "contract_management_workflow": {
                    "steps": [
                        {
                            "step": "create_contract",
                            "data": {
                                "contract_id": "MOCK-CONTRACT-001",
                                "title": "Mock Test Contract",
                                "vendor": "Mock Vendor",
                                "amount": 10000.00,
                                "currency": "USD"
                            },
                            "expected_result": {"status": "created"}
                        }
                    ]
                }
            },
            "data_flow_scenarios": {
                "contract_data_flow": {
                    "input": {"raw_data": {"title": "Test Contract", "amount": "1000.00"}},
                    "processing": {"validation": True, "transformation": True},
                    "output": {"contract_id": "CF-001", "status": "active"}
                }
            },
            "business_logic_scenarios": {
                "contract_validation_rules": {
                    "amount_validation": [
                        {"amount": 1000.00, "expected_valid": True}
                    ]
                }
            },
            "integration_scenarios": {
                "database_integration": {
                    "contract_operations": {
                        "create": {
                            "data": {"contract_id": "INT-CONTRACT-001"},
                            "expected_result": {"id": 1}
                        }
                    }
                }
            },
            "user_workflow_scenarios": {
                "admin_workflows": {
                    "contract_management": {
                        "user_role": "admin",
                        "workflow_steps": ["create_contract", "approve_contract"],
                        "expected_success": True
                    }
                }
            },
            "error_handling_scenarios": {
                "validation_errors": {
                    "missing_required_fields": {
                        "input": {"title": "Test"},  # Missing required fields
                        "expected_error": "validation_error",
                        "expected_status": 422
                    }
                }
            },
            "performance_scenarios": {
                "response_time_scenarios": {
                    "contract_operations": {
                        "create_contract": {"max_response_time": 2.0, "iterations": 10}
                    }
                }
            },
            "security_scenarios": {
                "authentication_scenarios": {
                    "valid_credentials": {
                        "username": "admin",
                        "password": "password",
                        "expected_result": "authenticated"
                    }
                }
            },
            "data_consistency_scenarios": {
                "referential_integrity": {
                    "contract_invoice_relationship": {
                        "contract": {"contract_id": "CONS-CONTRACT-001"},
                        "invoices": [{"invoice_id": "CONS-INV-001", "contract_id": "CONS-CONTRACT-001"}],
                        "expected_consistency": True
                    }
                }
            }
        }
        
    def _run_validation(self, validation_type: str, validation_data: Dict[str, Any]) -> Dict[str, Any]:
        """Run a specific validation type."""
        validator = self.validators[validation_type]
        
        try:
            if validation_type == "end_to_end":
                workflow_data = validation_data.get("end_to_end_workflow", {})
                return validator.validate_workflow(workflow_data)
            elif validation_type == "data_flow":
                flow_data = validation_data.get("data_flow_scenarios", {})
                return validator.validate_data_flow(flow_data)
            elif validation_type == "business_logic":
                logic_data = validation_data.get("business_logic_scenarios", {})
                return validator.validate_business_logic(logic_data)
            elif validation_type == "integration":
                integration_data = validation_data.get("integration_scenarios", {})
                return validator.validate_integrations(integration_data)
            elif validation_type == "user_workflow":
                workflow_data = validation_data.get("user_workflow_scenarios", {})
                return validator.validate_workflows(workflow_data)
            elif validation_type == "error_handling":
                error_data = validation_data.get("error_handling_scenarios", {})
                return validator.validate_error_handling(error_data)
            elif validation_type == "performance":
                perf_data = validation_data.get("performance_scenarios", {})
                return validator.validate_performance(perf_data)
            elif validation_type == "security":
                security_data = validation_data.get("security_scenarios", {})
                return validator.validate_security(security_data)
            elif validation_type == "data_consistency":
                consistency_data = validation_data.get("data_consistency_scenarios", {})
                return validator.validate_consistency(consistency_data)
            else:
                return {"status": "skipped", "message": f"Unknown validation type: {validation_type}"}
                
        except Exception as e:
            logger.error(f"Validation {validation_type} failed: {e}")
            return {"status": "failed", "error": str(e)}
            
    def _generate_summary(self, validations: Dict[str, Any]) -> Dict[str, Any]:
        """Generate validation summary."""
        total_validations = len(validations)
        passed_validations = sum(1 for result in validations.values() 
                               if isinstance(result, dict) and result.get("status") == "passed")
        
        return {
            "total_validations": total_validations,
            "passed_validations": passed_validations,
            "failed_validations": total_validations - passed_validations,
            "success_rate": passed_validations / total_validations if total_validations > 0 else 0,
            "overall_status": "passed" if passed_validations == total_validations else "failed"
        }
        
    def _configure_automation(self) -> None:
        """Configure validation automation."""
        automation_config = self.config.get("automation", {})
        self.automation.configure(automation_config)
        
    def generate_report(self, results: Dict[str, Any], report_type: str = "summary") -> Dict[str, Any]:
        """Generate functionality validation report."""
        validations = results.get("validations", {})
        return self.reporter.generate_report(validations, report_type)
        
    def save_results(self, results: Dict[str, Any], output_path: str) -> None:
        """Save functionality validation results to file."""
        with open(output_path, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        logger.info(f"Results saved to {output_path}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Run functionality validation tests")
    parser.add_argument("--config", "-c", help="Configuration file path")
    parser.add_argument("--output", "-o", default="functionality_validation_results.json", help="Output file path")
    parser.add_argument("--report-type", "-r", default="summary", 
                       choices=["summary", "detailed", "executive"], help="Report type")
    parser.add_argument("--validation-type", "-v", help="Run specific validation type only")
    
    args = parser.parse_args()
    
    # Initialize runner
    runner = FunctionalityValidationRunner(args.config)
    
    # Run functionality validations
    logger.info("Starting functionality validation execution")
    results = runner.run_functionality_validations()
    
    # Generate report
    report = runner.generate_report(results, args.report_type)
    
    # Save results
    runner.save_results(results, args.output)
    runner.save_results(report, args.output.replace('.json', '_report.json'))
    
    # Print summary
    summary = results.get("summary", {})
    print(f"\nFunctionality Validation Summary:")
    print(f"Total Validations: {summary.get('total_validations', 0)}")
    print(f"Passed: {summary.get('passed_validations', 0)}")
    print(f"Failed: {summary.get('failed_validations', 0)}")
    print(f"Success Rate: {summary.get('success_rate', 0):.2%}")
    
    if summary.get("overall_status") == "failed":
        print("\n⚠️  VALIDATION FAILURES DETECTED - REVIEW REQUIRED")
        sys.exit(1)
    else:
        print("\n✅ All functionality validations completed successfully")
        sys.exit(0)


if __name__ == "__main__":
    main()
