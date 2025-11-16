# TDDRAGON

Multi-main modular endpoints Python project following Test-Driven Development (TDD) principles.

## Project Structure

This project follows a multi-main modular architecture where:

- **Shared Code**: Common utilities, models, infrastructure, and exceptions live in `src/shared/`
- **Endpoints**: Independent domain-specific endpoints in `src/endpoints/`, each with its own main entry point
- **Tests**: Test suites mirror the source structure in `tests/`

```
project/
├── src/
│   ├── shared/                    # Shared/common code
│   │   ├── utils/                 # Common utilities
│   │   ├── models/                # Shared data models
│   │   ├── infrastructure/        # Shared infrastructure
│   │   └── exceptions/            # Shared exception classes
│   └── endpoints/                 # Domain-specific endpoints
│       └── [endpoint_name]/       # Each endpoint is independent
│           ├── main.py            # Main entry point
│           ├── domain/            # Domain logic
│           ├── application/       # Use cases / services
│           └── presentation/      # API handlers, CLI
├── tests/                         # Test suites
│   ├── shared/                    # Tests for shared code
│   │   ├── unit/                  # Unit tests for shared code
│   │   ├── integration/          # Integration tests for shared code
│   │   └── regression/            # Regression tests for shared code
│   ├── endpoints/                 # Tests for endpoints
│   ├── integration/               # Cross-component integration tests
│   ├── regression/                # Cross-component regression tests
│   └── conftest.py                # Shared pytest fixtures
├── docker/                        # Docker configurations
│   └── base/                      # Base Dockerfile
├── docs/                          # Documentation
├── requirements.txt               # Production dependencies
├── requirements-dev.txt           # Development dependencies
├── pyproject.toml                 # Project configuration
├── pytest.ini                    # Pytest configuration
└── docker-compose.yml             # Docker Compose configuration
```

## Getting Started

### Prerequisites

- Python 3.9 or higher
- pip
- make (pour utiliser le Makefile)
- (Optional) Docker and Docker Compose for containerized deployment

### Setup

1. **Clone the repository** (if applicable):
   ```bash
   git clone <repository-url>
   cd TDDRAGON
   ```

2. **Setup complet avec Makefile** (recommandé):
   ```bash
   make setup
   # ou
   make dev-setup
   ```

   Ou manuellement:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install --upgrade pip
   pip install -r requirements-dev.txt
   ```

3. **Voir toutes les commandes disponibles**:
   ```bash
   make help
   ```

4. **Vérifier l'installation**:
   ```bash
   make info
   ```

## Development Workflow

### Test-Driven Development (TDD)

This project follows strict TDD principles:

1. **Write tests first** - Write failing tests before implementation
2. **Make tests pass** - Write minimal code to pass tests
3. **Refactor** - Improve code while keeping tests green

### Running Tests

**Avec Makefile** (recommandé):
```bash
make test              # Tous les tests
make test-unit         # Tests unitaires seulement
make test-integration  # Tests d'intégration seulement
make test-regression   # Tests de régression seulement
make test-e2e          # Tests end-to-end seulement
make test-coverage     # Tests avec couverture
make test-warnings     # Tests avec vérification des warnings
```

**Avec pytest directement**:
```bash
# Run all tests with coverage
pytest

# Run tests with verbose output
pytest -v

# Run only unit tests
pytest -m unit

# Run only integration tests
pytest -m integration

# Run only regression tests
pytest -m regression

# Run integration and regression tests together
pytest -m "integration or regression"

# Run tests with coverage report
pytest --cov=src --cov-report=term-missing

# Run tests and fail on warnings
pytest -W error

# Run specific test file
pytest tests/shared/integration/test_validation_and_exceptions.py

# Run tests in specific directory
pytest tests/shared/integration/
pytest tests/shared/regression/
```

**Test Types:**

1. **Unit Tests** (`-m unit`): Test individual components in isolation
   - Must achieve 100% code coverage
   - Fast execution (< 1 second each)
   - No external dependencies

2. **Integration Tests** (`-m integration`): Test multiple components working together
   - Verify components integrate correctly
   - May interact with external systems
   - Coverage should be >90%

3. **Regression Tests** (`-m regression`): Ensure previously fixed bugs don't reoccur
   - Document specific bugs that were fixed
   - Critical for maintaining code quality over time
   - Should be run before every release

**Requirements:**
- Unit test coverage must be 100%
- Integration test coverage should be >90%
- All tests must pass with zero errors and zero warnings

### Code Quality

**Avec Makefile** (recommandé):
```bash
make format          # Formate le code (Black + isort)
make format-check    # Vérifie le formatage sans modifier
make lint            # Exécute le linter
make lint-fix        # Corrige automatiquement les erreurs de linting
make type-check      # Vérifie les types avec mypy
make check-all       # Exécute tous les checks (format, lint, types, tests)
make pre-commit      # Préparation avant commit (format, lint, types, tests)
```

**Avec les outils directement**:
```bash
# Format code with Black
black src tests

# Check import sorting with isort
isort src tests --check

# Auto-fix import sorting
isort src tests

# Run ruff linter
ruff check src tests

# Auto-fix ruff issues
ruff check --fix src tests

# Run mypy type checking
mypy src
```

#### Pre-commit Checks

Before committing, run:
```bash
make pre-commit
```

Or manually ensure:
- [ ] All tests pass (`make test` or `pytest`)
- [ ] Code is formatted (`make format` or `black src tests`)
- [ ] Imports are sorted (`make format` or `isort src tests`)
- [ ] No linting errors (`make lint` or `ruff check src tests`)
- [ ] No type errors (`make type-check` or `mypy src`)
- [ ] 100% unit test coverage (`make test-coverage` or `pytest --cov=src --cov-report=term-missing`)

## Docker Setup

**Avec Makefile** (recommandé):
```bash
make docker-build    # Construit les images Docker
make docker-up       # Démarre les conteneurs
make docker-down     # Arrête les conteneurs
make docker-logs     # Affiche les logs
make docker-dev      # Mode développement
make docker-prod     # Mode production
make docker-clean    # Nettoie les conteneurs et images
```

**Avec Docker Compose directement**:
```bash
# Build and run all services (development)
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up --build

# Build and run all services (production)
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up --build

# Run in background
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Building Individual Endpoint Images

Each endpoint should have its own Dockerfile in `docker/[endpoint_name]/Dockerfile`.

Example:
```bash
docker build -f docker/log-viewer/Dockerfile -t log-viewer:latest .
```

## Endpoints

### Log Collector (`log_collector`)

**Purpose**: Collects and stores Nginx access logs and uptime metrics.

**Port**: 8001

**Main Routes**:
- `GET /logs` - Query access logs with filters
- `GET /logs/uptime` - Get uptime percentage for a time range

**Start Server**:
```bash
python -m src.endpoints.log_collector.main
```

### Log Viewer (`log_viewer`) - v0.3.0

**Purpose**: Web UI for querying and visualizing Nginx access logs and uptime data.

**Port**: 8002

**Main Routes**:
- `GET /log-viewer/login` - Login page
- `GET /log-viewer/access-logs` - Access logs viewer (requires authentication)
- `GET /log-viewer/uptime` - Uptime monitoring page (requires authentication)
- `POST /log-viewer/api/filter-logs` - HTMX endpoint for filtering logs
- `GET /log-viewer/api/export-logs` - CSV export endpoint

**Features**:
- Filter logs by time range, status code, URI, and client IP
- Paginated log display
- HTTP status code histogram chart
- Uptime timeline visualization
- CSV export with filters
- Mock authentication (for v0.3.0)

**Mock Credentials**:
- `admin` / `admin123`
- `operator` / `operator123`
- `viewer` / `viewer123`

**Start Server**:
```bash
python -m src.endpoints.log_viewer.main
```

**Access via Nginx** (when running with docker-compose):
- `http://localhost/log-viewer/login` - Login page
- `http://localhost/log-viewer/access-logs` - Access logs viewer
- `http://localhost/log-viewer/uptime` - Uptime page

**Access Directly**:
- `http://localhost:8002/log-viewer/login` - Login page

## Architecture Guidelines

### Shared Code (`src/shared/`)

- **Domain-agnostic**: Shared code should not contain domain-specific logic
- **Well-tested**: Shared code must have comprehensive test coverage
- **Well-documented**: Document shared code thoroughly as it's used by multiple endpoints

### Endpoints (`src/endpoints/`)

- **Independent**: Each endpoint can be deployed and tested independently
- **No cross-dependencies**: Endpoints should NOT import from other endpoints
- **Use shared code**: Endpoints can import from `src/shared/`
- **Own main entry point**: Each endpoint has its own `main.py`

### Import Rules

- ✅ Endpoints can import from `src/shared/`
- ❌ Endpoints should NOT import from other endpoints
- ✅ Use clear import paths: `from src.shared.utils import logger`

## Code Standards

### Type Hints

All functions, methods, and class attributes must have type hints:

```python
def calculate_total(items: list[Item], discount: float = 0.0) -> float:
    """Calculate total with discount."""
    # Implementation
```

### Docstrings

All public functions, classes, and modules must have Google-style docstrings:

```python
def process_data(data: dict[str, Any]) -> dict[str, Any]:
    """
    Process input data and return processed result.
    
    This function validates and transforms the input data according to
    business rules.
    
    Args:
        data: Dictionary containing input data. Must contain 'id' key.
    
    Returns:
        Dictionary containing processed data with 'status' and 'result' keys.
    
    Raises:
        ValueError: If data is missing required keys.
    """
    # Implementation
```

### Code Style

- Follow PEP 8 strictly
- Maximum line length: 88 characters (Black default)
- Use Black for formatting
- Use isort for import sorting

## Makefile - Commandes principales

Toutes les commandes de développement sont disponibles via le Makefile:

```bash
make help              # Voir toutes les commandes disponibles
make setup             # Configuration initiale complète
make test              # Exécuter tous les tests
make format            # Formater le code
make lint              # Linter le code
make pre-commit        # Préparation avant commit
make docker-dev        # Docker en mode développement
```

Voir [docs/MAKEFILE.md](docs/MAKEFILE.md) pour la documentation complète du Makefile.

## Contributing

1. Create a feature branch
2. Write tests first (TDD)
3. Implement functionality
4. Ensure 100% test coverage
5. Run all quality checks: `make pre-commit`
6. Submit a pull request

## License

MIT License

## Support

For questions or issues, please refer to the project documentation or create an issue.

