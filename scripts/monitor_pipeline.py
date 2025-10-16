#!/usr/bin/env python3
"""
CI/CD Pipeline Monitoring Script

This script monitors CI/CD pipeline execution and provides real-time
monitoring capabilities for pipeline health and performance.

Usage:
    python scripts/monitor_pipeline.py [options]

Options:
    --start-monitoring    Start continuous monitoring
    --check-status        Check current pipeline status
    --get-metrics        Get current pipeline metrics
    --check-alerts       Check for active alerts
    --help               Show this help message
"""

import argparse
import time
import json
import sys
from pathlib import Path
from typing import Dict, Any, List

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from testing.cicd_pipeline import CICDPipelineMonitor


def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description="CI/CD Pipeline Monitoring Script",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/monitor_pipeline.py --check-status
  python scripts/monitor_pipeline.py --get-metrics
  python scripts/monitor_pipeline.py --check-alerts
  python scripts/monitor_pipeline.py --start-monitoring
        """
    )
    
    parser.add_argument(
        '--start-monitoring',
        action='store_true',
        help='Start continuous monitoring'
    )
    
    parser.add_argument(
        '--check-status',
        action='store_true',
        help='Check current pipeline status'
    )
    
    parser.add_argument(
        '--get-metrics',
        action='store_true',
        help='Get current pipeline metrics'
    )
    
    parser.add_argument(
        '--check-alerts',
        action='store_true',
        help='Check for active alerts'
    )
    
    parser.add_argument(
        '--output-file',
        type=str,
        help='Output file path for monitoring data'
    )
    
    args = parser.parse_args()
    
    # If no arguments provided, show help
    if not any([
        args.start_monitoring,
        args.check_status,
        args.get_metrics,
        args.check_alerts
    ]):
        parser.print_help()
        return
    
    # Initialize monitor
    monitor = CICDPipelineMonitor()
    
    try:
        # Execute requested operations
        if args.check_status:
            print("🔍 Checking pipeline status...")
            config = monitor.get_monitoring_config()
            print(f"Monitoring enabled: {config['enabled']}")
            print(f"Metrics configured: {list(config['metrics'].keys())}")
            print(f"Alert thresholds: {config['alerts']}")
        
        if args.get_metrics:
            print("📊 Collecting pipeline metrics...")
            metrics = monitor.collect_metrics()
            print(f"Execution Time: {metrics['execution_time']}s")
            print(f"Success Rate: {metrics['success_rate']:.2%}")
            print(f"Failure Rate: {metrics['failure_rate']:.2%}")
            print(f"Coverage: {metrics['coverage']}%")
            print(f"Security Score: {metrics['security_score']}")
            print(f"Performance Score: {metrics['performance_score']}")
            
            if args.output_file:
                with open(args.output_file, 'w') as f:
                    json.dump(metrics, f, indent=2)
        
        if args.check_alerts:
            print("⚠️  Checking for alerts...")
            alerts = monitor.check_alerts()
            
            if alerts:
                print(f"Found {len(alerts)} alerts:")
                for alert in alerts:
                    print(f"  - {alert['type']}: {alert['message']} (severity: {alert['severity']})")
            else:
                print("✅ No alerts found")
            
            if args.output_file:
                with open(args.output_file, 'w') as f:
                    json.dump(alerts, f, indent=2)
        
        if args.start_monitoring:
            print("🔄 Starting continuous monitoring...")
            print("Press Ctrl+C to stop")
            
            try:
                while True:
                    metrics = monitor.collect_metrics()
                    alerts = monitor.check_alerts()
                    
                    print(f"\n📊 Metrics at {time.strftime('%H:%M:%S')}:")
                    print(f"  Success Rate: {metrics['success_rate']:.2%}")
                    print(f"  Coverage: {metrics['coverage']}%")
                    print(f"  Security Score: {metrics['security_score']}")
                    
                    if alerts:
                        print(f"⚠️  {len(alerts)} alerts active")
                    
                    time.sleep(30)  # Check every 30 seconds
                    
            except KeyboardInterrupt:
                print("\n🛑 Monitoring stopped by user")
        
        print("✅ Pipeline monitoring completed successfully")
        
    except KeyboardInterrupt:
        print("🛑 Pipeline monitoring interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Pipeline monitoring failed: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()


