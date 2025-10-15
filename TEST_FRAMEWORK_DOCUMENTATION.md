# PyFSD GenAI - Comprehensive Test Framework Documentation

## Overview

This document describes the comprehensive test framework for PyFSD GenAI, following Test-Driven Development (TDD) principles and ensuring robust testing across all components.

## Test Framework Architecture

### Test Structure
```
tests/
├── conftest.py                 # Shared fixtures and configuration
├── test_helpers.py             # Test utilities and helper classes
├── unit/                       # Unit tests
│   └── test_unit_tests.py
├── integration/                # Integration tests
│   └── test_integration_tests.py
├── api/                        # API tests
│   └── test_api_tests.py
├── edge_cases/                 # Edge case tests
│   └── test_edge_case_tests.py
├── regression/                 # Regression tests
│   └── test_regression_tests.py
└── property/                   # Property-based tests (future)
```

### Test Categories

#### 1. Unit Tests (`@pytest.mark.unit`)
- **Purpose**: Test individual components in isolation
- **Scope**: Functions, classes, and modules
- **Dependencies**: Minimal external dependencies, heavy use of mocks
- **Coverage**: 95%+ code coverage requirement

#### 2. Integration Tests (`@pytest.mark.integration`)
- **Purpose**: Test interactions between components
- **Scope**: Service interactions, database operations, API workflows
- **Dependencies**: Real services and databases
- **Coverage**: Critical integration paths

#### 3. API Tests (`@pytest.mark.api`)
- **Purpose**: Test API endpoints and request/response handling
- **Scope**: HTTP endpoints, authentication, validation
- **Dependencies**: Test client, mock services
- **Coverage**: All API endpoints and error scenarios

#### 4. Edge Case Tests (`@pytest.mark.edge_case`)
- **Purpose**: Test boundary conditions and unusual inputs
- **Scope**: Boundary values, special characters, extreme inputs
- **Dependencies**: Edge case data generators
- **Coverage**: Boundary conditions and error handling

#### 5. Regression Tests (`@pytest.mark.regression`)
- **Purpose**: Ensure bugs don't reoccur
- **Scope**: Previously fixed issues, functionality preservation
- **Dependencies**: Historical bug scenarios
- **Coverage**: Critical functionality paths

## Test-Driven Development (TDD) Workflow

### Red-Green-Refactor Cycle

#### 1. Red Phase
```bash
# Write failing tests first
pytest tests/ -x --tb=short
# Expected: Tests fail (RED)
```

#### 2. Green Phase
```bash
# Implement minimal code to make tests pass
# Run tests again
pytest tests/ -x --tb=short
# Expected: Tests pass (GREEN)
```

#### 3. Refactor Phase
```bash
# Improve code while keeping tests green
# Run tests again
pytest tests/ -x --tb=short
# Expected: Tests still pass (REFACTOR)
```

### TDD Automation
```bash
# Run TDD cycle automatically
./run_tests.sh --tdd
```

## Test Configuration

### Pytest Configuration (`pytest.ini`)
- **Test Discovery**: Automatic test discovery in `tests/` directory
- **Markers**: Comprehensive marker system for test categorization
- **Coverage**: 95% minimum coverage requirement
- **Output**: Verbose output with colored results
- **Timeout**: 5-minute timeout for individual tests

### Test Markers
```python
@pytest.mark.unit          # Unit tests
@pytest.mark.integration  # Integration tests
@pytest.mark.api          # API tests
@pytest.mark.database     # Database tests
@pytest.mark.slow         # Slow-running tests
@pytest.mark.performance  # Performance tests
@pytest.mark.edge_case    # Edge case tests
@pytest.mark.regression   # Regression tests
```

## Test Fixtures and Utilities

### Core Fixtures (`conftest.py`)
- **Database**: Test database engine and session
- **Client**: FastAPI test client
- **Mocks**: OpenAI, Anthropic, Redis, MongoDB mocks
- **Data**: Sample contract, invoice, document data
- **Files**: Temporary file management

### Test Helpers (`test_helpers.py`)
- **TestDataFactory**: Create test data with overrides
- **APITestHelper**: API testing utilities
- **DatabaseTestHelper**: Database testing utilities
- **MockHelper**: Mock creation utilities
- **PerformanceTestHelper**: Performance testing utilities
- **EdgeCaseTestHelper**: Edge case data generation

### Example Usage
```python
def test_contract_creation(test_client, test_data_factory):
    """Test contract creation with test data factory."""
    contract_data = test_data_factory.create_contract_data(
        contract_id="TEST-001",
        amount=50000.00
    )
    
    response = test_client.post("/contracts", json=contract_data)
    assert response.status_code == 201
```

## Test Execution

### Command Line Options
```bash
# Run all tests
./run_tests.sh

# Run specific test type
./run_tests.sh -t unit

# Run with specific markers
./run_tests.sh -m "unit and not slow"

# Run in parallel
./run_tests.sh -p

# Run with verbose output
./run_tests.sh -v

# Run TDD cycle
./run_tests.sh --tdd
```

### Coverage Reporting
- **HTML Report**: `htmlcov/index.html`
- **XML Report**: `coverage.xml`
- **Terminal Report**: Coverage summary in terminal
- **Minimum Coverage**: 95%

## Test Data Management

### Test Data Factory
```python
# Create contract data with defaults
contract_data = TestDataFactory.create_contract_data()

# Create contract data with overrides
contract_data = TestDataFactory.create_contract_data(
    contract_id="CUSTOM-001",
    amount=75000.00
)
```

### Edge Case Data
```python
# Get edge case strings
edge_strings = EdgeCaseTestHelper.get_edge_case_strings()

# Get edge case numbers
edge_numbers = EdgeCaseTestHelper.get_edge_case_numbers()

# Get edge case dates
edge_dates = EdgeCaseTestHelper.get_edge_case_dates()
```

## Mocking Strategy

### External Service Mocks
- **OpenAI**: Mock AI responses for testing
- **Anthropic**: Mock AI responses for testing
- **Redis**: Mock caching operations
- **MongoDB**: Mock document storage
- **File System**: Mock file operations

### Example Mock Usage
```python
@patch('openai.OpenAI')
def test_ai_extraction(mock_openai, test_client):
    """Test AI extraction with mocked OpenAI."""
    mock_instance = Mock()
    mock_openai.return_value = mock_instance
    
    mock_response = MockHelper.mock_openai_response("Extracted data")
    mock_instance.chat.completions.create.return_value = mock_response
    
    response = test_client.post("/agents/extract", json={"text": "test"})
    assert response.status_code == 200
```

## Performance Testing

### Performance Test Helper
```python
def test_api_performance(test_client, performance_helper):
    """Test API response time."""
    performance_helper.start_timer()
    response = test_client.get("/health")
    performance_helper.stop_timer()
    
    performance_helper.assert_performance(1.0)  # Max 1 second
```

### Concurrent Testing
```python
def test_concurrent_requests(test_client):
    """Test concurrent request handling."""
    import threading
    
    results = []
    def make_request():
        response = test_client.get("/health")
        results.append(response.status_code)
    
    # Create and run multiple threads
    threads = [threading.Thread(target=make_request) for _ in range(10)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    
    assert all(status == 200 for status in results)
```

## Error Handling Testing

### Validation Error Testing
```python
def test_validation_errors(test_client, api_helper):
    """Test validation error handling."""
    invalid_data = {"invalid_field": "value"}
    
    response = test_client.post("/contracts", json=invalid_data)
    api_helper.assert_error_response(response, 422)
    
    error_data = response.json()
    assert "detail" in error_data
```

### Edge Case Error Testing
```python
def test_edge_case_handling(test_client):
    """Test edge case error handling."""
    edge_cases = EdgeCaseTestHelper.get_edge_case_strings()
    
    for edge_case in edge_cases:
        test_data = TestDataFactory.create_contract_data(title=edge_case)
        response = test_client.post("/contracts", json=test_data)
        
        # Should handle edge cases gracefully
        assert response.status_code in [200, 201, 400, 422]
```

## Continuous Integration

### GitHub Actions Integration
The test framework integrates with GitHub Actions for continuous integration:

```yaml
# .github/workflows/tdd-security-pipeline.yml
- name: Run Unit Tests
  run: pytest tests/unit/ -v --cov=src --cov-fail-under=95

- name: Run Integration Tests
  run: pytest tests/integration/ -v

- name: Run API Tests
  run: pytest tests/api/ -v

- name: Run Edge Case Tests
  run: pytest tests/edge_cases/ -v

- name: Run Regression Tests
  run: pytest tests/regression/ -v
```

### Test Matrix
- **Python Versions**: 3.9, 3.10, 3.11
- **Operating Systems**: Ubuntu, macOS, Windows
- **Test Types**: Unit, Integration, API, Edge Cases, Regression

## Best Practices

### Test Writing Guidelines
1. **Test Naming**: Use descriptive test names that explain the scenario
2. **Arrange-Act-Assert**: Structure tests with clear sections
3. **Single Responsibility**: Each test should verify one specific behavior
4. **Independence**: Tests should not depend on each other
5. **Deterministic**: Tests should produce consistent results

### Test Data Guidelines
1. **Realistic Data**: Use realistic test data that mirrors production
2. **Edge Cases**: Include boundary conditions and unusual inputs
3. **Data Isolation**: Each test should use isolated data
4. **Cleanup**: Clean up test data after each test

### Mock Guidelines
1. **Minimal Mocking**: Mock only external dependencies
2. **Realistic Mocks**: Mocks should behave like real services
3. **Mock Verification**: Verify mock interactions when necessary
4. **Mock Isolation**: Each test should have isolated mocks

## Troubleshooting

### Common Issues
1. **Test Failures**: Check test data and mock configurations
2. **Coverage Issues**: Ensure all code paths are tested
3. **Performance Issues**: Use performance helpers to identify bottlenecks
4. **Flaky Tests**: Make tests deterministic and independent

### Debugging Tips
1. **Verbose Output**: Use `-v` flag for detailed test output
2. **Single Test**: Use `-k` flag to run specific tests
3. **Debug Mode**: Use `--pdb` flag for interactive debugging
4. **Logging**: Enable logging to see test execution details

## Future Enhancements

### Planned Improvements
1. **Property-Based Testing**: Add Hypothesis for property-based tests
2. **Load Testing**: Add load testing capabilities
3. **Visual Testing**: Add visual regression testing
4. **Mutation Testing**: Add mutation testing for test quality
5. **Test Analytics**: Add test analytics and reporting

### Test Automation
1. **Auto Test Generation**: Generate tests from API specifications
2. **Test Data Generation**: Automatically generate test data
3. **Test Maintenance**: Automatically update tests when code changes
4. **Test Optimization**: Optimize test execution time

## Conclusion

The PyFSD GenAI test framework provides comprehensive testing capabilities following TDD principles. It ensures code quality, prevents regressions, and maintains high test coverage across all components. The framework is designed to be maintainable, scalable, and easy to use for developers.

For more information, refer to:
- [TDD Security Workflow](TDD_SECURITY_WORKFLOW.md)
- [Implementation Plan](IMPLEMENTATION_PLAN.md)
- [API Documentation](docs/API.md)

