# PyFSD GenAI - Contributing Guidelines

## Getting Started

Thank you for your interest in contributing to PyFSD GenAI! This document provides guidelines and information for contributors.

## Development Setup

### Prerequisites
- Python 3.9+
- Docker and Docker Compose
- Git
- Node.js (for frontend development, if applicable)

### Local Development Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd pyfsdgenai
   ```

2. **Set up environment**
   ```bash
   cp config.env.example .env
   # Edit .env with your configuration
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Start services with Docker**
   ```bash
   docker-compose up -d
   ```

5. **Run the application**
   ```bash
   python src/main.py
   ```

## Code Style and Standards

### Python Code Style
- Follow PEP 8 guidelines
- Use Black for code formatting
- Use type hints for all functions
- Write comprehensive docstrings

### Pre-commit Hooks
```bash
pip install pre-commit
pre-commit install
```

### Code Formatting
```bash
black src/ tests/
flake8 src/ tests/
mypy src/
```

## Testing

### Running Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/test_contract_processing.py
```

### Test Structure
- Unit tests for individual functions
- Integration tests for API endpoints
- End-to-end tests for complete workflows
- Mock external services and APIs

## Pull Request Process

### Before Submitting
1. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**
   - Write tests for new functionality
   - Update documentation if needed
   - Ensure all tests pass

3. **Commit your changes**
   ```bash
   git add .
   git commit -m "feat: add contract processing feature"
   ```

### Pull Request Guidelines
- Use descriptive titles
- Provide detailed descriptions
- Link related issues
- Include screenshots for UI changes
- Ensure CI/CD checks pass

### Commit Message Format
```
type(scope): description

[optional body]

[optional footer]
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Test additions/changes
- `chore`: Maintenance tasks

## Project Structure

```
pyfsdgenai/
├── src/
│   ├── agents/          # AI agent implementations
│   ├── api/             # API endpoints and routes
│   ├── core/            # Core business logic
│   ├── models/          # Data models and schemas
│   └── utils/           # Utility functions
├── tests/               # Test suites
├── docs/                # Documentation
├── config/              # Configuration files
└── scripts/             # Utility scripts
```

## AI Agent Development

### Creating New Agents
1. Create agent class in `src/agents/`
2. Implement required methods:
   - `process()`: Main processing logic
   - `validate()`: Input validation
   - `extract()`: Data extraction logic

3. Register agent in agent registry
4. Write comprehensive tests
5. Update documentation

### Agent Guidelines
- Single responsibility principle
- Idempotent operations
- Proper error handling
- Logging and monitoring
- Configurable parameters

## API Development

### Endpoint Guidelines
- RESTful design principles
- Proper HTTP status codes
- Request/response validation
- Error handling and responses
- API versioning

### Documentation
- OpenAPI/Swagger documentation
- Example requests/responses
- Error code documentation
- Rate limiting information

## Security Considerations

### Data Handling
- Encrypt sensitive data
- Implement proper access controls
- Audit logging for all operations
- Data anonymization where needed

### API Security
- Input validation and sanitization
- Rate limiting
- Authentication and authorization
- CORS configuration

## Performance Guidelines

### Optimization
- Database query optimization
- Caching strategies
- Async/await patterns
- Resource management

### Monitoring
- Application metrics
- Performance monitoring
- Error tracking
- Health checks

## Documentation

### Code Documentation
- Docstrings for all functions/classes
- Type hints for better IDE support
- README files for modules
- Architecture decision records (ADRs)

### User Documentation
- API documentation
- User guides
- Troubleshooting guides
- FAQ sections

## Issue Reporting

### Bug Reports
- Use the bug report template
- Include steps to reproduce
- Provide environment details
- Include error logs and screenshots

### Feature Requests
- Use the feature request template
- Describe the problem and solution
- Provide use cases and examples
- Consider implementation complexity

## Community Guidelines

### Code of Conduct
- Be respectful and inclusive
- Provide constructive feedback
- Help others learn and grow
- Follow professional standards

### Communication
- Use clear and concise language
- Provide context for discussions
- Be patient with questions
- Share knowledge and resources

## Release Process

### Versioning
- Follow Semantic Versioning (SemVer)
- Update version numbers in all relevant files
- Create release notes
- Tag releases appropriately

### Deployment
- Automated testing in CI/CD
- Staging environment testing
- Production deployment procedures
- Rollback procedures

## Getting Help

### Resources
- Documentation in `/docs`
- Issue tracker for questions
- Discussion forums for ideas
- Code review for feedback

### Contact
- Project maintainers
- Community channels
- Office hours (if available)
- Documentation and guides

---

Thank you for contributing to PyFSD GenAI! Your contributions help make this project better for everyone.

