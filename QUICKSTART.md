# Quick Start Guide

## Initial Setup

1. **Setup complet avec Makefile** (recommandé):
   ```bash
   make setup
   # ou
   make dev-setup
   ```

   Ou avec le script:
   ```bash
   ./setup.sh
   ```

   Ou manuellement:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install --upgrade pip
   pip install -r requirements-dev.txt
   ```

2. **Voir toutes les commandes disponibles**:
   ```bash
   make help
   ```

3. **Vérifier l'installation**:
   ```bash
   make info
   ```

## Running Tests

**Avec Makefile** (recommandé):
```bash
make test              # Tous les tests
make test-unit         # Tests unitaires seulement
make test-integration   # Tests d'intégration seulement
make test-regression    # Tests de régression seulement
make test-e2e          # Tests end-to-end seulement
make test-coverage     # Tests avec couverture
make test-warnings     # Tests avec vérification des warnings
make quick-test         # Test rapide (unit tests seulement)
```

**Avec pytest directement**:
```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=src --cov-report=term-missing

# Run only unit tests
pytest -m unit

# Run only integration tests
pytest -m integration

# Run only regression tests
pytest -m regression

# Run integration and regression tests together
pytest -m "integration or regression"

# Run specific test file
pytest tests/shared/utils/test_validation.py
pytest tests/shared/integration/test_validation_and_exceptions.py
pytest tests/shared/regression/test_validation_regression.py

# Run tests in specific directory
pytest tests/shared/integration/
pytest tests/shared/regression/

# Run tests and fail on warnings
pytest -W error
```

### Test Types

- **Unit Tests** (`-m unit`): Test individual components in isolation
- **Integration Tests** (`-m integration`): Test multiple components working together
- **Regression Tests** (`-m regression`): Ensure previously fixed bugs don't reoccur

## Code Quality Checks

**Avec Makefile** (recommandé):
```bash
make format          # Formate le code (Black + isort)
make format-check    # Vérifie le formatage sans modifier
make lint            # Exécute le linter
make lint-fix        # Corrige automatiquement les erreurs
make type-check      # Vérifie les types avec mypy
make check-all       # Tous les checks (format, lint, types, tests)
make pre-commit      # Préparation avant commit
make quick-check     # Vérification rapide (format + lint)
```

**Avec les outils directement**:
```bash
# Format code
black src tests
isort src tests

# Lint code
ruff check src tests
mypy src

# Auto-fix linting issues
ruff check --fix src tests
```

## Creating a New Endpoint

1. Create endpoint directory structure:
   ```bash
   mkdir -p src/endpoints/my_endpoint/{domain,application,presentation}
   touch src/endpoints/my_endpoint/__init__.py
   touch src/endpoints/my_endpoint/main.py
   ```

2. Create test directory:
   ```bash
   mkdir -p tests/endpoints/my_endpoint/{unit,integration,regression,e2e}
   ```

3. Write tests first (TDD), then implement functionality.

4. Ensure 100% test coverage before committing.

## Project Structure Overview

- `src/shared/` - Shared code used by all endpoints
- `src/endpoints/` - Independent domain-specific endpoints
- `tests/` - Test suites mirroring source structure
- `docker/` - Docker configurations for endpoints

## Next Steps

1. Review the example code in `src/shared/` to understand the structure
2. Review the example tests in `tests/shared/` to understand testing patterns:
   - Unit tests: `tests/shared/utils/test_validation.py`
   - Integration tests: `tests/shared/integration/test_validation_and_exceptions.py`
   - Regression tests: `tests/shared/regression/test_validation_regression.py`
3. Create your first endpoint following TDD principles
4. Write unit, integration, and regression tests for your code
5. Ensure all code quality checks pass before committing

