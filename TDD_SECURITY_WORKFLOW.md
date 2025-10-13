# PyFSD GenAI - TDD & Security Development Workflow

## 🔄 Test-Driven Development (TDD) Workflow

### Core TDD Principles
1. **Red-Green-Refactor Cycle**: Write failing test → Make it pass → Improve code
2. **Test First**: Always write tests before implementation
3. **Small Steps**: Make small, incremental changes
4. **Continuous Testing**: Run tests frequently during development
5. **Documentation**: Update documentation with each change

### TDD Implementation Process

#### Step 1: Write Failing Test (Red Phase)
```python
# Example: Testing contract processing
def test_contract_processing_extracts_pricing():
    """Test that contract processing extracts pricing information."""
    # Arrange
    contract_data = {
        "content": "Service fee: $1000/month",
        "contract_type": "service"
    }
    
    # Act
    result = process_contract(contract_data)
    
    # Assert
    assert result["pricing"]["base_fee"] == 1000
    assert result["pricing"]["frequency"] == "monthly"
    assert result["status"] == "completed"
```

#### Step 2: Implement Minimal Code (Green Phase)
```python
def process_contract(contract_data):
    """Process contract and extract information."""
    # Minimal implementation to pass the test
    return {
        "pricing": {
            "base_fee": 1000,
            "frequency": "monthly"
        },
        "status": "completed"
    }
```

#### Step 3: Refactor and Improve (Refactor Phase)
```python
def process_contract(contract_data):
    """Process contract and extract information using AI agents."""
    # Improved implementation with proper structure
    agents = initialize_pricing_agents()
    result = agents.process(contract_data)
    
    return {
        "pricing": result.pricing_info,
        "status": result.status,
        "confidence": result.confidence_score
    }
```

### Test Categories and Structure

#### Unit Tests
```python
# tests/unit/test_contract_processing.py
import pytest
from src.core.contract_processor import ContractProcessor

class TestContractProcessor:
    def test_extract_pricing_info(self):
        """Test pricing information extraction."""
        processor = ContractProcessor()
        contract_text = "Monthly fee: $500"
        
        result = processor.extract_pricing(contract_text)
        
        assert result["amount"] == 500
        assert result["frequency"] == "monthly"
    
    def test_handle_invalid_contract(self):
        """Test handling of invalid contract data."""
        processor = ContractProcessor()
        
        with pytest.raises(ValueError):
            processor.process_contract(None)
```

#### Integration Tests
```python
# tests/integration/test_api_endpoints.py
import pytest
from fastapi.testclient import TestClient
from src.main import app

class TestContractAPI:
    def test_upload_contract_success(self):
        """Test successful contract upload."""
        client = TestClient(app)
        
        response = client.post(
            "/api/v1/contracts/upload",
            json={
                "filename": "test_contract.pdf",
                "content_type": "application/pdf",
                "file_size": 1024,
                "document_type": "pdf"
            }
        )
        
        assert response.status_code == 201
        assert "contract_id" in response.json()
    
    def test_upload_contract_invalid_format(self):
        """Test contract upload with invalid format."""
        client = TestClient(app)
        
        response = client.post(
            "/api/v1/contracts/upload",
            json={
                "filename": "test.txt",
                "content_type": "text/plain",
                "file_size": 1024,
                "document_type": "unsupported"
            }
        )
        
        assert response.status_code == 422
        assert "error" in response.json()
```

#### Security Tests
```python
# tests/security/test_authentication.py
import pytest
from fastapi.testclient import TestClient
from src.main import app

class TestAuthentication:
    def test_protected_endpoint_requires_auth(self):
        """Test that protected endpoints require authentication."""
        client = TestClient(app)
        
        response = client.get("/api/v1/contracts")
        
        assert response.status_code == 401
        assert "unauthorized" in response.json()["detail"].lower()
    
    def test_valid_jwt_token_grants_access(self):
        """Test that valid JWT token grants access."""
        client = TestClient(app)
        token = create_valid_jwt_token()
        
        response = client.get(
            "/api/v1/contracts",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
    
    def test_invalid_jwt_token_denies_access(self):
        """Test that invalid JWT token denies access."""
        client = TestClient(app)
        
        response = client.get(
            "/api/v1/contracts",
            headers={"Authorization": "Bearer invalid_token"}
        )
        
        assert response.status_code == 401
```

## 🔒 Security-First Development Process

### Security Validation Checklist

#### Input Validation Security
```python
# Security test for input validation
def test_sql_injection_prevention():
    """Test that SQL injection attempts are prevented."""
    client = TestClient(app)
    malicious_input = "'; DROP TABLE contracts; --"
    
    response = client.post(
        "/api/v1/contracts/search",
        json={"query": malicious_input}
    )
    
    # Should not cause database error
    assert response.status_code in [200, 400, 422]
    # Verify no SQL injection occurred
    assert "error" not in response.json() or "sql" not in str(response.json()).lower()
```

#### Authentication Security
```python
def test_password_security():
    """Test password security requirements."""
    client = TestClient(app)
    
    # Test weak password rejection
    weak_password_data = {
        "username": "testuser",
        "password": "123",
        "email": "test@example.com"
    }
    
    response = client.post("/api/v1/auth/register", json=weak_password_data)
    assert response.status_code == 422
    assert "password" in response.json()["detail"].lower()
```

#### Authorization Security
```python
def test_role_based_access_control():
    """Test role-based access control."""
    client = TestClient(app)
    
    # Test user cannot access admin endpoints
    user_token = create_user_token()
    response = client.get(
        "/api/v1/admin/users",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    
    assert response.status_code == 403
    assert "forbidden" in response.json()["detail"].lower()
```

### Security Testing Tools Integration

#### Pre-commit Security Checks
```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/Yelp/detect-secrets
    rev: v1.4.0
    hooks:
      - id: detect-secrets
        args: ['--baseline', '.secrets.baseline']
  
  - repo: https://github.com/PyCQA/bandit
    rev: 1.7.5
    hooks:
      - id: bandit
        args: ['-r', 'src/', '-f', 'json', '-o', 'bandit-report.json']
```

#### CI/CD Security Pipeline
```yaml
# .github/workflows/security.yml
name: Security Validation
on: [push, pull_request]

jobs:
  security-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Run Bandit Security Scan
        run: |
          pip install bandit
          bandit -r src/ -f json -o bandit-report.json
      
      - name: Run Safety Check
        run: |
          pip install safety
          safety check --json --output safety-report.json
      
      - name: Upload Security Reports
        uses: actions/upload-artifact@v3
        with:
          name: security-reports
          path: |
            bandit-report.json
            safety-report.json
```

## 📚 Documentation-First Development

### Documentation Requirements
1. **API Documentation**: OpenAPI/Swagger specs updated before implementation
2. **Code Documentation**: Docstrings for all functions and classes
3. **User Documentation**: User guides updated with each feature
4. **Architecture Documentation**: System design documents maintained

### Documentation Workflow
```python
# Example: Documenting before implementing
def process_contract_with_ai_agents(contract_data: dict) -> ContractResult:
    """
    Process contract using AI agents to extract key information.
    
    This function orchestrates 20 specialized AI agents to analyze
    contract documents and extract structured information including
    pricing, terms, compliance, and risk assessment.
    
    Args:
        contract_data (dict): Contract document data containing:
            - content (str): Contract text content
            - contract_type (str): Type of contract (service, supply, etc.)
            - metadata (dict): Additional contract metadata
    
    Returns:
        ContractResult: Structured result containing:
            - pricing_info (dict): Extracted pricing information
            - terms_conditions (dict): Contract terms and conditions
            - compliance_status (dict): Compliance assessment
            - risk_assessment (dict): Risk analysis results
            - quality_score (float): Overall contract quality score
    
    Raises:
        ValidationError: If contract data is invalid
        ProcessingError: If AI agent processing fails
        TimeoutError: If processing exceeds time limit
    
    Example:
        >>> contract_data = {
        ...     "content": "Service fee: $1000/month",
        ...     "contract_type": "service"
        ... }
        >>> result = process_contract_with_ai_agents(contract_data)
        >>> print(result.pricing_info["base_fee"])
        1000
    """
    # Implementation follows...
```

## 🚀 Release and Deployment Process

### Pre-Release Validation
1. **Test Suite Execution**:
   ```bash
   # Run all tests
   pytest tests/ --cov=src --cov-report=html --cov-report=term
   
   # Run security tests
   pytest tests/security/ -v
   
   # Run performance tests
   pytest tests/performance/ -v
   ```

2. **Security Validation**:
   ```bash
   # Security scanning
   bandit -r src/
   safety check
   
   # Dependency vulnerability check
   pip-audit
   ```

3. **Documentation Validation**:
   ```bash
   # Check API documentation
   python -m src.api.validate_docs
   
   # Generate documentation
   sphinx-build docs/ docs/_build/
   ```

### Release Process
1. **Version Update**:
   ```bash
   # Update version in all files
   python scripts/update_version.py 1.1.0
   ```

2. **Create Release**:
   ```bash
   # Create and push tag
   git tag -a v1.1.0 -m "Release v1.1.0: Enhanced AI agent processing"
   git push origin v1.1.0
   
   # Create GitHub release
   gh release create v1.1.0 --title "PyFSD GenAI v1.1.0" --notes-file RELEASE_NOTES_v1.1.0.md
   ```

3. **Deploy to Staging**:
   ```bash
   # Deploy to staging environment
   docker-compose -f docker-compose.staging.yml up -d
   
   # Run smoke tests
   pytest tests/smoke/ --env=staging
   ```

4. **Deploy to Production**:
   ```bash
   # Deploy to production (only if staging passes)
   kubectl apply -f k8s/production/
   
   # Monitor deployment
   kubectl get pods -l app=pyfsdgenai
   ```

## 📊 Quality Metrics and Monitoring

### Code Quality Metrics
- **Test Coverage**: Minimum 90%
- **Code Complexity**: Maximum cyclomatic complexity of 10
- **Security Score**: Zero high/critical vulnerabilities
- **Performance**: API response time < 200ms
- **Documentation**: 100% API endpoint documentation

### Continuous Monitoring
```python
# Example: Performance monitoring
import time
from functools import wraps

def monitor_performance(func):
    """Monitor function performance."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        execution_time = time.time() - start_time
        
        # Log performance metrics
        logger.info(f"{func.__name__} executed in {execution_time:.2f}s")
        
        # Alert if performance threshold exceeded
        if execution_time > 5.0:  # 5 second threshold
            logger.warning(f"Performance alert: {func.__name__} took {execution_time:.2f}s")
        
        return result
    return wrapper
```

---

**TDD & Security Workflow Version**: 1.0  
**Created**: January 2025  
**Last Updated**: January 2025  
**Next Review**: Weekly
