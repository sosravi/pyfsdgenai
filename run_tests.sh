#!/bin/bash

# PyFSD GenAI - Test Runner Script
# This script provides various test execution options following TDD principles

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
TEST_TYPE="all"
VERBOSE=false
COVERAGE=true
PARALLEL=false
MARKERS=""
TIMEOUT=300

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to show usage
show_usage() {
    echo "PyFSD GenAI Test Runner"
    echo ""
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -t, --type TYPE        Test type: all, unit, integration, api, edge_case, regression"
    echo "  -m, --markers MARKERS  Pytest markers to run (e.g., 'unit and not slow')"
    echo "  -v, --verbose          Verbose output"
    echo "  -c, --coverage         Enable coverage reporting (default: true)"
    echo "  -p, --parallel         Run tests in parallel"
    echo "  --timeout SECONDS      Test timeout in seconds (default: 300)"
    echo "  -h, --help             Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0                                    # Run all tests"
    echo "  $0 -t unit                           # Run unit tests only"
    echo "  $0 -m 'unit and not slow'             # Run fast unit tests"
    echo "  $0 -t integration -p                 # Run integration tests in parallel"
    echo "  $0 -m 'regression' -v                # Run regression tests with verbose output"
}

# Function to check prerequisites
check_prerequisites() {
    print_status "Checking prerequisites..."
    
    # Check if virtual environment is activated
    if [[ "$VIRTUAL_ENV" == "" ]]; then
        print_warning "Virtual environment not activated. Activating..."
        source venv/bin/activate
    fi
    
    # Check if pytest is installed
    if ! command -v pytest &> /dev/null; then
        print_error "pytest is not installed. Please install it first."
        exit 1
    fi
    
    # Check if required packages are installed
    python -c "import pytest, pytest_cov, pytest_asyncio" 2>/dev/null || {
        print_error "Required test packages are not installed. Installing..."
        pip install pytest pytest-cov pytest-asyncio pytest-xdist pytest-mock hypothesis
    }
    
    print_success "Prerequisites check completed"
}

# Function to run tests
run_tests() {
    local test_args=()
    
    # Add test type or markers
    if [[ -n "$MARKERS" ]]; then
        test_args+=("-m" "$MARKERS")
    elif [[ "$TEST_TYPE" != "all" ]]; then
        test_args+=("-m" "$TEST_TYPE")
    fi
    
    # Add verbose flag
    if [[ "$VERBOSE" == true ]]; then
        test_args+=("-v" "-s")
    fi
    
    # Add coverage
    if [[ "$COVERAGE" == true ]]; then
        test_args+=("--cov=src" "--cov-report=html:htmlcov" "--cov-report=xml:coverage.xml" "--cov-report=term-missing")
    fi
    
    # Add parallel execution
    if [[ "$PARALLEL" == true ]]; then
        test_args+=("-n" "auto")
    fi
    
    # Add timeout
    # test_args+=("--timeout=$TIMEOUT")  # Commented out - not available in basic pytest
    
    # Add test directory
    test_args+=("tests/")
    
    print_status "Running tests with arguments: ${test_args[*]}"
    
    # Run pytest
    if pytest "${test_args[@]}"; then
        print_success "All tests passed!"
        return 0
    else
        print_error "Some tests failed!"
        return 1
    fi
}

# Function to run TDD cycle
run_tdd_cycle() {
    print_status "Starting TDD cycle..."
    
    # Red phase: Run tests (should fail)
    print_status "RED phase: Running tests (expecting failures)..."
    if pytest tests/ -x --tb=short; then
        print_warning "All tests passed in RED phase. No new functionality to implement?"
    else
        print_success "RED phase completed - tests failed as expected"
    fi
    
    # Green phase: Implement minimal code to make tests pass
    print_status "GREEN phase: Implement minimal code to make tests pass"
    print_warning "Please implement the minimal code to make tests pass, then press Enter to continue..."
    read -r
    
    # Run tests again
    print_status "Running tests after implementation..."
    if pytest tests/ -x --tb=short; then
        print_success "GREEN phase completed - tests now pass!"
    else
        print_error "GREEN phase failed - tests still failing"
        return 1
    fi
    
    # Refactor phase: Improve code while keeping tests green
    print_status "REFACTOR phase: Improve code while keeping tests green"
    print_warning "Please refactor your code, then press Enter to continue..."
    read -r
    
    # Run tests again
    print_status "Running tests after refactoring..."
    if pytest tests/ -x --tb=short; then
        print_success "REFACTOR phase completed - tests still pass!"
        print_success "TDD cycle completed successfully!"
    else
        print_error "REFACTOR phase failed - tests are now failing"
        return 1
    fi
}

# Function to run specific test categories
run_test_category() {
    case "$TEST_TYPE" in
        "unit")
            print_status "Running unit tests..."
            pytest tests/unit/ -v --tb=short
            ;;
        "integration")
            print_status "Running integration tests..."
            pytest tests/integration/ -v --tb=short
            ;;
        "api")
            print_status "Running API tests..."
            pytest tests/api/ -v --tb=short
            ;;
        "edge_case")
            print_status "Running edge case tests..."
            pytest tests/edge_cases/ -v --tb=short
            ;;
        "regression")
            print_status "Running regression tests..."
            pytest tests/regression/ -v --tb=short
            ;;
        "all")
            print_status "Running all tests..."
            pytest tests/ -v --tb=short
            ;;
        *)
            print_error "Unknown test type: $TEST_TYPE"
            show_usage
            exit 1
            ;;
    esac
}

# Function to generate test report
generate_report() {
    print_status "Generating test report..."
    
    # Generate HTML coverage report
    if [[ "$COVERAGE" == true ]]; then
        print_status "Coverage report generated in htmlcov/index.html"
    fi
    
    # Generate test results summary
    echo "Test execution completed at $(date)" > test_results.txt
    echo "Test type: $TEST_TYPE" >> test_results.txt
    echo "Markers: $MARKERS" >> test_results.txt
    echo "Coverage: $COVERAGE" >> test_results.txt
    echo "Parallel: $PARALLEL" >> test_results.txt
    
    print_success "Test report generated"
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -t|--type)
            TEST_TYPE="$2"
            shift 2
            ;;
        -m|--markers)
            MARKERS="$2"
            shift 2
            ;;
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        -c|--coverage)
            COVERAGE=true
            shift
            ;;
        --no-coverage)
            COVERAGE=false
            shift
            ;;
        -p|--parallel)
            PARALLEL=true
            shift
            ;;
        --timeout)
            TIMEOUT="$2"
            shift 2
            ;;
        --tdd)
            TDD_MODE=true
            shift
            ;;
        -h|--help)
            show_usage
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            show_usage
            exit 1
            ;;
    esac
done

# Main execution
main() {
    print_status "PyFSD GenAI Test Runner Starting..."
    
    # Check prerequisites
    check_prerequisites
    
    # Run TDD cycle if requested
    if [[ "$TDD_MODE" == true ]]; then
        run_tdd_cycle
        exit $?
    fi
    
    # Run tests
    if run_tests; then
        print_success "Test execution completed successfully!"
        generate_report
        exit 0
    else
        print_error "Test execution failed!"
        exit 1
    fi
}

# Run main function
main "$@"
