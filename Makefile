.PHONY: help install install-dev test test-unit test-integration test-regression test-e2e test-coverage lint format type-check clean setup venv docker-build docker-up docker-down docker-logs check-all ci postgres-up postgres-down postgres-status postgres-connect postgres-create-db postgres-drop-db postgres-reset postgres-migrate postgres-migrate-upgrade postgres-migrate-downgrade postgres-migrate-history postgres-migrate-current postgres-backup postgres-restore

# Variables
PYTHON := python3
VENV := .venv
VENV_BIN := $(VENV)/bin
PYTEST := $(VENV_BIN)/pytest
BLACK := $(VENV_BIN)/black
ISORT := $(VENV_BIN)/isort
RUFF := $(VENV_BIN)/ruff
MYPY := $(VENV_BIN)/mypy
PIP := $(VENV_BIN)/pip
ALEMBIC := $(VENV_BIN)/alembic

# Colors for output
BLUE := \033[0;34m
GREEN := \033[0;32m
YELLOW := \033[0;33m
RED := \033[0;31m
NC := \033[0m # No Color

help: ## Affiche cette aide
	@echo "$(BLUE)TDDRAGON - Makefile Commands$(NC)"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(GREEN)%-20s$(NC) %s\n", $$1, $$2}'
	@echo ""

setup: venv install-dev ## Configuration complète de l'environnement (venv + dépendances)
	@echo "$(GREEN)✓ Environnement configuré avec succès$(NC)"

venv: ## Crée le virtual environment Python
	@if [ ! -d "$(VENV)" ]; then \
		echo "$(BLUE)Création du virtual environment...$(NC)"; \
		$(PYTHON) -m venv $(VENV); \
		echo "$(GREEN)✓ Virtual environment créé$(NC)"; \
	else \
		echo "$(YELLOW)Virtual environment existe déjà$(NC)"; \
	fi

install: venv ## Installe les dépendances de production
	@echo "$(BLUE)Installation des dépendances de production...$(NC)"
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt
	@echo "$(GREEN)✓ Dépendances de production installées$(NC)"

install-dev: venv ## Installe les dépendances de développement
	@echo "$(BLUE)Installation des dépendances de développement...$(NC)"
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements-dev.txt
	@echo "$(GREEN)✓ Dépendances de développement installées$(NC)"

test: ## Exécute tous les tests
	@echo "$(BLUE)Exécution de tous les tests...$(NC)"
	$(PYTEST) -v
	@echo "$(GREEN)✓ Tous les tests terminés$(NC)"

test-parallel: ## Exécute tous les tests en parallèle (plus rapide)
	@echo "$(BLUE)Exécution de tous les tests en parallèle...$(NC)"
	$(PYTEST) -v -n auto
	@echo "$(GREEN)✓ Tous les tests terminés$(NC)"

test-integration: ## Exécute uniquement les tests d'intégration
	@echo "$(BLUE)Exécution des tests d'intégration...$(NC)"
	$(PYTEST) tests/endpoints/log_collector/integration/ -v --cov=src/endpoints/log_collector --cov-report=term-missing --cov-fail-under=100 -m integration --override-ini="addopts=" -W 'ignore::DeprecationWarning' -W 'ignore:unclosed.*:ResourceWarning'
	@echo "$(GREEN)✓ Tests d'intégration terminés$(NC)"

test-integration-parallel: ## Exécute les tests d'intégration en parallèle
	@echo "$(BLUE)Exécution des tests d'intégration en parallèle...$(NC)"
	$(PYTEST) -m integration -v -n auto
	@echo "$(GREEN)✓ Tests d'intégration terminés$(NC)"

test-regression: ## Exécute uniquement les tests de régression (en parallèle avec couverture)
	@echo "$(BLUE)Exécution des tests de régression en parallèle avec couverture...$(NC)"
	$(PYTEST) -m regression -v -n auto --cov=src/endpoints/demo_api/application/create_item --cov=src/endpoints/demo_api/application/list_items --cov=src/endpoints/demo_api/domain/models --cov=src/endpoints/demo_api/infrastructure/repositories --cov=src/endpoints/demo_api/main --cov=src/endpoints/demo_api/presentation/dependencies --cov=src/endpoints/demo_api/presentation/health --cov=src/endpoints/demo_api/presentation/routes --cov=src/shared/exceptions/validation_error --cov=src/shared/infrastructure/database --cov=src/shared/infrastructure/logger --cov=src/shared/utils/validation --cov-report=term-missing --cov-fail-under=100
	@echo "$(GREEN)✓ Tests de régression terminés avec 100% de couverture$(NC)"

test-e2e: ## Exécute uniquement les tests end-to-end
	@echo "$(BLUE)Exécution des tests end-to-end...$(NC)"
	$(PYTEST) -m e2e -v
	@echo "$(GREEN)✓ Tests end-to-end terminés$(NC)"

test-coverage: ## Exécute les tests avec rapport de couverture
	@echo "$(BLUE)Exécution des tests avec couverture...$(NC)"
	$(PYTEST) --cov=src --cov-report=term-missing --cov-report=html
	@echo "$(GREEN)✓ Rapport de couverture généré dans htmlcov/index.html$(NC)"

test-coverage-parallel: ## Exécute les tests avec couverture en parallèle
	@echo "$(BLUE)Exécution des tests avec couverture en parallèle...$(NC)"
	$(PYTEST) --cov=src --cov-report=term-missing --cov-report=html -n auto
	@echo "$(GREEN)✓ Rapport de couverture généré dans htmlcov/index.html$(NC)"

test-coverage-xml: ## Exécute les tests avec rapport de couverture XML
	@echo "$(BLUE)Exécution des tests avec couverture XML...$(NC)"
	$(PYTEST) --cov=src --cov-report=xml
	@echo "$(GREEN)✓ Rapport de couverture XML généré$(NC)"

test-warnings: ## Exécute les tests et échoue sur les warnings
	@echo "$(BLUE)Exécution des tests avec vérification des warnings...$(NC)"
	$(PYTEST) -W error -v
	@echo "$(GREEN)✓ Tests terminés sans warnings$(NC)"

format: ## Formate le code avec Black et isort
	@echo "$(BLUE)Formatage du code...$(NC)"
	$(BLACK) src tests
	$(ISORT) src tests
	@echo "$(GREEN)✓ Code formaté$(NC)"

format-check: ## Vérifie le formatage sans modifier les fichiers
	@echo "$(BLUE)Vérification du formatage...$(NC)"
	$(BLACK) --check src tests
	$(ISORT) --check src tests
	@echo "$(GREEN)✓ Formatage vérifié$(NC)"

lint: ## Exécute le linter Ruff
	@echo "$(BLUE)Exécution du linter...$(NC)"
	$(RUFF) check src tests
	@echo "$(GREEN)✓ Linting terminé$(NC)"

lint-fix: ## Exécute le linter et corrige automatiquement les erreurs
	@echo "$(BLUE)Correction automatique des erreurs de linting...$(NC)"
	$(RUFF) check --fix src tests
	@echo "$(GREEN)✓ Erreurs de linting corrigées$(NC)"

type-check: ## Vérifie les types avec mypy
	@echo "$(BLUE)Vérification des types...$(NC)"
	$(MYPY) src
	@echo "$(GREEN)✓ Vérification des types terminée$(NC)"

check-all: format-check lint type-check test-warnings ## Exécute tous les checks (format, lint, types, tests)
	@echo "$(GREEN)✓ Tous les checks sont passés$(NC)"

ci: install-dev check-all test-coverage ## Exécute la pipeline CI complète
	@echo "$(GREEN)✓ Pipeline CI terminée avec succès$(NC)"

clean: ## Nettoie les fichiers générés
	@echo "$(BLUE)Nettoyage des fichiers générés...$(NC)"
	find . -type d -name "__pycache__" -exec rm -r {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	find . -type d -name "*.egg-info" -exec rm -r {} + 2>/dev/null || true
	rm -rf .pytest_cache
	rm -rf .mypy_cache
	rm -rf .ruff_cache
	rm -rf .coverage
	rm -rf htmlcov
	rm -rf dist
	rm -rf build
	rm -rf *.egg-info
	@echo "$(GREEN)✓ Nettoyage terminé$(NC)"

clean-venv: ## Supprime le virtual environment
	@echo "$(BLUE)Suppression du virtual environment...$(NC)"
	rm -rf $(VENV)
	@echo "$(GREEN)✓ Virtual environment supprimé$(NC)"

clean-all: clean clean-venv ## Nettoie tout (fichiers générés + venv)
	@echo "$(GREEN)✓ Nettoyage complet terminé$(NC)"

# Docker commands
docker-build: ## Construit les images Docker
	@echo "$(BLUE)Construction des images Docker...$(NC)"
	docker-compose build
	@echo "$(GREEN)✓ Images Docker construites$(NC)"

docker-up: ## Démarre les conteneurs Docker
	@echo "$(BLUE)Démarrage des conteneurs Docker...$(NC)"
	docker-compose up -d
	@echo "$(GREEN)✓ Conteneurs Docker démarrés$(NC)"

docker-down: ## Arrête les conteneurs Docker
	@echo "$(BLUE)Arrêt des conteneurs Docker...$(NC)"
	docker-compose down
	@echo "$(GREEN)✓ Conteneurs Docker arrêtés$(NC)"

docker-logs: ## Affiche les logs des conteneurs Docker
	docker-compose logs -f

docker-dev: ## Démarre les conteneurs Docker en mode développement
	@echo "$(BLUE)Démarrage des conteneurs Docker en mode développement...$(NC)"
	docker-compose -f docker-compose.yml -f docker-compose.dev.yml up --build
	@echo "$(GREEN)✓ Conteneurs Docker démarrés en mode développement$(NC)"

docker-prod: ## Démarre les conteneurs Docker en mode production
	@echo "$(BLUE)Démarrage des conteneurs Docker en mode production...$(NC)"
	docker-compose -f docker-compose.yml -f docker-compose.prod.yml up --build -d
	@echo "$(GREEN)✓ Conteneurs Docker démarrés en mode production$(NC)"

docker-clean: ## Nettoie les conteneurs et images Docker
	@echo "$(BLUE)Nettoyage Docker...$(NC)"
	docker-compose down -v --rmi all
	@echo "$(GREEN)✓ Nettoyage Docker terminé$(NC)"

# PostgreSQL commands
POSTGRES_USER := $(shell grep POSTGRES_USER .env 2>/dev/null | cut -d '=' -f2 || echo "postgres")
POSTGRES_PASSWORD := $(shell grep POSTGRES_PASSWORD .env 2>/dev/null | cut -d '=' -f2 || echo "postgres")
POSTGRES_DB := $(shell grep POSTGRES_DB .env 2>/dev/null | cut -d '=' -f2 || echo "tddragon")
POSTGRES_HOST := $(shell grep POSTGRES_HOST .env 2>/dev/null | cut -d '=' -f2 || echo "localhost")
POSTGRES_PORT := $(shell grep POSTGRES_PORT .env 2>/dev/null | cut -d '=' -f2 || echo "5432")
POSTGRES_CONTAINER := postgres-db

postgres-up: ## Démarre PostgreSQL via Docker
	@echo "$(BLUE)Démarrage de PostgreSQL...$(NC)"
	@if docker ps -a --format '{{.Names}}' | grep -q "^$(POSTGRES_CONTAINER)$$"; then \
		docker start $(POSTGRES_CONTAINER); \
		echo "$(GREEN)✓ PostgreSQL démarré$(NC)"; \
	else \
		echo "$(YELLOW)PostgreSQL n'existe pas. Utilisez 'make docker-up' pour créer le conteneur$(NC)"; \
	fi

postgres-down: ## Arrête PostgreSQL
	@echo "$(BLUE)Arrêt de PostgreSQL...$(NC)"
	@if docker ps --format '{{.Names}}' | grep -q "^$(POSTGRES_CONTAINER)$$"; then \
		docker stop $(POSTGRES_CONTAINER); \
		echo "$(GREEN)✓ PostgreSQL arrêté$(NC)"; \
	else \
		echo "$(YELLOW)PostgreSQL n'est pas en cours d'exécution$(NC)"; \
	fi

postgres-status: ## Vérifie le statut de PostgreSQL
	@echo "$(BLUE)Statut de PostgreSQL:$(NC)"
	@if docker ps --format '{{.Names}}' | grep -q "^$(POSTGRES_CONTAINER)$$"; then \
		echo "  Status: $(GREEN)✓ En cours d'exécution$(NC)"; \
		docker exec $(POSTGRES_CONTAINER) pg_isready -U "$(POSTGRES_USER)" && echo "  Ready: $(GREEN)✓ Prêt$(NC)" || echo "  Ready: $(RED)✗ Non prêt$(NC)"; \
	else \
		echo "  Status: $(RED)✗ Arrêté$(NC)"; \
	fi

postgres-connect: ## Se connecte à PostgreSQL via psql
	@echo "$(BLUE)Connexion à PostgreSQL...$(NC)"
	@if docker ps --format '{{.Names}}' | grep -q "^$(POSTGRES_CONTAINER)$$"; then \
		docker exec -it $(POSTGRES_CONTAINER) psql -U "$(POSTGRES_USER)" -d "$(POSTGRES_DB)"; \
	else \
		echo "$(RED)✗ PostgreSQL n'est pas en cours d'exécution. Utilisez 'make postgres-up'$(NC)"; \
	fi

postgres-create-db: ## Crée la base de données PostgreSQL
	@echo "$(BLUE)Création de la base de données $(POSTGRES_DB)...$(NC)"
	@if docker ps --format '{{.Names}}' | grep -q "^$(POSTGRES_CONTAINER)$$"; then \
		docker exec $(POSTGRES_CONTAINER) psql -U "$(POSTGRES_USER)" -c "CREATE DATABASE $(POSTGRES_DB);" 2>/dev/null || echo "$(YELLOW)La base de données existe déjà$(NC)"; \
		echo "$(GREEN)✓ Base de données créée$(NC)"; \
		echo "$(BLUE)Astuce: Exécutez 'make postgres-migrate' pour appliquer les migrations$(NC)"; \
	else \
		echo "$(RED)✗ PostgreSQL n'est pas en cours d'exécution. Utilisez 'make postgres-up'$(NC)"; \
	fi

postgres-drop-db: ## Supprime la base de données PostgreSQL
	@echo "$(RED)ATTENTION: Suppression de la base de données $(POSTGRES_DB)...$(NC)"
	@read -p "Êtes-vous sûr? (yes/no): " confirm && [ "$$confirm" = "yes" ] || exit 1
	@if docker ps --format '{{.Names}}' | grep -q "^$(POSTGRES_CONTAINER)$$"; then \
		docker exec $(POSTGRES_CONTAINER) psql -U "$(POSTGRES_USER)" -c "DROP DATABASE IF EXISTS $(POSTGRES_DB);"; \
		echo "$(GREEN)✓ Base de données supprimée$(NC)"; \
	else \
		echo "$(RED)✗ PostgreSQL n'est pas en cours d'exécution$(NC)"; \
	fi

postgres-reset: postgres-drop-db postgres-create-db ## Réinitialise la base de données (supprime et recrée)
	@echo "$(GREEN)✓ Base de données réinitialisée$(NC)"

postgres-migrate-upgrade: venv ## Applique toutes les migrations Alembic en attente
	@echo "$(BLUE)Application des migrations Alembic...$(NC)"
	@if [ ! -d "$(VENV)" ]; then \
		echo "$(RED)✗ Virtual environment n'existe pas. Exécutez 'make setup'$(NC)"; \
		exit 1; \
	fi
	@if [ ! -f "$(CURDIR)/$(ALEMBIC)" ]; then \
		echo "$(RED)✗ Alembic n'est pas installé. Exécutez 'make install-dev'$(NC)"; \
		exit 1; \
	fi
	@if [ -f "src/endpoints/demo_api/alembic.ini" ]; then \
		echo "$(YELLOW)Demo API:$(NC)"; \
		cd src/endpoints/demo_api && \
		export DATABASE_URL="postgresql://$(POSTGRES_USER):$(POSTGRES_PASSWORD)@$(POSTGRES_HOST):$(POSTGRES_PORT)/$(POSTGRES_DB)" && \
		PYTHONPATH="$(CURDIR)" "$(CURDIR)/$(ALEMBIC)" upgrade head; \
	fi
	@if [ -f "src/endpoints/log_collector/alembic.ini" ]; then \
		echo "$(YELLOW)Log Collector:$(NC)"; \
		cd src/endpoints/log_collector && \
		export DATABASE_URL="postgresql://$(POSTGRES_USER):$(POSTGRES_PASSWORD)@$(POSTGRES_HOST):$(POSTGRES_PORT)/$(POSTGRES_DB)" && \
		PYTHONPATH="$(CURDIR)" "$(CURDIR)/$(ALEMBIC)" upgrade head; \
	fi
	@echo "$(GREEN)✓ Migrations appliquées$(NC)"

postgres-migrate-downgrade: venv ## Annule la dernière migration Alembic
	@echo "$(BLUE)Annulation de la dernière migration...$(NC)"
	@if [ ! -d "$(VENV)" ]; then \
		echo "$(RED)✗ Virtual environment n'existe pas. Exécutez 'make setup'$(NC)"; \
		exit 1; \
	fi
	@if [ ! -f "$(CURDIR)/$(ALEMBIC)" ]; then \
		echo "$(RED)✗ Alembic n'est pas installé. Exécutez 'make install-dev'$(NC)"; \
		exit 1; \
	fi
	@if [ -f "src/endpoints/demo_api/alembic.ini" ]; then \
		echo "$(YELLOW)Demo API:$(NC)"; \
		cd src/endpoints/demo_api && \
		export DATABASE_URL="postgresql://$(POSTGRES_USER):$(POSTGRES_PASSWORD)@$(POSTGRES_HOST):$(POSTGRES_PORT)/$(POSTGRES_DB)" && \
		PYTHONPATH="$(CURDIR)" "$(CURDIR)/$(ALEMBIC)" downgrade -1; \
	fi
	@if [ -f "src/endpoints/log_collector/alembic.ini" ]; then \
		echo "$(YELLOW)Log Collector:$(NC)"; \
		cd src/endpoints/log_collector && \
		export DATABASE_URL="postgresql://$(POSTGRES_USER):$(POSTGRES_PASSWORD)@$(POSTGRES_HOST):$(POSTGRES_PORT)/$(POSTGRES_DB)" && \
		PYTHONPATH="$(CURDIR)" "$(CURDIR)/$(ALEMBIC)" downgrade -1; \
	fi
	@echo "$(GREEN)✓ Migration annulée$(NC)"

postgres-migrate-history: venv ## Affiche l'historique des migrations Alembic
	@echo "$(BLUE)Historique des migrations:$(NC)"
	@if [ ! -d "$(VENV)" ]; then \
		echo "$(RED)✗ Virtual environment n'existe pas. Exécutez 'make setup'$(NC)"; \
		exit 1; \
	fi
	@if [ ! -f "$(CURDIR)/$(ALEMBIC)" ]; then \
		echo "$(RED)✗ Alembic n'est pas installé. Exécutez 'make install-dev'$(NC)"; \
		exit 1; \
	fi
	@if [ -f "src/endpoints/demo_api/alembic.ini" ]; then \
		echo "$(YELLOW)Demo API:$(NC)"; \
		cd src/endpoints/demo_api && \
		export DATABASE_URL="postgresql://$(POSTGRES_USER):$(POSTGRES_PASSWORD)@$(POSTGRES_HOST):$(POSTGRES_PORT)/$(POSTGRES_DB)" && \
		PYTHONPATH="$(CURDIR)" "$(CURDIR)/$(ALEMBIC)" history; \
	fi
	@if [ -f "src/endpoints/log_collector/alembic.ini" ]; then \
		echo "$(YELLOW)Log Collector:$(NC)"; \
		cd src/endpoints/log_collector && \
		export DATABASE_URL="postgresql://$(POSTGRES_USER):$(POSTGRES_PASSWORD)@$(POSTGRES_HOST):$(POSTGRES_PORT)/$(POSTGRES_DB)" && \
		PYTHONPATH="$(CURDIR)" "$(CURDIR)/$(ALEMBIC)" history; \
	fi

postgres-migrate-current: venv ## Affiche la version actuelle des migrations Alembic
	@echo "$(BLUE)Version actuelle des migrations:$(NC)"
	@if [ ! -d "$(VENV)" ]; then \
		echo "$(RED)✗ Virtual environment n'existe pas. Exécutez 'make setup'$(NC)"; \
		exit 1; \
	fi
	@if [ ! -f "$(CURDIR)/$(ALEMBIC)" ]; then \
		echo "$(RED)✗ Alembic n'est pas installé. Exécutez 'make install-dev'$(NC)"; \
		exit 1; \
	fi
	@if [ -f "src/endpoints/demo_api/alembic.ini" ]; then \
		echo "$(YELLOW)Demo API:$(NC)"; \
		cd src/endpoints/demo_api && \
		export DATABASE_URL="postgresql://$(POSTGRES_USER):$(POSTGRES_PASSWORD)@$(POSTGRES_HOST):$(POSTGRES_PORT)/$(POSTGRES_DB)" && \
		PYTHONPATH="$(CURDIR)" "$(CURDIR)/$(ALEMBIC)" current || echo "  Aucune migration appliquée"; \
	fi
	@if [ -f "src/endpoints/log_collector/alembic.ini" ]; then \
		echo "$(YELLOW)Log Collector:$(NC)"; \
		cd src/endpoints/log_collector && \
		export DATABASE_URL="postgresql://$(POSTGRES_USER):$(POSTGRES_PASSWORD)@$(POSTGRES_HOST):$(POSTGRES_PORT)/$(POSTGRES_DB)" && \
		PYTHONPATH="$(CURDIR)" "$(CURDIR)/$(ALEMBIC)" current || echo "  Aucune migration appliquée"; \
	fi

postgres-migrate: postgres-migrate-upgrade ## Alias pour postgres-migrate-upgrade

postgres-backup: ## Crée une sauvegarde de la base de données PostgreSQL
	@echo "$(BLUE)Création d'une sauvegarde de la base de données...$(NC)"
	@mkdir -p backups
	@BACKUP_FILE=backups/postgres_backup_$$(date +%Y%m%d_%H%M%S).sql; \
	if docker ps --format '{{.Names}}' | grep -q "^$(POSTGRES_CONTAINER)$$"; then \
		docker exec $(POSTGRES_CONTAINER) pg_dump -U $(POSTGRES_USER) $(POSTGRES_DB) > $$BACKUP_FILE; \
		echo "$(GREEN)✓ Sauvegarde créée: $$BACKUP_FILE$(NC)"; \
	else \
		echo "$(RED)✗ PostgreSQL n'est pas en cours d'exécution$(NC)"; \
	fi

postgres-restore: ## Restaure une sauvegarde PostgreSQL (usage: make postgres-restore BACKUP_FILE=backups/file.sql)
	@if [ -z "$(BACKUP_FILE)" ]; then \
		echo "$(RED)✗ Spécifiez le fichier de sauvegarde: make postgres-restore BACKUP_FILE=backups/file.sql$(NC)"; \
		exit 1; \
	fi
	@echo "$(BLUE)Restauration de la sauvegarde $(BACKUP_FILE)...$(NC)"
	@if docker ps --format '{{.Names}}' | grep -q "^$(POSTGRES_CONTAINER)$$"; then \
		cat $(BACKUP_FILE) | docker exec -i $(POSTGRES_CONTAINER) psql -U $(POSTGRES_USER) -d $(POSTGRES_DB); \
		echo "$(GREEN)✓ Sauvegarde restaurée$(NC)"; \
	else \
		echo "$(RED)✗ PostgreSQL n'est pas en cours d'exécution$(NC)"; \
	fi

# Development workflow
dev-setup: setup ## Configuration complète pour le développement
	@echo "$(GREEN)✓ Environnement de développement configuré$(NC)"

dev-test: test-coverage-parallel ## Exécute les tests avec couverture en parallèle (workflow de développement)
	@echo "$(GREEN)✓ Tests de développement terminés$(NC)"

dev-check: format lint type-check ## Vérifie le code avant commit (format, lint, types)
	@echo "$(GREEN)✓ Vérifications de développement terminées$(NC)"

pre-commit: format lint-fix type-check test-warnings test-coverage ## Préparation avant commit (format, lint, types, tests)
	@echo "$(GREEN)✓ Code prêt pour le commit$(NC)"

# Documentation
docs: ## Génère la documentation (si applicable)
	@echo "$(BLUE)Génération de la documentation...$(NC)"
	@echo "$(YELLOW)Documentation non configurée$(NC)"

# Verification
verify: check-all test-coverage ## Vérifie tout (checks + tests avec couverture)
	@echo "$(GREEN)✓ Vérification complète terminée$(NC)"

# Quick commands
quick-test: ## Test rapide (unit tests seulement)
	$(PYTEST) -m unit -v --tb=short

quick-check: format-check lint ## Vérification rapide (format + lint seulement)
	@echo "$(GREEN)✓ Vérification rapide terminée$(NC)"

# Info commands
info: ## Affiche les informations sur l'environnement
	@echo "$(BLUE)Informations sur l'environnement:$(NC)"
	@echo "  Python: $$($(PYTHON) --version)"
	@echo "  Virtual env: $(VENV)"
	@if [ -d "$(VENV)" ]; then \
		echo "  Status: $(GREEN)✓ Actif$(NC)"; \
	else \
		echo "  Status: $(RED)✗ Inactif$(NC)"; \
	fi
	@echo "  pytest: $$($(PYTEST) --version 2>/dev/null || echo 'Non installé')"
	@echo "  black: $$($(BLACK) --version 2>/dev/null || echo 'Non installé')"
	@echo "  mypy: $$($(MYPY) --version 2>/dev/null || echo 'Non installé')"
	@echo "  ruff: $$($(RUFF) --version 2>/dev/null || echo 'Non installé')"

