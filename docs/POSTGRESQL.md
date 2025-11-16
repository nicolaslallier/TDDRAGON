# Guide PostgreSQL

Ce guide explique comment utiliser PostgreSQL avec le projet TDDRAGON via le Makefile.

## Configuration

### Variables d'environnement

Créez un fichier `.env` à la racine du projet avec les variables suivantes :

```bash
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=tddragon
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
```

Ou utilisez le fichier `.env.example` comme modèle :

```bash
cp .env.example .env
```

### Configuration Docker

PostgreSQL est configuré dans `docker-compose.yml` et démarre automatiquement avec :

```bash
make docker-up
```

## Commandes disponibles

### Gestion de base de données

```bash
make postgres-up          # Démarre PostgreSQL via Docker
make postgres-down        # Arrête PostgreSQL
make postgres-status      # Vérifie le statut de PostgreSQL
make postgres-connect     # Se connecte à PostgreSQL via psql
```

### Création et gestion de bases de données

```bash
make postgres-create-db   # Crée la base de données
make postgres-drop-db     # Supprime la base de données (demande confirmation)
make postgres-reset       # Réinitialise la base de données (supprime et recrée)
```

### Migrations Alembic

```bash
make postgres-migrate              # Applique toutes les migrations en attente
make postgres-migrate-upgrade      # Applique toutes les migrations en attente
make postgres-migrate-downgrade    # Annule la dernière migration
make postgres-migrate-history      # Affiche l'historique des migrations
make postgres-migrate-current      # Affiche la version actuelle
```

### Sauvegarde et restauration

```bash
make postgres-backup               # Crée une sauvegarde de la base de données
make postgres-restore BACKUP_FILE=backups/file.sql  # Restaure une sauvegarde
```

## Workflow de développement

### Configuration initiale

1. **Démarrer PostgreSQL** :
   ```bash
   make docker-up
   # ou seulement PostgreSQL
   make postgres-up
   ```

2. **Créer la base de données** :
   ```bash
   make postgres-create-db
   ```

3. **Appliquer les migrations** :
   ```bash
   make postgres-migrate
   ```

### Développement quotidien

```bash
# Vérifier le statut
make postgres-status

# Se connecter à la base de données
make postgres-connect

# Appliquer les nouvelles migrations
make postgres-migrate

# Voir l'historique des migrations
make postgres-migrate-history
```

### Réinitialisation de la base de données

```bash
# Réinitialiser complètement (supprime et recrée)
make postgres-reset
make postgres-migrate
```

## Connexion manuelle

### Via Docker

```bash
docker exec -it postgres-db psql -U postgres -d tddragon
```

### Via psql local (si PostgreSQL est installé localement)

```bash
psql -h localhost -p 5432 -U postgres -d tddragon
```

## Migrations Alembic

Le projet utilise Alembic pour gérer les migrations de schéma de base de données.

### Structure des migrations

Les migrations sont organisées par endpoint :

```
src/endpoints/log_collector/alembic/
```

### Créer une nouvelle migration

Pour chaque endpoint, créez une migration dans son répertoire alembic :

```bash
# Pour log_collector
cd src/endpoints/log_collector
alembic revision --autogenerate -m "Description de la migration"
```

### Appliquer les migrations

```bash
# Toutes les migrations
make postgres-migrate

# Migration spécifique pour un endpoint
cd src/endpoints/log_collector
alembic upgrade head
```

### Annuler une migration

```bash
# Annuler la dernière migration
make postgres-migrate-downgrade

# Annuler plusieurs migrations
cd src/endpoints/log_collector
alembic downgrade -2  # Annule les 2 dernières migrations
```

## Sauvegarde et restauration

### Créer une sauvegarde

```bash
make postgres-backup
```

Les sauvegardes sont créées dans le répertoire `backups/` avec un nom horodaté :
```
backups/postgres_backup_20240115_143022.sql
```

### Restaurer une sauvegarde

```bash
make postgres-restore BACKUP_FILE=backups/postgres_backup_20240115_143022.sql
```

### Sauvegarde manuelle

```bash
docker exec postgres-db pg_dump -U postgres tddragon > backup.sql
```

### Restauration manuelle

```bash
cat backup.sql | docker exec -i postgres-db psql -U postgres -d tddragon
```

## Dépannage

### PostgreSQL ne démarre pas

```bash
# Vérifier les logs Docker
docker logs postgres-db

# Vérifier le statut
make postgres-status

# Redémarrer
make postgres-down
make postgres-up
```

### Erreur de connexion

1. Vérifier que PostgreSQL est en cours d'exécution :
   ```bash
   make postgres-status
   ```

2. Vérifier les variables d'environnement dans `.env`

3. Vérifier que le conteneur Docker est démarré :
   ```bash
   docker ps | grep postgres-db
   ```

### Réinitialiser complètement

```bash
# Arrêter PostgreSQL
make postgres-down

# Supprimer le volume Docker (ATTENTION: supprime toutes les données)
docker volume rm tddragon_postgres-data

# Redémarrer
make docker-up
make postgres-create-db
make postgres-migrate
```

## Variables d'environnement

Le Makefile lit les variables depuis le fichier `.env`. Les valeurs par défaut sont :

- `POSTGRES_HOST`: `localhost`
- `POSTGRES_PORT`: `5432`
- `POSTGRES_DB`: `tddragon`
- `POSTGRES_USER`: `postgres`
- `POSTGRES_PASSWORD`: `postgres`

## Intégration avec les tests

Pour les tests d'intégration, utilisez une base de données de test séparée :

```bash
# Créer une base de données de test
POSTGRES_DB=tddragon_test make postgres-create-db
```

Configurez les tests pour utiliser cette base de données via les variables d'environnement.

## Sécurité

⚠️ **Important** : 

- Ne commitez jamais le fichier `.env` contenant les mots de passe
- Utilisez des mots de passe forts en production
- Limitez l'accès réseau à PostgreSQL en production
- Utilisez des variables d'environnement sécurisées pour les secrets

## Ressources

- [Documentation PostgreSQL](https://www.postgresql.org/docs/)
- [Documentation Alembic](https://alembic.sqlalchemy.org/)
- [Documentation SQLAlchemy](https://docs.sqlalchemy.org/)

