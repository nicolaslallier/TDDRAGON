# Guide d'utilisation du Makefile

Le Makefile centralise toutes les commandes de développement pour simplifier le workflow.

## Commandes principales

### Configuration initiale

```bash
make setup          # Configuration complète (venv + dépendances)
make dev-setup      # Configuration pour le développement
make help           # Affiche toutes les commandes disponibles
make info           # Affiche les informations sur l'environnement
```

### Tests

```bash
make test                   # Tous les tests
make test-unit              # Tests unitaires seulement
make test-integration        # Tests d'intégration seulement
make test-regression        # Tests de régression seulement
make test-e2e               # Tests end-to-end seulement
make test-coverage          # Tests avec couverture HTML
make test-coverage-xml       # Tests avec couverture XML
make test-warnings           # Tests avec vérification des warnings
make quick-test             # Test rapide (unit tests seulement)
```

### Qualité du code

```bash
make format                 # Formate le code (Black + isort)
make format-check           # Vérifie le formatage sans modifier
make lint                   # Exécute le linter Ruff
make lint-fix               # Corrige automatiquement les erreurs
make type-check             # Vérifie les types avec mypy
make check-all              # Tous les checks (format, lint, types, tests)
make pre-commit             # Préparation avant commit
make quick-check            # Vérification rapide (format + lint)
```

### Docker

```bash
make docker-build           # Construit les images Docker
make docker-up              # Démarre les conteneurs
make docker-down            # Arrête les conteneurs
make docker-logs            # Affiche les logs
make docker-dev             # Mode développement
make docker-prod            # Mode production
make docker-clean           # Nettoie les conteneurs et images
```

### Nettoyage

```bash
make clean                  # Nettoie les fichiers générés
make clean-venv             # Supprime le virtual environment
make clean-all              # Nettoie tout (fichiers + venv)
```

### Workflow de développement

```bash
make dev-setup              # Configuration initiale
make dev-test               # Tests avec couverture
make dev-check              # Vérifications avant commit
make pre-commit             # Préparation complète avant commit
make verify                 # Vérification complète (checks + tests)
```

### CI/CD

```bash
make ci                     # Pipeline CI complète (install + checks + tests)
```

## Exemples d'utilisation

### Workflow quotidien

```bash
# 1. Configuration initiale (une seule fois)
make setup

# 2. Développement quotidien
make format                 # Formater le code
make lint-fix               # Corriger les erreurs de linting
make test-unit              # Tester rapidement
make test-coverage          # Vérifier la couverture

# 3. Avant de commiter
make pre-commit             # Vérifie tout et prépare le code
```

### Workflow avant commit

```bash
# Option 1: Préparation complète automatique
make pre-commit

# Option 2: Vérifications manuelles
make format-check           # Vérifier le formatage
make lint                   # Vérifier le linting
make type-check             # Vérifier les types
make test-warnings          # Vérifier les warnings
make test-coverage          # Vérifier la couverture
```

### Tests spécifiques

```bash
# Tests unitaires seulement (rapide)
make test-unit

# Tests d'intégration seulement
make test-integration

# Tests de régression seulement
make test-regression

# Tous les tests avec couverture
make test-coverage
```

### Docker

```bash
# Développement local avec Docker
make docker-dev             # Démarre en mode développement

# Production avec Docker
make docker-prod            # Démarre en mode production

# Voir les logs
make docker-logs

# Arrêter
make docker-down
```

## Commandes combinées

Le Makefile permet aussi d'exécuter plusieurs commandes en une seule fois:

```bash
# Vérification complète avant commit
make check-all test-coverage

# Nettoyage et reconstruction
make clean docker-build

# Setup complet avec vérification
make setup verify
```

## Variables d'environnement

Le Makefile utilise ces variables par défaut:

- `PYTHON`: `python3`
- `VENV`: `.venv`
- `VENV_BIN`: `.venv/bin`

Vous pouvez les surcharger:

```bash
PYTHON=python3.11 make setup
VENV=myenv make setup
```

## Dépannage

### Le virtual environment n'est pas créé

```bash
make venv                   # Crée le venv
make install-dev            # Installe les dépendances
```

### Les commandes ne fonctionnent pas

Vérifiez que le virtual environment est activé ou utilisez les chemins complets:

```bash
make info                   # Vérifie l'état de l'environnement
```

### Nettoyage complet

```bash
make clean-all              # Nettoie tout et supprime le venv
make setup                  # Reconfigure depuis le début
```

## Intégration avec les outils

Le Makefile utilise les outils installés dans le virtual environment:

- `pytest` pour les tests
- `black` et `isort` pour le formatage
- `ruff` pour le linting
- `mypy` pour la vérification des types

Tous ces outils sont installés automatiquement avec `make install-dev`.

## Commandes personnalisées

Pour ajouter vos propres commandes, éditez le `Makefile` et ajoutez:

```makefile
ma-commande: ## Description de ma commande
	@echo "Exécution de ma commande..."
	# Votre code ici
	@echo "✓ Terminé"
```

Puis utilisez `make help` pour voir votre nouvelle commande dans la liste.

