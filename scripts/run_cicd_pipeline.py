#!/usr/bin/env python3
"""
CI/CD Pipeline Automation Script

This script automates the execution of CI/CD pipeline testing and validation.
It provides comprehensive pipeline management, monitoring, and reporting capabilities.

Usage:
    python scripts/run_cicd_pipeline.py [options]

Options:
    --validate-config    Validate pipeline configuration
    --run-tests         Run all pipeline tests
    --generate-report   Generate pipeline report
    --monitor          Monitor pipeline execution
    --check-alerts     Check for pipeline alerts
    --help             Show this help message
"""

import argparse
import json
import sys
import time
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from testing.cicd_pipeline import (
    CICDPipelineValidator,
    CICDPipelineIntegration,
    CICDPipelineMonitor,
    CICDPipelineReporter,
    CICDPipelineManager
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class CICDPipelineAutomation:
    """CI/CD Pipeline Automation Manager."""
    
    def __init__(self):
        self.manager = CICDPipelineManager()
        self.config_path = Path("config/cicd_pipeline_config.json")
        self.load_config()
    
    def load_config(self):
        """Load pipeline configuration."""
        if self.config_path.exists():
            with open(self.config_path, 'r') as f:
                self.config = json.load(f)
        else:
            logger.error(f"Configuration file not found: {self.config_path}")
            sys.exit(1)
    
    def validate_configuration(self) -> Dict[str, Any]:
        """Validate pipeline configuration."""
        logger.info("Validating CI/CD pipeline configuration...")
        
        try:
            result = self.manager.validator.validate_pipeline_configuration(
                self.manager.validator.config
            )
            
            if result['valid']:
                logger.info("✅ Pipeline configuration is valid")
                logger.info(f"Jobs found: {result['jobs_found']}")
                logger.info(f"Jobs required: {result['jobs_required']}")
            else:
                logger.error("❌ Pipeline configuration validation failed")
                for error in result['errors']:
                    logger.error(f"  - {error}")
            
            if result['warnings']:
                logger.warning("⚠️  Configuration warnings:")
                for warning in result['warnings']:
                    logger.warning(f"  - {warning}")
            
            return result
            
        except Exception as e:
            logger.error(f"Configuration validation failed: {str(e)}")
            return {"valid": False, "errors": [str(e)], "warnings": []}
    
    def run_integration_tests(self) -> Dict[str, Any]:
        """Run pipeline integration tests."""
        logger.info("Running CI/CD pipeline integration tests...")
        
        try:
            results = {}
            
            # Test unit test integration
            logger.info("Testing unit test integration...")
            unit_result = self.manager.integration.integrate_unit_tests()
            results['unit_tests'] = unit_result
            
            if unit_result['status'] == 'success':
                logger.info(f"✅ Unit tests integrated: {unit_result['test_count']} tests")
            else:
                logger.error(f"❌ Unit test integration failed: {unit_result.get('error', 'Unknown error')}")
            
            # Test regression test integration
            logger.info("Testing regression test integration...")
            regression_result = self.manager.integration.integrate_regression_tests()
            results['regression_tests'] = regression_result
            
            if regression_result['status'] == 'success':
                logger.info(f"✅ Regression tests integrated: {regression_result['test_count']} tests")
            else:
                logger.error(f"❌ Regression test integration failed: {regression_result.get('error', 'Unknown error')}")
            
            # Test functionality validation integration
            logger.info("Testing functionality validation integration...")
            functionality_result = self.manager.integration.integrate_functionality_validation()
            results['functionality_validation'] = functionality_result
            
            if functionality_result['status'] == 'success':
                logger.info(f"✅ Functionality validation integrated: {functionality_result['validation_count']} validations")
            else:
                logger.error(f"❌ Functionality validation integration failed: {functionality_result.get('error', 'Unknown error')}")
            
            # Test security tools integration
            logger.info("Testing security tools integration...")
            security_result = self.manager.integration.integrate_security_tools()
            results['security_tools'] = security_result
            
            if security_result['status'] in ['success', 'partial']:
                logger.info(f"✅ Security tools integrated: {security_result['tools_integrated']}/{security_result['total_tools']} tools")
            else:
                logger.error(f"❌ Security tools integration failed: {security_result.get('error', 'Unknown error')}")
            
            # Test deployment processes integration
            logger.info("Testing deployment processes integration...")
            deployment_result = self.manager.integration.integrate_deployment_processes()
            results['deployment_processes'] = deployment_result
            
            if deployment_result['status'] in ['success', 'partial']:
                logger.info(f"✅ Deployment processes integrated: {deployment_result['environments_configured']}/{deployment_result['total_environments']} environments")
            else:
                logger.error(f"❌ Deployment processes integration failed: {deployment_result.get('error', 'Unknown error')}")
            
            return results
            
        except Exception as e:
            logger.error(f"Integration tests failed: {str(e)}")
            return {"error": str(e)}
    
    def run_pipeline_validation(self) -> Dict[str, Any]:
        """Run comprehensive pipeline validation."""
        logger.info("Running comprehensive CI/CD pipeline validation...")
        
        try:
            result = self.manager.run_pipeline_validation()
            
            # Validate configuration
            config_result = result['configuration_validation']
            if config_result['valid']:
                logger.info("✅ Pipeline configuration validation passed")
            else:
                logger.error("❌ Pipeline configuration validation failed")
                for error in config_result['errors']:
                    logger.error(f"  - {error}")
            
            # Validate integrations
            integration_result = result['integration_validation']
            
            # Check unit tests integration
            if integration_result['unit_tests']['status'] == 'success':
                logger.info(f"✅ Unit tests integration: {integration_result['unit_tests']['test_count']} tests")
            else:
                logger.error(f"❌ Unit tests integration failed")
            
            # Check regression tests integration
            if integration_result['regression_tests']['status'] == 'success':
                logger.info(f"✅ Regression tests integration: {integration_result['regression_tests']['test_count']} tests")
            else:
                logger.error(f"❌ Regression tests integration failed")
            
            # Check functionality validation integration
            if integration_result['functionality_validation']['status'] == 'success':
                logger.info(f"✅ Functionality validation integration: {integration_result['functionality_validation']['validation_count']} validations")
            else:
                logger.error(f"❌ Functionality validation integration failed")
            
            # Check security tools integration
            if integration_result['security_tools']['status'] in ['success', 'partial']:
                logger.info(f"✅ Security tools integration: {integration_result['security_tools']['tools_integrated']} tools")
            else:
                logger.error(f"❌ Security tools integration failed")
            
            # Check deployment processes integration
            if integration_result['deployment_processes']['status'] in ['success', 'partial']:
                logger.info(f"✅ Deployment processes integration: {integration_result['deployment_processes']['environments_configured']} environments")
            else:
                logger.error(f"❌ Deployment processes integration failed")
            
            # Check monitoring setup
            monitoring_result = result['monitoring_setup']
            if monitoring_result['enabled']:
                logger.info("✅ Pipeline monitoring is enabled")
            else:
                logger.warning("⚠️  Pipeline monitoring is disabled")
            
            return result
            
        except Exception as e:
            logger.error(f"Pipeline validation failed: {str(e)}")
            return {"error": str(e)}
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive pipeline report."""
        logger.info("Generating CI/CD pipeline report...")
        
        try:
            report = self.manager.generate_pipeline_report()
            
            # Log report summary
            summary = report['summary']
            logger.info("📊 Pipeline Report Summary:")
            logger.info(f"  Status: {summary['pipeline_status']}")
            logger.info(f"  Total Jobs: {summary['total_jobs']}")
            logger.info(f"  Successful Jobs: {summary['successful_jobs']}")
            logger.info(f"  Failed Jobs: {summary['failed_jobs']}")
            logger.info(f"  Execution Time: {summary['execution_time']}s")
            logger.info(f"  Coverage: {summary['coverage']}%")
            logger.info(f"  Security Score: {summary['security_score']}")
            logger.info(f"  Performance Score: {summary['performance_score']}")
            
            # Log test results
            test_results = report['test_results']
            logger.info("🧪 Test Results:")
            for test_type, results in test_results.items():
                logger.info(f"  {test_type}: {results['passed']}/{results['total']} passed ({results['coverage']}% coverage)")
            
            # Log security results
            security_results = report['security_results']
            logger.info("🔒 Security Results:")
            for tool, results in security_results.items():
                logger.info(f"  {tool}: {results['score']}% score")
            
            # Log performance results
            performance_results = report['performance_results']
            logger.info("⚡ Performance Results:")
            for test_type, results in performance_results.items():
                status_emoji = "✅" if results['status'] == 'pass' else "❌"
                logger.info(f"  {test_type}: {results['execution_time']}s (threshold: {results['threshold']}s) {status_emoji}")
            
            # Log recommendations
            recommendations = report['recommendations']
            if recommendations:
                logger.info("💡 Recommendations:")
                for rec in recommendations:
                    logger.info(f"  - {rec}")
            
            return report
            
        except Exception as e:
            logger.error(f"Report generation failed: {str(e)}")
            return {"error": str(e)}
    
    def monitor_pipeline(self) -> Dict[str, Any]:
        """Monitor pipeline execution."""
        logger.info("Monitoring CI/CD pipeline...")
        
        try:
            # Collect metrics
            metrics = self.manager.collect_pipeline_metrics()
            
            logger.info("📈 Pipeline Metrics:")
            logger.info(f"  Execution Time: {metrics['execution_time']}s")
            logger.info(f"  Success Rate: {metrics['success_rate']:.2%}")
            logger.info(f"  Failure Rate: {metrics['failure_rate']:.2%}")
            logger.info(f"  Coverage: {metrics['coverage']}%")
            logger.info(f"  Security Score: {metrics['security_score']}")
            logger.info(f"  Performance Score: {metrics['performance_score']}")
            
            return metrics
            
        except Exception as e:
            logger.error(f"Pipeline monitoring failed: {str(e)}")
            return {"error": str(e)}
    
    def check_alerts(self) -> List[Dict[str, Any]]:
        """Check for pipeline alerts."""
        logger.info("Checking CI/CD pipeline alerts...")
        
        try:
            alerts = self.manager.check_pipeline_alerts()
            
            if alerts:
                logger.warning(f"⚠️  {len(alerts)} alerts found:")
                for alert in alerts:
                    logger.warning(f"  - {alert['type']}: {alert['message']} (severity: {alert['severity']})")
            else:
                logger.info("✅ No alerts found")
            
            return alerts
            
        except Exception as e:
            logger.error(f"Alert checking failed: {str(e)}")
            return []


def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description="CI/CD Pipeline Automation Script",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/run_cicd_pipeline.py --validate-config
  python scripts/run_cicd_pipeline.py --run-tests
  python scripts/run_cicd_pipeline.py --generate-report
  python scripts/run_cicd_pipeline.py --monitor
  python scripts/run_cicd_pipeline.py --check-alerts
        """
    )
    
    parser.add_argument(
        '--validate-config',
        action='store_true',
        help='Validate pipeline configuration'
    )
    
    parser.add_argument(
        '--run-tests',
        action='store_true',
        help='Run all pipeline tests'
    )
    
    parser.add_argument(
        '--generate-report',
        action='store_true',
        help='Generate pipeline report'
    )
    
    parser.add_argument(
        '--monitor',
        action='store_true',
        help='Monitor pipeline execution'
    )
    
    parser.add_argument(
        '--check-alerts',
        action='store_true',
        help='Check for pipeline alerts'
    )
    
    parser.add_argument(
        '--output-format',
        choices=['json', 'html', 'pdf'],
        default='json',
        help='Output format for reports (default: json)'
    )
    
    parser.add_argument(
        '--output-file',
        type=str,
        help='Output file path for reports'
    )
    
    args = parser.parse_args()
    
    # If no arguments provided, show help
    if not any([
        args.validate_config,
        args.run_tests,
        args.generate_report,
        args.monitor,
        args.check_alerts
    ]):
        parser.print_help()
        return
    
    # Initialize automation
    automation = CICDPipelineAutomation()
    
    try:
        # Execute requested operations
        if args.validate_config:
            result = automation.validate_configuration()
            if args.output_file:
                with open(args.output_file, 'w') as f:
                    json.dump(result, f, indent=2)
        
        if args.run_tests:
            result = automation.run_pipeline_validation()
            if args.output_file:
                with open(args.output_file, 'w') as f:
                    json.dump(result, f, indent=2)
        
        if args.generate_report:
            result = automation.generate_report()
            if args.output_file:
                if args.output_format == 'json':
                    with open(args.output_file, 'w') as f:
                        json.dump(result, f, indent=2)
                else:
                    # Export in requested format
                    exported = automation.manager.reporter.export_report(result, args.output_format)
                    with open(args.output_file, 'wb' if args.output_format == 'pdf' else 'w') as f:
                        f.write(exported)
        
        if args.monitor:
            result = automation.monitor_pipeline()
            if args.output_file:
                with open(args.output_file, 'w') as f:
                    json.dump(result, f, indent=2)
        
        if args.check_alerts:
            alerts = automation.check_alerts()
            if args.output_file:
                with open(args.output_file, 'w') as f:
                    json.dump(alerts, f, indent=2)
        
        logger.info("✅ CI/CD pipeline automation completed successfully")
        
    except KeyboardInterrupt:
        logger.info("🛑 CI/CD pipeline automation interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ CI/CD pipeline automation failed: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
