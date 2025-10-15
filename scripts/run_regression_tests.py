#!/usr/bin/env python3
"""
Regression Test Automation Script

This script automates the execution of regression tests and generates reports.
It integrates with the regression testing framework to provide comprehensive
regression detection and reporting capabilities.
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

from testing.regression_framework import (
    PerformanceRegressionDetector,
    APIBehaviorRegressionDetector,
    DatabaseSchemaRegressionDetector,
    TestExecutionRegressionDetector,
    RegressionReporter,
    RegressionTestDataManager,
    RegressionBaselineManager,
    RegressionThresholdManager,
    RegressionNotificationSystem,
    RegressionHistoryTracker
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('regression_tests.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class RegressionTestRunner:
    """Main regression test runner."""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config = self._load_config(config_path)
        self.detectors = self._initialize_detectors()
        self.reporter = RegressionReporter()
        self.data_manager = RegressionTestDataManager()
        self.baseline_manager = RegressionBaselineManager()
        self.threshold_manager = RegressionThresholdManager()
        self.notification_system = RegressionNotificationSystem()
        self.history_tracker = RegressionHistoryTracker()
        
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
                    "execution_time": 50.0,
                    "memory_usage": 100.0,
                    "cpu_usage": 75.0,
                    "response_time": 100.0
                },
                "test_coverage": {
                    "minimum_coverage": 80.0,
                    "coverage_decrease": 5.0,
                    "test_failure_increase": 10.0
                }
            },
            "notifications": {
                "enabled": True,
                "methods": ["email", "slack"],
                "severity_thresholds": {
                    "high": ["email", "slack"],
                    "medium": ["slack"],
                    "low": []
                }
            },
            "baseline_version": "v1.0.0",
            "current_version": "v1.1.0"
        }
        
    def _initialize_detectors(self) -> Dict[str, Any]:
        """Initialize regression detectors."""
        return {
            "performance": PerformanceRegressionDetector(),
            "api_behavior": APIBehaviorRegressionDetector(),
            "database_schema": DatabaseSchemaRegressionDetector(),
            "test_execution": TestExecutionRegressionDetector()
        }
        
    def run_regression_tests(self) -> Dict[str, Any]:
        """Run comprehensive regression tests."""
        logger.info("Starting regression test execution")
        
        start_time = time.time()
        results = {
            "timestamp": datetime.now().isoformat(),
            "baseline_version": self.config.get("baseline_version"),
            "current_version": self.config.get("current_version"),
            "regressions": [],
            "summary": {}
        }
        
        try:
            # Load baseline data
            baseline_data = self._load_baseline_data()
            if not baseline_data:
                logger.error("No baseline data found - cannot run regression tests")
                return results
                
            # Load current data
            current_data = self._load_current_data()
            if not current_data:
                logger.error("No current data found - cannot run regression tests")
                return results
                
            # Run performance regression tests
            performance_regressions = self._test_performance_regressions(baseline_data, current_data)
            results["regressions"].extend(performance_regressions)
            
            # Run API behavior regression tests
            api_regressions = self._test_api_behavior_regressions(baseline_data, current_data)
            results["regressions"].extend(api_regressions)
            
            # Run database schema regression tests
            db_regressions = self._test_database_schema_regressions(baseline_data, current_data)
            results["regressions"].extend(db_regressions)
            
            # Run test execution regression tests
            test_regressions = self._test_execution_regressions(baseline_data, current_data)
            results["regressions"].extend(test_regressions)
            
            # Generate summary
            results["summary"] = self._generate_summary(results["regressions"])
            
            # Record in history
            self._record_regression_history(results)
            
            # Send notifications if enabled
            if self.config.get("notifications", {}).get("enabled", False):
                self._send_notifications(results["regressions"])
                
            execution_time = time.time() - start_time
            logger.info(f"Regression tests completed in {execution_time:.2f} seconds")
            
        except Exception as e:
            logger.error(f"Error during regression test execution: {e}")
            results["error"] = str(e)
            
        return results
        
    def _load_baseline_data(self) -> Optional[Dict[str, Any]]:
        """Load baseline data."""
        baseline_version = self.config.get("baseline_version")
        if baseline_version:
            baseline_data = self.baseline_manager.get_baseline(baseline_version)
            if baseline_data:
                logger.info(f"Loaded baseline data for version {baseline_version}")
                return baseline_data
                
        # Try to load from test data manager
        baseline_data = self.data_manager.get_test_dataset("baseline")
        if baseline_data:
            logger.info("Loaded baseline data from test dataset")
            return baseline_data
            
        logger.warning("No baseline data found")
        return None
        
    def _load_current_data(self) -> Optional[Dict[str, Any]]:
        """Load current data."""
        # Try to load from test data manager
        current_data = self.data_manager.get_test_dataset("current")
        if current_data:
            logger.info("Loaded current data from test dataset")
            return current_data
            
        # Generate mock current data for testing
        current_data = self._generate_mock_current_data()
        logger.info("Generated mock current data for testing")
        return current_data
        
    def _generate_mock_current_data(self) -> Dict[str, Any]:
        """Generate mock current data for testing."""
        return {
            "performance": {
                "execution_time": 2.5,  # 150% increase from baseline
                "memory_usage": 200.0,  # 100% increase
                "cpu_usage": 80.0,      # 60% increase
                "response_time": 1.5    # 200% increase
            },
            "api_responses": {
                "GET /api/contracts": {
                    "status_code": 200,
                    "response_time": 1.2,  # 300% increase
                    "data": {
                        "contracts": [
                            {"id": 1, "contract_id": "C-001", "title": "Test Contract"},  # Missing amount
                            {"id": 2, "contract_id": "C-002", "title": "Another Contract", "amount": 2000.00}
                        ],
                        "total": 2
                    }
                }
            },
            "database_schema": {
                "tables": {
                    "contracts": {
                        "columns": {
                            "id": {"type": "INTEGER"},
                            "contract_id": {"type": "VARCHAR(100)"},
                            "title": {"type": "VARCHAR(255)"},
                            "vendor": {"type": "VARCHAR(255)"},
                            # Missing amount column - regression!
                            "currency": {"type": "VARCHAR(3)"}
                        }
                    }
                }
            },
            "test_results": {
                "overall": {
                    "total": 175,
                    "passed": 140,  # 25 fewer passing tests
                    "failed": 35,   # 25 more failing tests
                    "execution_time": 160.0,  # 52% increase
                    "coverage": 73.3  # 10% decrease
                }
            }
        }
        
    def _test_performance_regressions(self, baseline_data: Dict, current_data: Dict) -> List[Dict]:
        """Test for performance regressions."""
        logger.info("Testing performance regressions")
        
        detector = self.detectors["performance"]
        
        # Set thresholds
        thresholds = self.config.get("thresholds", {}).get("performance", {})
        detector.set_thresholds(thresholds)
        
        # Set baseline and current data
        baseline_performance = baseline_data.get("performance", {})
        current_performance = current_data.get("performance", {})
        
        detector.set_baseline(baseline_performance)
        regressions = detector.detect_regressions(current_performance)
        
        logger.info(f"Detected {len(regressions)} performance regressions")
        return [regression.__dict__ for regression in regressions]
        
    def _test_api_behavior_regressions(self, baseline_data: Dict, current_data: Dict) -> List[Dict]:
        """Test for API behavior regressions."""
        logger.info("Testing API behavior regressions")
        
        detector = self.detectors["api_behavior"]
        regressions = []
        
        baseline_responses = baseline_data.get("api_responses", {})
        current_responses = current_data.get("api_responses", {})
        
        # Set baselines
        for endpoint, response in baseline_responses.items():
            detector.set_baseline(endpoint, response)
            
        # Detect regressions
        for endpoint, response in current_responses.items():
            endpoint_regressions = detector.detect_regressions(endpoint, response)
            regressions.extend(endpoint_regressions)
            
        logger.info(f"Detected {len(regressions)} API behavior regressions")
        return [regression.__dict__ for regression in regressions]
        
    def _test_database_schema_regressions(self, baseline_data: Dict, current_data: Dict) -> List[Dict]:
        """Test for database schema regressions."""
        logger.info("Testing database schema regressions")
        
        detector = self.detectors["database_schema"]
        
        baseline_schema = baseline_data.get("database_schema", {})
        current_schema = current_data.get("database_schema", {})
        
        detector.set_baseline(baseline_schema)
        regressions = detector.detect_regressions(current_schema)
        
        logger.info(f"Detected {len(regressions)} database schema regressions")
        return [regression.__dict__ for regression in regressions]
        
    def _test_execution_regressions(self, baseline_data: Dict, current_data: Dict) -> List[Dict]:
        """Test for test execution regressions."""
        logger.info("Testing test execution regressions")
        
        detector = self.detectors["test_execution"]
        
        # Set thresholds
        thresholds = self.config.get("thresholds", {}).get("test_coverage", {})
        detector.set_thresholds(thresholds)
        
        baseline_results = baseline_data.get("test_results", {})
        current_results = current_data.get("test_results", {})
        
        detector.set_baseline(baseline_results)
        regressions = detector.detect_regressions(current_results)
        
        logger.info(f"Detected {len(regressions)} test execution regressions")
        return [regression.__dict__ for regression in regressions]
        
    def _generate_summary(self, regressions: List[Dict]) -> Dict[str, Any]:
        """Generate regression summary."""
        severity_counts = {}
        type_counts = {}
        
        for regression in regressions:
            severity = regression.get("severity", "unknown")
            regression_type = regression.get("type", "unknown")
            
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
            type_counts[regression_type] = type_counts.get(regression_type, 0) + 1
            
        return {
            "total_regressions": len(regressions),
            "severity_distribution": severity_counts,
            "type_distribution": type_counts,
            "has_critical_regressions": severity_counts.get("critical", 0) > 0,
            "has_high_regressions": severity_counts.get("high", 0) > 0
        }
        
    def _record_regression_history(self, results: Dict[str, Any]) -> None:
        """Record regression results in history."""
        for regression in results["regressions"]:
            record = {
                "timestamp": datetime.now(),
                "type": regression.get("type"),
                "severity": regression.get("severity"),
                "details": regression
            }
            self.history_tracker.record_regression(record)
            
    def _send_notifications(self, regressions: List[Dict]) -> None:
        """Send notifications for regressions."""
        notification_config = self.config.get("notifications", {})
        methods = notification_config.get("methods", [])
        severity_thresholds = notification_config.get("severity_thresholds", {})
        
        for regression in regressions:
            severity = regression.get("severity", "low")
            methods_to_use = severity_thresholds.get(severity, [])
            
            for method in methods_to_use:
                if method in methods:
                    self.notification_system.send_notification([regression], method)
                    
    def generate_report(self, results: Dict[str, Any], report_type: str = "summary") -> Dict[str, Any]:
        """Generate regression report."""
        regressions = [regression for regression in results["regressions"]]
        return self.reporter.generate_report(regressions, report_type)
        
    def save_results(self, results: Dict[str, Any], output_path: str) -> None:
        """Save regression test results to file."""
        with open(output_path, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        logger.info(f"Results saved to {output_path}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Run regression tests")
    parser.add_argument("--config", "-c", help="Configuration file path")
    parser.add_argument("--output", "-o", default="regression_results.json", help="Output file path")
    parser.add_argument("--report-type", "-r", default="summary", 
                       choices=["summary", "detailed", "executive"], help="Report type")
    parser.add_argument("--baseline", "-b", help="Baseline version")
    parser.add_argument("--current", "-u", help="Current version")
    
    args = parser.parse_args()
    
    # Initialize runner
    runner = RegressionTestRunner(args.config)
    
    # Override versions if provided
    if args.baseline:
        runner.config["baseline_version"] = args.baseline
    if args.current:
        runner.config["current_version"] = args.current
        
    # Run regression tests
    logger.info("Starting regression test execution")
    results = runner.run_regression_tests()
    
    # Generate report
    report = runner.generate_report(results, args.report_type)
    
    # Save results
    runner.save_results(results, args.output)
    runner.save_results(report, args.output.replace('.json', '_report.json'))
    
    # Print summary
    summary = results.get("summary", {})
    print(f"\nRegression Test Summary:")
    print(f"Total Regressions: {summary.get('total_regressions', 0)}")
    print(f"Critical: {summary.get('severity_distribution', {}).get('critical', 0)}")
    print(f"High: {summary.get('severity_distribution', {}).get('high', 0)}")
    print(f"Medium: {summary.get('severity_distribution', {}).get('medium', 0)}")
    print(f"Low: {summary.get('severity_distribution', {}).get('low', 0)}")
    
    if summary.get("has_critical_regressions", False):
        print("\n⚠️  CRITICAL REGRESSIONS DETECTED - IMMEDIATE ACTION REQUIRED")
        sys.exit(1)
    elif summary.get("has_high_regressions", False):
        print("\n⚠️  HIGH SEVERITY REGRESSIONS DETECTED - ATTENTION REQUIRED")
        sys.exit(1)
    else:
        print("\n✅ Regression tests completed successfully")
        sys.exit(0)


if __name__ == "__main__":
    main()
