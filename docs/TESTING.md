# Testing Guide

This document provides comprehensive guidance on writing and running different types of tests in the TDDRAGON project.

## Test Types

### Unit Tests

**Purpose**: Test individual components in isolation.

**Characteristics**:
- Fast execution (< 1 second each)
- No external dependencies (databases, APIs, file systems)
- Mock all external interactions
- Must achieve 100% code coverage
- Located in `tests/shared/unit/` or `tests/endpoints/[endpoint]/unit/`

**Example**:
```python
import pytest
from src.shared.utils.validation import validate_email

class TestValidateEmail:
    """Test suite for validate_email function."""

    def test_valid_email_returns_true(self) -> None:
        """Test that valid email addresses return True."""
        # Arrange
        email = "user@example.com"
        
        # Act
        result = validate_email(email)
        
        # Assert
        assert result is True
```

**Running Unit Tests**:
```bash
pytest -m unit
pytest tests/shared/unit/
```

### Integration Tests

**Purpose**: Test multiple components working together correctly.

**Characteristics**:
- Verify components integrate correctly
- May interact with external systems (with proper setup/teardown)
- Test workflows and component interactions
- Coverage should be >90%
- Located in `tests/shared/integration/` or `tests/endpoints/[endpoint]/integration/`

**Example**:
```python
import pytest
from src.shared.utils.validation import validate_email
from src.shared.exceptions.validation_error import ValidationError

class TestValidationWithExceptions:
    """Integration tests for validation utilities with exceptions."""

    def test_validate_email_raises_validation_error_on_invalid(self) -> None:
        """Test that invalid email validation works with ValidationError."""
        # Arrange
        email = "invalid-email"
        
        # Act & Assert
        if not validate_email(email):
            with pytest.raises(ValidationError) as exc_info:
                raise ValidationError(f"Invalid email: {email}")
            assert "Invalid email" in str(exc_info.value)
```

**Running Integration Tests**:
```bash
pytest -m integration
pytest tests/shared/integration/
```

### Regression Tests

**Purpose**: Ensure previously fixed bugs do not reoccur.

**Characteristics**:
- Document specific bugs that were fixed
- Critical for maintaining code quality over time
- Should be run before every release
- Each test should document the bug it prevents
- Located in `tests/shared/regression/` or `tests/endpoints/[endpoint]/regression/`

**Example**:
```python
import pytest
from src.shared.utils.validation import validate_email

class TestValidationRegression:
    """Regression tests for validation utilities."""

    @pytest.mark.regression
    def test_email_validation_handles_none_correctly(self) -> None:
        """
        Regression test: Ensure None values are handled correctly.
        
        Bug: Previously, None values could cause AttributeError.
        Fix: Added None check before string operations.
        """
        # Arrange
        email = None
        
        # Act
        result = validate_email(email)  # type: ignore[arg-type]
        
        # Assert
        assert result is False
        # Should not raise AttributeError or TypeError
```

**Running Regression Tests**:
```bash
pytest -m regression
pytest tests/shared/regression/
```

### End-to-End (E2E) Tests

**Purpose**: Test complete user workflows from start to finish.

**Characteristics**:
- Test entire application flows
- May require full system setup
- Slower execution
- Located in `tests/shared/e2e/` or `tests/endpoints/[endpoint]/e2e/`

**Running E2E Tests**:
```bash
pytest -m e2e
pytest tests/shared/e2e/
```

## Test Structure

### Directory Organization

```
tests/
├── conftest.py                    # Shared fixtures
├── shared/
│   ├── unit/                      # Unit tests for shared code
│   ├── integration/              # Integration tests for shared code
│   ├── regression/                # Regression tests for shared code
│   └── e2e/                       # E2E tests for shared code
└── endpoints/
    └── [endpoint_name]/
        ├── unit/                  # Unit tests for endpoint
        ├── integration/           # Integration tests for endpoint
        ├── regression/            # Regression tests for endpoint
        └── e2e/                   # E2E tests for endpoint
```

### Test File Naming

- Unit tests: `test_<module_name>.py`
- Integration tests: `test_<component1>_and_<component2>.py`
- Regression tests: `test_<module_name>_regression.py`
- E2E tests: `test_<workflow_name>_e2e.py`

### Test Class Naming

- Use descriptive names: `Test<ComponentName>`
- Group related tests in classes
- Use docstrings to describe the test suite

### Test Function Naming

- Use descriptive names: `test_<functionality>_<scenario>_<expected_result>`
- Follow pattern: `test_<what>_<when>_<then>`
- Use docstrings to explain what the test verifies

## Test Markers

Use pytest markers to categorize tests:

```python
@pytest.mark.unit
def test_something() -> None:
    """Unit test."""

@pytest.mark.integration
def test_integration() -> None:
    """Integration test."""

@pytest.mark.regression
def test_regression() -> None:
    """Regression test."""

@pytest.mark.e2e
def test_e2e() -> None:
    """E2E test."""

@pytest.mark.slow
def test_slow_operation() -> None:
    """Slow running test."""
```

## Test Fixtures

Shared fixtures are defined in `tests/conftest.py`:

```python
@pytest.fixture
def logger() -> Generator:
    """Provide a logger instance for tests."""
    logger_instance = get_logger("test", level=10)
    yield logger_instance

@pytest.fixture
def sample_email_valid() -> str:
    """Provide a valid email address for testing."""
    return "test@example.com"
```

Use fixtures in tests:

```python
def test_something(logger, sample_email_valid: str) -> None:
    """Test using fixtures."""
    logger.info(f"Testing with {sample_email_valid}")
    # Test code here
```

## Best Practices

### 1. Arrange-Act-Assert (AAA) Pattern

```python
def test_example() -> None:
    """Test example using AAA pattern."""
    # Arrange
    email = "test@example.com"
    
    # Act
    result = validate_email(email)
    
    # Assert
    assert result is True
```

### 2. One Assertion Per Test (When Possible)

```python
# Good: One assertion
def test_email_is_valid() -> None:
    """Test email validation."""
    assert validate_email("test@example.com") is True

# Also good: Related assertions
def test_email_validation_results() -> None:
    """Test email validation returns correct results."""
    assert validate_email("test@example.com") is True
    assert validate_email("invalid") is False
```

### 3. Use Parametrize for Multiple Scenarios

```python
@pytest.mark.parametrize("email,expected", [
    ("user@example.com", True),
    ("invalid", False),
    ("", False),
])
def test_email_validation(email: str, expected: bool) -> None:
    """Test email validation with various inputs."""
    assert validate_email(email) == expected
```

### 4. Mock External Dependencies

```python
from unittest.mock import Mock, patch

def test_with_mock() -> None:
    """Test using mocks."""
    with patch('module.external_function') as mock_func:
        mock_func.return_value = "mocked_value"
        # Test code here
```

### 5. Document Regression Tests

```python
@pytest.mark.regression
def test_fixed_bug() -> None:
    """
    Regression test: Ensure bug #123 does not reoccur.
    
    Bug: Previously, function X would crash when given None.
    Fix: Added None check in function X.
    Date Fixed: 2024-01-15
    """
    # Test code here
```

## Running Tests

### Run All Tests
```bash
pytest
```

### Run Specific Test Types
```bash
pytest -m unit              # Unit tests only
pytest -m integration        # Integration tests only
pytest -m regression         # Regression tests only
pytest -m e2e                # E2E tests only
pytest -m "integration or regression"  # Multiple types
```

### Run Tests with Coverage
```bash
pytest --cov=src --cov-report=term-missing
pytest --cov=src --cov-report=html    # HTML report
```

### Run Specific Test File or Directory
```bash
pytest tests/shared/utils/test_validation.py
pytest tests/shared/integration/
```

### Run Tests with Verbose Output
```bash
pytest -v                    # Verbose
pytest -vv                   # More verbose
pytest -s                    # Show print statements
```

### Run Tests and Fail on Warnings
```bash
pytest -W error
```

## Coverage Requirements

- **Unit Tests**: Must achieve 100% code coverage
- **Integration Tests**: Should achieve >90% coverage
- **Regression Tests**: Focus on critical paths and previously buggy code
- **E2E Tests**: Cover main user workflows

## Continuous Integration

Tests should be run in CI/CD pipelines:

```yaml
# Example CI configuration
test:
  script:
    - pytest -m unit --cov=src --cov-report=xml
    - pytest -m integration
    - pytest -m regression
```

## Troubleshooting

### Tests Failing

1. Check test output for error messages
2. Run tests with `-v` for verbose output
3. Run tests with `-s` to see print statements
4. Check for missing dependencies
5. Verify test fixtures are set up correctly

### Coverage Issues

1. Run `pytest --cov=src --cov-report=term-missing` to see missing lines
2. Ensure all code paths are tested
3. Check that test files are in the correct directories
4. Verify pytest.ini configuration

### Slow Tests

1. Use `pytest -m slow` to identify slow tests
2. Optimize test setup/teardown
3. Use mocks instead of real external dependencies
4. Consider parallel test execution: `pytest -n auto`

## Additional Resources

- [pytest Documentation](https://docs.pytest.org/)
- [pytest-cov Documentation](https://pytest-cov.readthedocs.io/)
- [Testing Best Practices](https://docs.python.org/3/library/unittest.html)

