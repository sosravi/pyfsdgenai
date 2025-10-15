"""
Regression Testing Framework

This module provides comprehensive regression testing capabilities including:
1. Performance regression detection
2. API behavior regression detection
3. Database schema regression detection
4. Test execution regression detection
5. Regression reporting and notification
"""

import json
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, asdict
from enum import Enum
import sqlalchemy as sa
from sqlalchemy.orm import Session
from sqlalchemy import inspect

logger = logging.getLogger(__name__)


class RegressionSeverity(Enum):
    """Regression severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class RegressionType(Enum):
    """Types of regressions."""
    PERFORMANCE = "performance_regression"
    API_BEHAVIOR = "api_behavior_regression"
    DATABASE_SCHEMA = "database_schema_regression"
    TEST_EXECUTION = "test_execution_regression"
    FUNCTIONAL = "functional_regression"


@dataclass
class RegressionResult:
    """Represents a detected regression."""
    type: str
    severity: str
    metric: Optional[str] = None
    baseline_value: Optional[Union[float, int, str, Dict]] = None
    current_value: Optional[Union[float, int, str, Dict]] = None
    regression_percentage: Optional[float] = None
    description: Optional[str] = None
    timestamp: datetime = None
    affected_components: Optional[List[str]] = None
    recommendations: Optional[List[str]] = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


class RegressionDetector:
    """Base class for regression detection."""
    
    def __init__(self):
        self.baseline_metrics: Dict[str, Any] = {}
        self.current_metrics: Dict[str, Any] = {}
        self.thresholds: Dict[str, float] = {}
        
    def set_baseline(self, metrics: Dict[str, Any]) -> None:
        """Set baseline metrics for comparison."""
        self.baseline_metrics = metrics.copy()
        logger.info(f"Baseline metrics set: {len(metrics)} metrics")
        
    def set_current(self, metrics: Dict[str, Any]) -> None:
        """Set current metrics for comparison."""
        self.current_metrics = metrics.copy()
        logger.info(f"Current metrics set: {len(metrics)} metrics")
        
    def set_thresholds(self, thresholds: Dict[str, float]) -> None:
        """Set regression detection thresholds."""
        self.thresholds = thresholds.copy()
        logger.info(f"Thresholds set: {len(thresholds)} thresholds")
        
    def detect_regressions(self, current_metrics: Optional[Dict[str, Any]] = None) -> List[RegressionResult]:
        """Detect regressions by comparing current metrics with baseline."""
        if current_metrics:
            self.set_current(current_metrics)
            
        regressions = []
        
        for metric, current_value in self.current_metrics.items():
            if metric in self.baseline_metrics:
                baseline_value = self.baseline_metrics[metric]
                regression = self._compare_metric(metric, baseline_value, current_value)
                if regression:
                    regressions.append(regression)
                    
        logger.info(f"Detected {len(regressions)} regressions")
        return regressions
        
    def _compare_metric(self, metric: str, baseline: Any, current: Any) -> Optional[RegressionResult]:
        """Compare a single metric and detect regression."""
        if isinstance(baseline, (int, float)) and isinstance(current, (int, float)):
            if baseline == 0:
                return None  # Avoid division by zero
                
            percentage_change = ((current - baseline) / baseline) * 100
            
            # Check if regression exceeds threshold
            threshold = self.thresholds.get(metric, 50.0)  # Default 50% threshold
            
            if percentage_change > threshold:
                severity = self._determine_severity(percentage_change)
                return RegressionResult(
                    type=RegressionType.PERFORMANCE.value,
                    severity=severity,
                    metric=metric,
                    baseline_value=baseline,
                    current_value=current,
                    regression_percentage=percentage_change,
                    description=f"{metric} increased by {percentage_change:.1f}%"
                )
                
        return None
        
    def _determine_severity(self, percentage_change: float) -> str:
        """Determine regression severity based on percentage change."""
        if percentage_change >= 200:
            return RegressionSeverity.CRITICAL.value
        elif percentage_change >= 100:
            return RegressionSeverity.HIGH.value
        elif percentage_change >= 50:
            return RegressionSeverity.MEDIUM.value
        else:
            return RegressionSeverity.LOW.value


class PerformanceRegressionDetector(RegressionDetector):
    """Detects performance regressions."""
    
    def __init__(self):
        super().__init__()
        self.default_thresholds = {
            "execution_time": 50.0,
            "memory_usage": 100.0,
            "cpu_usage": 75.0,
            "response_time": 100.0,
            "database_queries": 100.0
        }
        self.set_thresholds(self.default_thresholds)


class APIBehaviorRegressionDetector:
    """Detects API behavior regressions."""
    
    def __init__(self):
        self.baseline_responses: Dict[str, Dict] = {}
        self.current_responses: Dict[str, Dict] = {}
        
    def set_baseline(self, endpoint: str, response: Dict[str, Any]) -> None:
        """Set baseline API response for an endpoint."""
        self.baseline_responses[endpoint] = response.copy()
        logger.info(f"Baseline response set for {endpoint}")
        
    def detect_regressions(self, endpoint: str, current_response: Dict[str, Any]) -> List[RegressionResult]:
        """Detect regressions in API behavior."""
        if endpoint not in self.baseline_responses:
            logger.warning(f"No baseline response for endpoint {endpoint}")
            return []
            
        baseline = self.baseline_responses[endpoint]
        regressions = []
        
        # Check response time regression
        if "response_time" in baseline and "response_time" in current_response:
            baseline_time = baseline["response_time"]
            current_time = current_response["response_time"]
            
            if current_time > baseline_time * 2:  # 100% increase threshold
                regressions.append(RegressionResult(
                    type=RegressionType.API_BEHAVIOR.value,
                    severity=RegressionSeverity.MEDIUM.value,
                    metric="response_time",
                    baseline_value=baseline_time,
                    current_value=current_time,
                    regression_percentage=((current_time - baseline_time) / baseline_time) * 100,
                    description=f"Response time increased from {baseline_time}s to {current_time}s"
                ))
                
        # Check status code changes
        if baseline.get("status_code") != current_response.get("status_code"):
            regressions.append(RegressionResult(
                type=RegressionType.API_BEHAVIOR.value,
                severity=RegressionSeverity.HIGH.value,
                metric="status_code",
                baseline_value=baseline.get("status_code"),
                current_value=current_response.get("status_code"),
                description=f"Status code changed from {baseline.get('status_code')} to {current_response.get('status_code')}"
            ))
            
        # Check data structure changes
        if "data" in baseline and "data" in current_response:
            data_regressions = self._compare_data_structures(baseline["data"], current_response["data"])
            regressions.extend(data_regressions)
        elif "data" in baseline and "data" not in current_response:
            regressions.append(RegressionResult(
                type=RegressionType.API_BEHAVIOR.value,
                severity=RegressionSeverity.HIGH.value,
                metric="missing_data_field",
                baseline_value="data",
                current_value=None,
                description="Missing data field in response"
            ))
            
        return regressions
        
    def _compare_data_structures(self, baseline_data: Dict, current_data: Dict) -> List[RegressionResult]:
        """Compare data structures for changes."""
        regressions = []
        
        # Check for missing fields
        baseline_keys = set(baseline_data.keys())
        current_keys = set(current_data.keys())
        
        missing_fields = baseline_keys - current_keys
        if missing_fields:
            regressions.append(RegressionResult(
                type=RegressionType.API_BEHAVIOR.value,
                severity=RegressionSeverity.MEDIUM.value,
                metric="missing_fields",
                baseline_value=list(missing_fields),
                current_value=None,
                description=f"Missing fields: {', '.join(missing_fields)}"
            ))
            
        # Check for new fields
        new_fields = current_keys - baseline_keys
        if new_fields:
            regressions.append(RegressionResult(
                type=RegressionType.API_BEHAVIOR.value,
                severity=RegressionSeverity.LOW.value,
                metric="new_fields",
                baseline_value=None,
                current_value=list(new_fields),
                description=f"New fields: {', '.join(new_fields)}"
            ))
            
        return regressions


class DatabaseSchemaRegressionDetector:
    """Detects database schema regressions."""
    
    def __init__(self):
        self.baseline_schema: Dict[str, Any] = {}
        self.current_schema: Dict[str, Any] = {}
        
    def set_baseline(self, schema: Dict[str, Any]) -> None:
        """Set baseline database schema."""
        self.baseline_schema = schema.copy()
        logger.info("Baseline database schema set")
        
    def detect_regressions(self, current_schema: Dict[str, Any]) -> List[RegressionResult]:
        """Detect database schema regressions."""
        self.current_schema = current_schema.copy()
        regressions = []
        
        # Check for missing tables
        baseline_tables = set(self.baseline_schema.get("tables", {}).keys())
        current_tables = set(self.current_schema.get("tables", {}).keys())
        
        missing_tables = baseline_tables - current_tables
        if missing_tables:
            regressions.append(RegressionResult(
                type=RegressionType.DATABASE_SCHEMA.value,
                severity=RegressionSeverity.CRITICAL.value,
                metric="missing_tables",
                baseline_value=list(missing_tables),
                current_value=None,
                description=f"Missing tables: {', '.join(missing_tables)}"
            ))
            
        # Check for missing columns in existing tables
        for table_name in baseline_tables & current_tables:
            baseline_table = self.baseline_schema["tables"][table_name]
            current_table = self.current_schema["tables"][table_name]
            
            # Handle both list and dict formats for columns
            if isinstance(baseline_table.get("columns"), list):
                baseline_columns = set(baseline_table.get("columns", []))
            else:
                baseline_columns = set(baseline_table.get("columns", {}).keys())
                
            if isinstance(current_table.get("columns"), list):
                current_columns = set(current_table.get("columns", []))
            else:
                current_columns = set(current_table.get("columns", {}).keys())
            
            missing_columns = baseline_columns - current_columns
            if missing_columns:
                regressions.append(RegressionResult(
                    type=RegressionType.DATABASE_SCHEMA.value,
                    severity=RegressionSeverity.HIGH.value,
                    metric="missing_column",
                    baseline_value=list(missing_columns),
                    current_value=None,
                    description=f"Missing columns in {table_name}: {', '.join(missing_columns)}",
                    affected_components=[table_name]
                ))
                
        return regressions


class TestExecutionRegressionDetector(RegressionDetector):
    """Detects test execution regressions."""
    
    def __init__(self):
        super().__init__()
        self.default_thresholds = {
            "execution_time": 50.0,
            "coverage": 5.0,  # 5% decrease threshold
            "test_failure_increase": 10.0  # 10% increase threshold
        }
        self.set_thresholds(self.default_thresholds)
        
    def detect_regressions(self, current_results: Dict[str, Any]) -> List[RegressionResult]:
        """Detect test execution regressions."""
        regressions = []
        
        # Check overall test results
        if "overall" in self.baseline_metrics and "overall" in current_results:
            overall_regressions = self._compare_test_results(
                self.baseline_metrics["overall"], 
                current_results["overall"]
            )
            regressions.extend(overall_regressions)
            
        # Check individual test categories
        for category in ["unit_tests", "integration_tests", "regression_tests"]:
            if category in self.baseline_metrics and category in current_results:
                category_regressions = self._compare_test_results(
                    self.baseline_metrics[category],
                    current_results[category]
                )
                regressions.extend(category_regressions)
                
        return regressions
        
    def _compare_test_results(self, baseline: Dict, current: Dict) -> List[RegressionResult]:
        """Compare test results for regressions."""
        regressions = []
        
        # Check test failure increase
        if "failed" in baseline and "failed" in current:
            baseline_failed = baseline["failed"]
            current_failed = current["failed"]
            
            if current_failed > baseline_failed:
                if baseline_failed == 0:
                    increase_percentage = 100.0  # Any failure from 0 is 100% increase
                else:
                    increase_percentage = ((current_failed - baseline_failed) / baseline_failed) * 100
                if increase_percentage > self.thresholds.get("test_failure_increase", 10.0):
                    regressions.append(RegressionResult(
                        type=RegressionType.TEST_EXECUTION.value,
                        severity=RegressionSeverity.HIGH.value,
                        metric="test_failure_increase",
                        baseline_value=baseline_failed,
                        current_value=current_failed,
                        regression_percentage=increase_percentage,
                        description=f"Test failures increased from {baseline_failed} to {current_failed}"
                    ))
                    
        # Check coverage decrease
        if "coverage" in baseline and "coverage" in current:
            baseline_coverage = baseline["coverage"]
            current_coverage = current["coverage"]
            
            if current_coverage < baseline_coverage:
                decrease_percentage = ((baseline_coverage - current_coverage) / baseline_coverage) * 100
                if decrease_percentage > self.thresholds.get("coverage", 5.0):
                    regressions.append(RegressionResult(
                        type=RegressionType.TEST_EXECUTION.value,
                        severity=RegressionSeverity.MEDIUM.value,
                        metric="coverage_decrease",
                        baseline_value=baseline_coverage,
                        current_value=current_coverage,
                        regression_percentage=decrease_percentage,
                        description=f"Test coverage decreased from {baseline_coverage}% to {current_coverage}%"
                    ))
                    
        # Check execution time increase
        if "execution_time" in baseline and "execution_time" in current:
            baseline_time = baseline["execution_time"]
            current_time = current["execution_time"]
            
            if current_time > baseline_time:
                increase_percentage = ((current_time - baseline_time) / baseline_time) * 100
                if increase_percentage > self.thresholds.get("execution_time", 50.0):
                    regressions.append(RegressionResult(
                        type=RegressionType.TEST_EXECUTION.value,
                        severity=RegressionSeverity.MEDIUM.value,
                        metric="execution_time_increase",
                        baseline_value=baseline_time,
                        current_value=current_time,
                        regression_percentage=increase_percentage,
                        description=f"Test execution time increased from {baseline_time}s to {current_time}s"
                    ))
                    
        return regressions


class RegressionReporter:
    """Generates regression reports."""
    
    def __init__(self):
        self.report_templates = {
            "summary": self._generate_summary_template,
            "detailed": self._generate_detailed_template,
            "executive": self._generate_executive_template
        }
        
    def generate_report(self, regressions: List[RegressionResult], 
                       report_type: str = "summary") -> Dict[str, Any]:
        """Generate a regression report."""
        if report_type not in self.report_templates:
            report_type = "summary"
            
        template_func = self.report_templates[report_type]
        return template_func(regressions)
        
    def _generate_summary_template(self, regressions: List[RegressionResult]) -> Dict[str, Any]:
        """Generate summary report template."""
        severity_counts = {}
        type_counts = {}
        
        for regression in regressions:
            severity_counts[regression.severity] = severity_counts.get(regression.severity, 0) + 1
            type_counts[regression.type] = type_counts.get(regression.type, 0) + 1
            
        return {
            "summary": {
                "total_regressions": len(regressions),
                "high_severity": severity_counts.get("high", 0),
                "medium_severity": severity_counts.get("medium", 0),
                "low_severity": severity_counts.get("low", 0),
                "critical_severity": severity_counts.get("critical", 0),
                "regression_types": type_counts
            },
            "regressions": [asdict(regression) for regression in regressions],
            "recommendations": self._generate_recommendations(regressions),
            "timestamp": datetime.now().isoformat()
        }
        
    def _generate_detailed_template(self, regressions: List[RegressionResult]) -> Dict[str, Any]:
        """Generate detailed report template."""
        summary = self._generate_summary_template(regressions)
        
        # Add detailed analysis
        summary["detailed_analysis"] = {
            "performance_impact": self._analyze_performance_impact(regressions),
            "affected_components": self._analyze_affected_components(regressions),
            "trend_analysis": self._analyze_trends(regressions)
        }
        
        return summary
        
    def _generate_executive_template(self, regressions: List[RegressionResult]) -> Dict[str, Any]:
        """Generate executive summary template."""
        summary = self._generate_summary_template(regressions)
        
        # Add executive summary
        summary["executive_summary"] = {
            "business_impact": self._assess_business_impact(regressions),
            "risk_level": self._assess_risk_level(regressions),
            "action_required": len([r for r in regressions if r.severity in ["high", "critical"]]) > 0
        }
        
        return summary
        
    def _generate_recommendations(self, regressions: List[RegressionResult]) -> List[str]:
        """Generate recommendations based on regressions."""
        recommendations = []
        
        high_severity_count = len([r for r in regressions if r.severity == "high"])
        critical_severity_count = len([r for r in regressions if r.severity == "critical"])
        
        if critical_severity_count > 0:
            recommendations.append("IMMEDIATE ACTION REQUIRED: Critical regressions detected")
            recommendations.append("Consider rolling back to previous stable version")
            
        if high_severity_count > 0:
            recommendations.append("High priority regressions require immediate attention")
            recommendations.append("Schedule emergency review meeting")
            
        performance_regressions = [r for r in regressions if r.type == "performance_regression"]
        if performance_regressions:
            recommendations.append("Performance optimization required")
            recommendations.append("Consider code profiling and bottleneck analysis")
            
        api_regressions = [r for r in regressions if r.type == "api_behavior_regression"]
        if api_regressions:
            recommendations.append("API compatibility review required")
            recommendations.append("Update API documentation and client integrations")
            
        return recommendations
        
    def _analyze_performance_impact(self, regressions: List[RegressionResult]) -> Dict[str, Any]:
        """Analyze performance impact of regressions."""
        performance_regressions = [r for r in regressions if r.type == "performance_regression"]
        
        if not performance_regressions:
            return {"impact": "none", "description": "No performance regressions detected"}
            
        total_impact = sum(r.regression_percentage or 0 for r in performance_regressions)
        avg_impact = total_impact / len(performance_regressions)
        
        if avg_impact > 100:
            impact_level = "severe"
        elif avg_impact > 50:
            impact_level = "moderate"
        else:
            impact_level = "minor"
            
        return {
            "impact": impact_level,
            "average_regression": avg_impact,
            "total_regressions": len(performance_regressions),
            "description": f"Average performance regression of {avg_impact:.1f}%"
        }
        
    def _analyze_affected_components(self, regressions: List[RegressionResult]) -> Dict[str, Any]:
        """Analyze affected components."""
        components = {}
        
        for regression in regressions:
            if regression.affected_components:
                for component in regression.affected_components:
                    if component not in components:
                        components[component] = {"count": 0, "severities": []}
                    components[component]["count"] += 1
                    components[component]["severities"].append(regression.severity)
                    
        return components
        
    def _analyze_trends(self, regressions: List[RegressionResult]) -> Dict[str, Any]:
        """Analyze regression trends."""
        # This would typically analyze historical data
        return {
            "trend_direction": "increasing" if len(regressions) > 5 else "stable",
            "regression_rate": len(regressions),
            "severity_trend": "concerning" if any(r.severity == "critical" for r in regressions) else "acceptable"
        }
        
    def _assess_business_impact(self, regressions: List[RegressionResult]) -> str:
        """Assess business impact of regressions."""
        critical_count = len([r for r in regressions if r.severity == "critical"])
        high_count = len([r for r in regressions if r.severity == "high"])
        
        if critical_count > 0:
            return "HIGH - Critical regressions may affect production systems"
        elif high_count > 2:
            return "MEDIUM - Multiple high-severity regressions require attention"
        elif high_count > 0:
            return "LOW - Limited high-severity regressions"
        else:
            return "MINIMAL - No high-severity regressions detected"
            
    def _assess_risk_level(self, regressions: List[RegressionResult]) -> str:
        """Assess overall risk level."""
        severity_scores = {"critical": 4, "high": 3, "medium": 2, "low": 1}
        total_score = sum(severity_scores.get(r.severity, 0) for r in regressions)
        
        if total_score >= 12:
            return "HIGH"
        elif total_score >= 6:
            return "MEDIUM"
        else:
            return "LOW"


class RegressionTestDataManager:
    """Manages regression test data."""
    
    def __init__(self):
        self.test_datasets: Dict[str, Dict[str, Any]] = {}
        
    def create_test_dataset(self, name: str, data: Dict[str, Any]) -> None:
        """Create a test dataset."""
        self.test_datasets[name] = data.copy()
        logger.info(f"Test dataset '{name}' created with {len(data)} categories")
        
    def get_test_dataset(self, name: str) -> Optional[Dict[str, Any]]:
        """Get a test dataset by name."""
        return self.test_datasets.get(name)
        
    def list_test_datasets(self) -> List[str]:
        """List all available test datasets."""
        return list(self.test_datasets.keys())
        
    def delete_test_dataset(self, name: str) -> bool:
        """Delete a test dataset."""
        if name in self.test_datasets:
            del self.test_datasets[name]
            logger.info(f"Test dataset '{name}' deleted")
            return True
        return False


class RegressionBaselineManager:
    """Manages regression baselines."""
    
    def __init__(self):
        self.baselines: Dict[str, Dict[str, Any]] = {}
        
    def establish_baseline(self, version: str, data: Dict[str, Any]) -> None:
        """Establish a baseline for a version."""
        self.baselines[version] = {
            "data": data.copy(),
            "timestamp": datetime.now(),
            "version": version
        }
        logger.info(f"Baseline established for version {version}")
        
    def get_baseline(self, version: str) -> Optional[Dict[str, Any]]:
        """Get baseline data for a version."""
        baseline = self.baselines.get(version)
        return baseline["data"] if baseline else None
        
    def list_baselines(self) -> List[str]:
        """List all available baselines."""
        return list(self.baselines.keys())
        
    def compare_baselines(self, version1: str, version2: str) -> Dict[str, Any]:
        """Compare two baselines."""
        baseline1 = self.get_baseline(version1)
        baseline2 = self.get_baseline(version2)
        
        if not baseline1 or not baseline2:
            return {"error": "One or both baselines not found"}
            
        # Simple comparison - could be enhanced
        return {
            "version1": version1,
            "version2": version2,
            "differences": self._find_differences(baseline1, baseline2)
        }
        
    def _find_differences(self, data1: Dict, data2: Dict) -> List[str]:
        """Find differences between two data structures."""
        differences = []
        
        for key in set(data1.keys()) | set(data2.keys()):
            if key not in data1:
                differences.append(f"Key '{key}' missing in first dataset")
            elif key not in data2:
                differences.append(f"Key '{key}' missing in second dataset")
            elif data1[key] != data2[key]:
                differences.append(f"Key '{key}' has different values")
                
        return differences


class RegressionThresholdManager:
    """Manages regression detection thresholds."""
    
    def __init__(self):
        self.thresholds: Dict[str, Dict[str, float]] = {}
        
    def set_thresholds(self, thresholds: Dict[str, Dict[str, float]]) -> None:
        """Set regression detection thresholds."""
        self.thresholds = thresholds.copy()
        logger.info(f"Thresholds set for {len(thresholds)} categories")
        
    def get_thresholds(self) -> Dict[str, Dict[str, float]]:
        """Get current thresholds."""
        return self.thresholds.copy()
        
    def get_threshold(self, category: str, metric: str) -> Optional[float]:
        """Get threshold for a specific category and metric."""
        return self.thresholds.get(category, {}).get(metric)
        
    def update_threshold(self, category: str, metric: str, value: float) -> None:
        """Update a specific threshold."""
        if category not in self.thresholds:
            self.thresholds[category] = {}
        self.thresholds[category][metric] = value
        logger.info(f"Threshold updated: {category}.{metric} = {value}")


class RegressionAutomationScheduler:
    """Schedules automated regression tests."""
    
    def __init__(self):
        self.schedule_config: Dict[str, Any] = {}
        self.is_scheduled: bool = False
        
    def schedule_regression_tests(self, config: Dict[str, Any]) -> None:
        """Schedule regression tests."""
        self.schedule_config = config.copy()
        self.is_scheduled = config.get("enabled", False)
        logger.info(f"Regression tests scheduled: {config.get('frequency', 'unknown')}")
        
    def is_regression_scheduled(self) -> bool:
        """Check if regression tests are scheduled."""
        return self.is_scheduled
        
    def get_schedule_config(self) -> Dict[str, Any]:
        """Get current schedule configuration."""
        return self.schedule_config.copy()


class RegressionNotificationSystem:
    """Handles regression notifications."""
    
    def __init__(self):
        self.notification_config: Dict[str, Any] = {}
        
    def configure_notifications(self, config: Dict[str, Any]) -> None:
        """Configure notification settings."""
        self.notification_config = config.copy()
        logger.info("Notification system configured")
        
    def send_notification(self, regressions: List[RegressionResult], 
                        method: str = "email") -> bool:
        """Send regression notification."""
        try:
            if method == "email":
                return self._send_email_notification(regressions)
            elif method == "slack":
                return self._send_slack_notification(regressions)
            else:
                logger.warning(f"Unknown notification method: {method}")
                return False
        except Exception as e:
            logger.error(f"Failed to send notification: {e}")
            return False
            
    def _send_email_notification(self, regressions: List[RegressionResult]) -> bool:
        """Send email notification."""
        # Mock implementation
        logger.info(f"Email notification sent for {len(regressions)} regressions")
        return True
        
    def _send_slack_notification(self, regressions: List[RegressionResult]) -> bool:
        """Send Slack notification."""
        # Mock implementation
        logger.info(f"Slack notification sent for {len(regressions)} regressions")
        return True


class RegressionHistoryTracker:
    """Tracks regression history."""
    
    def __init__(self):
        self.regression_history: List[Dict[str, Any]] = []
        
    def record_regression(self, regression_record: Dict[str, Any]) -> None:
        """Record a regression in history."""
        self.regression_history.append(regression_record.copy())
        logger.info("Regression recorded in history")
        
    def get_regression_history(self, days: int = 7) -> List[Dict[str, Any]]:
        """Get regression history for specified days."""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        filtered_history = [
            record for record in self.regression_history
            if record.get("timestamp", datetime.min) >= cutoff_date
        ]
        
        return filtered_history
        
    def get_regression_stats(self, days: int = 7) -> Dict[str, Any]:
        """Get regression statistics."""
        history = self.get_regression_history(days)
        
        severity_counts = {}
        type_counts = {}
        
        for record in history:
            severity = record.get("severity", "unknown")
            regression_type = record.get("type", "unknown")
            
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
            type_counts[regression_type] = type_counts.get(regression_type, 0) + 1
            
        return {
            "total_regressions": len(history),
            "severity_distribution": severity_counts,
            "type_distribution": type_counts,
            "period_days": days
        }


class RegressionTrendAnalyzer:
    """Analyzes regression trends."""
    
    def analyze_trends(self, historical_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze regression trends."""
        if not historical_data:
            return {"trend_direction": "insufficient_data", "regression_rate": 0}
            
        # Simple trend analysis
        regression_counts = [record.get("regressions", 0) for record in historical_data]
        
        if len(regression_counts) < 2:
            return {"trend_direction": "insufficient_data", "regression_rate": regression_counts[0] if regression_counts else 0}
            
        # Calculate trend direction
        recent_avg = sum(regression_counts[-3:]) / min(3, len(regression_counts))
        older_avg = sum(regression_counts[:-3]) / max(1, len(regression_counts) - 3) if len(regression_counts) > 3 else recent_avg
        
        if recent_avg > older_avg * 1.2:
            trend_direction = "increasing"
        elif recent_avg < older_avg * 0.8:
            trend_direction = "decreasing"
        else:
            trend_direction = "stable"
            
        return {
            "trend_direction": trend_direction,
            "regression_rate": recent_avg,
            "severity_trend": self._analyze_severity_trend(historical_data)
        }
        
    def _analyze_severity_trend(self, historical_data: List[Dict[str, Any]]) -> str:
        """Analyze severity trend."""
        recent_severities = [record.get("severity", "low") for record in historical_data[-3:]]
        
        if any(severity in ["critical", "high"] for severity in recent_severities):
            return "concerning"
        else:
            return "acceptable"


class RegressionImpactAssessor:
    """Assesses regression impact."""
    
    def assess_impact(self, regression: Dict[str, Any]) -> Dict[str, Any]:
        """Assess the impact of a regression."""
        severity = regression.get("severity", "low")
        regression_type = regression.get("type", "unknown")
        
        # Determine severity level
        if severity == "critical":
            severity_level = "CRITICAL"
        elif severity == "high":
            severity_level = "HIGH"
        elif severity == "medium":
            severity_level = "MEDIUM"
        else:
            severity_level = "LOW"
            
        # Assess affected users (mock calculation)
        affected_users = self._calculate_affected_users(regression)
        
        # Assess business impact
        business_impact = self._assess_business_impact(severity, regression_type)
        
        # Generate recommendations
        recommended_actions = self._generate_recommendations(severity, regression_type)
        
        return {
            "severity_level": severity_level,
            "affected_users": affected_users,
            "business_impact": business_impact,
            "recommended_actions": recommended_actions,
            "estimated_resolution_time": self._estimate_resolution_time(severity)
        }
        
    def _calculate_affected_users(self, regression: Dict[str, Any]) -> str:
        """Calculate affected users (mock implementation)."""
        severity = regression.get("severity", "low")
        
        if severity == "critical":
            return "All users"
        elif severity == "high":
            return "Most users"
        elif severity == "medium":
            return "Some users"
        else:
            return "Limited users"
            
    def _assess_business_impact(self, severity: str, regression_type: str) -> str:
        """Assess business impact."""
        if severity == "critical":
            return "HIGH - May cause service outages"
        elif severity == "high":
            return "MEDIUM - May affect user experience"
        elif severity == "medium":
            return "LOW - Minor impact on operations"
        else:
            return "MINIMAL - Negligible impact"
            
    def _generate_recommendations(self, severity: str, regression_type: str) -> List[str]:
        """Generate recommendations."""
        recommendations = []
        
        if severity == "critical":
            recommendations.extend([
                "Immediate rollback to previous stable version",
                "Emergency response team activation",
                "User communication about service disruption"
            ])
        elif severity == "high":
            recommendations.extend([
                "Priority fix development",
                "Monitoring and alerting setup",
                "User notification about potential issues"
            ])
        elif severity == "medium":
            recommendations.extend([
                "Scheduled fix in next release",
                "Enhanced monitoring",
                "Documentation update"
            ])
        else:
            recommendations.extend([
                "Fix in regular development cycle",
                "Monitor for escalation"
            ])
            
        return recommendations
        
    def _estimate_resolution_time(self, severity: str) -> str:
        """Estimate resolution time."""
        if severity == "critical":
            return "1-4 hours"
        elif severity == "high":
            return "4-24 hours"
        elif severity == "medium":
            return "1-3 days"
        else:
            return "1-2 weeks"


class RegressionMitigationManager:
    """Manages regression mitigation strategies."""
    
    def get_mitigation_strategies(self, regression: Dict[str, Any]) -> List[str]:
        """Get mitigation strategies for a regression."""
        strategies = []
        
        regression_type = regression.get("type", "unknown")
        severity = regression.get("severity", "low")
        
        # General strategies
        if severity in ["critical", "high"]:
            strategies.extend([
                "Immediate rollback to previous stable version",
                "Hotfix deployment",
                "Emergency response activation"
            ])
            
        # Type-specific strategies
        if regression_type == "performance_regression":
            strategies.extend([
                "Performance optimization",
                "Code profiling and bottleneck analysis",
                "Resource scaling",
                "Caching implementation"
            ])
        elif regression_type == "api_behavior_regression":
            strategies.extend([
                "API compatibility fixes",
                "Client integration updates",
                "Documentation updates",
                "Version deprecation strategy"
            ])
        elif regression_type == "database_schema_regression":
            strategies.extend([
                "Database migration rollback",
                "Schema restoration",
                "Data integrity verification",
                "Backup restoration"
            ])
        elif regression_type == "test_execution_regression":
            strategies.extend([
                "Test suite optimization",
                "Test data management",
                "Test environment stabilization",
                "Test coverage improvement"
            ])
            
        return strategies


class RegressionTestIntegrator:
    """Integrates regression tests with existing test suite."""
    
    def integrate_regression_tests(self, existing_tests: Dict[str, Any]) -> Dict[str, Any]:
        """Integrate regression tests with existing test results."""
        integrated_results = existing_tests.copy()
        
        # Add regression analysis
        integrated_results["regression_analysis"] = self._analyze_existing_tests(existing_tests)
        
        # Add performance metrics
        integrated_results["performance_metrics"] = self._extract_performance_metrics(existing_tests)
        
        # Add recommendations
        integrated_results["recommendations"] = self._generate_integration_recommendations(existing_tests)
        
        return integrated_results
        
    def _analyze_existing_tests(self, existing_tests: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze existing test results."""
        total_tests = sum(category.get("total", 0) for category in existing_tests.values() if isinstance(category, dict))
        total_passed = sum(category.get("passed", 0) for category in existing_tests.values() if isinstance(category, dict))
        total_failed = sum(category.get("failed", 0) for category in existing_tests.values() if isinstance(category, dict))
        
        return {
            "total_tests": total_tests,
            "total_passed": total_passed,
            "total_failed": total_failed,
            "success_rate": (total_passed / total_tests * 100) if total_tests > 0 else 0,
            "failure_rate": (total_failed / total_tests * 100) if total_tests > 0 else 0
        }
        
    def _extract_performance_metrics(self, existing_tests: Dict[str, Any]) -> Dict[str, Any]:
        """Extract performance metrics from test results."""
        execution_times = [category.get("execution_time", 0) for category in existing_tests.values() if isinstance(category, dict)]
        
        return {
            "total_execution_time": sum(execution_times),
            "average_execution_time": sum(execution_times) / len(execution_times) if execution_times else 0,
            "slowest_category": max(existing_tests.keys(), key=lambda k: existing_tests[k].get("execution_time", 0)) if existing_tests else None
        }
        
    def _generate_integration_recommendations(self, existing_tests: Dict[str, Any]) -> List[str]:
        """Generate integration recommendations."""
        recommendations = []
        
        # Analyze test results
        total_failed = sum(category.get("failed", 0) for category in existing_tests.values() if isinstance(category, dict))
        
        if total_failed > 10:
            recommendations.append("High number of test failures - investigate root causes")
            
        # Check execution times
        execution_times = [category.get("execution_time", 0) for category in existing_tests.values() if isinstance(category, dict)]
        if execution_times and max(execution_times) > 300:  # 5 minutes
            recommendations.append("Long execution times detected - consider test optimization")
            
        # Check coverage
        coverages = [category.get("coverage", 0) for category in existing_tests.values() if isinstance(category, dict)]
        if coverages and min(coverages) < 70:
            recommendations.append("Low test coverage detected - increase test coverage")
            
        return recommendations
